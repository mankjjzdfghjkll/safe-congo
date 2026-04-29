# utils/auth.py - Version complète avec toutes les fonctions exportées
import streamlit as st
import sqlite3
import hashlib
from pathlib import Path
import time
import pandas as pd

class AuthSystem:
    """Système d'authentification pour Admin et Autorités Sanitaires"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "database" / "users.db"
        
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=30)
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        for _ in range(5):
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Table des utilisateurs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL CHECK(role IN ('admin', 'autorite_sanitaire')),
                        nom TEXT NOT NULL,
                        prenom TEXT NOT NULL,
                        email TEXT NOT NULL,
                        telephone TEXT,
                        province TEXT,
                        zone_sante TEXT,
                        notification_email INTEGER DEFAULT 1,
                        notification_sms INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active INTEGER DEFAULT 1
                    )
                ''')
                
                # Table des données épidémiologiques
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS epidemiological_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        disease TEXT NOT NULL,
                        week INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        province TEXT NOT NULL,
                        zone_sante TEXT NOT NULL,
                        total_cases INTEGER DEFAULT 0,
                        total_deaths INTEGER DEFAULT 0,
                        incidence_rate REAL,
                        mortality_rate REAL,
                        entered_by INTEGER,
                        entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        validated INTEGER DEFAULT 0,
                        FOREIGN KEY (entered_by) REFERENCES users(id)
                    )
                ''')
                
                # Table des alertes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        disease TEXT NOT NULL,
                        province TEXT NOT NULL,
                        zone_sante TEXT NOT NULL,
                        week INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        current_cases INTEGER,
                        predicted_cases REAL,
                        growth_rate REAL,
                        alert_level TEXT,
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_read INTEGER DEFAULT 0,
                        pdf_generated INTEGER DEFAULT 0
                    )
                ''')
                
                # Table des notifications
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        alert_id INTEGER,
                        title TEXT,
                        message TEXT,
                        is_read INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (alert_id) REFERENCES alerts(id)
                    )
                ''')
                
                # Créer l'admin par défaut
                cursor.execute("SELECT * FROM users WHERE username = 'admin'")
                if not cursor.fetchone():
                    admin_password = self._hash_password('Admin@123')
                    cursor.execute('''
                        INSERT INTO users (username, password, role, nom, prenom, email, telephone)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', ('admin', admin_password, 'admin', 'ADMIN', 'System', 'admin@safe-congo.com', '+243800000001'))
                
                # Créer des autorités sanitaires par défaut
                default_authorities = [
                    ('autorite_kinshasa', 'Kinshasa', 'Kinshasa Centre', 'KABILA', 'Jean', 'jean.kabila@sante.gouv.cd', '+243811111111'),
                    ('autorite_kasai', 'Kasaï', 'Tshikapa', 'MUKENDI', 'Marie', 'marie.mukendi@sante.gouv.cd', '+243822222222'),
                    ('autorite_nordkivu', 'Nord-Kivu', 'Goma', 'KAMBALE', 'Paul', 'paul.kambale@sante.gouv.cd', '+243833333333'),
                    ('autorite_sudkivu', 'Sud-Kivu', 'Bukavu', 'MULONGO', 'Alice', 'alice.mulongo@sante.gouv.cd', '+243844444444'),
                ]
                
                for auth_data in default_authorities:
                    cursor.execute("SELECT * FROM users WHERE username = ?", (auth_data[0],))
                    if not cursor.fetchone():
                        auth_password = self._hash_password('Sante@2024')
                        cursor.execute('''
                            INSERT INTO users (username, password, role, nom, prenom, email, telephone, province, zone_sante)
                            VALUES (?, ?, 'autorite_sanitaire', ?, ?, ?, ?, ?, ?)
                        ''', (auth_data[0], auth_password, auth_data[3], auth_data[4], auth_data[5], auth_data[6], auth_data[1], auth_data[2]))
                
                conn.commit()
                conn.close()
                break
            except sqlite3.OperationalError:
                time.sleep(1)
                continue
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            hashed = self._hash_password(password)
            
            cursor.execute('''
                SELECT id, username, role, nom, prenom, email, telephone, province, zone_sante
                FROM users WHERE username = ? AND password = ? AND is_active = 1
            ''', (username, hashed))
            
            user = cursor.fetchone()
            if user:
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
                conn.commit()
                conn.close()
                return {
                    'id': user[0], 'username': user[1], 'role': user[2],
                    'nom': user[3], 'prenom': user[4], 'email': user[5],
                    'telephone': user[6], 'province': user[7], 'zone_sante': user[8],
                    'full_name': f"{user[3]} {user[4]}", 'authenticated': True
                }
            conn.close()
            return None
        except Exception:
            return None
    
    def register_authority(self, username, password, nom, prenom, email, telephone, province, zone_sante):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Nom d'utilisateur existe déjà"
            
            hashed = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password, role, nom, prenom, email, telephone, province, zone_sante)
                VALUES (?, ?, 'autorite_sanitaire', ?, ?, ?, ?, ?, ?)
            ''', (username, hashed, nom, prenom, email, telephone, province, zone_sante))
            
            conn.commit()
            conn.close()
            return True, "Autorité sanitaire créée avec succès"
        except Exception as e:
            return False, f"Erreur: {e}"
    
    def get_all_authorities(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, nom, prenom, email, telephone, province, zone_sante, created_at, last_login
                FROM users WHERE role = 'autorite_sanitaire' AND is_active = 1
            ''')
            users = cursor.fetchall()
            conn.close()
            return [{'id': u[0], 'username': u[1], 'nom': u[2], 'prenom': u[3], 
                     'email': u[4], 'telephone': u[5], 'province': u[6], 
                     'zone_sante': u[7], 'created_at': u[8], 'last_login': u[9]} for u in users]
        except:
            return []
    
    def get_all_users(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, role, nom, prenom, email, telephone, province, zone_sante, created_at, last_login, is_active
                FROM users ORDER BY created_at DESC
            ''')
            users = cursor.fetchall()
            conn.close()
            return [{'id': u[0], 'username': u[1], 'role': u[2], 'nom': u[3], 'prenom': u[4],
                     'email': u[5], 'telephone': u[6], 'province': u[7], 'zone_sante': u[8],
                     'created_at': u[9], 'last_login': u[10], 'is_active': u[11]} for u in users]
        except:
            return []
    
    def save_alert_notification(self, user_id, alert_id, title, message):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (user_id, alert_id, title, message)
                VALUES (?, ?, ?, ?)
            ''', (user_id, alert_id, title, message))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_notifications(self, user_id, unread_only=False):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            if unread_only:
                cursor.execute('''
                    SELECT id, title, message, is_read, created_at
                    FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, title, message, is_read, created_at
                    FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50
                ''', (user_id,))
            notifs = cursor.fetchall()
            conn.close()
            return [{'id': n[0], 'title': n[1], 'message': n[2], 'is_read': n[3], 'created_at': n[4]} for n in notifs]
        except:
            return []
    
    def mark_notification_read(self, notif_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notif_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def mark_all_notifications_read(self, user_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_unread_count(self, user_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def delete_user(self, user_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True, "Utilisateur désactivé"
        except Exception as e:
            return False, str(e)
    
    def get_stats(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'autorite_sanitaire' AND is_active = 1")
            total_authorities = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM alerts")
            total_alerts = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM epidemiological_data")
            total_entries = cursor.fetchone()[0]
            conn.close()
            return {
                'total_authorities': total_authorities,
                'total_alerts': total_alerts,
                'total_entries': total_entries
            }
        except:
            return {'total_authorities': 0, 'total_alerts': 0, 'total_entries': 0}


# ============ FONCTIONS STREAMLIT ============

def login_page():
    """Redirige vers la page d'authentification moderne."""
    st.switch_page("pages/auth.py")
    return None


