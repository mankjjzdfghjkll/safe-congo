import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ALERT_LEVEL_COLORS
from utils.auth import AuthSystem, require_auth
from utils.authority_ui import (
    alerts_for_user,
    apply_authority_theme,
    authority_panel_title,
    authority_section_label,
    load_historical_province,
    make_plotly_layout,
    render_authority_hero,
    render_authority_kpis,
    render_authority_sidebar,
)
from utils.chart_helpers import empty_state_figure
from utils.data_prep import prepare_periodic_alerts
from utils.navigation import switch_to_home_page


VISIBLE_ALERT_LEVELS = ["CRITIQUE", "HAUTE", "MODEREE", "FAIBLE"]


def _prepare_history(history_df: pd.DataFrame) -> pd.DataFrame:
    if history_df.empty:
        return pd.DataFrame()
    prepared = history_df.copy()
    if "DEBUTSEM" in prepared.columns:
        prepared["DEBUTSEM"] = pd.to_datetime(prepared["DEBUTSEM"], errors="coerce")
    if "TOTALCAS" in prepared.columns:
        prepared["TOTALCAS"] = pd.to_numeric(prepared["TOTALCAS"], errors="coerce").fillna(0)
    if "TOTALDECES" in prepared.columns:
        prepared["TOTALDECES"] = pd.to_numeric(prepared["TOTALDECES"], errors="coerce").fillna(0)
    return prepared.dropna(subset=["DEBUTSEM"]) if "DEBUTSEM" in prepared.columns else pd.DataFrame()


def _prepare_alerts(alerts_df: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_periodic_alerts(alerts_df, require_period=False)
    if prepared.empty:
        return prepared
    if "created_at" in prepared.columns:
        prepared["created_at"] = pd.to_datetime(prepared["created_at"], errors="coerce")
    prepared["alert_level"] = prepared["alert_level"].astype(str).str.upper().str.strip().replace({"NOUVELLE_DONNEE": "FAIBLE", "INFO": "FAIBLE"})
    prepared.loc[~prepared["alert_level"].isin(VISIBLE_ALERT_LEVELS), "alert_level"] = "FAIBLE"
    return prepared


def _historical_trend_chart(history_df: pd.DataFrame) -> go.Figure:
    prepared = _prepare_history(history_df)
    if prepared.empty or "TOTALCAS" not in prepared.columns:
        return empty_state_figure("Trajectoire provinciale", "Aucun historique provincial exploitable.", make_plotly_layout)

    chart_df = (
        prepared.groupby("DEBUTSEM", as_index=False)[["TOTALCAS", "TOTALDECES"]]
        .sum()
        .sort_values("DEBUTSEM")
        .tail(16)
    )
    chart_df["label"] = chart_df["DEBUTSEM"].dt.strftime("%d/%m/%Y")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["label"],
            y=chart_df["TOTALCAS"],
            mode="lines+markers",
            name="Cas",
            line=dict(color="#0a5fab", width=4, shape="spline"),
            marker=dict(size=8, color="#ffffff", line=dict(color="#0a5fab", width=2)),
            fill="tozeroy",
            fillcolor="rgba(10,95,171,.10)",
            hovertemplate="<b>%{x}</b><br>Cas: %{y}<extra></extra>",
        )
    )
    if "TOTALDECES" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df["label"],
                y=chart_df["TOTALDECES"],
                mode="lines+markers",
                name="Décès",
                line=dict(color="#ce1126", width=2.5, dash="dot"),
                marker=dict(size=7, color="#ce1126"),
                hovertemplate="<b>%{x}</b><br>Décès: %{y}<extra></extra>",
            )
        )
    fig.update_layout(hovermode="x unified")
    return make_plotly_layout(fig, "Trajectoire provinciale")


