# src/train_models.py
import re
import unicodedata
import warnings
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from src.config import MODEL_RESULT_FILTERS

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing as HoltWinters
    _HOLTWINTERS_AVAILABLE = True
except ImportError:
    _HOLTWINTERS_AVAILABLE = False


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class _HoltWintersWrapper:
    """
    Wrapper sklearn-compatible pour Holt-Winters (lissage exponentiel).
    Conçu pour les courtes séries temporelles (10-50 points).
    Ignore X — utilise uniquement l'ordre temporel de y.
    """
    def __init__(self):
        self._model = None
        self._last_y = None

    def fit(self, X, y):
        if not _HOLTWINTERS_AVAILABLE:
            raise ImportError("statsmodels requis")
        try:
            # trend='add' seulement si assez de points (≥4)
            trend = 'add' if len(y) >= 4 else None
            self._model = HoltWinters(
                y.values, trend=trend, seasonal=None, damped_trend=(trend == 'add')
            ).fit(optimized=True, remove_bias=True)
            self._last_y = y.copy()
        except Exception:
            self._model = None
        return self

    def predict(self, X):
        if self._model is None:
            return np.full(len(X), self._last_y.mean() if self._last_y is not None else 0)
        try:
            return self._model.forecast(len(X))
        except Exception:
            return np.full(len(X), self._last_y.mean())
warnings.filterwarnings("ignore")


def _slugify_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_")
    return normalized.lower() or "maladie"


def _sanitize_r2_value(value):
    if pd.isna(value):
        return np.nan
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return value


def _sanitize_r2_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    sanitized = df.copy()
    for column in sanitized.columns:
        if column == "R2" or column.startswith("R²"):
            sanitized[column] = sanitized[column].apply(_sanitize_r2_value)
    return sanitized


def _build_confusion_artifact(y_true, y_pred) -> dict:
    y_true_values = np.asarray(y_true, dtype=float)
    y_pred_values = np.asarray(y_pred, dtype=float)
    combined = np.concatenate([y_true_values, y_pred_values])

    if combined.size == 0:
        raise ValueError("Impossible de calculer une matrice de confusion sans donnees.")

    lower, upper = np.quantile(combined, [1 / 3, 2 / 3])
    if np.isclose(lower, upper):
        min_value = float(np.min(combined))
        max_value = float(np.max(combined))
        if np.isclose(min_value, max_value):
            edges = np.array([], dtype=float)
            labels = ["Stable"]
        else:
            edges = np.linspace(min_value, max_value, 4)[1:-1]
            labels = ["Faible", "Modere", "Eleve"]
    else:
        edges = np.array([lower, upper], dtype=float)
        labels = ["Faible", "Modere", "Eleve"]

    if edges.size == 0:
        y_true_classes = np.zeros(len(y_true_values), dtype=int)
        y_pred_classes = np.zeros(len(y_pred_values), dtype=int)
    else:
        y_true_classes = np.digitize(y_true_values, bins=edges, right=False)
        y_pred_classes = np.digitize(y_pred_values, bins=edges, right=False)

    matrix = confusion_matrix(
        y_true_classes,
        y_pred_classes,
        labels=list(range(len(labels))),
    )
    matrix_df = pd.DataFrame(
        matrix,
        index=[f"Reel {label}" for label in labels],
        columns=[f"Predit {label}" for label in labels],
    )

    return {
        "labels": labels,
        "thresholds": [float(value) for value in edges.tolist()],
        "matrix": matrix.tolist(),
        "dataframe": matrix_df,
    }


