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
LOGS_DIR = BASE_DIR / "logs"

# Création des dossiers
for d in [
    DATA_DIR,
    DATA_DIR / "raw",
    DATA_DIR / "processed",
    DB_DIR,
    MODELS_DIR,
    MODELS_DIR / "trained",
    MODELS_DIR / "evaluation",
    LOGS_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "raw" / "drc-2023_sem08.xlsx"
DB_FILE = DB_DIR / "users.db"
MODELS_FILE = MODELS_DIR / "trained" / "models.pkl"

# ============================================
# CONFIGURATION DE L'INTERFACE UTILISATEUR
# ============================================
UI_CONFIG = {
    'page_title': "SAFE CONGO - Surveillance Épidémiologique",
    'page_icon': "",
    'layout': "wide",
    'sidebar_state': "expanded",
    'primary_color': "#1a73e8",
    'secondary_color': "#00c853"
}

# ============================================
# NIVEAUX D'ALERTE OMS/IDSR — DÉFINITIONS OFFICIELLES
# ============================================
# Sources :
#   • OMS IDSR Technical Guidelines 3ème édition (WHO-AFRO, 2019)
#   • OMS — Integrated Disease Surveillance and Response (IDSR) Framework
#   • RSI (Règlement Sanitaire International, 2005) — cas à notification immédiate
#   • OMS — Epidemic preparedness and response guidelines (2022)
#
# Dans l'IDSR, chaque maladie dispose de deux seuils relatifs :
#   — Seuil d'alerte  : dépassement du 75e percentile historique → investigation
#   — Seuil épidémique: dépassement du 90e percentile historique → riposte
# Des seuils absolus (cas/zone de santé/semaine, population ≈ 100 000 habitants)
# complètent les seuils relatifs pour les maladies à fort potentiel épidémique.
# ============================================
WHO_ALERT_LEVELS = {
    'FAIBLE': {
        'label':      'Surveillance renforcée',
        'color':      '#22c55e',
        'icon':       '🟢',
        'who_criterion': (
            "Cas dépassant le niveau habituel mais inférieurs au seuil d'alerte OMS IDSR. "
            "Correspond au dépassement ponctuel du 50e percentile historique. "
            "Aucun doublement observé."
        ),
        'action':     (
            "Renforcer la collecte des données hebdomadaires, "
            "vérifier la complétude des rapports de zones de santé, "
            "informer le point focal provincial."
        ),
        'who_source': "OMS IDSR 3e éd. 2019 — Chapitre 4 : Niveaux de signal"
    },
    'MODEREE': {
        'label':      "Seuil d'alerte OMS",
        'color':      '#fcd116',
        'icon':       '🟡',
        'who_criterion': (
            "Dépassement du seuil d'alerte OMS/IDSR : nombre de cas ≥ 75e percentile "
            "historique pour la même semaine épidémiologique, OU croissance hebdomadaire "
            "≥ 25 % par rapport à la semaine précédente. "
            "Signale qu'une épidémie peut se développer."
        ),
        'action':     (
            "Déclencher une investigation épidémiologique de terrain. "
            "Vérifier la source (eau, alimentation, vecteur). "
            "Préparer les stocks de riposte (médicaments, matériel). "
            "Notifier le niveau provincial dans les 24 heures."
        ),
        'who_source': (
            "OMS IDSR 3e éd. 2019 — Seuil d'alerte (Alert Threshold) : "
            "75e percentile historique / croissance +25 %/semaine"
        )
    },
    'HAUTE': {
        'label':      'Seuil épidémique OMS',
        'color':      '#f59e0b',
        'icon':       '🟠',
        'who_criterion': (
            "Dépassement du seuil épidémique OMS/IDSR : nombre de cas ≥ 90e percentile "
            "historique OU doublement sur deux semaines consécutives (croissance ≥ 50 %). "
            "Confirme le début d'une flambée épidémique."
        ),
        'action':     (
            "Activer le Comité de Riposte aux Épidémies (CRE) provincial. "
            "Déployer une équipe d'intervention rapide. "
            "Notifier le niveau national et l'OMS dans les 48 heures. "
            "Mobiliser les partenaires humanitaires (OMS, UNICEF, MSF)."
        ),
        'who_source': (
            "OMS IDSR 3e éd. 2019 — Seuil épidémique (Epidemic Threshold) : "
            "90e percentile historique / doublement en 2 semaines"
        )
    },
    'CRITIQUE': {
        'label':      'Urgence de santé publique',
        'color':      '#ce1126',
        'icon':       '🔴',
        'who_criterion': (
            "Dépassement du seuil de crise OMS : cas > 2× le seuil épidémique, "
            "OU doublement hebdomadaire consécutif (croissance ≥ 100 %), "
            "OU maladie à tolérance zéro (RSI Art. 6 : peste, FHA/Ebola, fièvre jaune, "
            "dracunculose, cas confirmé de polio, MAPI grave). "
            "Constitue une Urgence de Santé Publique de Portée Nationale ou Internationale."
        ),
        'action':     (
            "Notification immédiate au Ministère de la Santé Publique de la RDC. "
            "Activation du Plan de Contingence National. "
            "Notification obligatoire à l'OMS via le RSI (≤ 24 h pour maladies RSI). "
            "Coordination HEOC (Health Emergency Operations Centre). "
            "Déploiement logistique d'urgence et isolement si applicable."
        ),
        'who_source': (
            "RSI (2005) Art. 6 & Annexe 2 — Urgence de santé publique de portée internationale. "
            "OMS IDSR 3e éd. 2019 — Seuil de crise : doublement hebdomadaire / maladies RSI"
        )
    },
    'INFO': {
        'label':      'Information de routine',
        'color':      '#0a5fab',
        'icon':       '🔵',
        'who_criterion': (
            "Niveau normal de surveillance : cas en-dessous des seuils OMS IDSR. "
            "Aucune tendance anormale détectée."
        ),
        'action':     "Maintenir la surveillance épidémiologique hebdomadaire standard.",
        'who_source': "OMS IDSR 3e éd. 2019 — Surveillance de routine"
    },
}

# ============================================
# PARAMÈTRES D'ENTRAÎNEMENT
# ============================================
TRAINING_CONFIG = {
    'min_cases': 50,
    'min_weeks': 20,
    'history_weeks': 4,
    'test_size': 0.2,
    'cv_splits': 5,
    'random_state': 42
}

MODEL_RESULT_FILTERS = {
    'min_acceptable_r2': 0.5,
}

ALERT_LEVEL_ORDER = [
    'CRITIQUE',
    'HAUTE',
    'MODEREE',
    'FAIBLE',
    'INFO',
]

ALERT_LEVEL_COLORS = {
    'CRITIQUE': '#ce1126',   # Rouge OMS — urgence
    'HAUTE':    '#f59e0b',   # Orange OMS — alerte épidémique
    'MODEREE':  '#fcd116',   # Jaune OMS — seuil d'alerte
    'FAIBLE':   '#22c55e',   # Vert OMS — surveillance renforcée
    'INFO':     '#0a5fab',   # Bleu — information de routine
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

