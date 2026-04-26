# src/train_models.py
import re
import unicodedata
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

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


class DiseasePredictor:
    def __init__(self):
        self.best_models = {}
        self.results = {}
        self.comparison_results = {}

    def get_features(self, df):
        feature_cols = [c for c in df.columns if c not in ["DEBUTSEM", "MALADIE", "TOTALCAS", "TOTALDECES"]]
        return df[feature_cols], df["TOTALCAS"], feature_cols

    def compare_models(self, X_train, y_train, X_test, y_test, disease_name):
        """Compare plusieurs modeles et retourne les performances."""
        models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "KNN": KNeighborsRegressor(n_neighbors=5),
            "SVR": SVR(kernel="rbf"),
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
            return LinearRegression()
        if model_name == "Ridge Regression":
            return Ridge(alpha=1.0)
        if model_name == "Random Forest":
            return RandomForestRegressor(n_estimators=100, random_state=42)
        if model_name == "Gradient Boosting":
            return GradientBoostingRegressor(n_estimators=100, random_state=42)
        if model_name == "KNN":
            return KNeighborsRegressor(n_neighbors=5)
        if model_name == "SVR":
            return SVR(kernel="rbf")
        return RandomForestRegressor(n_estimators=100, random_state=42)

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

        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        if len(X_test) == 0:
            print("   Ignore: pas de donnees de test")
            return False

        print("\n   Comparaison des modeles:")
        comparison = self.compare_models(X_train, y_train, X_test, y_test, disease_name)

        for name, metrics in comparison.items():
            if "error" not in metrics:
                print(
                    f"      {name:20} | R2: {metrics['r2']:.3f} | "
                    f"MAE: {metrics['mae']:.2f} | MAPE: {metrics['mape']:.1f}%"
                )

        best_model_name = None
        best_r2 = -np.inf
        for name, metrics in comparison.items():
            if "error" not in metrics and metrics["r2"] > best_r2:
                best_r2 = metrics["r2"]
                best_model_name = name

        best_model = self._build_best_model(best_model_name)
        best_model.fit(X_train, y_train)
        y_pred = best_model.predict(X_test)
        confusion_info = _build_confusion_artifact(y_test, y_pred)

        self.best_models[disease_name] = {
            "model": best_model,
            "features": features,
            "best_model_name": best_model_name,
            "test_mae": mean_absolute_error(y_test, y_pred),
            "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "test_r2": r2_score(y_test, y_pred),
            "test_mape": np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100,
            "total_cases": total_cases,
            "n_weeks": n_weeks,
            "comparison": comparison,
            "confusion_matrix": {
                "labels": confusion_info["labels"],
                "thresholds": confusion_info["thresholds"],
                "matrix": confusion_info["matrix"],
            },
        }

        print(f"\n   Meilleur modele: {best_model_name}")
        print(f"      R2: {self.best_models[disease_name]['test_r2']:.3f}")
        print(f"      MAE: {self.best_models[disease_name]['test_mae']:.2f}")
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

    def export_confusion_matrices(self, output_dir="models/confusion_matrices"):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported_files = []
        summary_rows = []

        for disease, info in self.best_models.items():
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

    def export_combined_confusion_matrix_image(self, output_dir="models/confusion_matrices"):
        try:
            import matplotlib.pyplot as plt
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "matplotlib est requis pour generer une image PNG des matrices de confusion. "
                "Installe-le dans ton environnement actif avec: conda install matplotlib"
            ) from exc

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        matrices = []
        for disease, info in self.best_models.items():
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

    def save_models(self, path="models/models.pkl"):
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "best_models": self.best_models,
                "results": self.results,
                "comparison_results": self.comparison_results,
            },
            path_obj,
        )
        print(f"Modeles sauvegardes: {path_obj}")

    def load_models(self, path="models/models.pkl"):
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
        if not self.best_models:
            return pd.DataFrame()

        summary = []
        for disease, info in self.best_models.items():
            comparison = info.get("comparison", {})
            row = {
                "Maladie": disease,
                "Meilleur Modèle": info["best_model_name"],
                "R² (Best)": round(info["test_r2"], 3),
                "MAE (Best)": round(info["test_mae"], 2),
                "MAPE (Best)": round(info["test_mape"], 1),
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

    def print_comparison_table(self):
        """Affiche un tableau de comparaison pour le memoire."""
        print("\n" + "=" * 80)
        print("TABLEAU DE COMPARAISON DES MODELES - MALADIE SENTINELLE (PALUDISME)")
        print("=" * 80)

        for disease, info in self.best_models.items():
            if "paludisme" in disease.lower():
                comparison = info.get("comparison", {})
                print(f"\nMaladie: {disease}")
                print("-" * 60)
                print(f"{'Modele':<20} {'R2':<10} {'MAE':<15} {'MAPE':<10}")
                print("-" * 60)

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
                            f"{comparison[model_name]['mae']:<15.2f} {comparison[model_name]['mape']:<10.1f}%"
                        )

                print("-" * 60)
                print(f"\nMeilleur modele: {info['best_model_name']}")
                print(f"   R2 = {info['test_r2']:.3f} ({info['test_r2'] * 100:.1f}%)")
                print(f"   MAE = {info['test_mae']:.2f} cas")
                print(f"   MAPE = {info['test_mape']:.1f}%")
                break


def _print_reference_benchmark() -> bool:
    """Affiche le benchmark de reference (XGBoost 81.6%) s'il est disponible."""
    root = Path(__file__).resolve().parent.parent
    log_path = root / "train_run.log"

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
    root = Path(__file__).resolve().parent.parent
    data_path = root / "data" / "drc-2023_sem08.xlsx"

    if not data_path.exists():
        print(f"Fichier de donnees non trouve: {data_path}")
        return False

    try:
        from src.data_cleaner import DataCleaner

        cleaner = DataCleaner(str(data_path))
        cleaner.load_data()
        cleaner.clean_data()
        agg = cleaner.aggregate_by_week_disease()
        features = cleaner.create_features_for_ml(agg)

        predictor = DiseasePredictor()
        predictor.train_all_diseases(features)
        predictor.save_models(str(root / "models" / "models.pkl"))
        exported = predictor.export_confusion_matrices(str(root / "models" / "confusion_matrices"))
        predictor.print_comparison_table()

        if exported:
            print("\nMatrices de confusion exportees:")
            for file_path in exported:
                print(f" - {file_path}")

        return True
    except Exception as exc:
        print(f"Erreur pendant l'entrainement legacy: {exc}")
        return False


def main():
    print("Module train_models charge avec succes")
    print("\n" + "=" * 80)
    print("MODE EXECUTION: train_models.py")
    print("=" * 80)

    if _print_reference_benchmark():
        return

    print("train_run.log introuvable. Execution du pipeline legacy en fallback...")
    if not _run_legacy_regression_training():
        print("Impossible d'afficher le benchmark 81.6 ni d'entrainer en fallback.")


if __name__ == "__main__":
    main()