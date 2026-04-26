# src/alert_system.py
"""Système de détection et gestion des alertes pour SAFE CONGO"""

from datetime import datetime
import pandas as pd
import numpy as np

class AlertSystem:
    """
    Système de détection et gestion des alertes épidémiologiques
    """
    
    def __init__(self):
        """Initialise le système d'alertes"""
        self.alerts = []
        self.acknowledged_alerts = []
        self.alert_history = []
    
    def get_thresholds_for_disease(self, disease_name):
        """
        Retourne les seuils appropriés pour une maladie
        
        Args:
            disease_name (str): Nom de la maladie
            
        Returns:
            dict: Seuils
        """
        disease_lower = disease_name.lower()
        if 'paludisme' in disease_lower or 'malaria' in disease_lower:
            return {
                'critical_cases': 500,
                'high_cases': 250,
                'critical_growth': 100,
                'high_growth': 50,
                'medium_growth': 25
            }
        return {
            'critical_cases': 100,
            'high_cases': 50,
            'critical_growth': 100,
            'high_growth': 50,
            'medium_growth': 25
        }
    
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
            
            # Déterminer le niveau d'alerte
            alert_level = None
            reason = []
            
            # Critères basés sur les cas prédits
            if pred > thresholds['critical_cases']:
                alert_level = 'CRITICAL'
                reason.append(f"Cas prédits ({int(pred)}) > seuil critique ({thresholds['critical_cases']})")
            elif pred > thresholds['high_cases']:
                alert_level = 'HIGH'
                reason.append(f"Cas prédits ({int(pred)}) > seuil élevé ({thresholds['high_cases']})")
            
            # Critères basés sur la croissance
            if alert_level != 'CRITICAL':
                if growth_rate > thresholds['critical_growth']:
                    alert_level = 'CRITICAL'
                    reason.append(f"Croissance de {growth_rate:.1f}% > seuil critique ({thresholds['critical_growth']}%)")
                elif growth_rate > thresholds['high_growth']:
                    if alert_level is None or alert_level == 'MEDIUM':
                        alert_level = 'HIGH'
                    reason.append(f"Croissance de {growth_rate:.1f}% > seuil élevé ({thresholds['high_growth']}%)")
                elif growth_rate > thresholds['medium_growth']:
                    if alert_level is None:
                        alert_level = 'MEDIUM'
                    reason.append(f"Croissance de {growth_rate:.1f}% > seuil moyen ({thresholds['medium_growth']}%)")
            
            if alert_level:
                alert = {
                    'id': alert_id,
                    'maladie': disease,
                    'niveau': alert_level,
                    'cas_actuels': int(current_cases),
                    'cas_predits': int(pred),
                    'croissance': round(growth_rate, 1),
                    'raison': '; '.join(reason),
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
            'critical': len([a for a in active if a['niveau'] == 'CRITICAL']),
            'high': len([a for a in active if a['niveau'] == 'HIGH']),
            'medium': len([a for a in active if a['niveau'] == 'MEDIUM'])
        }


# Fonction de test
if __name__ == "__main__":
    print("Module alert_system chargé avec succès!")
    alert_system = AlertSystem()
    print(f" AlertSystem initialisé")