import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import AuthSystem, require_auth
import utils.authority_ui as authority_ui
from utils.navigation import switch_to_home_page


def _historical_trend_chart(history_df: pd.DataFrame) -> go.Figure:
    if history_df.empty or "DEBUTSEM" not in history_df.columns or "TOTALCAS" not in history_df.columns:
        chart_df = pd.DataFrame({"DEBUTSEM": ["Aucune donnee"], "TOTALCAS": [0]})
    else:
        chart_df = history_df.groupby("DEBUTSEM", as_index=False)["TOTALCAS"].sum().tail(12)
    fig = go.Figure(go.Scatter(x=chart_df["DEBUTSEM"], y=chart_df["TOTALCAS"], mode="lines+markers", line=dict(color="#0e7490", width=3), marker=dict(color="#14b8a6", size=8), fill="tozeroy", fillcolor="rgba(20,184,166,.12)"))
    return authority_ui.make_plotly_layout(fig, "Evolution recente des cas")


def _top_diseases_chart(history_df: pd.DataFrame) -> go.Figure:
    if history_df.empty or "MALADIE" not in history_df.columns or "TOTALCAS" not in history_df.columns:
        chart_df = pd.DataFrame({"MALADIE": ["Aucune donnee"], "TOTALCAS": [0]})
    else:
        chart_df = history_df.groupby("MALADIE", as_index=False)["TOTALCAS"].sum().sort_values("TOTALCAS", ascending=True).tail(6)
    fig = go.Figure(go.Bar(x=chart_df["TOTALCAS"], y=chart_df["MALADIE"], orientation="h", marker_color="#0a5fab"))
    return authority_ui.make_plotly_layout(fig, "Principales maladies surveillees")


def _assigned_levels_chart(alerts_df: pd.DataFrame) -> go.Figure:
    if alerts_df.empty:
        chart_df = pd.DataFrame({"alert_level": ["Aucune"], "count": [0]})
    else:
        chart_df = alerts_df.groupby("alert_level", as_index=False).size().rename(columns={"size": "count"})
    fig = go.Figure(go.Bar(x=chart_df["alert_level"], y=chart_df["count"], marker_color=["#ef4444", "#f97316", "#eab308", "#0a5fab"][: len(chart_df)]))
    return authority_ui.make_plotly_layout(fig, "Alertes qui vous sont adressees")