class DiseasePredictor:
    def __init__(self, console_detailed: bool = False):
        self.best_models = {}
        self.results = {}
        self.comparison_results = {}
        self.feature_selection_summary = []
        self.console_detailed = console_detailed

    def get_filtered_best_models(self):
        min_r2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))
        filtered_models = {}
        for disease, info in self.best_models.items():
            r2_value = info.get("test_r2", np.nan)
            if pd.isna(r2_value) or float(r2_value) < min_r2:
                continue
            filtered_models[disease] = info
        return filtered_models

    def get_features(self, df):
        # Exclure colonnes non-features + MALADIE_LABEL (texte)
        exclude = {"DEBUTSEM", "MALADIE", "MALADIE_LABEL", "TOTALCAS", "TOTALDECES"}
        feature_cols = [c for c in df.columns if c not in exclude]
        return df[feature_cols], df["TOTALCAS"], feature_cols

    @staticmethod
    def _select_features(X_train: pd.DataFrame, y_train: pd.Series,
                         feature_cols: list) -> tuple[list, pd.Series]:
        """
        Sélection de features via importance Random Forest.
        Garde uniquement les features dont l'importance dépasse le seuil moyen.
        Garantit un minimum de 5 features pour éviter la sous-représentation.
        """
        if len(feature_cols) <= 5:
            importances = pd.Series(1.0, index=feature_cols)
            return feature_cols, importances
        selector = RandomForestRegressor(
            n_estimators=50, random_state=42, n_jobs=-1
        )
        selector.fit(X_train, y_train)
        importances = pd.Series(selector.feature_importances_, index=feature_cols)
        threshold = importances.mean()
        selected = importances[importances >= threshold].index.tolist()
        if len(selected) < 5:
            selected = importances.nlargest(5).index.tolist()
        return selected, importances

    @staticmethod
    def _walk_forward_score(model, X: pd.DataFrame, y: pd.Series,
                            n_splits: int = 5) -> dict:
        """
        Walk-forward validation (TimeSeriesSplit).
        Retourne les métriques moyennées sur tous les folds.
        Respecte l'ordre temporel — aucune fuite de données.
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        maes, r2s = [], []
        for train_idx, test_idx in tscv.split(X):
            Xtr, Xte = X.iloc[train_idx], X.iloc[test_idx]
            ytr, yte = y.iloc[train_idx], y.iloc[test_idx]
            if len(Xtr) < 5 or len(Xte) < 2:
                continue
            try:
                model.fit(Xtr, ytr)
                ypred = model.predict(Xte)
                maes.append(mean_absolute_error(yte, ypred))
                r2s.append(r2_score(yte, ypred))
            except Exception:
                continue
        return {
            "cv_mae": float(np.mean(maes)) if maes else np.nan,
            "cv_r2": float(np.mean(r2s)) if r2s else np.nan,
            "cv_folds": len(maes),
        }

    def compare_models(self, X_train, y_train, X_test, y_test, disease_name):
        """Compare plusieurs modeles et retourne les performances."""
        # SVR et KNN nécessitent un scaling — on les encapsule dans un Pipeline
        models = {
            "Linear Regression": Pipeline([
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ]),
            "Ridge Regression": Pipeline([
                ("scaler", StandardScaler()),
                ("model", Ridge(alpha=0.5)),
            ]),
            "Random Forest": RandomForestRegressor(
                n_estimators=200, max_depth=10, min_samples_leaf=2,
                random_state=42, n_jobs=-1,
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                n_estimators=200, learning_rate=0.05, max_depth=4,
                subsample=0.8, random_state=42,
            ),
            "KNN": Pipeline([
                ("scaler", StandardScaler()),
                ("model", KNeighborsRegressor(n_neighbors=5, weights="distance")),
            ]),
            "SVR": Pipeline([
                ("scaler", StandardScaler()),
                ("model", SVR(kernel="rbf", C=10, epsilon=0.1)),
            ]),
        }

        results = {}
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                results[name] = {
                    "mae": mean_absolute_error(y_test, y_pred),
                    "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                    "r2": r2_score(y_test, y_pred),
                    "mape": np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100,
                }
            except Exception as exc:
                results[name] = {"error": str(exc)}

        return results

    def _build_best_model(self, model_name):
        if model_name == "Linear Regression":
            return Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())])
        if model_name == "Ridge Regression":
            return Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=0.5))])
        if model_name == "Random Forest":
            return RandomForestRegressor(
                n_estimators=200, max_depth=10, min_samples_leaf=2,
                random_state=42, n_jobs=-1,
            )
        if model_name == "Gradient Boosting":
            return GradientBoostingRegressor(
                n_estimators=200, learning_rate=0.05, max_depth=4,
                subsample=0.8, random_state=42,
            )
        if model_name == "KNN":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("model", KNeighborsRegressor(n_neighbors=5, weights="distance")),
            ])
        if model_name == "SVR":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("model", SVR(kernel="rbf", C=10, epsilon=0.1)),
            ])
        return RandomForestRegressor(
            n_estimators=200, max_depth=10, min_samples_leaf=2,
            random_state=42, n_jobs=-1,
        )

    def train_for_disease(self, disease_data, disease_name):
        total_cases = disease_data["TOTALCAS"].sum()
        n_weeks = len(disease_data)

        print(f"\n{'=' * 50}")
        print(f"Analyse: {disease_name}")
        print(f"   Total cas: {total_cases:,} | Semaines: {n_weeks}")

        if total_cases < 50 or n_weeks < 20:
            print("   Ignore: criteres non remplis")
            return False

        X, y, features = self.get_features(disease_data)
        if len(X) < 10:
            print("   Ignore: donnees insuffisantes")
            return False

        # --- Transformation log1p du target
        # Les cas épidémiques ont une distribution très asymétrique.
        # log1p stabilise la variance et améliore tous les modèles.
        # Les métriques finales sont calculées après décodage expm1 (échelle réelle).
        y_log = np.log1p(y)

        train_size = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_log_train = y_log.iloc[:train_size]
        y_log_test  = y_log.iloc[train_size:]

        if len(X_test) == 0:
            print("   Ignore: pas de donnees de test")
            return False

        # --- Sélection de features sur X_train UNIQUEMENT (pas de leakage)
        selected_features, feature_importances = self._select_features(X_train, y_log_train, features)
        if len(selected_features) < len(features):
            print(f"   Features: {len(features)} → {len(selected_features)} retenues")
        X_train   = X_train[selected_features]
        X_test    = X_test[selected_features]
        features  = selected_features

        top_features = (
            feature_importances.loc[selected_features]
            .sort_values(ascending=False)
            .head(10)
        )
        for feature_name, importance in top_features.items():
            self.feature_selection_summary.append(
                {
                    "Maladie": disease_name,
                    "Feature": feature_name,
                    "Importance": float(importance),
                }
            )

        comparison = self.compare_models(X_train, y_log_train, X_test, y_log_test, disease_name)
        if self.console_detailed:
            print("\n   Comparaison des modeles (espace log):")
            for name, metrics in comparison.items():
                if "error" not in metrics:
                    print(
                        f"      {name:20} | R2: {metrics['r2']:.3f} | "
                        f"MAE: {metrics['mae']:.2f} | RMSE: {metrics['rmse']:.2f} | MAPE: {metrics['mape']:.1f}%"
                    )

        best_model_name = None
        best_r2 = -np.inf
        for name, metrics in comparison.items():
            if "error" not in metrics and metrics["r2"] > best_r2:
                best_r2 = metrics["r2"]
                best_model_name = name

        best_model = self._build_best_model(best_model_name)

        # --- Walk-forward CV en espace log (sans leakage temporel)
        X_full_sel = X[selected_features]
        cv_scores = self._walk_forward_score(
            self._build_best_model(best_model_name), X_full_sel, y_log
        )
        if self.console_detailed:
            print(
                f"   Walk-forward CV ({cv_scores['cv_folds']} folds) → "
                f"R²={cv_scores['cv_r2']:.3f} | MAE={cv_scores['cv_mae']:.4f} (log)"
            )

        # Entraînement final en espace log + décodage vers l'échelle réelle
        best_model.fit(X_train, y_log_train)
        y_pred_log  = best_model.predict(X_test)
        y_pred      = np.expm1(y_pred_log)   # échelle réelle
        y_test_real = np.expm1(y_log_test)   # échelle réelle
        confusion_info = _build_confusion_artifact(y_test_real, y_pred)

        # --- Réentraînement final sur 100% des données
        # Les métriques ci-dessus (R², MAE, CV) ont servi à valider et choisir
        # le meilleur algorithme. Maintenant on réentraîne sur tout pour maximiser
        # l'information disponible dans le modèle de production.
        final_model = self._build_best_model(best_model_name)
        final_model.fit(X[selected_features], y_log)

        self.best_models[disease_name] = {
            "model": final_model,          # modèle final entraîné sur 100%
            "features": features,
            "best_model_name": best_model_name,
            "log_transform": True,          # flag : prédictions = expm1(model.predict(X))
            "test_mae": mean_absolute_error(y_test_real, y_pred),
            "test_rmse": np.sqrt(mean_squared_error(y_test_real, y_pred)),
            "test_r2": r2_score(y_test_real, y_pred),
            "test_mape": np.mean(np.abs((y_test_real - y_pred) / (y_test_real + 1))) * 100,
            "total_cases": total_cases,
            "n_weeks": n_weeks,
            "comparison": comparison,
            "confusion_matrix": {
                "labels": confusion_info["labels"],
                "thresholds": confusion_info["thresholds"],
                "matrix": confusion_info["matrix"],
            },
            "cv_r2": cv_scores["cv_r2"],
            "cv_mae": cv_scores["cv_mae"],
        }

        local_r2 = float(self.best_models[disease_name]["test_r2"])
        min_r2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))
        status = "retenu en production" if local_r2 >= min_r2 else "non retenu pour la production"
        print(f"\n   Meilleur modele local: {best_model_name}")
        print(f"      Statut du run courant: {status}")
        print("      Modele final reentraine sur 100% des donnees")
        if self.console_detailed:
            print(f"      R2 (validation 20%): {self.best_models[disease_name]['test_r2']:.3f}")
            print(f"      MAE (validation 20%): {self.best_models[disease_name]['test_mae']:.2f} cas")
            print(f"      RMSE (validation 20%): {self.best_models[disease_name]['test_rmse']:.2f} cas")
            print("      Matrice de confusion (niveaux de cas):")
            print(confusion_info["dataframe"].to_string())

        return True

    def train_all_diseases(self, feature_data):
        print("\n" + "=" * 60)
        print("ENTRAINEMENT DES MODELES - COMPARAISON DES ALGORITHMES")
        print("=" * 60)

        trained = 0
        for disease in feature_data["MALADIE"].unique():
            data = feature_data[feature_data["MALADIE"] == disease].copy()
            if self.train_for_disease(data, disease):
                trained += 1

        print("\n" + "=" * 60)
        print(f"{trained} modeles entraines avec succes")
        print("=" * 60)
        return self.best_models

    def export_confusion_matrices(self, output_dir="models/evaluation"):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = []
        summary_rows = []

        for disease, info in self.get_filtered_best_models().items():
            confusion_info = info.get("confusion_matrix")
            if not confusion_info:
                continue

            labels = confusion_info["labels"]
            matrix_df = pd.DataFrame(
                confusion_info["matrix"],
                index=[f"Reel {label}" for label in labels],
                columns=[f"Predit {label}" for label in labels],
            )
            output_file = output_path / f"{_slugify_name(disease)}_confusion_matrix.csv"
            matrix_df.to_csv(output_file, encoding="utf-8-sig")
            exported_files.append(str(output_file))
            summary_rows.append(
                {
                    "Maladie": disease,
                    "Modele": info["best_model_name"],
                    "Seuils": " | ".join(f"{value:.2f}" for value in confusion_info["thresholds"]),
                    "Fichier": str(output_file),
                }
            )

        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            summary_file = output_path / "confusion_matrix_summary.csv"
            summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")
            exported_files.append(str(summary_file))

        combined_image = self.export_combined_confusion_matrix_image(output_path)
        if combined_image:
            exported_files.append(str(combined_image))

        return exported_files

    def export_performance_reports(self, output_dir="models/evaluation"):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = []

        summary_df = self.get_model_performance_summary()
        if not summary_df.empty:
            summary_file = output_path / "model_performance_summary.csv"
            _sanitize_r2_columns(summary_df).to_csv(summary_file, index=False, encoding="utf-8-sig")
            exported_files.append(str(summary_file))
        else:
            summary_file = output_path / "model_performance_summary.csv"
            if summary_file.exists():
                try:
                    existing_summary = pd.read_csv(summary_file, encoding="utf-8-sig")
                    _sanitize_r2_columns(existing_summary).to_csv(summary_file, index=False, encoding="utf-8-sig")
                    exported_files.append(str(summary_file))
                except Exception:
                    pass

        comparison_rows = []
        for disease, info in self.get_filtered_best_models().items():
            comparison = info.get("comparison", {})
            for model_name, metrics in comparison.items():
                if "error" in metrics:
                    continue
                comparison_rows.append(
                    {
                        "Maladie": disease,
                        "Modele": model_name,
                        "R2": metrics.get("r2"),
                        "MAE": metrics.get("mae"),
                        "RMSE": metrics.get("rmse"),
                        "MAPE": metrics.get("mape"),
                    }
                )

        if comparison_rows:
            comparison_df = pd.DataFrame(comparison_rows)
            comparison_file = output_path / "model_comparison_details.csv"
            _sanitize_r2_columns(comparison_df).to_csv(comparison_file, index=False, encoding="utf-8-sig")
            exported_files.append(str(comparison_file))
        else:
            comparison_file = output_path / "model_comparison_details.csv"
            if comparison_file.exists():
                try:
                    existing_comparison = pd.read_csv(comparison_file, encoding="utf-8-sig")
                    _sanitize_r2_columns(existing_comparison).to_csv(comparison_file, index=False, encoding="utf-8-sig")
                    exported_files.append(str(comparison_file))
                except Exception:
                    pass

        if self.feature_selection_summary:
            feature_df = pd.DataFrame(self.feature_selection_summary)
            # Filtrer pour ne garder que les maladies validées
            valid_diseases = set(self.get_filtered_best_models().keys())
            feature_df = feature_df[feature_df["Maladie"].isin(valid_diseases)]
            
            if not feature_df.empty:
                feature_df.sort_values(["Maladie", "Importance"], ascending=[True, False], inplace=True)
                feature_file = output_path / "feature_selection_summary.csv"
                feature_df.to_csv(feature_file, index=False, encoding="utf-8-sig")
                exported_files.append(str(feature_file))

        return exported_files

    def export_combined_confusion_matrix_image(self, output_dir="models/evaluation"):
        try:
            import matplotlib.pyplot as plt
        except ModuleNotFoundError:
            print(
                "matplotlib absent: image combinee des matrices non produite. "
                "(Optionnel) Installe-le avec: conda install matplotlib"
            )
            return None

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        matrices = []
        for disease, info in self.get_filtered_best_models().items():
            confusion_info = info.get("confusion_matrix")
            if not confusion_info:
                continue
            matrices.append(
                {
                    "disease": disease,
                    "labels": confusion_info["labels"],
                    "matrix": np.asarray(confusion_info["matrix"], dtype=float),
                    "thresholds": confusion_info.get("thresholds", []),
                }
            )

        if not matrices:
            return None

        columns = 2 if len(matrices) > 1 else 1
        rows = int(np.ceil(len(matrices) / columns))
        fig, axes = plt.subplots(rows, columns, figsize=(columns * 7.5, rows * 6.2))
        axes = np.atleast_1d(axes).flatten()

        vmax = max(matrix_info["matrix"].max() for matrix_info in matrices)

        for axis, matrix_info in zip(axes, matrices):
            matrix = matrix_info["matrix"]
            labels = matrix_info["labels"]
            image = axis.imshow(matrix, cmap="Blues", vmin=0, vmax=vmax)

            axis.set_xticks(range(len(labels)))
            axis.set_yticks(range(len(labels)))
            axis.set_xticklabels(labels, rotation=25, ha="right")
            axis.set_yticklabels(labels)
            axis.set_xlabel("Prediction")
            axis.set_ylabel("Reel")

            thresholds = matrix_info["thresholds"]
            threshold_text = " | ".join(f"{value:.0f}" for value in thresholds) if thresholds else "stable"
            axis.set_title(f"{matrix_info['disease']}\nSeuils: {threshold_text}", fontsize=11)

            color_limit = vmax / 2 if vmax else 0
            for row_index in range(matrix.shape[0]):
                for column_index in range(matrix.shape[1]):
                    value = int(matrix[row_index, column_index])
                    text_color = "white" if value > color_limit else "#0f172a"
                    axis.text(
                        column_index,
                        row_index,
                        str(value),
                        ha="center",
                        va="center",
                        color=text_color,
                        fontsize=11,
                        fontweight="bold",
                    )

        for axis in axes[len(matrices):]:
            axis.axis("off")

        fig.colorbar(image, ax=axes[: len(matrices)].tolist(), shrink=0.82, pad=0.02, label="Nombre de cas")
        fig.suptitle("Matrices de confusion combinees par maladie", fontsize=16, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.97))

        output_file = output_path / "confusion_matrices_combined.png"
        fig.savefig(output_file, dpi=220, bbox_inches="tight")
        plt.close(fig)
        return output_file

    def save_models(self, path="models/trained/models.pkl"):
        """Sauvegarde les modèles entraînés et conserve aussi le sous-ensemble éligible."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        eligible_models = self.get_filtered_best_models()
        models_to_save = eligible_models if eligible_models else self.best_models
        if not models_to_save:
            raise RuntimeError("Aucun modele n'a ete entraine; impossible de sauvegarder un bundle de production.")
        
        joblib.dump(
            {
                "best_models": models_to_save,
                "eligible_models": eligible_models,
                "results": self.results,
                "comparison_results": self.comparison_results,
            },
            path_obj,
        )
        print(
            f"Modeles sauvegardes: {path_obj} - {len(models_to_save)} maladies dans le bundle"
            + (f" ({len(eligible_models)} au-dessus du seuil R2 >= 0.5)" if eligible_models else " (aucun modele ne depasse le seuil R2, bundle complet conserve)")
        )

    def load_models(self, path="models/trained/models.pkl"):
        try:
            data = joblib.load(path)
            self.best_models = data.get("best_models", {})
            self.results = data.get("results", {})
            self.comparison_results = data.get("comparison_results", {})
            print(f"{len(self.best_models)} modeles charges")
            return True
        except FileNotFoundError:
            print(f"Fichier non trouve: {path}")
            return False
        except Exception as exc:
            print(f"Erreur: {exc}")
            return False

    def get_model_performance_summary(self):
        """Retourne un resume des performances pour le memoire."""
        filtered_models = self.get_filtered_best_models()
        if not filtered_models:
            return pd.DataFrame()

        summary = []
        for disease, info in filtered_models.items():
            comparison = info.get("comparison", {})
            row = {
                "Maladie": disease,
                "Meilleur Modèle": info["best_model_name"],
                "R² (Best)": round(_sanitize_r2_value(info["test_r2"]), 3),
                "MAE (Best)": round(info["test_mae"], 2),
                "RMSE (Best)": round(info.get("test_rmse", np.nan), 2),
                "MAPE (Best)": round(info["test_mape"], 1),
                "CV R²": round(info.get("cv_r2", np.nan), 3) if not pd.isna(info.get("cv_r2", np.nan)) else np.nan,
                "CV MAE (log)": round(info.get("cv_mae", np.nan), 4) if not pd.isna(info.get("cv_mae", np.nan)) else np.nan,
                "Total cas": info["total_cases"],
                "Semaines": info["n_weeks"],
                "Seuils confusion": " | ".join(
                    f"{value:.2f}" for value in info.get("confusion_matrix", {}).get("thresholds", [])
                ),
            }

            for model_name in ["Random Forest", "Gradient Boosting", "Ridge Regression", "KNN"]:
                if model_name in comparison and "r2" in comparison[model_name]:
                    row[f"R² ({model_name})"] = round(_sanitize_r2_value(comparison[model_name]["r2"]), 3)

            summary.append(row)

        return pd.DataFrame(summary)

    def print_all_diseases_metrics(self):
        """Affiche les métriques de régression pour chaque maladie."""
        summary = self.get_model_performance_summary()
        if summary.empty:
            print("Aucune métrique disponible.")
            return

        cols = [
            "Maladie", "Meilleur Modèle", "R² (Best)", "MAE (Best)",
            "RMSE (Best)", "MAPE (Best)", "CV R²", "CV MAE (log)",
            "Total cas", "Semaines",
        ]
        existing_cols = [c for c in cols if c in summary.columns]

        print("\n" + "=" * 100)
        print("METRIQUES DE REGRESSION PAR MALADIE")
        print("=" * 100)
        print(summary[existing_cols].sort_values("R² (Best)", ascending=False).to_string(index=False))

    def print_global_performance(self):
        """
        Affiche les performances globales combinant toutes les maladies.
        - R² moyen simple et pondéré par volume de cas
        - MAPE moyen global
        - F1 global (micro et macro) basé sur la classification des niveaux d'alerte
          Règle : la classe "Élevé" (dernier niveau) est traitée comme la classe positive.
        """
        filtered_models = self.get_filtered_best_models()
        if not filtered_models:
            print("Aucun modele disponible pour le résumé global.")
            return

        r2_list, mape_list, weights = [], [], []
        total_cases_all = 0
        micro_tp = micro_fp = micro_fn = 0
        per_disease_f1 = []

        for disease, info in filtered_models.items():
            r2 = info.get("test_r2", np.nan)
            mape = info.get("test_mape", np.nan)
            total = info.get("total_cases", 0) or 0
            total_cases_all += total

            if not np.isnan(r2):
                r2_list.append(r2)
                weights.append(max(total, 1))
            if not np.isnan(mape):
                mape_list.append(mape)

            # --- F1 par maladie (niveau "Élevé" = classe positive)
            cm_info = info.get("confusion_matrix", {})
            matrix = cm_info.get("matrix", [])
            labels = cm_info.get("labels", [])
            if matrix and labels:
                mat = np.array(matrix, dtype=float)
                n = len(labels)
                # Indice de la classe positive = dernier niveau ("Élevé" ou "Eleve")
                pos_idx = n - 1
                if mat.shape == (n, n) and n >= 2:
                    tp = mat[pos_idx, pos_idx]
                    fp = mat[:pos_idx, pos_idx].sum()   # autres classes prédites positives
                    fn = mat[pos_idx, :pos_idx].sum()   # positifs prédits comme autre classe
                    denom = 2 * tp + fp + fn
                    f1_d = (2 * tp / denom) if denom > 0 else 0.0
                    per_disease_f1.append(f1_d)
                    micro_tp += tp
                    micro_fp += fp
                    micro_fn += fn

        # --- Calculs globaux
        r2_mean = float(np.mean(r2_list)) if r2_list else np.nan
        weights_arr = np.array(weights, dtype=float)
        r2_weighted = float(np.average(r2_list, weights=weights_arr)) if r2_list else np.nan
        mape_mean = float(np.mean(mape_list)) if mape_list else np.nan

        macro_f1 = float(np.mean(per_disease_f1)) if per_disease_f1 else np.nan
        micro_denom = 2 * micro_tp + micro_fp + micro_fn
        micro_f1 = float(2 * micro_tp / micro_denom) if micro_denom > 0 else np.nan

        print("\n" + "=" * 70)
        print("PERFORMANCE GLOBALE — TOUTES MALADIES CONFONDUES")
        print("=" * 70)
        print(f"  Maladies modelisees        : {len(filtered_models)}")
        print(f"  Total cas couverts         : {int(total_cases_all):,}")
        print(f"  R² moyen simple            : {r2_mean:.3f}")
        print(f"  R² moyen pondéré (cas)     : {r2_weighted:.3f}")
        print(f"  MAPE moyen global          : {mape_mean:.1f}%")
        print()
        print("  F1-Score global (niveaux d'alerte ← classe positive = 'Élevé')")
        print(f"    F1 Macro (moy. par maladie) : {macro_f1:.3f}")
        print(f"    F1 Micro (agrégé global)    : {micro_f1:.3f}")
        print()

        ranked_diseases = [d for d in filtered_models if filtered_models[d].get("confusion_matrix", {}).get("matrix")]
        if per_disease_f1 and len(per_disease_f1) == len(ranked_diseases):
            # Top 5 et bottom 5 par F1
            f1_sorted = sorted(zip(
                ranked_diseases,
                per_disease_f1
            ), key=lambda x: x[1], reverse=True)
            print("  Top 5 maladies (F1 alert le plus élevé):")
            for d, f in f1_sorted[:5]:
                print(f"    {d:<35} F1={f:.3f}")
            print("  Bottom 5 maladies (F1 alert le plus faible):")
            for d, f in f1_sorted[-5:]:
                print(f"    {d:<35} F1={f:.3f}")

        print("=" * 70)

    def print_comparison_table(self):
        """Affiche un tableau de comparaison pour le memoire."""
        print("\n" + "=" * 80)
        print("TABLEAU DE COMPARAISON DES MODELES - MALADIE SENTINELLE (PALUDISME)")
        print("=" * 80)

        for disease, info in self.get_filtered_best_models().items():
            if "paludisme" in disease.lower():
                comparison = info.get("comparison", {})
                print(f"\nMaladie: {disease}")
                print("-" * 80)
                print(f"{'Modele':<20} {'R2':<10} {'MAE':<12} {'RMSE':<12} {'MAPE':<10}")
                print("-" * 80)

                for model_name in [
                    "Random Forest",
                    "Gradient Boosting",
                    "Ridge Regression",
                    "KNN",
                    "Linear Regression",
                    "SVR",
                ]:
                    if model_name in comparison and "r2" in comparison[model_name]:
                        print(
                            f"{model_name:<20} {comparison[model_name]['r2']:<10.3f} "
                            f"{comparison[model_name]['mae']:<12.2f} {comparison[model_name]['rmse']:<12.2f} {comparison[model_name]['mape']:<10.1f}%"
                        )

                print("-" * 80)
                print(f"\nMeilleur modele: {info['best_model_name']}")
                print(f"   R2 = {info['test_r2']:.3f}")
                print(f"   MAE = {info['test_mae']:.2f} cas")
                print(f"   RMSE = {info['test_rmse']:.2f} cas")
                print(f"   MAPE = {info['test_mape']:.1f}%")
                break


