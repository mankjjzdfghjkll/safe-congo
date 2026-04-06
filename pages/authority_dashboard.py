# pages/authority_dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.auth import require_auth, AuthSystem
from src.pdf_generator import BarrierMeasuresPDF

st.set_page_config(page_title="Tableau de bord - Autorité Sanitaire", layout="wide")

auth = AuthSystem()
user = require_auth(auth)

if not user or user['role'] != 'autorite_sanitaire':
    st.error("⛔ Accès réservé aux autorités sanitaires")
    st.stop()

st.title(f"🏥 Tableau de bord - {user['full_name']}")
st.markdown(f"**Province:** {user['province']} | **Zone de santé:** {user['zone_sante']}")

# Récupérer les alertes et notifications
conn = sqlite3.connect(auth.db_path)

# Alertes non lues
alerts_df = pd.read_sql_query('''
    SELECT a.*, n.is_read, n.id as notif_id
    FROM alerts a
    JOIN notifications n ON a.id = n.alert_id
    WHERE n.user_id = ? AND n.is_read = 0
    ORDER BY a.created_at DESC
''', conn, params=(user['id'],))

# Afficher les alertes
if not alerts_df.empty:
    st.subheader("🚨 Nouvelles alertes")
    for _, alert in alerts_df.iterrows():
        color = "#dc3545" if alert['alert_level'] == 'CRITIQUE' else "#fd7e14" if alert['alert_level'] == 'ÉLEVÉ' else "#ffc107"
        st.markdown(f"""
        <div style="background: {color}; padding: 20px; border-radius: 15px; color: white; margin: 15px 0;">
            <h3>⚠️ ALERTE {alert['alert_level']}</h3>
            <p><strong>Maladie:</strong> {alert['disease']}</p>
            <p><strong>Province:</strong> {alert['province']}</p>
            <p><strong>Zone de santé:</strong> {alert['zone_sante']}</p>
            <p><strong>Semaine:</strong> {alert['week']}/{alert['year']}</p>
            <p><strong>Cas actuels:</strong> {alert['current_cases']:,}</p>
            <p><strong>Prédiction:</strong> {int(alert['predicted_cases']):,} cas</p>
            <p><strong>Croissance:</strong> {alert['growth_rate']:.1f}%</p>
            <p>{alert['message']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ Marquer comme lue", key=f"read_{alert['notif_id']}"):
                auth.mark_notification_read(alert['notif_id'])
                st.rerun()
        with col2:
            # Générer PDF des mesures barrières
            pdf_gen = BarrierMeasuresPDF()
            pdf_data = pdf_gen.generate_alert_pdf(
                disease=alert['disease'],
                province=alert['province'],
                zone_sante=alert['zone_sante'],
                current_cases=alert['current_cases'],
                predicted_cases=int(alert['predicted_cases']),
                growth_rate=alert['growth_rate'],
                alert_level=alert['alert_level'],
                r2_score=0.85
            )
            st.download_button(
                label="📄 Mesures barrières (PDF)",
                data=pdf_data,
                file_name=f"mesures_barrieres_{alert['disease']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key=f"pdf_{alert['notif_id']}"
            )

# Historique des alertes
st.subheader("📋 Historique des alertes")
history_df = pd.read_sql_query('''
    SELECT a.disease, a.province, a.zone_sante, a.week, a.year, a.current_cases, a.predicted_cases, a.growth_rate, a.alert_level, a.created_at
    FROM alerts a
    JOIN notifications n ON a.id = n.alert_id
    WHERE n.user_id = ?
    ORDER BY a.created_at DESC LIMIT 20
''', conn, params=(user['id'],))

if not history_df.empty:
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("Aucune alerte reçue pour le moment")

conn.close()

# Statistiques personnalisées
st.subheader("📊 Statistiques de votre zone")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Alertes reçues", len(history_df))
with col2:
    alertes_critiques = len(history_df[history_df['alert_level'] == 'CRITIQUE']) if not history_df.empty else 0
    st.metric("Alertes critiques", alertes_critiques)
with col3:
    st.metric("Dernière alerte", history_df.iloc[0]['created_at'][:10] if not history_df.empty else "Aucune")