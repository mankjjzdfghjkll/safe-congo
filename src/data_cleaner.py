# src/data_cleaner.py
"""Module de nettoyage des données pour SAFE CONGO"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataCleaner:
    """Classe pour le nettoyage et la préparation des données épidémiologiques"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_data = None
        self.cleaned_data = None
        
    def load_data(self):
        print("📂 Chargement des données...")
        self.raw_data = pd.read_excel(self.file_path, sheet_name=0)
        print(f"✅ Données chargées: {self.raw_data.shape[0]} lignes")
        return self.raw_data
    
    def clean_data(self):
        print("\n🧹 Nettoyage des données...")
        df = self.raw_data.copy()
        
        # Suppression des colonnes inutiles
        cols_to_drop = ['NUM', 'C328TNN', 'DTNN', 'C011MOIS', 'D011MOIS', 
                       'C1259MOIS', 'D1259MOIS', 'C515ANS', 'D515ANS',
                       'CP15ANS', 'DP15ANS', 'RecStatus']
        existing = [c for c in cols_to_drop if c in df.columns]
        df.drop(columns=existing, errors='ignore', inplace=True)
        
        # Conversion des dates
        if 'DEBUTSEM' in df.columns:
            df['DEBUTSEM'] = pd.to_datetime(df['DEBUTSEM'], errors='coerce')
        
        # Standardisation des maladies
        mapping = {
            'PALUDISME SUSP': 'Paludisme (suspect)',
            'PALUDISME CONF': 'Paludisme (confirmé)',
            'DIARRHEE DHY M5': 'Diarrhée aqueuse',
            'DIARR SANGLANTE': 'Diarrhée sanglante',
            'FIEVRE TYPHOIDE': 'Fièvre typhoïde',
            'GRIPPE': 'Grippe',
            'IRA': 'Infection respiratoire aiguë',
            'MENINGITE': 'Méningite',
            'ROUGEOLE': 'Rougeole',
            'CHOLERA': 'Choléra',
            'MONKEYPOX': 'Monkeypox',
            'COVID-19': 'COVID-19'
        }
        df['MALADIE'] = df['MALADIE'].replace(mapping)
        
        # Nettoyage des valeurs numériques
        if 'TOTALCAS' in df.columns:
            df['TOTALCAS'] = pd.to_numeric(df['TOTALCAS'], errors='coerce').fillna(0)
        if 'TOTALDECES' in df.columns:
            df['TOTALDECES'] = pd.to_numeric(df['TOTALDECES'], errors='coerce').fillna(0)
        
        df = df[df['TOTALCAS'] >= 0]
        
        self.cleaned_data = df
        print(f"✅ Nettoyage terminé: {len(df)} lignes")
        return df
    
    def aggregate_by_week_disease(self):
        agg = self.cleaned_data.groupby(['DEBUTSEM', 'MALADIE']).agg({
            'TOTALCAS': 'sum',
            'TOTALDECES': 'sum'
        }).reset_index()
        agg = agg.sort_values(['MALADIE', 'DEBUTSEM'])
        return agg
    
    def create_features_for_ml(self, agg_data):
        print("\n🔧 Création des features...")
        feature_data = []
        
        for disease in agg_data['MALADIE'].unique():
            data = agg_data[agg_data['MALADIE'] == disease].copy()
            data = data.sort_values('DEBUTSEM')
            
            if len(data) < 5:
                continue
            
            for lag in [1, 2, 3, 4]:
                data[f'lag_{lag}'] = data['TOTALCAS'].shift(lag)
            
            for window in [2, 3, 4]:
                data[f'ma_{window}'] = data['TOTALCAS'].rolling(window, min_periods=1).mean()
            
            data['growth_rate'] = data['TOTALCAS'].pct_change().fillna(0)
            data['week_rank'] = range(len(data))
            data['month'] = data['DEBUTSEM'].dt.month
            
            feature_data.append(data.dropna())
        
        if feature_data:
            result = pd.concat(feature_data, ignore_index=True)
            print(f"✅ {len(result)} lignes de features créées")
            return result
        return pd.DataFrame()


# Test direct du module
if __name__ == "__main__":
    print("Test du module data_cleaner...")
    test_path = "data/drc-2023_sem08.xlsx"
    cleaner = DataCleaner(test_path)
    cleaner.load_data()
    cleaned = cleaner.clean_data()
    print("✅ Module fonctionne correctement!")