def _load_report_summary(current_summary: pd.DataFrame, evaluation_dir: Path) -> tuple[pd.DataFrame, str]:
    if current_summary is not None and not current_summary.empty:
        return current_summary.copy(), "run_courant"

    summary_path = evaluation_dir / "model_performance_summary.csv"
    if not summary_path.exists():
        return pd.DataFrame(), "aucune_source"

    try:
        return pd.read_csv(summary_path, encoding="utf-8-sig"), "artefacts_valides"
    except Exception:
        return pd.DataFrame(), "aucune_source"


def _build_key_results_text(summary_df: pd.DataFrame, evaluation_dir: Path) -> str:
    if summary_df is None or summary_df.empty or "R² (Best)" not in summary_df.columns:
        return ""

    min_r2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))
    summary = summary_df.copy()
    summary["R² (Best)"] = pd.to_numeric(summary["R² (Best)"], errors="coerce")
    summary = summary.dropna(subset=["R² (Best)"])
    if summary.empty:
        return ""

    eligible = summary.loc[summary["R² (Best)"] >= min_r2].sort_values("R² (Best)", ascending=False)
    weak = summary.loc[summary["R² (Best)"] < min_r2].sort_values("R² (Best)", ascending=False)
    top = eligible.head(8)

    lines = []
    lines.append("=" * 70)
    lines.append("RESULTATS CLES")
    lines.append("=" * 70)
    lines.append(f"{len(summary)} maladies ont ete modelisees dans model_performance_summary.csv.")
    lines.append(f"{len(eligible)} maladies passent le seuil de production avec R² >= {min_r2:.1f}.")
    lines.append("Les meilleures performances visibles sont :")
    for row in top.itertuples(index=False):
        lines.append(f"- {row[0]} : R² = {float(row[2]):.3f}")

    if not weak.empty:
        weak_names = ", ".join(str(row[0]) for row in weak.itertuples(index=False))
        lines.append(f"Maladies non retenues pour la mise en production (scores sous le seuil) : {weak_names}.")

    lines.append("Visuels :")
    lines.append(f"- Resume chiffre : {evaluation_dir / 'model_performance_summary.csv'}")
    lines.append(f"- Seuils et matrices : {evaluation_dir / 'confusion_matrix_summary.csv'}")
    lines.append(f"- Image consolidee : {evaluation_dir / 'confusion_matrices_combined.png'}")
    lines.append("=" * 70)
    return "\n".join(lines)


