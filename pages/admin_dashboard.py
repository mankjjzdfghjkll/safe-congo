import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.admin_ui import (
    admin_notifications_snapshot,
    alerts_frame,
    apply_admin_theme,
    make_plotly_layout,
    recent_entries_frame,
    render_admin_hero,
    render_admin_sidebar,
    render_kpi_cards,
    section_label,
    users_frame,
)
from utils.auth import AuthSystem, require_auth
from utils.chart_helpers import empty_state_figure
from utils.data_prep import prepare_periodic_alerts, prepare_periodic_entries
from utils.navigation import switch_to_home_page


def _build_weekly_trend(entries_df: pd.DataFrame) -> go.Figure:
    prepared = prepare_periodic_entries(entries_df, required_columns={"total_deaths", "province", "disease"})
    if prepared.empty:
        return empty_state_figure("Trajectoire epidemiologique nationale", "Aucune dynamique recente disponible.", make_plotly_layout)

    trend_df = (
        prepared.groupby(["year", "week", "period"], as_index=False)[["total_cases", "total_deaths"]]
        .sum()
        .sort_values(["year", "week"])
        .tail(16)
        .rename(columns={"total_cases": "cases", "total_deaths": "deaths"})
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_df["period"],
            y=trend_df["cases"],
            mode="lines+markers",
            name="Cas observes",
            line=dict(color="#0a5fab", width=4, shape="spline"),
            marker=dict(size=8, color="#ffffff", line=dict(color="#0a5fab", width=2)),
            fill="tozeroy",
            fillcolor="rgba(10, 95, 171, 0.10)",
            hovertemplate="<b>%{x}</b><br>Cas: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend_df["period"],
            y=trend_df["deaths"],
            mode="lines+markers",
            name="Deces",
            line=dict(color="#ce1126", width=2.5, dash="dot"),
            marker=dict(size=7, color="#ce1126"),
            hovertemplate="<b>%{x}</b><br>Deces: %{y}<extra></extra>",
        )
    )
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(title="Volume hebdomadaire")
    fig.update_layout(height=410)
    return make_plotly_layout(fig, "Trajectoire epidemiologique nationale")


def _build_prediction_gap(alerts_df: pd.DataFrame) -> go.Figure:
    prepared = prepare_periodic_alerts(alerts_df)
    if not prepared.empty and "prediction_available" in prepared.columns:
        prepared = prepared.loc[prepared["prediction_available"]]
    if prepared.empty:
        return empty_state_figure("Prediction IA vs terrain", "Aucune alerte recente exploitable.", make_plotly_layout)

    forecast_df = (
        prepared.groupby(["year", "week", "period"], as_index=False)[["current_cases", "predicted_cases"]]
        .sum()
        .sort_values(["year", "week"])
        .tail(14)
    )
    forecast_df["gap"] = forecast_df["predicted_cases"] - forecast_df["current_cases"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=forecast_df["period"],
            y=forecast_df["current_cases"],
            name="Observe",
            marker_color="rgba(10,95,171,.82)",
            hovertemplate="<b>%{x}</b><br>Observe: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df["period"],
            y=forecast_df["predicted_cases"],
            mode="lines+markers",
            name="Projete par IA",
            line=dict(color="#f59e0b", width=3, shape="spline"),
            marker=dict(size=8, color="#ffffff", line=dict(color="#f59e0b", width=2)),
            hovertemplate="<b>%{x}</b><br>Projete: %{y}<extra></extra>",
        )
    )
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(title="Cas")
    fig.update_layout(height=410)
    return make_plotly_layout(fig, "Prediction IA vs terrain")


