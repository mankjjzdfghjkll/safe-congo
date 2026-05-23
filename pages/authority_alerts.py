import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_generator import BarrierMeasuresPDF
from src.config import ALERT_LEVEL_COLORS, ALERT_LEVEL_ORDER
from utils.auth import AuthSystem, require_auth
from utils.authority_ui import (
    alert_delivery_health,
    alerts_for_user,
    apply_authority_theme,
    authority_panel_title,
    authority_section_label,
    make_plotly_layout,
    render_authority_hero,
    render_authority_kpis,
    render_authority_sidebar,
)
from utils.chart_helpers import empty_state_figure
from utils.navigation import switch_to_home_page


def _level_class(level: str) -> str:
    normalized = (level or "").lower()
    if normalized == "critique":
        return "critique"
    if normalized == "haute":
        return "haute"
    if normalized == "moderee":
        return "moderee"
    if normalized == "info":
        return "info"
    return "info"


def _normalize_alert_levels(alerts_df: pd.DataFrame) -> pd.DataFrame:
    if alerts_df.empty or "alert_level" not in alerts_df.columns:
        return alerts_df
    normalized = alerts_df.copy()
    normalized["alert_level"] = normalized["alert_level"].astype(str).str.upper().str.strip().replace({"NOUVELLE_DONNEE": "INFO"})
    return normalized


def _level_distribution_chart(alerts_df) -> go.Figure:
    if alerts_df.empty:
        return empty_state_figure("Repartition des niveaux", "Aucune alerte ciblee pour composer la distribution.", make_plotly_layout)
    grouped = _normalize_alert_levels(alerts_df).groupby("alert_level", as_index=False).size().rename(columns={"size": "count"})
    chart_df = (
        pd.DataFrame({"alert_level": ALERT_LEVEL_ORDER})
        .merge(grouped, on="alert_level", how="left")
        .fillna(0)
    )
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
    return make_plotly_layout(fig, "Repartition des niveaux")


