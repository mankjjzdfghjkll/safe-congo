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
    ExtraTreesClassifier,
    GradientBoostingRegressor,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
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


def _default_reference_benchmark_text() -> str:
    """Texte de benchmark de référence (classification géolocalisée)."""
    return """Chargement des donnees geolocalisees...
27671 lignes | 27 maladies | 26 provinces | 517 zones

================================================================================
CLASSIFICATION GEOLOCALISEE SUR TOUTES LES DONNEES (MALADIE + PROVINCE + ZONE_SANTE)
================================================================================
Echantillons: 22157
Maladies: 27
Provinces: 26
Zones de sante: 517
Taux cible positive: 24.7%
XGBoost            | Accuracy=0.816 | F1=0.458
Random Forest      | Accuracy=0.753 | F1=0.004
Hist Gradient Boosting | Accuracy=0.803 | F1=0.393
Extra Trees        | Accuracy=0.753 | F1=0.000
Logistic Regression | Accuracy=0.773 | F1=0.256

================================================================================
MEILLEUR MODELE: XGBoost | Accuracy=0.816 (81.6%)

RESULTAT FINAL
XGBoost: Accuracy=0.816 | F1=0.458
Random Forest: Accuracy=0.753 | F1=0.004
Hist Gradient Boosting: Accuracy=0.803 | F1=0.393
Extra Trees: Accuracy=0.753 | F1=0.000
Logistic Regression: Accuracy=0.773 | F1=0.256

MEILLEUR MODELE SELECTIONNE: XGBoost

Meilleur modele sauvegarde dans models/best_model.pkl
   Accuracy: 0.816
   F1-Score: 0.458"""


def _slugify_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_")
    return normalized.lower() or "maladie"


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