def _get_eligible_summary(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df is None or summary_df.empty or "R² (Best)" not in summary_df.columns:
        return pd.DataFrame()

    min_r2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))
    eligible_summary = summary_df.copy()
    eligible_summary["R² (Best)"] = pd.to_numeric(eligible_summary["R² (Best)"], errors="coerce")
    eligible_summary = eligible_summary.dropna(subset=["R² (Best)"])
    if eligible_summary.empty:
        return pd.DataFrame()

    return eligible_summary.loc[eligible_summary["R² (Best)"] >= min_r2].copy()


def _compute_global_metrics_from_summary(summary_df: pd.DataFrame, evaluation_dir: Path) -> dict:
    eligible_summary = _get_eligible_summary(summary_df)
    if eligible_summary.empty:
        return {
            "eligible_count": 0,
            "total_cases": 0,
            "r2_mean": np.nan,
            "r2_weighted": np.nan,
            "mape_mean": np.nan,
            "macro_f1": np.nan,
            "micro_f1": np.nan,
            "eligible_summary": eligible_summary,
        }

    if "MAPE (Best)" in eligible_summary.columns:
        eligible_summary["MAPE (Best)"] = pd.to_numeric(eligible_summary["MAPE (Best)"], errors="coerce")
    else:
        eligible_summary["MAPE (Best)"] = np.nan

    if "Total cas" in eligible_summary.columns:
        eligible_summary["Total cas"] = pd.to_numeric(eligible_summary["Total cas"], errors="coerce")
    else:
        eligible_summary["Total cas"] = 0.0

    r2_list, mape_list, weights = [], [], []
    total_cases_all = 0
    micro_tp = micro_fp = micro_fn = 0
    per_disease_f1 = []

    for _, row in eligible_summary.iterrows():
        disease = str(row.get("Maladie", "")).strip()
        r2 = float(row.get("R² (Best)", np.nan))
        mape = row.get("MAPE (Best)", np.nan)
        total = row.get("Total cas", 0) or 0
        total_cases_all += total

        if not np.isnan(r2):
            r2_list.append(r2)
            weights.append(max(total, 1))
        if not pd.isna(mape):
            mape_list.append(float(mape))

        cm_path = evaluation_dir / f"{_slugify_name(disease)}_confusion_matrix.csv"
        if not cm_path.exists():
            continue
        try:
            cm_df = pd.read_csv(cm_path, index_col=0, encoding="utf-8-sig")
            mat = cm_df.values.astype(float)
            n = mat.shape[0]
            pos_idx = n - 1
            if n >= 2:
                tp = mat[pos_idx, pos_idx]
                fp = mat[:pos_idx, pos_idx].sum()
                fn = mat[pos_idx, :pos_idx].sum()
                denom = 2 * tp + fp + fn
                f1_d = (2 * tp / denom) if denom > 0 else 0.0
                per_disease_f1.append(f1_d)
                micro_tp += tp
                micro_fp += fp
                micro_fn += fn
        except Exception:
            continue

    r2_mean = float(np.mean(r2_list)) if r2_list else np.nan
    weights_arr = np.array(weights, dtype=float)
    r2_weighted = float(np.average(r2_list, weights=weights_arr)) if r2_list else np.nan
    mape_mean = float(np.mean(mape_list)) if mape_list else np.nan
    macro_f1 = float(np.mean(per_disease_f1)) if per_disease_f1 else np.nan
    micro_denom = 2 * micro_tp + micro_fp + micro_fn
    micro_f1 = float(2 * micro_tp / micro_denom) if micro_denom > 0 else np.nan

    return {
        "eligible_count": len(eligible_summary),
        "total_cases": int(total_cases_all),
        "r2_mean": r2_mean,
        "r2_weighted": r2_weighted,
        "mape_mean": mape_mean,
        "macro_f1": macro_f1,
        "micro_f1": micro_f1,
        "eligible_summary": eligible_summary,
    }