def _read_distribution_chart(alerts_df) -> go.Figure:
    if alerts_df.empty:
        return empty_state_figure("Lecture des alertes", "Aucune lecture a mesurer pour le moment.", make_plotly_layout)
    grouped = alerts_df.assign(statut=alerts_df["is_read"].map({1: "Lues", 0: "Non lues"}).fillna("Non lues"))
    chart_df = grouped.groupby("statut", as_index=False).size().rename(columns={"size": "count"})
    fig = go.Figure(
        go.Pie(
            labels=chart_df["statut"],
            values=chart_df["count"],
            hole=0.68,
            marker=dict(colors=["#059669", "#f59e0b"]),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Alertes: %{value}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Lecture des alertes")


def main() -> None:
    st.set_page_config(page_title="Alertes autorite | SAFE CONGO", layout="wide")
    apply_authority_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "autorite_sanitaire":
        switch_to_home_page()
        st.stop()

    render_authority_sidebar(user, auth, active_item=2)
    alerts_df = _normalize_alert_levels(alerts_for_user(auth.db_path, user["id"]))
    unread_count = auth.get_unread_count(user["id"])
    delivery_health = alert_delivery_health(auth.db_path, user["id"])

    render_authority_hero(
        title="Centre d'alertes ciblees",
        subtitle="Toutes les alertes ci-dessous vous ont ete explicitement diffusees. La page se concentre sur l'action, le niveau de gravite et les sorties PDF terrain.",
        chips=["Urgence lisible", f"{unread_count} non lue(s)", user.get("province", "—")],
        eyebrow="Alertes adressees",
    )

    chip_class = "dot-ok" if delivery_health.get("ok") else "dot-warn"
    st.markdown(
        f'<div class="authority-status-chip {chip_class}">{delivery_health.get("message")} ({delivery_health.get("linked_alert_count", 0)}/{delivery_health.get("notification_count", 0)} liees)</div>',
        unsafe_allow_html=True,
    )

    critique_count = int((alerts_df["alert_level"] == "CRITIQUE").sum()) if not alerts_df.empty else 0
    haute_count = int((alerts_df["alert_level"] == "HAUTE").sum()) if not alerts_df.empty else 0
    moderee_count = int((alerts_df["alert_level"] == "MODEREE").sum()) if not alerts_df.empty else 0

    render_authority_kpis(
        [
            {
                "label": "Alertes totales",
                "value": str(len(alerts_df)),
                "delta": "Ciblees pour votre compte",
                "copy": "Le flux d'alerte est pilote par les notifications qui vous ont ete adressees, y compris si elles viennent d'un autre territoire.",
                "accent": "#0a5fab",
                "accent_soft": "#49acef",
                "pill": "rgba(10,95,171,.12)",
            },
            {
                "label": "Critiques",
                "value": str(critique_count),
                "delta": "Priorite maximale",
                "copy": "Les signaux critiques remontent en premier pour accelerer la decision sanitaire et la coordination locale.",
                "accent": "#dc2626",
                "accent_soft": "#fca5a5",
                "pill": "rgba(220,38,38,.12)",
            },
            {
                "label": "Hautes",
                "value": str(haute_count),
                "delta": f"{moderee_count} moderees",
                "copy": "Les alertes hautes exigent une lecture rapide, meme si elles ne sont pas encore au niveau critique.",
                "accent": "#ea580c",
                "accent_soft": "#fdba74",
                "pill": "rgba(234,88,12,.12)",
            },
            {
                "label": "Non lues",
                "value": str(unread_count),
                "delta": "File d'attente terrain",
                "copy": "Le compteur non lu sert de repere simple pour traiter les alertes une a une sans perdre de priorite.",
                "accent": "#059669",
                "accent_soft": "#34d399",
                "pill": "rgba(5,150,105,.12)",
            },
        ]
    )

    authority_section_label("Lecture et action")
    if alerts_df.empty:
        st.markdown('<div class="authority-empty-state">Aucune alerte ne vous a encore ete assignee.</div>', unsafe_allow_html=True)
        return

    st.markdown(
        """
<div class="authority-grid-3">
  <div class="authority-mini-card"><h4>Filtrage simple</h4><p>Le niveau, le statut de lecture et la carte detaillee restent dans la meme page sans rupture de parcours.</p></div>
  <div class="authority-highlight"><strong>PDF terrain</strong><span>Chaque alerte peut produire directement un document de mesures barrieres pret a partager sur le terrain.</span></div>
  <div class="authority-mini-card"><h4>Traitement rapide</h4><p>Les alertes non lues peuvent etre marquees individuellement ou lues globalement selon votre rythme d'intervention.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )

    filter_col, stats_col = st.columns([1.2, 0.8], gap="large")
    with filter_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_panel_title("Affiner le flux d'alertes")
        st.markdown('<div class="authority-support-copy">Filtrez par niveau, parcourez les cartes detaillees puis telechargez les mesures barrieres correspondantes sans quitter la page.</div>', unsafe_allow_html=True)
        filter_level = st.radio("Niveau", ["Toutes", "CRITIQUE", "HAUTE", "MODEREE", "INFO"], horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with stats_col:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        if st.button("Rafraichir mes alertes", use_container_width=True, key="authority_refresh_alerts"):
            st.rerun()
        if unread_count > 0 and st.button("Tout marquer comme lu", use_container_width=True, key="authority_read_all"):
            auth.mark_all_notifications_read(user["id"])
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    filtered_df = alerts_df if filter_level == "Toutes" else alerts_df.loc[alerts_df["alert_level"] == filter_level].copy()

    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_level_distribution_chart(filtered_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with chart_right:
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        st.plotly_chart(_read_distribution_chart(filtered_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    pdf_generator = BarrierMeasuresPDF()
    for _, row in filtered_df.iterrows():
        level = row["alert_level"]
        css_level = _level_class(level)
        growth_value = float(row["growth_rate"] or 0)
        growth_label = f"{growth_value:.1f}%"
        if growth_value > 0:
            growth_label = f"+{growth_label}"

        status_label = "NON LUE" if int(row["is_read"]) == 0 else "LUE"
        summary_label = f"{status_label} • {level} • {row['disease']} • {row['province']} • {int(row['current_cases']):,} cas"
        with st.expander(summary_label):
            st.markdown(
                f'<div class="authority-alert-card {css_level}"><div class="authority-alert-top"><div><div class="authority-alert-badge {css_level}">{status_label} • {level}</div><div class="authority-alert-title">{row["disease"]}</div><div class="authority-alert-meta">Observation source: {row["province"]} • {row["zone_sante"]} • Semaine {int(row["week"])}' + f'/{int(row["year"])}' + f'</div></div><div class="authority-alert-meta">Emission: {row["created_at"]}</div></div><div class="authority-alert-stats"><div class="authority-alert-stat"><strong>{int(row["current_cases"]):,}</strong><span>Cas actuels</span></div><div class="authority-alert-stat"><strong>{int(row["predicted_cases"]):,}</strong><span>Projection</span></div><div class="authority-alert-stat"><strong>{growth_label}</strong><span>Croissance</span></div></div><div class="authority-alert-meta" style="font-size:.86rem;color:#566f88">{row["message"]}</div></div>',
                unsafe_allow_html=True,
            )

            action_col, pdf_col = st.columns([0.72, 1.28], gap="large")
            with action_col:
                if int(row["is_read"]) == 0 and st.button("Marquer comme lue", key=f"read_{int(row['notif_id'])}", use_container_width=True):
                    auth.mark_notification_read(int(row["notif_id"]))
                    st.rerun()
            with pdf_col:
                try:
                    pdf_bytes = pdf_generator.generate_alert_pdf(
                        disease=row["disease"],
                        province=row["province"],
                        zone_sante=row["zone_sante"],
                        current_cases=int(row["current_cases"]),
                        predicted_cases=int(row["predicted_cases"]),
                        growth_rate=float(row["growth_rate"]),
                        alert_level=level,
                        r2_score=float(row.get("r2_score", 0.0) or 0.0),
                    )
                    st.download_button(
                        "Telecharger la fiche barrieres",
                        pdf_bytes,
                        file_name=f"alerte_{row['disease']}_{int(row['week'])}_{int(row['year'])}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{int(row['id'])}",
                        use_container_width=True,
                    )
                except Exception:
                    pass

    authority_section_label("Assistance")
    st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
    authority_panel_title("Aide et contact")
    st.markdown('<div class="authority-support-copy">Pour toute question sur la gestion des alertes ou pour signaler un probleme technique, passez par l\'administration SAFE CONGO et par votre circuit de coordination provincial. La page Contact rappelle deja les partenaires de reference et le parcours d\'activation retenu par l\'application.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()