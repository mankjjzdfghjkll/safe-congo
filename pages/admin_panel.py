import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.admin_ui import (
    alerts_frame,
    apply_admin_theme,
    make_plotly_layout,
    panel_title,
    recent_entries_frame,
    render_admin_hero,
    render_admin_sidebar,
    render_kpi_cards,
    section_label,
    users_frame,
)
from utils.auth import AuthSystem, require_auth
from utils.navigation import switch_to_home_page


def _health_chart(entries_df: pd.DataFrame, alerts_df: pd.DataFrame, users_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(x=["Saisies", "Alertes", "Utilisateurs"], y=[len(entries_df), len(alerts_df), len(users_df)], marker_color=["#0a5fab", "#f59e0b", "#34d399"]))
    return make_plotly_layout(fig, "Pulse systeme")


def _latest_logins(users_df: pd.DataFrame) -> pd.DataFrame:
    if users_df.empty:
        return pd.DataFrame()
    df = users_df.copy()
    df["Nom complet"] = df["nom"].fillna("") + " " + df["prenom"].fillna("")
    return df[["Nom complet", "username", "role", "last_login", "province"]].rename(columns={"username": "Identifiant", "role": "Role", "last_login": "Derniere connexion", "province": "Province"})


def main() -> None:
    st.set_page_config(page_title="Admin Control Center - SAFE CONGO", page_icon=None, layout="wide")
    apply_admin_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        return

    render_admin_sidebar(user, active_item=4)
    render_admin_hero(
        "Centre de pilotage systeme",
        "Une salle de controle admin pour surveiller la sante de la plateforme, le poids des donnees, les connexions recentes et les points d'attention operationnels.",
        ["Controle central", "Etat du socle", "Actions rapides"],
        eyebrow="Pilotage systeme",
    )

    entries_df = recent_entries_frame(auth.db_path)
    alerts_df = alerts_frame(auth.db_path)
    users_df = users_frame(auth)
    db_size = Path(auth.db_path).stat().st_size / 1024 if Path(auth.db_path).exists() else 0

    render_kpi_cards(
        [
            {"label": "Poids base", "value": f"{db_size:,.0f} Ko", "delta": "Empreinte locale", "copy": "Le volume SQLite donne une lecture rapide de la croissance des donnees et de la charge de stockage courante.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.1)"},
            {"label": "Saisies recentes", "value": str(len(entries_df)), "delta": "Fenetre 200 lignes", "copy": "Le centre de pilotage suit la densite de production admin sans ouvrir le detail de chaque formulaire.", "accent": "#059669", "accent_soft": "#34d399", "pill": "rgba(5,150,105,.12)"},
            {"label": "Alertes recentes", "value": str(len(alerts_df)), "delta": "Signal conserve", "copy": "Les alertes restent visibles ici pour mesurer la pression systemique globale et non page par page.", "accent": "#d97706", "accent_soft": "#f9c74f", "pill": "rgba(217,119,6,.12)"},
            {"label": "Comptes connus", "value": str(len(users_df)), "delta": "Population plateforme", "copy": "Le nombre de comptes aide a arbitrer les besoins de gouvernance et de support institutionnel.", "accent": "#7c3aed", "accent_soft": "#a78bfa", "pill": "rgba(124,58,237,.12)"},
        ]
    )

    left_col, right_col = st.columns([1.05, 0.95], gap="large")
    with left_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Pulse systeme")
        st.plotly_chart(_health_chart(entries_df, alerts_df, users_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Connexions recentes")
        logins_df = _latest_logins(users_df)
        if logins_df.empty:
            st.info("Aucune connexion recente disponible.")
        else:
            st.dataframe(logins_df.head(15), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(
            """
<div class="admin-panel">
  <div class="admin-panel-title">Actions rapides</div>
  <div class="admin-grid-3">
    <div class="admin-mini-card"><h4>Vers le dashboard</h4><p>Relire la situation generale, les courbes et les derniers signaux critiques.</p></div>
    <div class="admin-mini-card"><h4>Vers la saisie</h4><p>Produire une nouvelle observation terrain et declencher l'intelligence d'alerte.</p></div>
    <div class="admin-mini-card"><h4>Vers les utilisateurs</h4><p>Ouvrir, encadrer ou desactiver un acces territorial selon les besoins de gouvernance.</p></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Dashboard executif", use_container_width=True):
                st.switch_page("pages/admin_dashboard.py")
        with c2:
            if st.button("Saisie admin", use_container_width=True):
                st.switch_page("pages/admin_data_entry.py")
        with c3:
            if st.button("Utilisateurs", use_container_width=True):
                st.switch_page("pages/admin_users.py")

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Qualite d'exploitation")
        st.markdown(
            """
<div class="admin-highlight"><strong>Socle simplifie et robuste</strong><span>Le centre de pilotage a ete recentre sur les operations reelles du projet: donnees, alertes, comptes et navigation admin.</span></div>
<div style="height:12px"></div>
<div class="admin-highlight"><strong>Moins de dette visuelle</strong><span>Les composants sont harmonises pour reduire la rupture entre pages et renforcer la lecture de commandement.</span></div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    section_label("Veille operationnelle")
    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    panel_title("Dernieres alertes pour arbitrage")
    if alerts_df.empty:
        st.info("Aucune alerte disponible dans la base.")
    else:
        view_df = alerts_df.rename(columns={"disease": "Maladie", "province": "Province", "zone_sante": "Zone", "alert_level": "Niveau", "growth_rate": "Croissance (%)", "current_cases": "Cas actuels", "predicted_cases": "Projection", "created_at": "Emission"})
        st.dataframe(view_df.head(20), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()