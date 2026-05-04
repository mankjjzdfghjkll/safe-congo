# scripts/train.py
"""Script d'entraînement autonome des modèles pour SAFE CONGO"""

import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports src.*
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.pipeline.data_cleaner import DataCleaner
from src.pipeline.train_models import DiseasePredictor


def main():
    print("=" * 60)
    print(" SAFE CONGO - Entraînement des Modèles IA")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "data" / "raw" / "drc-2023_sem08.xlsx"

    if not data_file.exists():
        print(f"\n Erreur: Fichier non trouvé: {data_file}")
        return

    # ------------------------------------------------------------------
    # Étape 1 : Nettoyage complet
    # ------------------------------------------------------------------
    print("\n Étape 1: Nettoyage des données...")
    try:
        cleaner = DataCleaner(str(data_file))
        cleaner.load_data()
        cleaner.clean_data()
        agg_data = cleaner.aggregate_by_week_disease()
        agg_data = cleaner.remove_outliers(agg_data)
        agg_data = cleaner.handle_sparse_series(agg_data)
        cleaner.export_clean_dataset(
            agg_data,
            str(base_dir / "data" / "processed" / "dataset_propre.csv"),
        )
        feature_data = cleaner.create_features_for_ml(agg_data)
        feature_data = cleaner.encode_disease_labels(feature_data)
        print(" Nettoyage terminé!")
    except Exception as e:
        print(f" Erreur nettoyage: {e}")
        raise

    if feature_data.empty:
        print(" Pas assez de données pour l'entraînement")
        return

    # ------------------------------------------------------------------
    # Étape 2 : Entraînement via DiseasePredictor (log1p, CV, sélection)
    # ------------------------------------------------------------------
    print("\n Étape 2: Entraînement des modèles...")
    predictor = DiseasePredictor()
    predictor.train_all_diseases(feature_data)

    if not predictor.best_models:
        print(" Aucun modèle entraîné (critères non remplis)")
        return

    # ------------------------------------------------------------------
    # Étape 3 : Sauvegarde
    # ------------------------------------------------------------------
    print("\n Étape 3: Sauvegarde des modèles...")
    models_path = base_dir / "models" / "trained" / "models.pkl"
    predictor.save_models(str(models_path))

    # ------------------------------------------------------------------
    # Étape 4 : Export matrices de confusion
    # ------------------------------------------------------------------
    print("\n Étape 4: Export matrices de confusion...")
    exported = predictor.export_confusion_matrices(
        str(base_dir / "models" / "evaluation")
    )
    for f in exported:
        print(f"   → {f}")

    print("\n" + "=" * 60)
    print(f" Entraînement terminé — {len(predictor.best_models)} modèles sauvegardés")
    print("=" * 60)


if __name__ == "__main__":
    main()