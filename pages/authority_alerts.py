import sys
from pathlib import Path
import re
import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_generator import BarrierMeasuresPDF
from src.config import ALERT_LEVEL_COLORS, WHO_ALERT_LEVELS
from utils.auth import AuthSystem, require_auth
from utils.authority_ui import (
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


VISIBLE_ALERT_LEVELS = ["CRITIQUE", "HAUTE", "MODEREE", "FAIBLE"]


def _level_class(level: str) -> str:
    normalized = (level or "").lower()
    if normalized == "critique":
        return "critique"
    if normalized == "haute":
        return "haute"
    if normalized == "moderee":
        return "moderee"
    return "faible"


def _normalize_alert_levels(alerts_df: pd.DataFrame) -> pd.DataFrame:
    if alerts_df.empty or "alert_level" not in alerts_df.columns:
        return alerts_df
    normalized = alerts_df.copy()
    normalized["alert_level"] = normalized["alert_level"].astype(str).str.upper().str.strip().replace({"NOUVELLE_DONNEE": "FAIBLE", "INFO": "FAIBLE"})
    normalized.loc[~normalized["alert_level"].isin(VISIBLE_ALERT_LEVELS), "alert_level"] = "FAIBLE"
    return normalized


def _level_distribution_chart(alerts_df) -> go.Figure:
    if alerts_df.empty:
        return empty_state_figure("Repartition des niveaux", "Aucune alerte ciblee pour composer la distribution.", make_plotly_layout)
    grouped = _normalize_alert_levels(alerts_df).groupby("alert_level", as_index=False).size().rename(columns={"size": "count"})
    chart_df = (
        pd.DataFrame({"alert_level": VISIBLE_ALERT_LEVELS})
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


def _is_terrain_signal(message: str) -> bool:
    text = str(message or "").strip().lower()
    return text.startswith("nouveau signal terrain safe congo")


def _is_fallback_prediction(row: pd.Series) -> bool:
    raw_message = str(row.get("message", "") or "").strip().lower()
    message = "".join(
        ch for ch in unicodedata.normalize("NFKD", raw_message)
        if unicodedata.category(ch) != "Mn"
    )
    if "source:model" in message:
        return False
    if "source:fallback" in message:
        return True
    if "prevision safe congo" not in message:
        return False
    try:
        current_cases = int(row.get("current_cases", 0) or 0)
        predicted_cases = int(row.get("predicted_cases", 0) or 0)
        growth = float(row.get("growth_rate", 0.0) or 0.0)
    except Exception:
        return False
    return current_cases == predicted_cases and abs(growth) < 1e-9


def _should_hide_terrain_growth(row: pd.Series) -> bool:
    if not _is_terrain_signal(row.get("message", "")):
        return False
    try:
        growth_value = float(row.get("growth_rate", 0.0) or 0.0)
        current_cases = int(row.get("current_cases", 0) or 0)
        predicted_cases = int(row.get("predicted_cases", 0) or 0)
    except Exception:
        return False
    return current_cases == predicted_cases and growth_value >= 100.0


def _display_alert_message(row: pd.Series, hide_growth: bool) -> str:
    message = str(row.get("message", "") or "").strip()
    if not hide_growth:
        return message
    cleaned = re.sub(
        r",\s*croissance estimee\s*:\s*[+-]?\d+(?:\.\d+)?%\.?",
        "",
        message,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if cleaned.endswith(","):
        cleaned = cleaned[:-1].rstrip()
    if not cleaned.endswith("."):
        cleaned += "."
    return f"{cleaned} Croissance non comparee faute de base historique locale."


def main() -> None:
    st.set_page_config(page_title="Alertes autorite | SAFE CONGO", layout="wide")
    apply_authority_theme()
    st.markdown(
        """
<style>
    @media (max-width: 1180px) {
        div[data-testid="stHorizontalBlock"] { gap: .85rem !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        [data-testid="stExpander"] div[data-testid="stHorizontalBlock"] { gap: .65rem !important; }
    }
    @media (max-width: 760px) {
        .authority-support-copy { font-size: .84rem !important; line-height: 1.6 !important; }
        .authority-highlight, .authority-mini-card { padding: .95rem !important; }
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

    render_authority_sidebar(user, auth, active_item=2)
    alerts_df = _normalize_alert_levels(alerts_for_user(auth.db_path, user["id"]))
    unread_count = auth.get_unread_count(user["id"])

    render_authority_hero(
        title="Centre d'alertes ciblees",
        subtitle="Toutes les alertes ci-dessous vous ont ete explicitement diffusees. La page se concentre sur l'action, le niveau de gravite et les sorties PDF terrain.",
        chips=["Urgence lisible", user.get("province", "—")],
        eyebrow="Alertes adressees",
        auth=auth,
        user_id=user["id"],
        notification_count=unread_count,
        inbox_key_prefix="authority_alerts_inbox",
        inbox_limit=8,
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
                "copy": "Le flux d'alerte regroupe les signaux qui vous sont assignes, y compris si leur origine depasse votre seul territoire de reference.",
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
        ]
    )

    authority_section_label("Lecture et action")
    if alerts_df.empty:
        st.markdown('<div class="authority-empty-state">Aucune alerte ne vous a encore ete assignee.</div>', unsafe_allow_html=True)
        return

    st.markdown(
        """
<div class="authority-grid-2">
  <div class="authority-highlight"><strong>Filtrer, lire, agir</strong><span>Le niveau, le statut de lecture, la carte detaillee et le telechargement PDF restent dans le meme parcours sans rupture de page.</span></div>
  <div class="authority-mini-card"><h4>PDF terrain</h4><p>Chaque alerte peut produire directement une fiche de mesures barrieres prete a partager sur le terrain.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
    controls_left, controls_right = st.columns([1.5, 0.5], gap="large")
    with controls_left:
        authority_panel_title("Affiner le flux d'alertes")
        st.markdown('<div class="authority-support-copy">Filtrez par niveau puis parcourez les cartes detaillees sans multiplier les blocs vides. Les mesures barrieres restent telechargeables depuis chaque alerte.</div>', unsafe_allow_html=True)
        if hasattr(st, "segmented_control"):
            filter_level = st.segmented_control(
                "Niveau d'alerte",
                ["Toutes", "CRITIQUE", "HAUTE", "MODEREE", "FAIBLE"],
                default="Toutes",
                selection_mode="single",
                label_visibility="collapsed",
            )
        else:
            filter_level = st.radio(
                "Niveau d'alerte",
                ["Toutes", "CRITIQUE", "HAUTE", "MODEREE", "FAIBLE"],
                horizontal=True,
                label_visibility="collapsed",
            )
    with controls_right:
        st.markdown('<div style="height:2.2rem"></div>', unsafe_allow_html=True)
        if st.button("Rafraichir mes alertes", use_container_width=True, key="authority_refresh_alerts"):
            st.rerun()
    with st.expander("📋 Voir le referentiel OMS/IDSR des niveaux d'alerte", expanded=False):
        st.markdown(
            "<p style='font-size:.88rem;color:#566f88;margin-bottom:.8rem'>"
            "Les niveaux d'alerte SAFE CONGO suivent le cadre <strong>OMS IDSR 3e edition (2019)</strong> "
            "et le <strong>Reglement Sanitaire International (RSI 2005)</strong>. Chaque seuil combine un critere absolu "
            "et un critere de croissance hebdomadaire pour accelerer la decision terrain."
            "</p>",
            unsafe_allow_html=True,
        )
        cols = st.columns(4, gap="small")
        for col, level_key in zip(cols, ["FAIBLE", "MODEREE", "HAUTE", "CRITIQUE"]):
            lvl = WHO_ALERT_LEVELS[level_key]
            with col:
                st.markdown(
                    f"""<div style='border-left:4px solid {lvl["color"]};padding:.7rem .8rem;background:linear-gradient(180deg,#f8fbff 0%,#eef6ff 100%);border:1px solid rgba(207,227,244,.75);border-radius:10px;height:100%'>
                      <div style='font-weight:700;font-size:.9rem;color:{lvl["color"]}'>{lvl["icon"]} {level_key}</div>
                      <div style='font-size:.8rem;color:#334155;margin:.45rem 0'>{lvl["who_criterion"]}</div>
                      <div style='font-size:.77rem;color:#0a5fab;font-weight:700'>Action: {lvl["action"]}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_df = alerts_df if filter_level == "Toutes" else alerts_df.loc[alerts_df["alert_level"] == filter_level].copy()

    if filtered_df.empty:
        st.markdown('<div class="authority-empty-state">Aucune alerte ne correspond au filtre selectionne. Passez sur "Toutes" ou choisissez un autre niveau.</div>', unsafe_allow_html=True)
        authority_section_label("Assistance")
        st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
        authority_panel_title("Aide et contact")
        st.markdown('<div class="authority-support-copy">Pour toute question sur la gestion des alertes ou pour signaler un probleme technique, contactez l\'administration SAFE CONGO et suivez votre circuit de coordination provincial.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
    st.plotly_chart(_level_distribution_chart(filtered_df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    pdf_generator = BarrierMeasuresPDF()
    for _, row in filtered_df.iterrows():
        level = row["alert_level"]
        css_level = _level_class(level)
        growth_value = float(row["growth_rate"] or 0)
        growth_label = f"{growth_value:.1f}%"
        if growth_value > 0:
            growth_label = f"+{growth_label}"

        terrain_signal = _is_terrain_signal(row.get("message", ""))
        hide_growth = _should_hide_terrain_growth(row)
        if hide_growth:
            growth_label = "Non comparee"
        fallback_prediction = _is_fallback_prediction(row)
        if terrain_signal:
            projection_value_label = "Non disponible"
            projection_caption = "Projection IA"
        elif fallback_prediction:
            projection_value_label = f"{int(row['predicted_cases']):,}"
            projection_caption = "IA-secours"
        else:
            projection_value_label = f"{int(row['predicted_cases']):,}"
            projection_caption = "Projection IA"

        summary_label = f"{level} • {row['disease']} • {row['province']} • {int(row['current_cases']):,} cas"
        with st.expander(summary_label):
            st.markdown(
                f'<div class="authority-alert-card {css_level}"><div class="authority-alert-top"><div><div class="authority-alert-badge {css_level}">{level}</div><div class="authority-alert-title">{row["disease"]}</div><div class="authority-alert-meta">Observation source: {row["province"]} • {row["zone_sante"]} • Semaine {int(row["week"])}' + f'/{int(row["year"])}' + f'</div></div><div class="authority-alert-meta">Emission: {row["created_at"]}</div></div><div class="authority-alert-stats"><div class="authority-alert-stat"><strong>{int(row["current_cases"]):,}</strong><span>Cas actuels</span></div><div class="authority-alert-stat"><strong>{projection_value_label}</strong><span>{projection_caption}</span></div><div class="authority-alert-stat"><strong>{growth_label}</strong><span>Croissance</span></div></div><div class="authority-alert-meta" style="font-size:.86rem;color:#566f88">{_display_alert_message(row, hide_growth)}</div></div>',
                unsafe_allow_html=True,
            )

            try:
                pdf_bytes = pdf_generator.generate_alert_pdf(
                    disease=row["disease"],
                    province=row["province"],
                    zone_sante=row["zone_sante"],
                    current_cases=int(row["current_cases"]),
                    predicted_cases=int(row["predicted_cases"]),
                    growth_rate=0.0 if hide_growth else float(row["growth_rate"]),
                    alert_level=level,
                    r2_score=(float(row["r2_score"]) if row.get("r2_score") not in (None, "") else None),
                    week=int(row["week"]),
                    year=int(row["year"]),
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
                st.markdown('<div class="authority-empty-state">La fiche PDF n\'est pas disponible pour cette alerte.</div>', unsafe_allow_html=True)

    authority_section_label("Assistance")
    st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
    authority_panel_title("Aide et contact")
    st.markdown('<div class="authority-support-copy">Pour toute question sur la gestion des alertes ou pour signaler un probleme technique, contactez l\'administration SAFE CONGO et suivez votre circuit de coordination provincial. La page Contact reprend deja les partenaires de reference et le parcours d\'activation de l\'application.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()