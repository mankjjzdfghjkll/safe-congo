# app.py - Version complète avec interface moderne et couleurs attrayantes

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
import sys
from pathlib import Path
import time
import sqlite3

warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="SAFE CONGO - Surveillance Épidémiologique",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ STYLES CSS AMÉLIORÉS ============
st.markdown("""
<style>
    /* Police et couleurs de base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Couleurs principales */
    :root {
        --primary: #0066CC;
        --primary-dark: #004D99;
        --secondary: #00A86B;
        --danger: #DC3545;
        --warning: #FFC107;
        --info: #17A2B8;
        --dark: #1a1a2e;
        --light: #f8f9fa;
    }
    
    /* Animation fadeIn */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0,102,204,0.4); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(0,102,204,0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0,102,204,0); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Background principal */
    .stApp {
        background: linear-gradient(135deg, #f0f2f5 0%, #e8ecf1 100%);
    }
    
    /* Cartes modernes */
    .modern-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
        animation: fadeIn 0.6s ease-out;
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* En-tête animé */
    .animated-header {
        text-align: center;
        padding: 40px 30px;
        background: linear-gradient(135deg, #0066CC 0%, #004D99 100%);
        border-radius: 24px;
        margin-bottom: 30px;
        animation: fadeIn 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .animated-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    .animated-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2em;
    }
    
    .animated-header p {
        color: rgba(255,255,255,0.9);
        margin-top: 10px;
    }
    
    /* Métriques animées */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    .metric-icon {
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    /* Boutons stylisés */
    .stButton > button {
        background: linear-gradient(135deg, #0066CC 0%, #004D99 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,102,204,0.3);
    }
    
    /* Sidebar stylisée */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    /* Alertes stylisées */
    .alert-critical {
        background: linear-gradient(135deg, #DC3545 0%, #c82333 100%);
        color: white;
        padding: 20px;
        border-radius: 16px;
        margin: 15px 0;
        animation: pulse 2s infinite;
    }
    
    .alert-high {
        background: linear-gradient(135deg, #FD7E14 0%, #E8590C 100%);
        color: white;
        padding: 20px;
        border-radius: 16px;
        margin: 15px 0;
    }
    
    .alert-medium {
        background: linear-gradient(135deg, #FFC107 0%, #E0A800 100%);
        color: #333;
        padding: 20px;
        border-radius: 16px;
        margin: 15px 0;
    }
    
    /* Badge de notification */
    .notification-badge {
        display: inline-block;
        background: #DC3545;
        color: white;
        border-radius: 50%;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
        animation: pulse 1s infinite;
    }
    
    /* Progress bar animée */
    .custom-progress {
        height: 4px;
        background: linear-gradient(90deg, #0066CC, #00A86B);
        border-radius: 2px;
        animation: shimmer 2s infinite;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 0.8em;
        border-top: 1px solid rgba(0,0,0,0.1);
        margin-top: 30px;
    }
    
    /* Tabs stylisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066CC 0%, #004D99 100%);
        color: white;
    }
    
    /* Inputs stylisés */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        padding: 12px 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0066CC;
        box-shadow: 0 0 0 2px rgba(0,102,204,0.1);
    }
    
    /* Selectbox stylisé */
    .stSelectbox > div > div {
        border-radius: 12px;
    }
    
    /* Dataframe stylisé */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ============ IMPORTS ============
from src.config import UI_CONFIG, ALERT_THRESHOLDS
from src.data_cleaner import DataCleaner
from src.train_models import DiseasePredictor
from src.alert_system import AlertSystem

# Import conditionnel de pdf_generator
try:
    from src.pdf_generator import BarrierMeasuresPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    BarrierMeasuresPDF = None

# Import du système d'authentification
from utils.auth import AuthSystem, require_auth, logout, show_user_profile, get_current_user, show_admin_panel

# ============ INITIALISATION ============
@st.cache_resource
def init_components():
    auth = AuthSystem()
    data_path = Path(__file__).parent / "data" / "drc-2023_sem08.xlsx"
    
    if not data_path.exists():
        st.error(f"❌ Fichier de données non trouvé: {data_path}")
        st.info("Veuillez placer le fichier 'drc-2023_sem08.xlsx' dans le dossier 'data/'")
        return auth, None, None, None, None
    
    cleaner = DataCleaner(str(data_path))
    predictor = DiseasePredictor()
    alert_system = AlertSystem()
    
    pdf_gen = BarrierMeasuresPDF() if PDF_AVAILABLE and BarrierMeasuresPDF else None
    
    return auth, cleaner, predictor, alert_system, pdf_gen

@st.cache_data
def load_data(_cleaner):
    """Charge et nettoie les données"""
    if _cleaner is None:
        return None, None, None
    
    try:
        _cleaner.load_data()
        cleaned = _cleaner.clean_data()
        agg = _cleaner.aggregate_by_week_disease()
        features = _cleaner.create_features_for_ml(agg)
        return cleaned, agg, features
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None, None, None

def show_metric_card(label, value, icon, color):
    """Affiche une carte métrique stylisée"""
    return f"""
    <div class="metric-card" style="border-left-color: {color};">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def show_authority_dashboard(user, agg, predictor, alert_system, auth):
    """Dashboard pour les autorités sanitaires"""
    
    st.markdown(f"""
    <div class="animated-header">
        <h1>🏥 Tableau de bord - Autorité Sanitaire</h1>
        <p>Bienvenue <strong>{user['full_name']}</strong> | {user.get('province', 'N/A')} - {user.get('zone_sante', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cases = agg['TOTALCAS'].sum() if agg is not None else 0
        st.markdown(show_metric_card("Total Cas", total_cases, "📈", "#0066CC"), unsafe_allow_html=True)
    
    with col2:
        total_deaths = agg['TOTALDECES'].sum() if agg is not None else 0
        st.markdown(show_metric_card("Total Décès", total_deaths, "⚰️", "#DC3545"), unsafe_allow_html=True)
    
    with col3:
        diseases = agg['MALADIE'].nunique() if agg is not None else 0
        st.markdown(show_metric_card("Maladies", diseases, "🦠", "#00A86B"), unsafe_allow_html=True)
    
    with col4:
        unread = auth.get_unread_count(user['id']) if auth else 0
        st.markdown(show_metric_card("Nouvelles alertes", unread, "🔔", "#FFC107"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Notifications
    st.subheader("🔔 Dernières notifications")
    notifications = auth.get_notifications(user['id'], unread_only=True) if auth else []
    
    if notifications:
        for notif in notifications:
            color = "#DC3545" if "ALERTE" in notif['title'] else "#0066CC"
            st.markdown(f"""
            <div style="background: {color}10; border-left: 4px solid {color}; 
                        padding: 15px; border-radius: 12px; margin: 10px 0;">
                <strong>{notif['title']}</strong>
                <p style="margin: 5px 0; color: #555;">{notif['message'][:200]}</p>
                <span style="color: #999; font-size: 0.8em;">{notif['created_at']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ Marquer comme lue", key=f"read_{notif['id']}"):
                auth.mark_notification_read(notif['id'])
                st.rerun()
    else:
        st.info("📭 Aucune nouvelle notification")
    
    st.markdown("---")
    
    # Graphique d'évolution
    st.subheader("📈 Évolution des épidémies")
    
    if agg is not None:
        top5 = agg.groupby('MALADIE')['TOTALCAS'].sum().nlargest(5).index
        
        fig = go.Figure()
        colors = ['#0066CC', '#00A86B', '#FFC107', '#DC3545', '#17A2B8']
        
        for idx, disease in enumerate(top5):
            data = agg[agg['MALADIE'] == disease].sort_values('DEBUTSEM')
            fig.add_trace(go.Scatter(
                x=data['DEBUTSEM'], 
                y=data['TOTALCAS'], 
                name=disease, 
                mode='lines+markers',
                line=dict(color=colors[idx % len(colors)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            height=400,
            title="Évolution des 5 principales maladies",
            xaxis_title="Semaine",
            yaxis_title="Nombre de cas",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    # Animation de chargement
    with st.spinner("🛡️ Initialisation de SAFE CONGO..."):
        time.sleep(0.5)
    
    auth, cleaner, predictor, alert_system, pdf_gen = init_components()
    
    if cleaner is None:
        st.stop()
    
    user = require_auth(auth)
    if not user:
        return
    
    # Chargement des données
    with st.spinner("📊 Chargement des données épidémiologiques..."):
        try:
            cleaned, agg, features = load_data(cleaner)
            if predictor:
                predictor.load_models()
            if agg is None:
                st.error("❌ Impossible de charger les données")
                return
        except Exception as e:
            st.error(f"❌ Erreur de chargement: {e}")
            return
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 3em;">🛡️</div>
            <h2 style="color: white; margin: 10px 0;">SAFE CONGO</h2>
            <p style="color: rgba(255,255,255,0.8); font-size: 0.9em;">Surveillance Épidémiologique</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        show_user_profile()
        
        st.markdown("---")
        
        # Menu
        if user.get('role') == 'admin':
            menu_options = ["📊 Dashboard", "🔬 Analyse", "⚠️ Alertes", "📈 Prédictions", "👑 Administration"]
        else:
            menu_options = ["📊 Dashboard", "🔬 Analyse", "⚠️ Alertes", "📈 Prédictions", "🏥 Mon tableau de bord"]
        
        menu = st.radio("Navigation", menu_options)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; font-size: 0.75em; color: rgba(255,255,255,0.6);">
            <p>© 2024 SAFE CONGO</p>
            <p>Version 3.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pages
    if menu == "📊 Dashboard":
        st.markdown("""
        <div class="animated-header">
            <h1>📊 Tableau de Bord Épidémiologique</h1>
            <p>Surveillance en temps réel des épidémies en République Démocratique du Congo</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_cases = agg['TOTALCAS'].sum()
            st.markdown(show_metric_card("Total Cas", total_cases, "📈", "#0066CC"), unsafe_allow_html=True)
        
        with col2:
            total_deaths = agg['TOTALDECES'].sum()
            st.markdown(show_metric_card("Total Décès", total_deaths, "⚰️", "#DC3545"), unsafe_allow_html=True)
        
        with col3:
            diseases_count = agg['MALADIE'].nunique()
            st.markdown(show_metric_card("Maladies", diseases_count, "🦠", "#00A86B"), unsafe_allow_html=True)
        
        with col4:
            alert_count = len(alert_system.get_active_alerts()) if alert_system else 0
            st.markdown(show_metric_card("Alertes Actives", alert_count, "⚠️", "#FFC107"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Graphique principal
        st.subheader("📈 Évolution des principales maladies")
        top5 = agg.groupby('MALADIE')['TOTALCAS'].sum().nlargest(5).index
        
        fig = go.Figure()
        colors = ['#0066CC', '#00A86B', '#FFC107', '#DC3545', '#17A2B8']
        
        for idx, disease in enumerate(top5):
            data = agg[agg['MALADIE'] == disease].sort_values('DEBUTSEM')
            fig.add_trace(go.Scatter(
                x=data['DEBUTSEM'], 
                y=data['TOTALCAS'], 
                name=disease, 
                mode='lines+markers',
                line=dict(color=colors[idx % len(colors)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            height=500,
            xaxis_title="Semaine",
            yaxis_title="Nombre de cas",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Répartition
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🥧 Répartition par maladie")
            disease_sum = agg.groupby('MALADIE')['TOTALCAS'].sum().sort_values(ascending=False).head(8)
            fig_pie = px.pie(
                values=disease_sum.values, 
                names=disease_sum.index,
                title="Top 8 maladies",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📊 Statistiques clés")
            stats_data = {
                "Indicateur": ["Moyenne cas/semaine", "Médiane cas/semaine", "Max cas/semaine", "Taux létalité"],
                "Valeur": [
                    f"{agg['TOTALCAS'].mean():.0f}",
                    f"{agg['TOTALCAS'].median():.0f}",
                    f"{agg['TOTALCAS'].max():,}",
                    f"{(agg['TOTALDECES'].sum() / agg['TOTALCAS'].sum() * 100):.2f}%"
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)
    
    elif menu == "🔬 Analyse":
        st.markdown("""
        <div class="animated-header">
            <h1>🔬 Analyse Détaillée par Maladie</h1>
            <p>Analyse approfondie des tendances épidémiologiques</p>
        </div>
        """, unsafe_allow_html=True)
        
        diseases = sorted(agg['MALADIE'].unique())
        disease = st.selectbox("📌 Sélectionner une maladie", diseases)
        
        data = agg[agg['MALADIE'] == disease].sort_values('DEBUTSEM')
        
        if len(data) > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📈 Total Cas", f"{data['TOTALCAS'].sum():,}")
            with col2:
                st.metric("⚰️ Total Décès", f"{data['TOTALDECES'].sum():,}")
            with col3:
                st.metric("📊 Moyenne/semaine", f"{data['TOTALCAS'].mean():.1f}")
            with col4:
                mortality = (data['TOTALDECES'].sum() / data['TOTALCAS'].sum() * 100) if data['TOTALCAS'].sum() > 0 else 0
                st.metric("💀 Taux Létalité", f"{mortality:.2f}%")
            
            st.markdown("---")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=data['DEBUTSEM'], 
                y=data['TOTALCAS'], 
                name="Cas",
                marker_color='#0066CC',
                opacity=0.7
            ))
            fig.add_trace(go.Scatter(
                x=data['DEBUTSEM'], 
                y=data['TOTALDECES'], 
                name="Décès",
                line=dict(color='#DC3545', width=3),
                marker=dict(color='#DC3545', size=10)
            ))
            
            fig.update_layout(
                height=450,
                title=f"{disease} - Évolution hebdomadaire",
                xaxis_title="Semaine",
                yaxis_title="Nombre de cas/décès",
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if predictor and disease in predictor.best_models:
                st.subheader("🤖 Performance du modèle IA")
                info = predictor.best_models[disease]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🎯 R² Score", f"{info['test_r2']:.3f}")
                with col2:
                    st.metric("📊 MAE", f"{info['test_mae']:.2f}")
                with col3:
                    st.metric("📈 MAPE", f"{info['test_mape']:.1f}%")
                st.info(f"✨ **Meilleur modèle:** {info['best_model_name']}")
    
    elif menu == "⚠️ Alertes":
        st.markdown("""
        <div class="animated-header">
            <h1>⚠️ Centre d'Alertes Épidémiologiques</h1>
            <p>Surveillance et gestion des alertes sanitaires</p>
        </div>
        """, unsafe_allow_html=True)
        
        if alert_system:
            active_alerts = alert_system.get_active_alerts()
            critical = [a for a in active_alerts if a.get('niveau') == 'CRITICAL']
            high = [a for a in active_alerts if a.get('niveau') == 'HIGH']
            medium = [a for a in active_alerts if a.get('niveau') == 'MEDIUM']
            
            if critical:
                st.subheader("🔴 Alertes Critiques")
                for alert in critical:
                    st.error(f"""
                    **{alert.get('maladie', 'N/A')}** - {alert.get('raison', 'Alerte')}
                    - Cas actuels: {alert.get('cas_actuels', 0):,}
                    - Croissance: {alert.get('croissance', 0):.1f}%
                    """)
            
            if high:
                st.subheader("🟠 Alertes Hautes")
                for alert in high:
                    st.warning(f"**{alert.get('maladie', 'N/A')}** - Croissance: {alert.get('croissance', 0):.1f}%")
            
            if medium:
                st.subheader("🟡 Alertes Modérées")
                for alert in medium:
                    st.info(f"**{alert.get('maladie', 'N/A')}** - {alert.get('raison', 'Surveillance recommandée')}")
            
            if not any([critical, high, medium]):
                st.success("✅ Aucune alerte active - Situation stable")
    
    elif menu == "📈 Prédictions":
        st.markdown("""
        <div class="animated-header">
            <h1>📈 Prédictions et Modèles IA</h1>
            <p>Anticipation de l'évolution des épidémies</p>
        </div>
        """, unsafe_allow_html=True)
        
        if predictor and predictor.best_models:
            st.success(f"✅ {len(predictor.best_models)} modèles entraînés")
            
            pred_data = []
            for disease, info in predictor.best_models.items():
                data = agg[agg['MALADIE'] == disease].sort_values('DEBUTSEM')
                if len(data) > 0:
                    pred_data.append({
                        'Maladie': disease,
                        'Cas actuels': int(data['TOTALCAS'].iloc[-1]),
                        'R²': round(info['test_r2'], 3),
                        'MAE': round(info['test_mae'], 2),
                        'Modèle': info['best_model_name']
                    })
            
            df = pd.DataFrame(pred_data).sort_values('Cas actuels', ascending=False)
            st.dataframe(df, use_container_width=True)
            
            fig = px.bar(df.head(10), x='Maladie', y='Cas actuels', color='R²',
                        color_continuous_scale='Viridis', title="Top 10 maladies")
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
    
    elif menu == "👑 Administration" and user.get('role') == 'admin':
        show_admin_panel()
    
    elif menu == "🏥 Mon tableau de bord":
        show_authority_dashboard(user, agg, predictor, alert_system, auth)

if __name__ == "__main__":
    main()