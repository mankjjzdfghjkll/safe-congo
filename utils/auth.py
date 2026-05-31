# utils/auth.py - Version complète avec toutes les fonctions exportées
import hashlib
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path

import pandas as pd
import streamlit as st


SCHEMA_PATH = Path(__file__).parent.parent / "database" / "schema.sql"
APP_ENV = os.environ.get("SAFE_CONGO_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV in {"prod", "production"}
BOOTSTRAP_USERS_ENABLED = os.environ.get(
    "SAFE_CONGO_ENABLE_BOOTSTRAP_USERS",
    "0" if IS_PRODUCTION else "1",
).strip().lower() in {"1", "true", "yes", "on"}
LOCAL_DEV_ADMIN_PASSWORD = "Admin@123"
LOCAL_DEV_AUTHORITY_PASSWORD = "Sante@2024"

class AuthSystem:
    """Système d'authentification pour Admin et Autorités Sanitaires"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "database" / "users.db"
        
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def _load_schema_sql(self):
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema introuvable: {SCHEMA_PATH}")
        return SCHEMA_PATH.read_text(encoding="utf-8")

    def _clean_text(self, value):
        return " ".join(str(value or "").strip().split())

    def _strip_html(self, value):
        text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
        if "<" in text and ">" in text:
            text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("&nbsp;", " ")
        lines = [" ".join(line.split()) for line in text.split("\n")]
        return "\n".join(line for line in lines if line).strip()

    def _normalize_notification_title(self, value):
        cleaned = self._clean_text(self._strip_html(value))
        upper = cleaned.upper()
        legacy_tokens = ("ALERTE INFO", "INFORMATION TERRAIN", "NOUVELLE_DONNEE", "NOUVELLE DONNEE")
        if any(token in upper for token in legacy_tokens):
            suffix = ""
            if " - " in cleaned:
                suffix = cleaned.split(" - ", 1)[1].strip()
            elif "-" in cleaned:
                suffix = cleaned.split("-", 1)[1].strip()
            return f"ALERTE FAIBLE - {suffix}" if suffix else "ALERTE FAIBLE"
        return cleaned

    def _normalize_notification_message(self, value):
        return self._strip_html(value)

    def _normalize_legacy_notifications(self, cursor):
        cursor.execute(
            """
            UPDATE alerts
            SET alert_level = 'FAIBLE'
            WHERE upper(trim(coalesce(alert_level, ''))) IN ('INFO', 'NOUVELLE_DONNEE', 'NOUVELLE DONNEE')
            """
        )

        cursor.execute(
            """
            SELECT id, title, message
            FROM notifications
            WHERE instr(upper(coalesce(title, '')), 'INFO') > 0
               OR instr(upper(coalesce(title, '')), 'INFORMATION TERRAIN') > 0
               OR instr(upper(coalesce(title, '')), 'NOUVELLE_DONNEE') > 0
               OR instr(upper(coalesce(title, '')), 'NOUVELLE DONNEE') > 0
               OR instr(coalesce(title, ''), '<') > 0
               OR instr(coalesce(message, ''), '<') > 0
            """
        )
        for notif_id, title, message in cursor.fetchall():
            normalized_title = self._normalize_notification_title(title)
            normalized_message = self._normalize_notification_message(message)
            if normalized_title != (title or "") or normalized_message != (message or ""):
                cursor.execute(
                    "UPDATE notifications SET title = ?, message = ? WHERE id = ?",
                    (normalized_title, normalized_message, notif_id),
                )

    def _normalize_login_identifier(self, value):
        return self._clean_text(value).casefold()

    def _bootstrap_password(self, role):
        env_var = (
            "SAFE_CONGO_BOOTSTRAP_ADMIN_PASSWORD"
            if role == "admin"
            else "SAFE_CONGO_BOOTSTRAP_AUTHORITY_PASSWORD"
        )
        configured = os.environ.get(env_var, "").strip()
        if configured:
            return configured
        if IS_PRODUCTION and BOOTSTRAP_USERS_ENABLED:
            raise RuntimeError(
                f"La variable d'environnement {env_var} est obligatoire quand le bootstrap des comptes est actif en production."
            )
        return LOCAL_DEV_ADMIN_PASSWORD if role == "admin" else LOCAL_DEV_AUTHORITY_PASSWORD

    def _is_legacy_sha256_hash(self, value):
        return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())

    def _verify_password(self, stored_hash, password):
        if not stored_hash:
            return False
        if self._is_legacy_sha256_hash(stored_hash):
            legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
            return secrets.compare_digest(stored_hash, legacy)

        try:
            algorithm, n_value, r_value, p_value, salt_hex, digest_hex = stored_hash.split("$")
            if algorithm != "scrypt":
                return False
            salt = bytes.fromhex(salt_hex)
            digest = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt,
                n=int(n_value),
                r=int(r_value),
                p=int(p_value),
                dklen=len(bytes.fromhex(digest_hex)),
            ).hex()
            return secrets.compare_digest(digest, digest_hex)
        except (TypeError, ValueError):
            return False

    def _bootstrap_default_users(self, cursor):
        if not BOOTSTRAP_USERS_ENABLED:
            return
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                '''
                INSERT INTO users (username, password, role, nom, prenom, email, telephone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    'admin',
                    self._hash_password(self._bootstrap_password("admin")),
                    'admin',
                    'ADMIN',
                    'System',
                    'admin@safe-congo.com',
                    '+243800000001',
                ),
            )

        default_authorities = [
            ('autorite_kinshasa', 'Kinshasa', 'Kinshasa Centre', 'KABILA', 'Jean', 'jean.kabila@sante.gouv.cd', '+243811111111'),
            ('autorite_kasai', 'Kasaï', 'Tshikapa', 'MUKENDI', 'Marie', 'marie.mukendi@sante.gouv.cd', '+243822222222'),
            ('autorite_nordkivu', 'Nord-Kivu', 'Goma', 'KAMBALE', 'Paul', 'paul.kambale@sante.gouv.cd', '+243833333333'),
            ('autorite_sudkivu', 'Sud-Kivu', 'Bukavu', 'MULONGO', 'Alice', 'alice.mulongo@sante.gouv.cd', '+243844444444'),
        ]
        for auth_data in default_authorities:
            cursor.execute("SELECT id FROM users WHERE username = ?", (auth_data[0],))
            if not cursor.fetchone():
                cursor.execute(
                    '''
                    INSERT INTO users (username, password, role, nom, prenom, email, telephone, province, zone_sante)
                    VALUES (?, ?, 'autorite_sanitaire', ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        auth_data[0],
                        self._hash_password(self._bootstrap_password("autorite_sanitaire")),
                        auth_data[3],
                        auth_data[4],
                        auth_data[5],
                        auth_data[6],
                        auth_data[1],
                        auth_data[2],
                    ),
                )
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        for _ in range(5):
            try:
                conn = self._get_connection()
                conn.executescript(self._load_schema_sql())
                cursor = conn.cursor()
                self._bootstrap_default_users(cursor)
                self._normalize_legacy_notifications(cursor)
                
                conn.commit()
                conn.close()
                break
            except sqlite3.OperationalError:
                time.sleep(1)
                continue
    
    def _hash_password(self, password):
        salt = secrets.token_bytes(16)
        n_value = 2**14
        r_value = 8
        p_value = 1
        digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n_value, r=r_value, p=p_value, dklen=64)
        return f"scrypt${n_value}${r_value}${p_value}${salt.hex()}${digest.hex()}"
    
    def authenticate(self, username, password):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            identifier = self._normalize_login_identifier(username)
            if not identifier:
                conn.close()
                return None
            
            cursor.execute('''
                SELECT id, username, password, role, nom, prenom, email, telephone, province, zone_sante, is_active
                FROM users
                WHERE lower(trim(username)) = ? OR lower(trim(email)) = ?
                ORDER BY is_active DESC, id DESC
                LIMIT 1
            ''', (identifier, identifier))
            
            user = cursor.fetchone()
            if user and int(user[10]) == 1 and self._verify_password(user[2], password):
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
                if self._is_legacy_sha256_hash(user[2]):
                    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (self._hash_password(password), user[0]))
                conn.commit()
                conn.close()
                return {
                    'id': user[0], 'username': user[1], 'role': user[3],
                    'nom': user[4], 'prenom': user[5], 'email': user[6],
                    'telephone': user[7], 'province': user[8], 'zone_sante': user[9],
                    'full_name': f"{user[4]} {user[5]}", 'authenticated': True
                }
            conn.close()
            return None
        except Exception:
            return None

    def diagnose_login_attempt(self, identifier):
        try:
            normalized = self._normalize_login_identifier(identifier)
            if not normalized:
                return {"status": "missing"}

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT username, email, is_active
                FROM users
                WHERE lower(trim(username)) = ? OR lower(trim(email)) = ?
                ORDER BY is_active DESC, id DESC
                LIMIT 1
                ''',
                (normalized, normalized),
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return {"status": "not_found"}
            if int(row[2]) != 1:
                return {"status": "disabled", "username": row[0], "email": row[1]}
            return {"status": "password_mismatch", "username": row[0], "email": row[1]}
        except Exception:
            return {"status": "unknown"}
    
    def register_user(self, username, password, nom, prenom, email, telephone, role, province="", zone_sante=""):
        try:
            normalized_username = self._clean_text(username)
            normalized_nom = self._clean_text(nom)
            normalized_prenom = self._clean_text(prenom)
            normalized_email = self._clean_text(email).lower()
            normalized_phone = self._clean_text(telephone)
            normalized_role = self._clean_text(role)
            normalized_province = self._clean_text(province)
            normalized_zone = self._clean_text(zone_sante)

            if normalized_role not in {"admin", "autorite_sanitaire"}:
                return False, "Role invalide"
            if normalized_role == "autorite_sanitaire" and not all([normalized_province, normalized_zone]):
                return False, "La province et la zone de sante sont obligatoires pour une autorite sanitaire"

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE lower(trim(username)) = ?",
                (normalized_username.casefold(),),
            )
            if cursor.fetchone():
                conn.close()
                return False, "Nom d'utilisateur existe déjà"
            
            cursor.execute('''
                INSERT INTO users (username, password, role, nom, prenom, email, telephone, province, zone_sante)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                normalized_username,
                self._hash_password(password),
                normalized_role,
                normalized_nom,
                normalized_prenom,
                normalized_email,
                normalized_phone,
                normalized_province,
                normalized_zone,
            ))
            
            conn.commit()
            conn.close()
            if normalized_role == "admin":
                return True, "Administrateur cree avec succes"
            return True, "Autorité sanitaire créée avec succès"
        except Exception as e:
            return False, f"Erreur: {e}"

    def register_authority(self, username, password, nom, prenom, email, telephone, province, zone_sante):
        return self.register_user(username, password, nom, prenom, email, telephone, "autorite_sanitaire", province, zone_sante)
    
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
    
    def delete_notification(self, notif_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM notifications WHERE id = ?', (notif_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    def delete_all_notifications(self, user_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
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

    def reactivate_user(self, user_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_active = 1 WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True, "Utilisateur réactivé"
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
            cursor.execute("SELECT COUNT(*) FROM prediction_runs")
            total_prediction_runs = cursor.fetchone()[0]
            conn.close()
            return {
                'total_authorities': total_authorities,
                'total_alerts': total_alerts,
                'total_entries': total_entries,
                'total_prediction_runs': total_prediction_runs,
            }
        except:
            return {'total_authorities': 0, 'total_alerts': 0, 'total_entries': 0, 'total_prediction_runs': 0}

    def database_snapshot(self):
        snapshot = {
            'database_exists': Path(self.db_path).exists(),
            'database_size_kb': 0,
            'users_total': 0,
            'alerts_total': 0,
            'notifications_total': 0,
            'entries_total': 0,
            'prediction_runs_total': 0,
        }
        if not snapshot['database_exists']:
            return snapshot

        try:
            snapshot['database_size_kb'] = round(Path(self.db_path).stat().st_size / 1024, 1)
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            snapshot['users_total'] = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM alerts")
            snapshot['alerts_total'] = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM notifications")
            snapshot['notifications_total'] = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM epidemiological_data")
            snapshot['entries_total'] = int(cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM prediction_runs")
            snapshot['prediction_runs_total'] = int(cursor.fetchone()[0])
            conn.close()
        except Exception:
            return snapshot
        return snapshot

    def save_epidemiological_entry(
        self,
        disease,
        province,
        zone_sante,
        observed_date,
        total_cases,
        total_deaths,
        entered_by,
        validated=0,
    ):
        try:
            normalized_cases = None if total_cases is None else int(total_cases)
            normalized_deaths = None if total_deaths is None else int(total_deaths)
            clean_disease = self._clean_text(disease)
            clean_province = self._clean_text(province)
            clean_zone = self._clean_text(zone_sante)
            iso_year, week_num, _ = observed_date.isocalendar()

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT id
                FROM epidemiological_data
                WHERE lower(trim(disease)) = ?
                  AND week = ?
                  AND year = ?
                  AND lower(trim(province)) = ?
                  AND lower(trim(zone_sante)) = ?
                LIMIT 1
                ''',
                (
                    clean_disease.casefold(),
                    int(week_num),
                    int(iso_year),
                    clean_province.casefold(),
                    clean_zone.casefold(),
                ),
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    '''
                    UPDATE epidemiological_data
                    SET total_cases = ?,
                        total_deaths = ?,
                        entered_by = ?,
                        validated = ?,
                        entry_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                    ''',
                    (normalized_cases, normalized_deaths, int(entered_by), int(validated), int(existing[0])),
                )
                action = "mise a jour"
            else:
                cursor.execute(
                    '''
                    INSERT INTO epidemiological_data (
                        disease, week, year, province, zone_sante,
                        total_cases, total_deaths, entered_by, validated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        clean_disease,
                        int(week_num),
                        int(iso_year),
                        clean_province,
                        clean_zone,
                        normalized_cases,
                        normalized_deaths,
                        int(entered_by),
                        int(validated),
                    ),
                )
                action = "creation"

            conn.commit()
            conn.close()
            return True, {
                'action': action,
                'week': int(week_num),
                'year': int(iso_year),
                'disease': clean_disease,
                'province': clean_province,
                'zone_sante': clean_zone,
            }
        except Exception as exc:
            return False, str(exc)

    def record_prediction_run(
        self,
        disease,
        province,
        zone_sante,
        target_date,
        week,
        year,
        previous_cases,
        predicted_cases,
        model_r2,
        delivery_mode,
        delivery_target,
        emitted_by,
        alert_id,
    ):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO prediction_runs (
                    disease, province, zone_sante, target_date, week, year,
                    previous_cases, predicted_cases, model_r2, delivery_mode,
                    delivery_target, emitted_by, alert_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    disease,
                    province,
                    zone_sante,
                    str(target_date),
                    int(week),
                    int(year),
                    int(previous_cases),
                    int(predicted_cases),
                    float(model_r2),
                    delivery_mode,
                    delivery_target,
                    int(emitted_by),
                    int(alert_id),
                ),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_prediction_runs(self, limit=100):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT disease, province, zone_sante, target_date, week, year,
                       previous_cases, predicted_cases, model_r2, delivery_mode,
                       delivery_target, created_at
                FROM prediction_runs
                ORDER BY created_at DESC
                LIMIT ?
                ''',
                (int(limit),),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    'disease': row[0],
                    'province': row[1],
                    'zone_sante': row[2],
                    'target_date': row[3],
                    'week': row[4],
                    'year': row[5],
                    'previous_cases': row[6],
                    'predicted_cases': row[7],
                    'model_r2': row[8],
                    'delivery_mode': row[9],
                    'delivery_target': row[10],
                    'created_at': row[11],
                }
                for row in rows
            ]
        except Exception:
            return []


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
        st.metric("Alertes diffusees", stats['total_alerts'])
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