# utils/notifications.py
import streamlit as st
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sqlite3
from pathlib import Path

class NotificationSystem:
    """Système de notifications pour les autorités sanitaires"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "database" / "users.db"
        self.db_path = db_path
        
        # Configuration email (à configurer avec vos identifiants)
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'safe.congo@example.com',  # À modifier
            'sender_password': 'your_password'  # À modifier
        }
    
    def create_notification(self, user_id, notif_type, title, message):
        """Crée une notification dans la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (user_id, type, title, message)
                VALUES (?, ?, ?, ?)
            ''', (user_id, notif_type, title, message))
            
            conn.commit()
            notification_id = cursor.lastrowid
            conn.close()
            
            # Envoyer immédiatement si l'utilisateur a activé les notifications
            self._send_notification_to_user(user_id, title, message, notification_id)
            
            return notification_id
        except Exception as e:
            print(f"Erreur création notification: {e}")
            return None
    
    def _send_notification_to_user(self, user_id, title, message, notification_id):
        """Envoie la notification selon les préférences de l'utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, phone, notification_email, notification_sms
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return
            
            email, phone, notif_email, notif_sms = user
            
            # Envoi par email
            if notif_email and email:
                self.send_email(email, title, message)
                self._mark_notification_sent(notification_id, 'email')
            
            # Envoi par SMS (optionnel, nécessite API SMS)
            if notif_sms and phone:
                self.send_sms(phone, f"{title}: {message[:160]}")
                self._mark_notification_sent(notification_id, 'sms')
                
        except Exception as e:
            print(f"Erreur envoi notification: {e}")
    
    def send_email(self, to_email, subject, message):
        """Envoie un email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = to_email
            msg['Subject'] = f"[SAFE CONGO] {subject}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h2 style="color: white;">🛡️ SAFE CONGO</h2>
                    <p style="color: white;">Système de Surveillance Épidémiologique</p>
                </div>
                <div style="padding: 20px;">
                    <h3>{subject}</h3>
                    <p>{message}</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Ce message est automatique. Pour ne plus recevoir ces notifications, 
                        veuillez modifier vos préférences dans l'application.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Envoi (décommenter quand les identifiants sont configurés)
            # server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            # server.starttls()
            # server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            # server.send_message(msg)
            # server.quit()
            
            print(f"Email envoyé à {to_email}")
            return True
        except Exception as e:
            print(f"Erreur email: {e}")
            return False
    
    def send_sms(self, phone, message):
        """Envoie un SMS (à configurer avec un service comme Twilio)"""
        # À implémenter avec Twilio ou autre service SMS
        print(f"SMS envoyé à {phone}: {message}")
        return True
    
    def _mark_notification_sent(self, notification_id, method):
        """Marque la notification comme envoyée"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if method == 'email':
                cursor.execute('UPDATE notifications SET sent_email = 1 WHERE id = ?', (notification_id,))
            elif method == 'sms':
                cursor.execute('UPDATE notifications SET sent_sms = 1 WHERE id = ?', (notification_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur: {e}")
    
    def get_user_notifications(self, user_id, unread_only=True):
        """Récupère les notifications d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if unread_only:
                cursor.execute('''
                    SELECT id, type, title, message, created_at
                    FROM notifications
                    WHERE user_id = ? AND is_read = 0
                    ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, type, title, message, created_at, is_read
                    FROM notifications
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 50
                ''', (user_id,))
            
            notifications = cursor.fetchall()
            conn.close()
            
            return [{
                'id': n[0],
                'type': n[1],
                'title': n[2],
                'message': n[3],
                'created_at': n[4],
                'is_read': n[5] if len(n) > 5 else 0
            } for n in notifications]
        except Exception as e:
            print(f"Erreur: {e}")
            return []
    
    def mark_as_read(self, notification_id):
        """Marque une notification comme lue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def mark_all_as_read(self, user_id):
        """Marque toutes les notifications comme lues"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def send_alert_to_all_authorities(self, disease, current_cases, predicted_cases, growth_rate):
        """Envoie une alerte à toutes les autorités sanitaires"""
        title = f"⚠️ ALERTE ÉPIDÉMIOLOGIQUE - {disease}"
        message = f"""
        Une augmentation significative a été détectée pour {disease}.
        
        📊 Cas actuels: {current_cases:,}
        📈 Cas prédits: {predicted_cases:,}
        📈 Taux de croissance: {growth_rate:.1f}%
        
        Action recommandée: Surveillance renforcée et mesures préventives.
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Récupérer tous les utilisateurs avec rôle autorite_sanitaire
            cursor.execute('''
                SELECT id FROM users 
                WHERE role = 'autorite_sanitaire' AND is_active = 1
            ''')
            
            authorities = cursor.fetchall()
            conn.close()
            
            for auth in authorities:
                self.create_notification(auth[0], 'alert', title, message)
            
            return len(authorities)
        except Exception as e:
            print(f"Erreur: {e}")
            return 0


def get_notification_badge():
    """Affiche un badge de notification dans la sidebar"""
    if 'user' in st.session_state and st.session_state.user:
        notif_system = NotificationSystem()
        notifications = notif_system.get_user_notifications(st.session_state.user['id'])
        count = len(notifications)
        
        if count > 0:
            return f"🔔 {count}"
    return "🔔"