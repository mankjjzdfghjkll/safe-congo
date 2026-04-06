# src/config.py
"""Configuration centralisée pour SAFE CONGO"""

from pathlib import Path

# ============================================
# CHEMINS DES FICHIERS
# ============================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "database"
MODELS_DIR = BASE_DIR / "models"

# Création des dossiers
for d in [DATA_DIR, DB_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "drc-2023_sem08.xlsx"
DB_FILE = DB_DIR / "users.db"
MODELS_FILE = MODELS_DIR / "models.pkl"

# ============================================
# CONFIGURATION DE L'INTERFACE UTILISATEUR
# ============================================
UI_CONFIG = {
    'page_title': "SAFE CONGO - Surveillance Épidémiologique",
    'page_icon': "🛡️",
    'layout': "wide",
    'sidebar_state': "expanded",
    'primary_color': "#1a73e8",
    'secondary_color': "#00c853"
}

# ============================================
# SEUILS D'ALERTE PAR MALADIE
# ============================================
ALERT_THRESHOLDS = {
    'paludisme': {
        'critical_cases': 500,
        'high_cases': 250,
        'critical_growth': 100,
        'high_growth': 50,
        'medium_growth': 25
    },
    'cholera': {
        'critical_cases': 50,
        'high_cases': 20,
        'critical_growth': 100,
        'high_growth': 50,
        'medium_growth': 25
    },
    'default': {
        'critical_cases': 100,
        'high_cases': 50,
        'critical_growth': 100,
        'high_growth': 50,
        'medium_growth': 25
    }
}

# ============================================
# PARAMÈTRES D'ENTRAÎNEMENT
# ============================================
TRAINING_CONFIG = {
    'min_cases': 50,
    'min_weeks': 20,
    'test_size': 0.2,
    'cv_splits': 5,
    'random_state': 42
}

# ============================================
# MODÈLES À COMPARER
# ============================================
MODELS_TO_COMPARE = [
    'Random Forest',
    'Gradient Boosting',
    'Ridge Regression',
    'KNN'
]

print("✅ Configuration SAFE CONGO chargée avec succès!")