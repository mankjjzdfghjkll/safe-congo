# pages/admin_panel.py
import streamlit as st
from utils.auth import require_auth, check_role, AuthSystem

st.set_page_config(page_title="Admin - SAFE CONGO", layout="wide")

auth = AuthSystem()
user = require_auth(auth)

if not user or user['role'] != 'admin':
    st.error(" Accès non autorisé")
    st.stop()

st.title(" Panneau d'Administration")

# Gestion des utilisateurs
st.subheader(" Gestion des utilisateurs")

users = auth.get_all_users()
if users:
    import pandas as pd
    df = pd.DataFrame(users)
    st.dataframe(df[['username', 'role', 'full_name', 'email', 'created_at', 'last_login']], use_container_width=True)
    
    # Modifier le rôle
    st.subheader("Modifier un rôle")
    col1, col2 = st.columns(2)
    with col1:
        user_to_modify = st.selectbox("Sélectionner un utilisateur", [u['username'] for u in users if u['username'] != 'admin'])
    with col2:
        new_role = st.selectbox("Nouveau rôle", ['admin', 'medecin', 'analyste', 'responsable', 'chercheur'])
    
    if st.button("Mettre à jour"):
        user_id = next((u['id'] for u in users if u['username'] == user_to_modify), None)
        if user_id:
            success, msg = auth.update_user_role(user_id, new_role)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# Logs système
st.subheader(" Logs système")
logs = auth.get_user_logs(limit=100)
if logs:
    logs_df = pd.DataFrame(logs)
    st.dataframe(logs_df, use_container_width=True)