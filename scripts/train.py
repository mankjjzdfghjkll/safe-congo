# scripts/train.py
"""Script d'entraînement autonome des modèles pour SAFE CONGO"""

import sys
import os
from pathlib import Path

# Ajouter le chemin parent
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import direct sans passer par __init__
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Import de la classe DataCleaner directement
from src.pipeline.data_cleaner import DataCleaner

def main():
    print("="*60)
    print(" SAFE CONGO - Entraînement des Modèles IA")
    print("="*60)
    
    # Chemins
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "data" / "raw" / "drc-2023_sem08.xlsx"
    
    if not data_file.exists():
        print(f"\n Erreur: Fichier non trouvé: {data_file}")
        return
    
    # 1. Nettoyage des données
    print("\n Étape 1: Nettoyage des données...")
    try:
        cleaner = DataCleaner(str(data_file))
        cleaner.load_data()
        cleaner.clean_data()
        agg_data = cleaner.aggregate_by_week_disease()
        agg_data = cleaner.remove_outliers(agg_data)
        agg_data = cleaner.handle_sparse_series(agg_data)
        # Export CSV lisible du dataset nettoyé (avant feature engineering)
        cleaner.export_clean_dataset(agg_data, str(base_dir / "data" / "processed" / "dataset_propre.csv"))
        feature_data = cleaner.create_features_for_ml(agg_data)
        feature_data = cleaner.encode_disease_labels(feature_data)
        print(" Nettoyage terminé!")
    except Exception as e:
        print(f" Erreur: {e}")
        return
    
    if feature_data.empty:
        print(" Pas assez de données pour l'entraînement")
        return
    
    # 2. Entraînement
    print("\n Étape 2: Entraînement des modèles...")
    models = {}
    
    for disease in feature_data['MALADIE'].unique():
        data = feature_data[feature_data['MALADIE'] == disease].copy()
        total_cases = data['TOTALCAS'].sum()
        
        if total_cases < 50 or len(data) < 20:
            print(f" {disease}: {total_cases} cas, {len(data)} semaines - ignoré")
            continue
        
        # Features
        feature_cols = [c for c in data.columns if c not in ['DEBUTSEM', 'MALADIE', 'TOTALCAS', 'TOTALDECES']]
        X = data[feature_cols]
        y = data['TOTALCAS']
        
        # Division
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        if len(X_test) == 0:
            continue
        
        # Modèle
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        models[disease] = {
            'model': model,
            'features': feature_cols,
            'mae': mae,
            'r2': r2,
            'total_cases': total_cases
        }
        
        print(f" {disease}: MAE={mae:.2f}, R²={r2:.3f}")
    
    # 3. Sauvegarde
    print("\n Étape 3: Sauvegarde des modèles...")
    models_dir = base_dir / "models" / "trained"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(models, str(models_dir / "models.pkl"))
    print(f" {len(models)} modèles sauvegardés dans {models_dir / 'models.pkl'}")
    
    print("\n" + "="*60)
    print(" Entraînement terminé avec succès!")
    print("="*60)


if __name__ == "__main__":
    main()