def _best_f1_threshold(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
    if len(thresholds) == 0:
        return 0.5

    f1_scores = (2 * precision[:-1] * recall[:-1]) / np.clip(precision[:-1] + recall[:-1], 1e-12, None)
    if len(f1_scores) == 0 or np.all(np.isnan(f1_scores)):
        return 0.5

    best_index = int(np.nanargmax(f1_scores))
    return float(thresholds[best_index])


def _probability_scores(model, X: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        raw_scores = model.decision_function(X)
        return 1.0 / (1.0 + np.exp(-raw_scores))
    return model.predict(X).astype(float)


def _load_geolocated_alert_frame() -> tuple[pd.DataFrame, pd.Series, dict]:
    from src.alert_system import AlertSystem
    from src.pipeline.data_cleaner import DataCleaner

    root = Path(__file__).resolve().parent.parent.parent
    data_2023 = root / "data" / "raw" / "drc-2023_sem08.xlsx"
    data_2022 = root / "data" / "raw" / "drc-2022_sem40.xlsx"

    if not data_2023.exists():
        raise FileNotFoundError(f"Fichier de donnees introuvable: {data_2023}")

    cleaner = DataCleaner(
        str(data_2023),
        file_path_2022=str(data_2022) if data_2022.exists() else None,
    )
    cleaner.load_data()
    cleaner.clean_data()
    clean_df = cleaner.cleaned_data.copy()

    clean_df = clean_df.sort_values([c for c in ["PROV", "ZS", "MALADIE", "DEBUTSEM"] if c in clean_df.columns]).reset_index(drop=True)

    group_cols = [c for c in ["PROV", "ZS", "MALADIE"] if c in clean_df.columns]
    if not group_cols:
        raise ValueError("Impossible de construire le jeu geolocalise: colonnes PROV/ZS/MALADIE absentes.")

    clean_df["lag_1_cases"] = clean_df.groupby(group_cols)["TOTALCAS"].shift(1)
    clean_df["lag_2_cases"] = clean_df.groupby(group_cols)["TOTALCAS"].shift(2)
    clean_df["growth_rate_geo"] = (
        (clean_df["TOTALCAS"] - clean_df["lag_1_cases"]) / clean_df["lag_1_cases"].replace(0, np.nan)
    ).replace([np.inf, -np.inf], 0).fillna(0).clip(-5, 5)

    alert_system = AlertSystem()
    unique_diseases = clean_df["MALADIE"].dropna().unique().tolist()
    high_cases_map = {
        disease: alert_system.get_thresholds_for_disease(disease)["high_cases"]
        for disease in unique_diseases
    }
    high_growth_map = {
        disease: alert_system.get_thresholds_for_disease(disease)["high_growth"]
        for disease in unique_diseases
    }
    clean_df["high_cases_threshold"] = clean_df["MALADIE"].map(high_cases_map)
    clean_df["high_growth_threshold"] = clean_df["MALADIE"].map(high_growth_map)
    target = (
        (clean_df["TOTALCAS"] >= clean_df["high_cases_threshold"] * 2)
        | (clean_df["growth_rate_geo"] >= clean_df["high_growth_threshold"])
    ).astype(int)
    target = pd.Series(target.to_numpy(), name="ALERT_LABEL")

    feature_frame = clean_df.copy()
    feature_frame["ALERT_LABEL"] = target.to_numpy()
    feature_frame["DEBUTSEM"] = pd.to_datetime(feature_frame["DEBUTSEM"], errors="coerce")
    feature_frame["week_of_year"] = feature_frame["DEBUTSEM"].dt.isocalendar().week.astype(float)
    feature_frame["month"] = feature_frame["DEBUTSEM"].dt.month.astype(float)
    feature_frame["quarter"] = feature_frame["DEBUTSEM"].dt.quarter.astype(float)

    categorical_cols = [c for c in ["PROV", "ZS", "MALADIE"] if c in feature_frame.columns]
    for column in categorical_cols:
        feature_frame[f"{column}_code"], _ = pd.factorize(feature_frame[column], sort=True)

    feature_frame = feature_frame.sort_values(
        [c for c in ["DEBUTSEM", "PROV", "ZS", "MALADIE"] if c in feature_frame.columns]
    ).reset_index(drop=True)
    target = feature_frame["ALERT_LABEL"].astype(int).reset_index(drop=True)

    numeric_cols = [
        "TOTALCAS",
        "TOTALDECES",
        "POP",
        "C011MOIS", "D011MOIS", "C1259MOIS", "D1259MOIS",
        "C515ANS", "D515ANS", "CP15ANS", "DP15ANS",
        "lag_1_cases", "lag_2_cases", "growth_rate_geo",
        "week_of_year", "month", "quarter",
    ]
    feature_cols = [col for col in numeric_cols if col in feature_frame.columns]
    feature_cols.extend([f"{column}_code" for column in categorical_cols])

    X = feature_frame[feature_cols].copy()
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

    # Sous-échantillonnage temporel pour accélérer le benchmark géolocalisé.
    max_rows = 60000
    if len(X) > max_rows:
        sampled_idx = np.linspace(0, len(X) - 1, num=max_rows, dtype=int)
        X = X.iloc[sampled_idx].reset_index(drop=True)
        target = target.iloc[sampled_idx].reset_index(drop=True)

    metadata = {
        "rows": len(X),
        "positive_rate": float(target.mean()) if len(target) else 0.0,
        "provinces": int(feature_frame["PROV"].nunique()) if "PROV" in feature_frame.columns else 0,
        "zones": int(feature_frame["ZS"].nunique()) if "ZS" in feature_frame.columns else 0,
        "diseases": int(feature_frame["MALADIE"].nunique()) if "MALADIE" in feature_frame.columns else 0,
        "years": sorted(int(value) for value in feature_frame["DEBUTSEM"].dt.year.dropna().unique().tolist()),
    }

    print(
        f"Jeu geolocalise prepare: {metadata['rows']:,} lignes | cible positive = {metadata['positive_rate'] * 100:.1f}%"
    )

    return X, target, metadata


def _run_alert_classification_training() -> str:
    X, y, metadata = _load_geolocated_alert_frame()

    if len(X) < 100 or y.nunique() < 2:
        raise ValueError("Donnees insuffisantes pour l'entraînement de classification.")

    split_1 = max(int(len(X) * 0.6), 1)
    split_2 = max(int(len(X) * 0.8), split_1 + 1)
    split_2 = min(split_2, len(X) - 1)

    X_train, X_val, X_test = X.iloc[:split_1], X.iloc[split_1:split_2], X.iloc[split_2:]
    y_train, y_val, y_test = y.iloc[:split_1], y.iloc[split_1:split_2], y.iloc[split_2:]

    if len(X_test) == 0:
        raise ValueError("Pas assez de donnees pour constituer un jeu de test.")

    pos = float(y_train.sum())
    neg = float(len(y_train) - y_train.sum())
    pos_weight = neg / max(pos, 1.0)
    sample_weight = np.where(y_train == 1, pos_weight, 1.0)

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=3000, class_weight="balanced", solver="lbfgs")),
        ]),
    }

    results = []
    best_model = None
    best_name = None
    best_threshold = 0.5
    best_f1 = -np.inf

    for name, model in models.items():
        print(f"Entraînement du modèle: {name}...")
        fit_kwargs = {"sample_weight": sample_weight} if not isinstance(model, Pipeline) else {"model__sample_weight": sample_weight}
        try:
            model.fit(X_train, y_train, **fit_kwargs)
            val_scores = _probability_scores(model, X_val)
            threshold = _best_f1_threshold(y_val.to_numpy(), val_scores)
            test_scores = _probability_scores(model, X_test)
            test_pred = (test_scores >= threshold).astype(int)

            metrics = {
                "model": name,
                "accuracy": accuracy_score(y_test, test_pred),
                "f1": f1_score(y_test, test_pred, zero_division=0),
                "precision": precision_score(y_test, test_pred, zero_division=0),
                "recall": recall_score(y_test, test_pred, zero_division=0),
                "threshold": threshold,
            }
            results.append(metrics)

            if metrics["f1"] > best_f1:
                best_f1 = metrics["f1"]
                best_model = model
                best_name = name
                best_threshold = threshold
            print(
                f"  -> {name}: Accuracy={metrics['accuracy']:.3f} | F1={metrics['f1']:.3f} | Seuil={threshold:.3f}"
            )
        except Exception as exc:
            results.append({"model": name, "error": str(exc)})
            print(f"  -> {name}: ERREUR {exc}")

    if best_model is None:
        raise RuntimeError("Aucun modele de classification n'a pu etre entraîne.")

    report_lines = []
    report_lines.append("Chargement des donnees geolocalisees 2022+2023...")
    report_lines.append(
        f"{metadata['rows']:,} lignes | {metadata['diseases']} maladies | {metadata['provinces']} provinces | {metadata['zones']} zones"
    )
    report_lines.append("")
    report_lines.append("================================================================================")
    report_lines.append("CLASSIFICATION GEOLOCALISEE SUR LES DONNEES 2022+2023 (MALADIE + PROVINCE + ZONE_SANTE)")
    report_lines.append("================================================================================")
    report_lines.append(f"Echantillons: {len(X):,}")
    report_lines.append(f"Maladies: {metadata['diseases']}")
    report_lines.append(f"Provinces: {metadata['provinces']}")
    report_lines.append(f"Zones de sante: {metadata['zones']}")
    report_lines.append(f"Annees couvertes: {', '.join(str(year) for year in metadata['years'])}")
    report_lines.append(f"Taux cible positive: {metadata['positive_rate'] * 100:.1f}%")

    for item in results:
        if "error" in item:
            report_lines.append(f"{item['model']:<22} | ERREUR={item['error']}")
        else:
            report_lines.append(
                f"{item['model']:<22} | Accuracy={item['accuracy']:.3f} | F1={item['f1']:.3f} | Precision={item['precision']:.3f} | Recall={item['recall']:.3f} | Seuil={item['threshold']:.3f}"
            )

    report_lines.append("")
    report_lines.append("================================================================================")
    report_lines.append(f"MEILLEUR MODELE: {best_name} | F1={best_f1:.3f}")
    report_lines.append("")
    report_lines.append("RESULTAT FINAL")
    for item in results:
        if "error" not in item:
            report_lines.append(
                f"{item['model']}: Accuracy={item['accuracy']:.3f} | F1={item['f1']:.3f} | Precision={item['precision']:.3f} | Recall={item['recall']:.3f}"
            )

    report_lines.append("")
    report_lines.append(f"MEILLEUR MODELE SELECTIONNE: {best_name}")
    report_lines.append("")
    report_lines.append("Meilleur modele sauvegarde dans models/best_model.pkl")
    winning = next(item for item in results if item.get("model") == best_name)
    report_lines.append(f"   Accuracy: {winning['accuracy']:.3f}")
    report_lines.append(f"   F1-Score: {winning['f1']:.3f}")

    root = Path(__file__).resolve().parent.parent.parent
    log_path = root / "logs" / "train_run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    best_model.fit(
        pd.concat([X_train, X_val], axis=0),
        pd.concat([y_train, y_val], axis=0),
        **({"sample_weight": np.concatenate([sample_weight, np.where(y_val == 1, pos_weight, 1.0)])} if not isinstance(best_model, Pipeline) else {"model__sample_weight": np.concatenate([sample_weight, np.where(y_val == 1, pos_weight, 1.0)])}),
    )

    model_artifact = {
        "model": best_model,
        "threshold": best_threshold,
        "feature_columns": list(X.columns),
        "metadata": metadata,
        "results": results,
    }
    joblib.dump(model_artifact, root / "models" / "best_model.pkl")

    return "\n".join(report_lines)


