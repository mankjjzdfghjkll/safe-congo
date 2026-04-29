import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.admin_ui import (
    aggregated_csv_frame,
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


def _build_weekly_trend(entries_df: pd.DataFrame) -> go.Figure:
    trend_df = entries_df.copy()
    if trend_df.empty:
        trend_df = pd.DataFrame({"period": ["Aucune donnee"], "cases": [0], "deaths": [0]})
    else:
        trend_df["period"] = trend_df["year"].astype(str) + "-S" + trend_df["week"].astype(int).astype(str).str.zfill(2)
        trend_df = (
            trend_df.groupby("period", as_index=False)[["total_cases", "total_deaths"]]
            .sum()
            .tail(10)
            .rename(columns={"total_cases": "cases", "total_deaths": "deaths"})
        )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_df["period"],
            y=trend_df["cases"],
            mode="lines+markers",
            name="Cas",
            line=dict(color="#0a5fab", width=3),
            marker=dict(size=8, color="#0a5fab"),
            fill="tozeroy",
            fillcolor="rgba(10,95,171,.12)",
        )
    )
    fig.add_trace(
        go.Bar(
            x=trend_df["period"],
            y=trend_df["deaths"],
            name="Deces",
            marker_color="rgba(217,119,6,.78)",
        )
    )
    return make_plotly_layout(fig, "Trajectoire hebdomadaire")


def _build_top_provinces(entries_df: pd.DataFrame) -> go.Figure:
    province_df = entries_df.copy()
    if province_df.empty:
        province_df = pd.DataFrame({"province": ["Aucune donnee"], "total_cases": [0]})
    else:
        province_df = province_df.groupby("province", as_index=False)["total_cases"].sum().sort_values("total_cases", ascending=True).tail(8)
    fig = go.Figure(
        go.Bar(
            x=province_df["total_cases"],
            y=province_df["province"],
            orientation="h",
            marker=dict(color="#1aa2e2"),
        )
    )
    return make_plotly_layout(fig, "Provinces sous observation")


def _build_disease_mix(entries_df: pd.DataFrame) -> go.Figure:
    disease_df = entries_df.copy()
    if disease_df.empty:
        disease_df = pd.DataFrame({"disease": ["Aucune donnee"], "total_cases": [1]})
    else:
        disease_df = disease_df.groupby("disease", as_index=False)["total_cases"].sum().sort_values("total_cases", ascending=False).head(6)
    fig = go.Figure(
        go.Pie(
            labels=disease_df["disease"],
            values=disease_df["total_cases"],
            hole=0.56,
            marker=dict(colors=["#0a5fab", "#1aa2e2", "#49acef", "#8ed0ff", "#f9c74f", "#f9844a"]),
        )
    )
    return make_plotly_layout(fig, "Mix epidemiologique")


def _build_alert_levels(alerts_df: pd.DataFrame) -> go.Figure:
    level_df = alerts_df.copy()
    if level_df.empty:
        level_df = pd.DataFrame({"alert_level": ["Aucune"], "count": [0]})
    else:
        level_df = alerts_df.groupby("alert_level", as_index=False).size().rename(columns={"size": "count"})
    fig = go.Figure(
        go.Bar(
            x=level_df["alert_level"],
            y=level_df["count"],
            marker_color=["#ef4444", "#f59e0b", "#38bdf8", "#94a3b8"][: len(level_df)],
        )
    )
    return make_plotly_layout(fig, "Intensite des alertes")