def main() -> None:
    st.set_page_config(page_title="Tableau de bord autorite - SAFE CONGO", page_icon=None, layout="wide")
    authority_ui.apply_authority_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "autorite_sanitaire":
        switch_to_home_page()
        return

    authority_ui.render_authority_sidebar(user, auth, active_item=1)
    authority_ui.render_authority_hero("Tableau de bord territorial", "Une console plus nette pour lire vos alertes, votre contexte provincial et les signaux qui demandent une action rapide sur le terrain.", ["Veille locale", user.get("province", "—"), user.get("zone_sante", "—")])

    history_df = authority_ui.load_historical_province(user.get("province", ""))
    assigned_alerts_df = authority_ui.alerts_for_user(auth.db_path, user["id"])
    unread_count = auth.get_unread_count(user["id"])

    try:
        conn = sqlite3.connect(str(auth.db_path))
        prov_df = pd.read_sql_query("SELECT SUM(total_cases) AS total_cases, SUM(total_deaths) AS total_deaths, COUNT(*) AS entries FROM epidemiological_data WHERE province=?", conn, params=(user.get("province", ""),))
        conn.close()
        prov_cases = int(prov_df["total_cases"].iloc[0] or 0)
        prov_deaths = int(prov_df["total_deaths"].iloc[0] or 0)
        prov_entries = int(prov_df["entries"].iloc[0] or 0)
    except Exception:
        prov_cases = 0
        prov_deaths = 0
        prov_entries = 0

    authority_ui.render_authority_kpis([
        {"label": "Alertes recues", "value": str(len(assigned_alerts_df)), "delta": "Flux cible pour votre compte", "copy": "Le tableau ne montre plus une province brute mais les alertes qui vous ont ete reellement adressees.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.1)"},
        {"label": "Notifications non lues", "value": str(unread_count), "delta": "Priorites immediates", "copy": "Le nombre non lu sert de file d'attente claire pour organiser la reaction terrain sans perdre d'information.", "accent": "#059669", "accent_soft": "#34d399", "pill": "rgba(5,150,105,.12)"},
        {"label": "Cas consolides", "value": f"{prov_cases:,}", "delta": "Lecture provinciale", "copy": "Le cumul provincial garde la profondeur de contexte local meme si les alertes vous arrivent de facon ciblee.", "accent": "#d97706", "accent_soft": "#f9c74f", "pill": "rgba(217,119,6,.12)"},
        {"label": "Saisies suivies", "value": str(prov_entries), "delta": f"{prov_deaths:,} deces suivis", "copy": "Le stock d'entrees aide a situer la densite de surveillance dans votre zone de responsabilite.", "accent": "#7c3aed", "accent_soft": "#a78bfa", "pill": "rgba(124,58,237,.12)"},
    ])

    authority_ui.authority_section_label("Lecture immediate")
    st.markdown("""
<div class=\"authority-panel\">
  <div class=\"authority-support-copy\">Cette page distingue ce qui vous est directement notifie, ce qui releve de votre contexte territorial et ce qui doit etre traite en priorite.</div>
  <div class=\"authority-grid-3\">
    <div class=\"authority-mini-card\"><h4>Vue ciblee</h4><p>Les alertes visibles ici correspondent a votre compte et non plus uniquement a un filtrage provincial general.</p></div>
    <div class=\"authority-mini-card\"><h4>Contexte local</h4><p>Les courbes historiques gardent la memoire de votre province pour mettre les alertes recues dans une perspective utile.</p></div>
    <div class=\"authority-mini-card\"><h4>Cadence d'action</h4><p>Les notifications non lues et les derniers signaux critiques restent en premier plan pour accelerer l'arbitrage terrain.</p></div>
  </div>
</div>
""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.15, 0.85], gap="large")
    with left_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_ui.authority_panel_title("Trajectoire provinciale")
        st.plotly_chart(_historical_trend_chart(history_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_ui.authority_panel_title("Vos dernieres notifications")
        preview_notifications = auth.get_notifications(user["id"], unread_only=False)
        if not preview_notifications:
            st.markdown('<div class="authority-empty-state">Aucune notification disponible pour le moment.</div>', unsafe_allow_html=True)
        else:
            for notification in preview_notifications[:5]:
                st.markdown(f"<div class=\"authority-highlight\" style=\"margin-bottom:12px\"><strong>{notification['title']}</strong><span>{notification['message']}</span><span style=\"display:block;margin-top:8px;font-size:.74rem;color:#7b91a5\">{notification['created_at']}</span></div>", unsafe_allow_html=True)
            if unread_count > 0 and st.button("Tout marquer comme lu", use_container_width=True):
                auth.mark_all_notifications_read(user["id"])
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_ui.authority_panel_title("Maladies dominantes")
        st.plotly_chart(_top_diseases_chart(history_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_ui.authority_panel_title("Niveaux d'alerte assignes")
        st.plotly_chart(_assigned_levels_chart(assigned_alerts_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_ui.authority_panel_title("Capsule terrain")
        st.markdown(f"<div class=\"authority-highlight\"><strong>Province: {user.get('province', '—')}</strong><span>Zone de sante de reference: {user.get('zone_sante', '—')}.</span></div><div style=\"height:12px\"></div><div class=\"authority-highlight\"><strong>{len(assigned_alerts_df)} alertes a suivre</strong><span>Les alertes reelles recues par votre compte peuvent inclure des signaux cibles en dehors de votre province si l'administration vous les diffuse.</span></div>", unsafe_allow_html=True)
        if st.button("Ouvrir mes alertes detaillees", use_container_width=True):
            st.switch_page("pages/authority_alerts.py")
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