def require_auth(auth):
    """Vérifie l'authentification et redirige vers la page de login moderne."""
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        st.switch_page("pages/auth.py")
        return None
    return st.session_state.user


def logout():
    """Déconnecte l'utilisateur"""
    st.session_state.user = None
    st.rerun()


def get_current_user():
    """Retourne l'utilisateur courant"""
    return st.session_state.user if 'user' in st.session_state else None


def check_role(allowed_roles):
    """Vérifie si l'utilisateur a le rôle requis"""
    user = get_current_user()
    if not user:
        return False
    return user.get('role') in allowed_roles


def show_user_profile():
    """Affiche le profil utilisateur dans la sidebar"""
    user = get_current_user()
    if not user:
        return False
    
    role_icon = "" if user['role'] == 'admin' else ""
    role_color = "#0066CC" if user['role'] == 'admin' else "#00A86B"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 20px; border-radius: 16px; margin: 10px 0; text-align: center;">
        <div style="font-size: 3em;">{role_icon}</div>
        <div style="font-weight: 600; font-size: 1.1em;">{user['full_name']}</div>
        <div style="color: #666; font-size: 0.85em;">@{user['username']}</div>
        <div style="background: {role_color}; color: white; padding: 4px 12px; border-radius: 20px; 
                    font-size: 0.75em; display: inline-block; margin-top: 8px;">
            {user['role'].replace('_', ' ').upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if user['role'] == 'autorite_sanitaire' and user.get('province'):
        st.info(f" {user['province']} - {user.get('zone_sante', 'N/A')}")
    
    if st.button(" Déconnexion", use_container_width=True):
        logout()
    
    return True


def show_admin_panel():
    """Affiche le panneau d'administration"""
    user = get_current_user()
    if not user or user['role'] != 'admin':
        st.error(" Accès réservé aux administrateurs")
        return
    
    st.subheader(" Panneau d'Administration")
    
    auth = AuthSystem()
    stats = auth.get_stats()
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Autorités sanitaires", stats['total_authorities'])
    with col2:
        st.metric("Alertes générées", stats['total_alerts'])
    with col3:
        st.metric("Saisies épidémio", stats['total_entries'])
    
    st.markdown("---")
    
    # Liste des utilisateurs
    st.subheader(" Gestion des utilisateurs")
    users = auth.get_all_users()
    
    if users:
        df = pd.DataFrame(users)
        st.dataframe(df[['username', 'role', 'nom', 'prenom', 'email', 'province', 'created_at']], use_container_width=True)
        
        # Supprimer un utilisateur
        with st.expander(" Désactiver un utilisateur"):
            user_to_delete = st.selectbox("Sélectionner un utilisateur", [u['username'] for u in users if u['username'] != 'admin'])
            if st.button("Désactiver", type="secondary"):
                user_id = next((u['id'] for u in users if u['username'] == user_to_delete), None)
                if user_id:
                    success, msg = auth.delete_user(user_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
    
    st.markdown("---")
    
    # Notifications
    st.subheader(" Centre de notifications")
    notifs = auth.get_notifications(user['id'], unread_only=False)
    if notifs:
        for n in notifs[:10]:
            st.markdown(f"""
            <div style="background: {'#e3f2fd' if not n['is_read'] else '#f5f5f5'}; 
                        padding: 10px; border-radius: 10px; margin: 5px 0;">
                <strong>{n['title']}</strong>
                <p style="margin: 5px 0; font-size: 0.9em;">{n['message'][:150]}</p>
                <span style="color: #999; font-size: 0.75em;">{n['created_at']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucune notification")