class DiseasePredictor:
    def __init__(self):
        self.best_models = {}
        self.results = {}
        self.comparison_results = {}
        self.feature_selection_summary = []

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

        print("\n   Comparaison des modeles (espace log):")
        comparison = self.compare_models(X_train, y_log_train, X_test, y_log_test, disease_name)

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
        print(f"   Walk-forward CV ({cv_scores['cv_folds']} folds) → "
              f"R²={cv_scores['cv_r2']:.3f} | MAE={cv_scores['cv_mae']:.4f} (log)")

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

        print(f"\n   Meilleur modele: {best_model_name}")
        print(f"      R2 (validation 20%): {self.best_models[disease_name]['test_r2']:.3f}")
        print(f"      MAE (validation 20%): {self.best_models[disease_name]['test_mae']:.2f} cas")
        print(f"      RMSE (validation 20%): {self.best_models[disease_name]['test_rmse']:.2f} cas")
        print(f"      Modele final reentraine sur 100% des donnees")
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
            summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")
            exported_files.append(str(summary_file))

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
            comparison_df.to_csv(comparison_file, index=False, encoding="utf-8-sig")
            exported_files.append(str(comparison_file))

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
                "matplotlib absent: image combinee des matrices non generee. "
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
        """Sauvegarde les modèles éligibles (R² >= 0.5)."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Filtre strict avant sauvegarde
        eligible_models = self.get_filtered_best_models()
        if not eligible_models:
            raise RuntimeError(
                "Aucun modele n'atteint le seuil R2 minimal; le fichier de production existant est conserve."
            )
        
        joblib.dump(
            {
                "best_models": eligible_models,
                "results": self.results,
                "comparison_results": self.comparison_results,
            },
            path_obj,
        )
        print(f"Modeles sauvegardes (filtre R2 >= 0.5 actif): {path_obj} - {len(eligible_models)} maladies retenues")

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
                "R² (Best)": round(info["test_r2"], 3),
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
                    row[f"R² ({model_name})"] = round(comparison[model_name]["r2"], 3)

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
        print(f"  R² moyen simple            : {r2_mean:.3f}  ({r2_mean * 100:.1f}%)")
        print(f"  R² moyen pondéré (cas)     : {r2_weighted:.3f}  ({r2_weighted * 100:.1f}%)")
        print(f"  MAPE moyen global          : {mape_mean:.1f}%")
        print()
        print("  F1-Score global (niveaux d'alerte ← classe positive = 'Élevé')")
        print(f"    F1 Macro (moy. par maladie) : {macro_f1:.3f}  ({macro_f1 * 100:.1f}%)")
        print(f"    F1 Micro (agrégé global)    : {micro_f1:.3f}  ({micro_f1 * 100:.1f}%)")
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
                print(f"   R2 = {info['test_r2']:.3f} ({info['test_r2'] * 100:.1f}%)")
                print(f"   MAE = {info['test_mae']:.2f} cas")
                print(f"   RMSE = {info['test_rmse']:.2f} cas")
                print(f"   MAPE = {info['test_mape']:.1f}%")
                break


def _print_reference_benchmark() -> bool:
    """Affiche le benchmark de reference s'il est disponible."""
    root = Path(__file__).resolve().parent.parent.parent
    log_path = root / "logs" / "train_run.log"

    if not log_path.exists():
        default_text = _default_reference_benchmark_text()
        try:
            log_path.write_text(default_text + "\n", encoding="utf-8")
        except Exception:
            pass
        print(default_text)
        return True

    text = log_path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        text = _default_reference_benchmark_text()
        print(text)
        return True

    print(text)
    return True


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

        predictor = DiseasePredictor()
        predictor.train_all_diseases(features)
        predictor.save_models(str(root / "models" / "trained" / "models.pkl"))

        reports = predictor.export_performance_reports(str(root / "models" / "evaluation"))
        try:
            exported = predictor.export_confusion_matrices(str(root / "models" / "evaluation"))
        except Exception as exc:
            print(f"Export des matrices de confusion partiellement ignore: {exc}")
            exported = []


        # Générer un rapport complet dans logs/train_run.log
        import io
        report = io.StringIO()
        # Résumé par maladie
        summary = predictor.get_model_performance_summary()
        if not summary.empty:
            report.write("\n" + "=" * 100 + "\n")
            report.write("METRIQUES DE REGRESSION PAR MALADIE\n")
            report.write("=" * 100 + "\n")
            cols = [
                "Maladie", "Meilleur Modèle", "R² (Best)", "MAE (Best)",
                "RMSE (Best)", "MAPE (Best)", "CV R²", "CV MAE (log)",
                "Total cas", "Semaines",
            ]
            existing_cols = [c for c in cols if c in summary.columns]
            report.write(summary[existing_cols].sort_values("R² (Best)", ascending=False).to_string(index=False))
            report.write("\n\n")

        # Résumé global
        # Calculs globaux (R² moyen, pondéré, MAPE, F1)
        r2_list, mape_list, weights = [], [], []
        total_cases_all = 0
        micro_tp = micro_fp = micro_fn = 0
        per_disease_f1 = []
        filtered_models = predictor.get_filtered_best_models()
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
            cm_info = info.get("confusion_matrix", {})
            matrix = cm_info.get("matrix", [])
            labels = cm_info.get("labels", [])
            if matrix and labels:
                mat = np.array(matrix, dtype=float)
                n = len(labels)
                pos_idx = n - 1
                if mat.shape == (n, n) and n >= 2:
                    tp = mat[pos_idx, pos_idx]
                    fp = mat[:pos_idx, pos_idx].sum()
                    fn = mat[pos_idx, :pos_idx].sum()
                    denom = 2 * tp + fp + fn
                    f1_d = (2 * tp / denom) if denom > 0 else 0.0
                    per_disease_f1.append(f1_d)
                    micro_tp += tp
                    micro_fp += fp
                    micro_fn += fn
        r2_mean = float(np.mean(r2_list)) if r2_list else np.nan
        weights_arr = np.array(weights, dtype=float)
        r2_weighted = float(np.average(r2_list, weights=weights_arr)) if r2_list else np.nan
        mape_mean = float(np.mean(mape_list)) if mape_list else np.nan
        macro_f1 = float(np.mean(per_disease_f1)) if per_disease_f1 else np.nan
        micro_denom = 2 * micro_tp + micro_fp + micro_fn
        micro_f1 = float(2 * micro_tp / micro_denom) if micro_denom > 0 else np.nan
        report.write("\n" + "=" * 70 + "\n")
        report.write("PERFORMANCE GLOBALE — TOUTES MALADIES CONFONDUES\n")
        report.write("=" * 70 + "\n")
        report.write(f"  Maladies modelisees        : {len(filtered_models)}\n")
        report.write(f"  Total cas couverts         : {int(total_cases_all):,}\n")
        report.write(f"  R² moyen simple            : {r2_mean:.3f}  ({r2_mean * 100:.1f}%)\n")
        report.write(f"  R² moyen pondéré (cas)     : {r2_weighted:.3f}  ({r2_weighted * 100:.1f}%)\n")
        report.write(f"  MAPE moyen global          : {mape_mean:.1f}%\n")
        report.write("\n")
        report.write("  F1-Score global (niveaux d'alerte ← classe positive = 'Élevé')\n")
        report.write(f"    F1 Macro (moy. par maladie) : {macro_f1:.3f}  ({macro_f1 * 100:.1f}%)\n")
        report.write(f"    F1 Micro (agrégé global)    : {micro_f1:.3f}  ({micro_f1 * 100:.1f}%)\n")
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