def _top_diseases_chart(history_df: pd.DataFrame) -> go.Figure:
    prepared = _prepare_history(history_df)
    if prepared.empty or "MALADIE" not in prepared.columns or "TOTALCAS" not in prepared.columns:
        return empty_state_figure("Pathologies dominantes", "Aucune répartition pathologique récente.", make_plotly_layout)

    chart_df = (
        prepared.groupby("MALADIE", as_index=False)["TOTALCAS"]
        .sum()
        .sort_values("TOTALCAS", ascending=True)
        .tail(8)
    )
    fig = go.Figure(
        go.Bar(
            x=chart_df["TOTALCAS"],
            y=chart_df["MALADIE"],
            orientation="h",
            marker=dict(color=chart_df["TOTALCAS"], colorscale=[[0, "#dbeafe"], [0.45, "#49acef"], [1, "#0a5fab"]]),
            text=chart_df["TOTALCAS"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cas: %{x}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Pathologies dominantes")


def _assigned_levels_chart(alerts_df: pd.DataFrame) -> go.Figure:
    prepared = _prepare_alerts(alerts_df)
    if prepared.empty:
        return empty_state_figure("Intensité des alertes", "Aucune alerte ciblée disponible.", make_plotly_layout)

    grouped = prepared.groupby("alert_level", as_index=False).size().rename(columns={"size": "count"})
    chart_df = pd.DataFrame({"alert_level": VISIBLE_ALERT_LEVELS}).merge(grouped, on="alert_level", how="left").fillna(0)
    chart_df["count"] = chart_df["count"].astype(int)
    fig = go.Figure(
        go.Bar(
            x=chart_df["count"],
            y=chart_df["alert_level"],
            orientation="h",
            marker_color=[ALERT_LEVEL_COLORS[level] for level in chart_df["alert_level"]],
            text=chart_df["count"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Alertes: %{x}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Intensité des alertes")


def _province_summary(auth: AuthSystem, province: str) -> tuple[int, int, int]:
    try:
        conn = sqlite3.connect(str(auth.db_path))
        query = """
            SELECT SUM(total_cases) AS total_cases, SUM(total_deaths) AS total_deaths, COUNT(*) AS entries
            FROM epidemiological_data
            WHERE province = ?
        """
        frame = pd.read_sql_query(query, conn, params=(province,))
        conn.close()
        return (
            int(frame["total_cases"].iloc[0] or 0),
            int(frame["total_deaths"].iloc[0] or 0),
            int(frame["entries"].iloc[0] or 0),
        )
    except Exception:
        return 0, 0, 0


def main() -> None:
    st.set_page_config(page_title="Tableau de bord autorité | SAFE CONGO", layout="wide")
    apply_authority_theme()
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
    if not user or user["role"] != "autorite_sanitaire":
        switch_to_home_page()
        st.stop()

    render_authority_sidebar(user, auth, active_item=1)
    render_authority_hero(
        title="Tableau de bord territorial",
        subtitle="Une console territoriale plus nette pour lire vos alertes ciblées, replacer les signaux dans le contexte provincial et accélérer les décisions de terrain.",
        chips=["Veille locale", user.get("province", "—"), user.get("zone_sante", "—")],
        eyebrow="Surveillance territoriale",
        auth=auth,
        user_id=user["id"],
        notification_count=auth.get_unread_count(user["id"]),
        inbox_key_prefix="authority_dashboard_inbox",
        inbox_limit=8,
    )

    history_df = load_historical_province(user.get("province", ""))
    assigned_alerts_df = alerts_for_user(auth.db_path, user["id"])
    prov_cases, prov_deaths, prov_entries = _province_summary(auth, user.get("province", ""))

    prepared_alerts = _prepare_alerts(assigned_alerts_df)
    max_growth = prepared_alerts["growth_rate"].max() if not prepared_alerts.empty else 0.0
    critical_count = int((prepared_alerts["alert_level"] == "CRITIQUE").sum()) if not prepared_alerts.empty else 0

    render_authority_kpis(
        [
            {
                "label": "Alertes reçues",
                "value": str(len(assigned_alerts_df)),
                "delta": "Flux cible pour votre compte",
                "copy": "La vue se concentre sur les alertes réellement adressées à votre compte, pas sur un simple filtre provincial brut.",
                "accent": "#0a5fab",
                "accent_soft": "#49acef",
                "pill": "rgba(10,95,171,.12)",
            },
            {
                "label": "Cas provinciaux",
                "value": f"{prov_cases:,}",
                "delta": f"{prov_deaths:,} décès suivis",
                "copy": "Le contexte provincial reste visible pour éviter qu'une alerte ciblée soit lue hors de sa réalité locale.",
                "accent": "#d97706",
                "accent_soft": "#fcd116",
                "pill": "rgba(217,119,6,.12)",
            },
            {
                "label": "Saisies suivies",
                "value": str(prov_entries),
                "delta": f"{critical_count} critiques",
                "copy": "Le stock d'entrées et le nombre de critiques donnent une lecture rapide de la pression territoriale actuelle.",
                "accent": "#7c3aed",
                "accent_soft": "#a78bfa",
                "pill": "rgba(124,58,237,.12)",
            },
        ]
    )

    authority_section_label("Vue territoriale")
    left_col, right_col = st.columns(2, gap="large")
    with left_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_historical_trend_chart(history_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_top_diseases_chart(history_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_assigned_levels_chart(assigned_alerts_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_panel_title("Capsule terrain")
        pressure_label = "Escalade active" if max_growth >= 30 else "Sous tension" if max_growth >= 10 else "Sous contrôle"
        st.markdown(
            f'<div class="authority-highlight"><strong>Province : {user.get("province", "—")}</strong>'
            f'<span>Zone de santé : {user.get("zone_sante", "—")} &nbsp;|&nbsp; {pressure_label} (pic +{max_growth:.0f}%)</span></div>'
            f'<div style="height:10px"></div>'
            f'<div class="authority-highlight"><strong>{len(assigned_alerts_df)} alertes à suivre</strong>'
            f'<span>{critical_count} critique(s) dans votre file.</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("Ouvrir mes alertes détaillées", use_container_width=True, key="authority_to_alerts"):
            st.switch_page("pages/authority_alerts.py")
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
