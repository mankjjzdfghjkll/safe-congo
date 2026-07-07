# src/alert_system.py
"""Système de détection et gestion des alertes pour SAFE CONGO"""

from datetime import datetime
import pandas as pd
import numpy as np

class AlertSystem:
    """
    Système de détection et gestion des alertes épidémiologiques
    Seuils basés sur les directives OMS/IDSR (Integrated Disease Surveillance
    and Response) 3e édition 2019, adaptés au contexte RDC.
    Niveaux : FAIBLE (vert) → MODEREE (jaune) → HAUTE (orange) → CRITIQUE (rouge)
    """
    
    # Seuils de croissance hebdomadaire OMS communs à toutes les maladies
    # Source : OMS IDSR — dépassement du 75e/90e percentile historique
    GROWTH_THRESHOLDS = {
        'moderate_growth': 25,   # +25 % → FAIBLE→MODEREE
        'high_growth':     50,   # +50 % → MODEREE→HAUTE
        'critical_growth': 100,  # ×2    → HAUTE→CRITIQUE (doublement)
    }

    def __init__(self):
        """Initialise le système d'alertes"""
        self.alerts = []
        self.acknowledged_alerts = []
        self.alert_history = []

    # ------------------------------------------------------------------
    # Seuils OMS par maladie  (cas/zone de santé/semaine, pop ≈ 100 000)
    # Références :
    #   • OMS IDSR Technical Guidelines 3rd ed. (WHO-AFRO, 2019)
    #   • OMS — Cholera Technical Note (2023)
    #   • OMS — Malaria Epidemic Detection & Response (2004, updated 2022)
    #   • OMS — Measles elimination guidelines (2022)
    #   • OMS — Meningococcal disease guidelines (2018)
    #   • RSI (2005) — maladies à notification immédiate
    # ------------------------------------------------------------------
    _THRESHOLDS = {
        # ---- Paludisme -----------------------------------------------
        'paludisme conf': {
            'faible_cases': 50,   'moderate_cases': 101, 'high_cases': 501,
            'critical_cases': 2001, 'zero_tolerance': False,
            'note': "OMS : seuil épidémique = dépassement 90e pctile historique ; "
                    "RDC charge élevée → seuil absolu 2 001 cas/zone/sem"
        },
        'paludisme susp': {
            'faible_cases': 100,  'moderate_cases': 201, 'high_cases': 1001,
            'critical_cases': 3001, 'zero_tolerance': False,
            'note': "Cas suspects incluent non-confirmés ; seuils ×1,5 du confirmé"
        },
        # ---- Maladies diarrhéiques -----------------------------------
        'cholera': {
            'faible_cases': 1,    'moderate_cases': 6,   'high_cases': 21,
            'critical_cases': 51, 'zero_tolerance': False,
            'note': "OMS : 1 cas confirmé en zone libre = alerte immédiate ; "
                    "taux d'attaque >5/10 000/sem = HAUTE ; >20/10 000/sem = CRITIQUE"
        },
        'diarr sanglante': {
            'faible_cases': 5,    'moderate_cases': 21,  'high_cases': 51,
            'critical_cases': 101, 'zero_tolerance': False,
            'note': "OMS IDSR : diarrhée sanglante (shigellose probable) — "
                    "cluster ≥20 cas/sem → enquête ; ≥50 → riposte"
        },
        'diarrhee dhy m5': {
            'faible_cases': 20,   'moderate_cases': 51,  'high_cases': 151,
            'critical_cases': 301, 'zero_tolerance': False,
            'note': "Diarrhée aqueuse <5 ans ; seuils OMS contexte DRC"
        },
        # ---- Maladies respiratoires ----------------------------------
        'pneumonie': {
            'faible_cases': 10,   'moderate_cases': 31,  'high_cases': 101,
            'critical_cases': 251, 'zero_tolerance': False,
            'note': "OMS IDSR : pneumonie grave — cluster ≥30 cas/zone/sem → alerte"
        },
        'ira': {
            'faible_cases': 30,   'moderate_cases': 51,  'high_cases': 201,
            'critical_cases': 501, 'zero_tolerance': False,
            'note': "IRA (infection respiratoire aiguë) — seuil relatif 75e pctile"
        },
        'grippe': {
            'faible_cases': 10,   'moderate_cases': 21,  'high_cases': 76,
            'critical_cases': 201, 'zero_tolerance': False,
            'note': "OMS FluNet : dépassement seuil saisonnier 90e pctile → HAUTE ; "
                    "souche pandémique → CRITIQUE immédiat"
        },
        'coqueluche': {
            'faible_cases': 1,    'moderate_cases': 6,   'high_cases': 16,
            'critical_cases': 31, 'zero_tolerance': False,
            'note': "OMS IDSR : ≥3 cas confirmés/sem OU doublement 2 sem consécutives"
        },
        'diphterie': {
            'faible_cases': 1,    'moderate_cases': 2,   'high_cases': 3,
            'critical_cases': 6,  'zero_tolerance': False,
            'note': "OMS IDSR : tout cas confirmé → notification immédiate ; "
                    "cluster ≥5 → riposte nationale (RSI)"
        },
        # ---- Maladies à vaccin (PEV) ---------------------------------
        'rougeole': {
            'faible_cases': 1,    'moderate_cases': 4,   'high_cases': 11,
            'critical_cases': 26, 'zero_tolerance': False,
            'note': "OMS : tout cas confirmé → enquête ; taux d'attaque >1/100 000/mois "
                    "= épidémie ; >25 cas/zone/sem = CRITIQUE"
        },
        'pfa': {
            'faible_cases': 1,    'moderate_cases': 3,   'high_cases': 6,
            'critical_cases': 11, 'zero_tolerance': False,
            'note': "OMS IDSR : taux AFP attendu ≥2/100 000 enfants <15 ans/an (surveillance adéquate) ; "
                    "cluster ≥6 cas/zone/sem → enquête intensive ; ≥11 cas/zone/sem → CRITIQUE. "
                    "Tout poliovirus confirmé déclenche une CRITIQUE immédiate hors de ce calcul (RSI 2005)."
        },
        # ---- Méningite -----------------------------------------------
        'meningite': {
            'faible_cases': 1,    'moderate_cases': 5,   'high_cases': 11,
            'critical_cases': 21, 'zero_tolerance': False,
            'note': "OMS : seuil alerte = 5/100 000/sem (ceinture méningite) ; "
                    "seuil épidémique = 10/100 000/sem ; RDC hors ceinture → ≥5/zone/sem"
        },
        # ---- Fièvre typhoïde -----------------------------------------
        'fievre typhoide': {
            'faible_cases': 2,    'moderate_cases': 11,  'high_cases': 31,
            'critical_cases': 76, 'zero_tolerance': False,
            'note': "OMS IDSR : ≥5 cas/sem liés à une source commune → enquête"
        },
        # ---- Maladies à déclaration immédiate OMS (zéro tolérance) --
        'dracunculose': {
            'faible_cases': 0,    'moderate_cases': 0,   'high_cases': 0,
            'critical_cases': 1,  'zero_tolerance': True,
            'note': "OMS programme éradication : TOUT cas = CRITIQUE ; "
                    "objectif mondial = 0 cas ; chaque cas déclenche réponse immédiate"
        },
        'fievre jaune': {
            'faible_cases': 0,    'moderate_cases': 1,   'high_cases': 0,
            'critical_cases': 1,  'zero_tolerance': True,
            'note': "OMS RSI Art.6 : cas confirmé = urgence internationale ; "
                    "cas suspect = alerte immédiate"
        },
        'monkeypox': {
            'faible_cases': 1,    'moderate_cases': 3,   'high_cases': 11,
            'critical_cases': 26, 'zero_tolerance': False,
            'note': "OMS URGSP 2022/2024 : ≥5 cas/zone/sem → alerte ; "
                    ">25 cas/zone/sem → CRITIQUE (urgence santé publique RDC)"
        },
        'peste': {
            'faible_cases': 0,    'moderate_cases': 0,   'high_cases': 0,
            'critical_cases': 1,  'zero_tolerance': True,
            'note': "OMS RSI : tout cas suspect = notification immédiate internationale ; "
                    "tolérance zéro — Ituri/Nord-Kivu zones endémiques RDC"
        },
        'fha': {
            'faible_cases': 0,    'moderate_cases': 1,   'high_cases': 0,
            'critical_cases': 1,  'zero_tolerance': True,
            'note': "Fièvre hémorragique aiguë (Ebola/Marburg/etc.) — "
                    "RSI Art.6 : 1 cas suspect = alerte internationale ; confirmé = CRITIQUE"
        },
        'rage': {
            'faible_cases': 1,    'moderate_cases': 1,   'high_cases': 3,
            'critical_cases': 6,  'zero_tolerance': False,
            'note': "OMS : tout cas humain confirmé = CRITIQUE (létalité 100 % sans PEP) ; "
                    "clusters exposition → riposte"
        },
        'chikungunya': {
            'faible_cases': 1,    'moderate_cases': 11,  'high_cases': 51,
            'critical_cases': 151, 'zero_tolerance': False,
            'note': "OMS IDSR : cluster ≥10 cas/zone/sem → enquête vecteur ; "
                    ">150 cas/sem → riposte d'urgence"
        },
        'covid 19': {
            'faible_cases': 1,    'moderate_cases': 11,  'high_cases': 51,
            'critical_cases': 201, 'zero_tolerance': False,
            'note': "Seuils adaptés post-pandémie ; variant émergent → escalade CRITIQUE"
        },
        # ---- Santé maternelle & néonatale ----------------------------
        'tnn': {
            'faible_cases': 0,    'moderate_cases': 1,   'high_cases': 3,
            'critical_cases': 5,  'zero_tolerance': False,
            'note': "OMS : objectif élimination <1/1 000 naissances vivantes/district/an ; "
                    "≥1 cas/sem = excès → enquête ; ≥5 cas/sem = CRITIQUE"
        },
        'tetanos materne': {
            'faible_cases': 0,    'moderate_cases': 1,   'high_cases': 3,
            'critical_cases': 5,  'zero_tolerance': False,
            'note': "Mêmes seuils que TNN — élimination OMS"
        },
        'deces maternels': {
            'faible_cases': 1,    'moderate_cases': 3,   'high_cases': 6,
            'critical_cases': 11, 'zero_tolerance': False,
            'note': "OMS ODD 3.1 : cible <70/100 000 naissance ; "
                    ">10 décès/zone/sem = CRITIQUE — cluster exige audit immédiat"
        },
        # ---- MAPI (manifestations post-vaccination) ------------------
        'mapi legeres': {
            'faible_cases': 1,    'moderate_cases': 11,  'high_cases': 31,
            'critical_cases': 51, 'zero_tolerance': False,
            'note': "OMS : cluster MAPI légères ≥10 cas/lot/zone → signal ; "
                    "≥50 → suspension lot en attente enquête"
        },
        'mapi graves': {
            'faible_cases': 1,    'moderate_cases': 2,   'high_cases': 4,
            'critical_cases': 1,  'zero_tolerance': True,
            'note': "OMS : tout MAPI grave (hospitalisation/décès) = CRITIQUE immédiat ; "
                    "suspicion cluster → retrait lot"
        },
    }

    # Clé de secours si maladie non répertoriée
    _DEFAULT_THRESHOLDS = {
        'faible_cases': 5,    'moderate_cases': 21, 'high_cases': 51,
        'critical_cases': 101, 'zero_tolerance': False,
        'note': "Seuils génériques OMS IDSR — maladie non spécifiée"
    }

    # Levels ordered by severity
    _LEVEL_ORDER = ['INFO', 'FAIBLE', 'MODEREE', 'HAUTE', 'CRITIQUE']

    _REFERENCE_PRINCIPLES = {
        "idsr": (
            "OMS AFRO - Technical Guidelines for Integrated Disease Surveillance "
            "and Response in the African Region, third edition"
        ),
        "ihr": "Règlement Sanitaire International (RSI/IHR 2005)",
        "implementation": (
            "SAFE CONGO combine les seuils absolus par maladie, la croissance "
            "hebdomadaire et la notification immédiate des maladies à tolérance zéro."
        ),
    }

    @classmethod
    def _key(cls, disease_name: str) -> str:
        """Normalise le nom de maladie pour la correspondance dictionnaire."""
        import unicodedata
        s = disease_name.lower().strip()
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        return s

    def get_thresholds_for_disease(self, disease_name: str) -> dict:
        """
        Retourne les seuils OMS/IDSR pour une maladie donnée.
        
        Sources : OMS IDSR 3e éd. 2019, RSI 2005, guides spécifiques OMS
        par pathologie (cholera 2023, paludisme 2022, rougeole 2022, etc.)
        
        Returns:
            dict avec faible_cases, moderate_cases, high_cases, critical_cases,
                       moderate_growth, high_growth, critical_growth,
                       zero_tolerance (bool), note (str source OMS)
        """
        key = self._key(disease_name)
        # Recherche exacte puis partielle
        base = self._THRESHOLDS.get(key)
        if base is None:
            for k, v in self._THRESHOLDS.items():
                if k in key or key in k:
                    base = v
                    break
        if base is None:
            base = self._DEFAULT_THRESHOLDS
        result = dict(base)
        result.update(self.GROWTH_THRESHOLDS)
        # Compatibilité ascendante avec l'ancienne API
        result['high_cases']     = base['high_cases']
        result['critical_cases'] = base['critical_cases']
        result['high_growth']    = self.GROWTH_THRESHOLDS['high_growth']
        result['medium_growth']  = self.GROWTH_THRESHOLDS['moderate_growth']
        return result

    @classmethod
    def _severity_index(cls, level: str) -> int:
        return cls._LEVEL_ORDER.index(level)

    @classmethod
    def _max_level(cls, *levels: str) -> str:
        return max(levels, key=cls._severity_index)

    @staticmethod
    def _positive_number(value) -> bool:
        try:
            return float(value) > 0
        except (TypeError, ValueError):
            return False

    @classmethod
    def _case_level(cls, thresholds: dict, cases: int) -> str:
        """Classe le niveau par cas absolus sans déclencher sur des seuils à zéro."""
        cases = max(int(cases or 0), 0)
        if cases <= 0:
            return 'INFO'

        if thresholds.get('zero_tolerance'):
            return 'CRITIQUE'

        if cls._positive_number(thresholds.get('critical_cases')) and cases >= thresholds['critical_cases']:
            return 'CRITIQUE'
        if cls._positive_number(thresholds.get('high_cases')) and cases >= thresholds['high_cases']:
            return 'HAUTE'
        if cls._positive_number(thresholds.get('moderate_cases')) and cases >= thresholds['moderate_cases']:
            return 'MODEREE'
        if cls._positive_number(thresholds.get('faible_cases')) and cases >= thresholds['faible_cases']:
            return 'FAIBLE'
        return 'INFO'

    @classmethod
    def _growth_level(cls, thresholds: dict, growth_rate: float) -> str:
        """Classe le niveau par croissance hebdomadaire."""
        try:
            growth_rate = float(growth_rate or 0.0)
        except (TypeError, ValueError):
            growth_rate = 0.0

        if growth_rate <= 0:
            return 'INFO'
        if growth_rate >= thresholds['critical_growth']:
            return 'CRITIQUE'
        if growth_rate >= thresholds['high_growth']:
            return 'HAUTE'
        if growth_rate >= thresholds['moderate_growth']:
            return 'MODEREE'
        return 'FAIBLE'

    def get_threshold_audit(self, disease_name: str) -> dict:
        """Retourne les seuils et les références utilisées pour une maladie."""
        thresholds = self.get_thresholds_for_disease(disease_name)
        return {
            "disease": disease_name,
            "normalized_key": self._key(disease_name),
            "thresholds": thresholds,
            "references": dict(self._REFERENCE_PRINCIPLES),
        }

    @classmethod
    def classify_alert_level(cls, disease_name: str, cases: int, growth_rate: float) -> str:
        """
        Classe l'alerte selon les seuils OMS/IDSR.
        
        Retourne le niveau le plus sévère entre la classification par cas absolus
        et la classification par taux de croissance hebdomadaire.
        
        Niveaux : CRITIQUE > HAUTE > MODEREE > FAIBLE > INFO
        """
        inst = cls.__new__(cls)
        t = inst.get_thresholds_for_disease(disease_name)

        # Retourne le niveau le plus sévère
        level_cases = cls._case_level(t, cases)
        level_growth = cls._growth_level(t, growth_rate)
        return cls._max_level(level_cases, level_growth)
    
    def detect_alerts(self, predictions, historical_data, model_performances=None):
        """
        Détecte les alertes basées sur les prédictions et les données historiques
        
        Args:
            predictions (dict): Prédictions par maladie
            historical_data (DataFrame): Données historiques
            model_performances (dict): Performances des modèles
            
        Returns:
            list: Alertes détectées
        """
        alerts = []
        alert_id = len(self.alerts) + len(self.acknowledged_alerts) + 1
        
        for disease, pred in predictions.items():
            if pred is None:
                continue
            
            thresholds = self.get_thresholds_for_disease(disease)
            
            # Récupérer les données récentes
            disease_data = historical_data[historical_data['MALADIE'] == disease].sort_values('DEBUTSEM')
            if len(disease_data) < 2:
                continue
            
            current_cases = disease_data['TOTALCAS'].iloc[-1]
            previous_cases = disease_data['TOTALCAS'].iloc[-2]
            growth_rate = ((current_cases - previous_cases) / (previous_cases + 1)) * 100
            
            # Déterminer le niveau d'alerte via la méthode OMS unifiée
            alert_level = self.classify_alert_level(disease, int(current_cases), growth_rate)
            thresholds = self.get_thresholds_for_disease(disease)

            reason = []
            t = thresholds
            if t.get('zero_tolerance') and current_cases >= 1:
                reason.append(f"Tolérance zéro OMS — {int(current_cases)} cas détectés ({t.get('note', '')})")
            else:
                if current_cases >= t['critical_cases']:
                    reason.append(f"Cas ({int(current_cases)}) ≥ seuil critique OMS ({t['critical_cases']})")
                elif current_cases >= t['high_cases']:
                    reason.append(f"Cas ({int(current_cases)}) ≥ seuil élevé OMS ({t['high_cases']})")
                elif current_cases >= t.get('moderate_cases', 0):
                    reason.append(f"Cas ({int(current_cases)}) ≥ seuil modéré OMS ({t.get('moderate_cases')})")
                if growth_rate >= t['critical_growth']:
                    reason.append(f"Croissance {growth_rate:.1f}% ≥ seuil doublement OMS ({t['critical_growth']}%)")
                elif growth_rate >= t['high_growth']:
                    reason.append(f"Croissance {growth_rate:.1f}% ≥ seuil élevé OMS ({t['high_growth']}%)")
                elif growth_rate >= t['moderate_growth']:
                    reason.append(f"Croissance {growth_rate:.1f}% ≥ seuil modéré OMS ({t['moderate_growth']}%)")

            if alert_level and alert_level != 'INFO':
                alert = {
                    'id': alert_id,
                    'maladie': disease,
                    'niveau': alert_level,
                    'cas_actuels': int(current_cases),
                    'cas_predits': int(pred),
                    'croissance': round(growth_rate, 1),
                    'raison': '; '.join(reason) if reason else f"Seuil OMS dépassé : {alert_level}",
                    'source_oms': thresholds.get('note', ''),
                    'confiance_modele': 'moyenne',
                    'date_detection': datetime.now(),
                    'acknowledged': False
                }
                
                alerts.append(alert)
                alert_id += 1
        
        self.alerts = alerts
        return alerts
    
    def acknowledge_alert(self, alert_id, username):
        """
        Acquitte une alerte
        
        Args:
            alert_id (int): ID de l'alerte
            username (str): Nom de l'utilisateur qui acquitte
            
        Returns:
            bool: Succès de l'opération
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now()
                alert['acknowledged_by'] = username
                self.acknowledged_alerts.append(alert)
                self.alerts.remove(alert)
                self.alert_history.append(alert)
                return True
        return False
    
    def get_active_alerts(self):
        """
        Retourne les alertes actives (non acquittées)
        
        Returns:
            list: Alertes actives
        """
        return [a for a in self.alerts if not a.get('acknowledged', False)]
    
    def get_alert_history(self, limit=50):
        """
        Retourne l'historique des alertes acquittées
        
        Args:
            limit (int): Nombre maximum d'alertes
            
        Returns:
            list: Historique des alertes
        """
        history = self.alert_history + self.acknowledged_alerts
        history.sort(key=lambda x: x.get('date_detection', datetime.min), reverse=True)
        return history[:limit]
    
    def get_alert_summary(self):
        """
        Retourne un résumé des alertes
        
        Returns:
            dict: Résumé des alertes
        """
        active = self.get_active_alerts()
        return {
            'total_active': len(active),
            'critical': len([a for a in active if a['niveau'] == 'CRITIQUE']),
            'high': len([a for a in active if a['niveau'] == 'HAUTE']),
            'medium': len([a for a in active if a['niveau'] == 'MODEREE'])
        }


# Fonction de test
if __name__ == "__main__":
    print("Module alert_system chargé avec succès!")
    alert_system = AlertSystem()
    print(f" AlertSystem initialisé")