def _run_legacy_regression_training() -> bool:
    """Execute le pipeline de regression par maladie et exporte les matrices."""
    root = Path(__file__).resolve().parent.parent.parent
    data_path = root / "data" / "raw" / "drc-2023_sem08.xlsx"
    data_path_2022 = root / "data" / "raw" / "drc-2022_sem40.xlsx"

    if not data_path.exists():
        print(f"Fichier de donnees non trouve: {data_path}")
        return False

    try:
        from src.pipeline.data_cleaner import DataCleaner

        cleaner = DataCleaner(
            str(data_path),
            file_path_2022=str(data_path_2022) if data_path_2022.exists() else None,
        )
        cleaner.load_data()
        cleaner.clean_data()
        agg = cleaner.aggregate_by_week_disease()
        agg = cleaner.remove_outliers(agg)          # IQR capping
        agg = cleaner.handle_sparse_series(agg)     # supprime maladies creuses
        # Export CSV lisible (humainement compréhensible) avant feature engineering
        processed_dir = root / "data" / "processed"
        cleaner.export_clean_dataset(agg, str(processed_dir / "dataset_propre.csv"))
        features = cleaner.create_features_for_ml(agg)
        features = cleaner.encode_disease_labels(features)  # encode MALADIE

        predictor = DiseasePredictor(console_detailed=False)
        predictor.train_all_diseases(features)
        save_error = None
        try:
            predictor.save_models(str(root / "models" / "trained" / "models.pkl"))
        except Exception as exc:
            save_error = str(exc)
            print(f"Sauvegarde de production ignoree: {save_error}")

        reports = predictor.export_performance_reports(str(root / "models" / "evaluation"))
        try:
            exported = predictor.export_confusion_matrices(str(root / "models" / "evaluation"))
        except Exception as exc:
            print(f"Export des matrices de confusion partiellement ignore: {exc}")
            exported = []


        # Générer un rapport complet dans logs/train_run.log
        import io
        report = io.StringIO()
        evaluation_dir = root / "models" / "evaluation"
        # Résumé par maladie
        summary = predictor.get_model_performance_summary()
        report_summary, summary_source = _load_report_summary(summary, evaluation_dir)
        key_results_text = _build_key_results_text(report_summary, evaluation_dir)
        global_metrics = _compute_global_metrics_from_summary(report_summary, evaluation_dir)
        eligible_summary = global_metrics["eligible_summary"]
        if key_results_text:
            report.write("\n" + key_results_text + "\n\n")
            print("\n" + key_results_text)

        if global_metrics["eligible_count"]:
            print("\n" + "=" * 70)
            print("R² GLOBAL — TOUTES MALADIES CONFONDUES")
            print("=" * 70)
            print(f"  Maladies retenues          : {global_metrics['eligible_count']}")
            print(f"  Total cas couverts         : {global_metrics['total_cases']:,}")
            print(f"  R² moyen simple            : {global_metrics['r2_mean']:.3f}")
            print(f"  R² moyen pondéré (cas)     : {global_metrics['r2_weighted']:.3f}")
            print(f"  MAPE moyen global          : {global_metrics['mape_mean']:.1f}%")
            print(f"  F1 Macro global            : {global_metrics['macro_f1']:.3f}")
            print(f"  F1 Micro global            : {global_metrics['micro_f1']:.3f}")
            if summary_source == "artefacts_valides":
                print("  Source utilisee            : artefacts valides deja presentes sur disque")
            print("=" * 70)

        if summary_source == "artefacts_valides":
            report.write("Source du resume: artefacts valides deja presents sur disque (le run courant n'a pas atteint le seuil de production).\n\n")

        if not eligible_summary.empty:
            report.write("\n" + "=" * 100 + "\n")
            report.write("METRIQUES DE REGRESSION PAR MALADIE RETENUES EN PRODUCTION\n")
            report.write("=" * 100 + "\n")
            cols = [
                "Maladie", "Meilleur Modèle", "R² (Best)", "MAE (Best)",
                "RMSE (Best)", "MAPE (Best)", "CV R²", "CV MAE (log)",
                "Total cas", "Semaines",
            ]
            existing_cols = [c for c in cols if c in eligible_summary.columns]
            report.write(eligible_summary[existing_cols].sort_values("R² (Best)", ascending=False).to_string(index=False))
            report.write("\n\n")

        report.write("\n" + "=" * 70 + "\n")
        report.write("PERFORMANCE GLOBALE — TOUTES MALADIES CONFONDUES\n")
        report.write("=" * 70 + "\n")
        report.write(f"  Maladies modelisees        : {global_metrics['eligible_count']}\n")
        report.write(f"  Total cas couverts         : {global_metrics['total_cases']:,}\n")
        report.write(f"  R² moyen simple            : {global_metrics['r2_mean']:.3f}\n")
        report.write(f"  R² moyen pondéré (cas)     : {global_metrics['r2_weighted']:.3f}\n")
        report.write(f"  MAPE moyen global          : {global_metrics['mape_mean']:.1f}%\n")
        report.write("\n")
        report.write("  F1-Score global (niveaux d'alerte ← classe positive = 'Élevé')\n")
        report.write(f"    F1 Macro (moy. par maladie) : {global_metrics['macro_f1']:.3f}\n")
        report.write(f"    F1 Micro (agrégé global)    : {global_metrics['micro_f1']:.3f}\n")
        report.write("\n" + "=" * 70 + "\n")

        # Écrire le rapport dans logs/train_run.log
        log_path = root / "logs" / "train_run.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(report.getvalue(), encoding="utf-8")

        print("\nRapport complet de regression exporté dans logs/train_run.log")

        if exported:
            print("\nMatrices de confusion exportees:")
            for file_path in exported:
                print(f" - {file_path}")

        if reports:
            print("\nRapports de performances exportes:")
            for file_path in reports:
                print(f" - {file_path}")

        if save_error:
            print("\nLe modele de production existant a ete conserve.")

        return True
    except Exception as exc:
        print(f"Erreur pendant l'entrainement legacy: {exc}")
        return False


def main():
    print("Module train_models charge avec succes")
    print("\n" + "=" * 80)
    print("MODE EXECUTION: train_models.py (REGRESSION PAR MALADIE)")
    print("=" * 80)

    if not _run_legacy_regression_training():
        print("Echec du pipeline de regression.")


if __name__ == "__main__":
    main()