import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ALERT_LEVEL_COLORS, ALERT_LEVEL_ORDER
from utils.auth import AuthSystem, require_auth
from utils.authority_ui import (
    alert_delivery_health,
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
from utils.navigation import switch_to_home_page


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
    if alerts_df.empty:
        return pd.DataFrame()
    prepared = alerts_df.copy()
    for column in ["current_cases", "predicted_cases", "growth_rate", "week", "year", "is_read"]:
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0)
    if "created_at" in prepared.columns:
        prepared["created_at"] = pd.to_datetime(prepared["created_at"], errors="coerce")
    prepared["alert_level"] = prepared["alert_level"].astype(str).str.upper().str.strip().replace({"NOUVELLE_DONNEE": "INFO"})
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
                name="Deces",
                line=dict(color="#ce1126", width=2.5, dash="dot"),
                marker=dict(size=7, color="#ce1126"),
                hovertemplate="<b>%{x}</b><br>Deces: %{y}<extra></extra>",
            )
        )
    fig.update_layout(hovermode="x unified")
    return make_plotly_layout(fig, "Trajectoire provinciale")


def _top_diseases_chart(history_df: pd.DataFrame) -> go.Figure:
    prepared = _prepare_history(history_df)
    if prepared.empty or "MALADIE" not in prepared.columns or "TOTALCAS" not in prepared.columns:
        return empty_state_figure("Pathologies dominantes", "Aucune repartition pathologique recente.", make_plotly_layout)

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
        return empty_state_figure("Intensite des alertes", "Aucune alerte ciblee disponible.", make_plotly_layout)

    grouped = prepared.groupby("alert_level", as_index=False).size().rename(columns={"size": "count"})
    chart_df = pd.DataFrame({"alert_level": ALERT_LEVEL_ORDER}).merge(grouped, on="alert_level", how="left").fillna(0)
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
    return make_plotly_layout(fig, "Intensite des alertes")