def main() -> None:
    st.set_page_config(page_title="Admin Dashboard - SAFE CONGO", page_icon=None, layout="wide")
    apply_admin_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        return

    render_admin_sidebar(user, active_item=1)
    render_admin_hero(
        "Tableau de bord executif SAFE CONGO",
        "Une vue d'orchestration qui combine activite terrain, signal epidemiologique et capacite institutionnelle dans une seule lecture de pilotage.",
        ["Pilotage national", "Vue unifiee", "Decision acceleree"],
    )

    stats = auth.get_stats()
    entries_df = recent_entries_frame(auth.db_path)
    alerts_df = alerts_frame(auth.db_path)
    users_df = users_frame(auth)
    aggregate_df = aggregated_csv_frame()

    total_cases = int(entries_df["total_cases"].sum()) if not entries_df.empty else int(aggregate_df["TOTALCAS"].sum()) if "TOTALCAS" in aggregate_df.columns else 0
    total_deaths = int(entries_df["total_deaths"].sum()) if not entries_df.empty else int(aggregate_df["TOTALDECES"].sum()) if "TOTALDECES" in aggregate_df.columns else 0
    active_authorities = int((users_df["role"].eq("autorite_sanitaire") & users_df["is_active"].eq(1)).sum()) if not users_df.empty else 0
    disease_count = int(entries_df["disease"].nunique()) if not entries_df.empty else int(aggregate_df["MALADIE"].nunique()) if "MALADIE" in aggregate_df.columns else 0

    render_kpi_cards(
        [
            {"label": "Cas consolides", "value": f"{total_cases:,}", "delta": "Vision terrain + historiques", "copy": "Le volume agrege reste visible en permanence pour arbitrer la charge epidemiologique.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.1)"},
            {"label": "Deces suivis", "value": f"{total_deaths:,}", "delta": "Lecture de severite", "copy": "La mortalite remonte dans une lecture distincte pour soutenir la priorisation des actions.", "accent": "#d97706", "accent_soft": "#f9c74f", "pill": "rgba(217,119,6,.12)"},
            {"label": "Autorites actives", "value": str(active_authorities or stats.get("total_authorities", 0)), "delta": "Reseau institutionnel", "copy": "Le maillage des utilisateurs actifs mesure la profondeur d'execution dans les territoires.", "accent": "#059669", "accent_soft": "#34d399", "pill": "rgba(5,150,105,.12)"},
            {"label": "Maladies observees", "value": str(disease_count), "delta": f"{stats.get('total_alerts', 0)} alertes historiques", "copy": "Le spectre epidemiologique aide a distinguer surcharge ponctuelle et diversification du risque.", "accent": "#7c3aed", "accent_soft": "#a78bfa", "pill": "rgba(124,58,237,.12)"},
        ]
    )

    section_label("Lecture strategique")
    st.markdown(
        """
<div class="admin-panel">
    <div class="admin-support-copy">Les blocs ci-dessous clarifient la lecture du pilotage admin avant d'entrer dans les graphiques et les listes detaillees.</div>
<div class="admin-grid-3">
  <div class="admin-mini-card"><h4>Cap de commandement</h4><p>Les operations administratives, les alertes et les saisies restent alignees pour eviter les angles morts entre supervision et execution.</p></div>
  <div class="admin-mini-card"><h4>Cadence du signal</h4><p>La plateforme fait remonter les rythmes hebdomadaires, les niveaux d'alerte et les territoires les plus exposes en lecture immediate.</p></div>
  <div class="admin-mini-card"><h4>Qualite de couverture</h4><p>Le reseau d'autorites actives indique si l'appareil d'observation est suffisamment dense pour soutenir la vigilance nationale.</p></div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.2, 0.8], gap="large")
    with left_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Rythme des saisies et gravite")
        st.plotly_chart(_build_weekly_trend(entries_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Dernieres alertes critiques")
        latest_alerts = alerts_df.head(8).copy()
        if latest_alerts.empty:
            st.info("Aucune alerte enregistree pour le moment.")
        else:
            latest_alerts = latest_alerts.rename(
                columns={
                    "disease": "Maladie",
                    "province": "Province",
                    "zone_sante": "Zone",
                    "alert_level": "Niveau",
                    "growth_rate": "Croissance (%)",
                    "current_cases": "Cas actuels",
                    "predicted_cases": "Projection",
                    "created_at": "Emission",
                }
            )
            st.dataframe(latest_alerts, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Territoires prioritaires")
        st.plotly_chart(_build_top_provinces(entries_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Composition des maladies")
        st.plotly_chart(_build_disease_mix(entries_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Intensite des niveaux d'alerte")
        st.plotly_chart(_build_alert_levels(alerts_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    section_label("Gouvernance immediate")
    overview_col, roster_col = st.columns([0.9, 1.1], gap="large")
    with overview_col:
        st.markdown(
            f"""
<div class="admin-panel">
    <div class="admin-support-copy">Resume rapide des volumes admin pour eviter de devoir lire le tableau complet avant de comprendre l'etat du socle.</div>
    <div class="admin-grid-3" style="margin-bottom:18px">
        <div class="admin-mini-card"><h4>Autorites actives</h4><p><strong>{active_authorities}</strong> comptes terrain actuellement disponibles pour recevoir les alertes et agir localement.</p></div>
        <div class="admin-mini-card"><h4>Provinces couvertes</h4><p><strong>{int(users_df.loc[(users_df['role'] == 'autorite_sanitaire') & (users_df['is_active'] == 1), 'province'].nunique()) if not users_df.empty else 0}</strong> provinces disposent d'au moins une autorite active.</p></div>
        <div class="admin-mini-card"><h4>Derniere activite</h4><p><strong>{entries_df['entry_date'].iloc[0] if not entries_df.empty else 'Aucune saisie'}</strong> reste la derniere remontee admin enregistree.</p></div>
    </div>
  <div class="admin-highlight">
    <strong>{stats.get('total_entries', 0)} enregistrements admin consolides</strong>
    <span>Chaque saisie enrichit la lecture nationale et alimente les seuils d'alerte automatiquement.</span>
  </div>
  <div style="height:14px"></div>
  <div class="admin-highlight">
    <strong>{stats.get('total_alerts', 0)} alertes conservees</strong>
    <span>Le stock historique d'alertes permet une comparaison rapide entre tensions recentes et precedents connus.</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    with roster_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Autorites sanitaires actives")
        st.markdown("<div class=\"admin-support-copy\">Le registre est isole ici pour donner de l'air aux indicateurs et separer nettement la lecture des comptes du reste du dashboard.</div>", unsafe_allow_html=True)
        if users_df.empty:
            st.markdown('<div class="admin-empty-state">Aucun utilisateur disponible pour le moment.</div>', unsafe_allow_html=True)
        else:
            authorities_df = users_df.loc[users_df["role"] == "autorite_sanitaire", ["nom", "prenom", "province", "zone_sante", "last_login", "is_active"]].copy()
            authorities_df["Responsable"] = authorities_df["nom"].fillna("") + " " + authorities_df["prenom"].fillna("")
            authorities_df["Statut"] = authorities_df["is_active"].map({1: "Actif", 0: "Desactive"})
            display_df = authorities_df[["Responsable", "province", "zone_sante", "last_login", "Statut"]].rename(columns={"province": "Province", "zone_sante": "Zone", "last_login": "Derniere connexion"})
            if display_df.empty:
                st.markdown('<div class="admin-empty-state">Aucune autorite sanitaire active n\'est encore rattachee au systeme.</div>', unsafe_allow_html=True)
            else:
                st.dataframe(display_df.head(12), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