def _build_top_provinces(entries_df: pd.DataFrame) -> go.Figure:
    prepared = prepare_periodic_entries(entries_df, required_columns={"province"})
    if prepared.empty:
        return empty_state_figure("Charge par province", "Aucune couverture provinciale recente.", make_plotly_layout)

    province_df = (
        prepared.groupby("province", as_index=False)["total_cases"]
        .sum()
        .sort_values("total_cases", ascending=True)
        .tail(8)
    )

    fig = go.Figure(
        go.Bar(
            x=province_df["total_cases"],
            y=province_df["province"],
            orientation="h",
            marker=dict(
                color=province_df["total_cases"],
                colorscale=[[0, "#dbeafe"], [0.45, "#49acef"], [1, "#0a5fab"]],
                line=dict(color="#ffffff", width=1.5),
            ),
            text=province_df["total_cases"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cas cumules: %{x}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Cas recents")
    fig.update_layout(height=390)
    return make_plotly_layout(fig, "Charge par province")


def _build_top_diseases(entries_df: pd.DataFrame) -> go.Figure:
    prepared = prepare_periodic_entries(entries_df, required_columns={"disease"})
    if prepared.empty:
        return empty_state_figure("Pathologies dominantes", "Aucune repartition pathologique recente.", make_plotly_layout)

    disease_df = (
        prepared.groupby("disease", as_index=False)["total_cases"]
        .sum()
        .sort_values("total_cases", ascending=True)
        .tail(8)
    )

    fig = go.Figure(
        go.Bar(
            x=disease_df["total_cases"],
            y=disease_df["disease"],
            orientation="h",
            marker=dict(
                color=disease_df["total_cases"],
                colorscale=[[0, "#dbeafe"], [0.45, "#49acef"], [1, "#0a5fab"]],
            ),
            text=disease_df["total_cases"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cas: %{x}<extra></extra>",
        )
    )
    fig.update_layout(height=390)
    return make_plotly_layout(fig, "Pathologies dominantes")


def main() -> None:
    st.set_page_config(page_title="Dashboard National | SAFE CONGO", layout="wide")
    apply_admin_theme()
    st.markdown(
        """
<style>
    @media (max-width: 1180px) {
        div[data-testid="stHorizontalBlock"] { gap: .85rem !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }
</style>
""",
        unsafe_allow_html=True,
    )

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        st.stop()

    render_admin_sidebar(user, active_item=1, show_logo=False)
    _, admin_unread = admin_notifications_snapshot(auth, user["id"])
    render_admin_hero(
        title="Command center epidemiologique",
        subtitle="Une vue executive nette, centree sur la dynamique nationale, la qualite des projections et les zones qui demandent une decision rapide.",
        chips=["Surveillance structuree", "Analyse IA active", "Lecture sans doublons"],
        eyebrow="Niveau national",
        notification_count=admin_unread,
        auth=auth,
        user_id=user["id"],
        inbox_key_prefix="admin_dashboard_inbox",
        inbox_limit=8,
    )

    entries_df = recent_entries_frame(auth.db_path)
    alerts_df = alerts_frame(auth.db_path)
    users_df = users_frame(auth)
    prepared_entries = prepare_periodic_entries(entries_df, required_columns={"province", "disease", "total_deaths"})
    prepared_alerts = prepare_periodic_alerts(alerts_df)
    provinces_covered = prepared_entries["province"].nunique() if not prepared_entries.empty else 0
    latest_cases = int(prepared_entries["total_cases"].sum()) if not prepared_entries.empty else 0
    critical_alerts = int((prepared_alerts["alert_level"].astype(str).str.upper() == "CRITIQUE").sum()) if not prepared_alerts.empty else 0
    active_users = len(users_df)

    render_kpi_cards(
        [
            {
                "label": "Charge recente",
                "value": f"{latest_cases}",
                "delta": "Cas consolides",
                "copy": "Volume cumule sur la fenetre recente retenue pour le pilotage executif.",
                "accent": "#0a5fab",
                "accent_soft": "#49acef",
                "pill": "rgba(10,95,171,.12)",
            },
            {
                "label": "Alertes critiques",
                "value": f"{critical_alerts}",
                "delta": "Priorite immediate",
                "copy": "Nombre de signaux critiques actuellement presents dans la file d'alerte.",
                "accent": "#ce1126",
                "accent_soft": "#f87171",
                "pill": "rgba(206,17,38,.12)",
            },
            {
                "label": "Provinces couvertes",
                "value": f"{provinces_covered}",
                "delta": f"{active_users} operateurs",
                "copy": "Empreinte territoriale visible par le reseau terrain et les administrateurs actifs.",
                "accent": "#059669",
                "accent_soft": "#34d399",
                "pill": "rgba(5,150,105,.12)",
            },
        ]
    )

    section_label("Vue executive simplifiee")
    top_left, top_right = st.columns(2, gap="large")
    with top_left:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_build_weekly_trend(entries_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with top_right:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_build_prediction_gap(alerts_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns(2, gap="large")
    with bottom_left:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_build_top_provinces(entries_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with bottom_right:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_build_top_diseases(entries_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()