def _read_status_chart(alerts_df: pd.DataFrame) -> go.Figure:
    prepared = _prepare_alerts(alerts_df)
    if prepared.empty:
        return empty_state_figure("Lecture du flux", "Aucune notification a mesurer.", make_plotly_layout)

    prepared["Statut"] = prepared["is_read"].map({1: "Lue", 0: "Non lue"}).fillna("Non lue")
    chart_df = prepared.groupby("Statut", as_index=False).size().rename(columns={"size": "count"})
    fig = go.Figure(
        go.Pie(
            labels=chart_df["Statut"],
            values=chart_df["count"],
            hole=0.68,
            marker=dict(colors=["#059669", "#f59e0b"]),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Alertes: %{value}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Lecture du flux")


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
    st.set_page_config(page_title="Tableau de bord autorite | SAFE CONGO", layout="wide")
    apply_authority_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "autorite_sanitaire":
        switch_to_home_page()
        st.stop()

    render_authority_sidebar(user, auth, active_item=1)
    render_authority_hero(
        title="Tableau de bord territorial",
        subtitle="Une console territoriale plus nette pour lire vos alertes ciblees, replacer les signaux dans le contexte provincial et accelerer les decisions de terrain.",
        chips=["Veille locale", user.get("province", "—"), user.get("zone_sante", "—")],
        eyebrow="Surveillance territoriale",
    )

    history_df = load_historical_province(user.get("province", ""))
    assigned_alerts_df = alerts_for_user(auth.db_path, user["id"])
    unread_count = auth.get_unread_count(user["id"])
    delivery_health = alert_delivery_health(auth.db_path, user["id"])
    prov_cases, prov_deaths, prov_entries = _province_summary(auth, user.get("province", ""))

    prepared_alerts = _prepare_alerts(assigned_alerts_df)
    max_growth = prepared_alerts["growth_rate"].max() if not prepared_alerts.empty else 0.0
    critical_count = int((prepared_alerts["alert_level"] == "CRITIQUE").sum()) if not prepared_alerts.empty else 0

    render_authority_kpis(
        [
            {
                "label": "Alertes recues",
                "value": str(len(assigned_alerts_df)),
                "delta": "Flux cible pour votre compte",
                "copy": "La vue se concentre sur les alertes reellement adressees a votre compte, pas sur un simple filtre provincial brut.",
                "accent": "#0a5fab",
                "accent_soft": "#49acef",
                "pill": "rgba(10,95,171,.12)",
            },
            {
                "label": "Non lues",
                "value": str(unread_count),
                "delta": "Priorites immediates",
                "copy": "Le compteur non lu sert de file d'attente claire pour prioriser votre reaction terrain.",
                "accent": "#059669",
                "accent_soft": "#34d399",
                "pill": "rgba(5,150,105,.12)",
            },
            {
                "label": "Cas provinciaux",
                "value": f"{prov_cases:,}",
                "delta": f"{prov_deaths:,} deces suivis",
                "copy": "Le contexte provincial reste visible pour eviter qu'une alerte ciblee soit lue hors de sa realite locale.",
                "accent": "#d97706",
                "accent_soft": "#fcd116",
                "pill": "rgba(217,119,6,.12)",
            },
            {
                "label": "Saisies suivies",
                "value": str(prov_entries),
                "delta": f"{critical_count} critiques",
                "copy": "Le stock d'entrees et le nombre de critiques donnent une lecture rapide de la pression territoriale actuelle.",
                "accent": "#7c3aed",
                "accent_soft": "#a78bfa",
                "pill": "rgba(124,58,237,.12)",
            },
        ]
    )

    health_class = "dot-ok" if delivery_health.get("ok") else "dot-warn"
    st.markdown(
        f'<div class="authority-status-chip {health_class}">{delivery_health.get("message")} ({delivery_health.get("linked_alert_count", 0)}/{delivery_health.get("notification_count", 0)} liees, {delivery_health.get("unread_count", 0)} non lues)</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="authority-grid-3">
  <div class="authority-mini-card"><h4>Lecture ciblee</h4><p>Votre cockpit met en avant les alertes qui vous ont effectivement ete diffusees, puis les replace dans le contexte provincial.</p></div>
  <div class="authority-highlight"><strong>Pression actuelle</strong><span>{'Escalade active' if max_growth >= 30 else 'Sous tension' if max_growth >= 10 else 'Sous controle'} avec un pic de croissance observe a {max_growth:.1f}%.</span></div>
  <div class="authority-mini-card"><h4>Decision rapide</h4><p>Depuis cette page, vous identifiez les critiques, les signaux non lus et l'ouverture directe vers le centre d'alertes detaillees.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )

    authority_section_label("Vue territoriale")
    left_col, right_col = st.columns([1.18, 0.92], gap="large")
    with left_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_historical_trend_chart(history_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_panel_title("Dernieres notifications")
        preview_notifications = auth.get_notifications(user["id"], unread_only=False)
        if not preview_notifications:
            st.markdown('<div class="authority-empty-state">Aucune notification disponible pour le moment.</div>', unsafe_allow_html=True)
        else:
            for notification in preview_notifications[:5]:
                status_label = "NON LUE" if int(notification["is_read"]) == 0 else "LUE"
                with st.expander(f"{status_label} • {notification['title']}"):
                    st.markdown(
                        f'<div class="authority-highlight" style="margin-bottom:12px"><strong>{notification["title"]}</strong><span>{notification["message"]}</span><span style="display:block;margin-top:8px;font-size:.74rem;color:#7b91a5">{notification["created_at"]}</span></div>',
                        unsafe_allow_html=True,
                    )
                    if int(notification["is_read"]) == 0 and st.button(
                        "Marquer cette notification comme lue",
                        use_container_width=True,
                        key=f"authority_preview_read_{int(notification['id'])}",
                    ):
                        auth.mark_notification_read(int(notification["id"]))
                        st.rerun()
            if unread_count > 0 and st.button("Tout marquer comme lu", use_container_width=True, key="authority_mark_all_read"):
                auth.mark_all_notifications_read(user["id"])
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_top_diseases_chart(history_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_assigned_levels_chart(assigned_alerts_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_read_status_chart(assigned_alerts_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_panel_title("Capsule terrain")
        st.markdown(
            f'<div class="authority-highlight"><strong>Province: {user.get("province", "—")}</strong><span>Zone de sante de reference: {user.get("zone_sante", "—")}.</span></div><div style="height:12px"></div><div class="authority-highlight"><strong>{len(assigned_alerts_df)} alertes a suivre</strong><span>Les signaux diffuses a votre compte peuvent depasser la seule province d\'affectation si l\'administration le decide.</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Ouvrir mes alertes detaillees", use_container_width=True, key="authority_to_alerts"):
            st.switch_page("pages/authority_alerts.py")
        st.markdown('</div>', unsafe_allow_html=True)

    authority_section_label("Assistance")
    st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
    authority_panel_title("Aide et contact")
    st.markdown('<div class="authority-support-copy">Pour toute question sur l\'utilisation du tableau de bord ou pour signaler un probleme technique, passez par l\'administration SAFE CONGO et par votre circuit de coordination provincial. La page Contact presente les partenaires institutionnels et le parcours d\'acces deja retenu dans l\'application.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()