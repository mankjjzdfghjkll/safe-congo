# src/train_models.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class DiseasePredictor:
    def __init__(self):
        self.best_models = {}
        self.results = {}
        self.comparison_results = {}  # Pour stocker les résultats de comparaison
    
    def get_features(self, df):
        feature_cols = [c for c in df.columns if c not in ['DEBUTSEM', 'MALADIE', 'TOTALCAS', 'TOTALDECES']]
        return df[feature_cols], df['TOTALCAS'], feature_cols
    
    def compare_models(self, X_train, y_train, X_test, y_test, disease_name):
        """Compare plusieurs modèles et retourne les performances"""
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'KNN': KNeighborsRegressor(n_neighbors=5),
            'SVR': SVR(kernel='rbf')
        }
        
        results = {}
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                results[name] = {
                    'mae': mean_absolute_error(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'r2': r2_score(y_test, y_pred),
                    'mape': np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100
                }
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results
    
    def train_for_disease(self, disease_data, disease_name):
        total_cases = disease_data['TOTALCAS'].sum()
        n_weeks = len(disease_data)
        
        print(f"\n{'='*50}")
        print(f"📊 Analyse: {disease_name}")
        print(f"   Total cas: {total_cases:,} | Semaines: {n_weeks}")
        
        if total_cases < 50 or n_weeks < 20:
            print(f"   ⚠️ Ignoré: critères non remplis")
            return False
        
        X, y, features = self.get_features(disease_data)
        
        if len(X) < 10:
            print(f"   ⚠️ Ignoré: données insuffisantes")
            return False
        
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        if len(X_test) == 0:
            print(f"   ⚠️ Ignoré: pas de données de test")
            return False
        
        # Comparer tous les modèles
        print(f"\n   📈 Comparaison des modèles:")
        comparison = self.compare_models(X_train, y_train, X_test, y_test, disease_name)
        
        # Afficher les résultats
        for name, metrics in comparison.items():
            if 'error' not in metrics:
                print(f"      {name:20} | R²: {metrics['r2']:.3f} | MAE: {metrics['mae']:.2f} | MAPE: {metrics['mape']:.1f}%")
        
        # Sélectionner le meilleur modèle (celui avec le R² le plus élevé)
        best_model_name = None
        best_r2 = -1
        for name, metrics in comparison.items():
            if 'error' not in metrics and metrics['r2'] > best_r2:
                best_r2 = metrics['r2']
                best_model_name = name
        
        # Réentraîner le meilleur modèle sur toutes les données
        if best_model_name == 'Linear Regression':
            best_model = LinearRegression()
        elif best_model_name == 'Ridge Regression':
            best_model = Ridge(alpha=1.0)
        elif best_model_name == 'Random Forest':
            best_model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif best_model_name == 'Gradient Boosting':
            best_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif best_model_name == 'KNN':
            best_model = KNeighborsRegressor(n_neighbors=5)
        elif best_model_name == 'SVR':
            best_model = SVR(kernel='rbf')
        else:
            best_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        best_model.fit(X_train, y_train)
        y_pred = best_model.predict(X_test)
        
        self.best_models[disease_name] = {
            'model': best_model,
            'features': features,
            'best_model_name': best_model_name,
            'test_mae': mean_absolute_error(y_test, y_pred),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'test_r2': r2_score(y_test, y_pred),
            'test_mape': np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100,
            'total_cases': total_cases,
            'n_weeks': n_weeks,
            'comparison': comparison
        }
        
        print(f"\n   ✅ MEILLEUR MODÈLE: {best_model_name}")
        print(f"      R²: {self.best_models[disease_name]['test_r2']:.3f}")
        print(f"      MAE: {self.best_models[disease_name]['test_mae']:.2f}")
        
        return True
    
    def train_all_diseases(self, feature_data):
        print("\n" + "="*60)
        print("🚀 ENTRAÎNEMENT DES MODÈLES - COMPARAISON DES ALGORITHMES")
        print("="*60)
        
        trained = 0
        for disease in feature_data['MALADIE'].unique():
            data = feature_data[feature_data['MALADIE'] == disease].copy()
            if self.train_for_disease(data, disease):
                trained += 1
        
        print("\n" + "="*60)
        print(f"✅ {trained} modèles entraînés avec succès!")
        print("="*60)
        
        return self.best_models
    
    def save_models(self, path='models/models.pkl'):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'best_models': self.best_models,
            'results': self.results,
            'comparison_results': self.comparison_results
        }, path)
        print(f"💾 Modèles sauvegardés: {path}")
    
    def load_models(self, path='models/models.pkl'):
        try:
            data = joblib.load(path)
            self.best_models = data.get('best_models', {})
            self.results = data.get('results', {})
            self.comparison_results = data.get('comparison_results', {})
            print(f"✅ {len(self.best_models)} modèles chargés")
            return True
        except FileNotFoundError:
            print(f"⚠️ Fichier non trouvé: {path}")
            return False
        except Exception as e:
            print(f"⚠️ Erreur: {e}")
            return False
    
    def get_model_performance_summary(self):
        """Retourne un résumé des performances pour le mémoire"""
        if not self.best_models:
            return pd.DataFrame()
        
        summary = []
        for disease, info in self.best_models.items():
            # Récupérer les performances de tous les modèles pour cette maladie
            comparison = info.get('comparison', {})
            
            row = {
                'Maladie': disease,
                'Meilleur Modèle': info['best_model_name'],
                'R² (Best)': round(info['test_r2'], 3),
                'MAE (Best)': round(info['test_mae'], 2),
                'MAPE (Best)': round(info['test_mape'], 1),
                'Total cas': info['total_cases'],
                'Semaines': info['n_weeks']
            }
            
            # Ajouter les performances des autres modèles pour comparaison
            for model_name in ['Random Forest', 'Gradient Boosting', 'Ridge Regression', 'KNN']:
                if model_name in comparison and 'r2' in comparison[model_name]:
                    row[f'R² ({model_name})'] = round(comparison[model_name]['r2'], 3)
            
            summary.append(row)
        
        return pd.DataFrame(summary)
    
    def print_comparison_table(self):
        """Affiche un tableau de comparaison pour le mémoire"""
        print("\n" + "="*80)
        print("📊 TABLEAU DE COMPARAISON DES MODÈLES - MALADIE SENTINELLE (PALUDISME)")
        print("="*80)
        
        # Chercher le paludisme
        for disease, info in self.best_models.items():
            if 'paludisme' in disease.lower():
                comparison = info.get('comparison', {})
                
                print(f"\nMaladie: {disease}")
                print("-" * 60)
                print(f"{'Modèle':<20} {'R²':<10} {'MAE':<15} {'MAPE':<10}")
                print("-" * 60)
                
                for model_name in ['Random Forest', 'Gradient Boosting', 'Ridge Regression', 'KNN', 'Linear Regression', 'SVR']:
                    if model_name in comparison and 'r2' in comparison[model_name]:
                        print(f"{model_name:<20} {comparison[model_name]['r2']:<10.3f} {comparison[model_name]['mae']:<15.2f} {comparison[model_name]['mape']:<10.1f}%")
                
                print("-" * 60)
                print(f"\n✅ MEILLEUR MODÈLE: {info['best_model_name']}")
                print(f"   R² = {info['test_r2']:.3f} ({info['test_r2']*100:.1f}%)")
                print(f"   MAE = {info['test_mae']:.2f} cas")
                print(f"   MAPE = {info['test_mape']:.1f}%")
                break

print("✅ Module train_models chargé avec succès!")