import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_generator import BarrierMeasuresPDF
from utils.auth import AuthSystem, require_auth
from utils.authority_ui import alerts_for_user, apply_authority_theme, authority_panel_title, authority_section_label, render_authority_hero, render_authority_kpis, render_authority_sidebar
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
    return "nouvelle_donnee"


def main() -> None:
    st.set_page_config(page_title="Alertes autorite - SAFE CONGO", page_icon=None, layout="wide")
    apply_authority_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "autorite_sanitaire":
        switch_to_home_page()
        return

    render_authority_sidebar(user, auth, active_item=2)
    alerts_df = alerts_for_user(auth.db_path, user["id"])
    unread_count = auth.get_unread_count(user["id"])

    render_authority_hero("Centre d'alertes ciblees", "Toutes les alertes ci-dessous vous ont ete explicitement diffusees. La page se concentre sur l'action, la lecture du niveau et les sorties PDF terrain.", ["Urgence lisible", f"{unread_count} non lue(s)", user.get("province", "—")], eyebrow="Alertes adressees")

    critique_count = int((alerts_df["alert_level"] == "CRITIQUE").sum()) if not alerts_df.empty else 0
    haute_count = int((alerts_df["alert_level"] == "HAUTE").sum()) if not alerts_df.empty else 0
    moderee_count = int((alerts_df["alert_level"] == "MODEREE").sum()) if not alerts_df.empty else 0

    render_authority_kpis([
        {"label": "Alertes totales", "value": str(len(alerts_df)), "delta": "Ciblees pour votre compte", "copy": "Le flux d'alerte est maintenant pilote par les notifications qui vous ont ete adressees, y compris si la diffusion vient d'un autre territoire.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.1)"},
        {"label": "Critiques", "value": str(critique_count), "delta": "Priorite maximale", "copy": "Les signaux critiques remontent en premier pour accelerer la decision sanitaire et la coordination locale.", "accent": "#dc2626", "accent_soft": "#fca5a5", "pill": "rgba(220,38,38,.12)"},
        {"label": "Hautes", "value": str(haute_count), "delta": f"{moderee_count} moderees en soutien", "copy": "Les alertes hautes exigent une lecture rapide, meme si elles ne sont pas encore au niveau critique.", "accent": "#ea580c", "accent_soft": "#fdba74", "pill": "rgba(234,88,12,.12)"},
        {"label": "Non lues", "value": str(unread_count), "delta": "File d'attente terrain", "copy": "Le compteur non lu sert de repere clair pour traiter vos alertes une a une sans perdre de priorite.", "accent": "#059669", "accent_soft": "#34d399", "pill": "rgba(5,150,105,.12)"},
    ])

    authority_section_label("Filtrage & lecture")
    if alerts_df.empty:
        st.markdown('<div class="authority-empty-state">Aucune alerte ne vous a encore ete assignee.</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="authority-panel">', unsafe_allow_html=True)
    authority_panel_title("Affiner le flux d'alertes")
    st.markdown('<div class="authority-support-copy">Filtrez par niveau, parcourez les cartes detaillees puis telechargez les mesures barrieres correspondantes sans quitter la page.</div>', unsafe_allow_html=True)
    filter_level = st.radio("Niveau", ["Toutes", "CRITIQUE", "HAUTE", "MODEREE", "INFO", "NOUVELLE_DONNEE"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_df = alerts_df if filter_level == "Toutes" else alerts_df.loc[alerts_df["alert_level"] == filter_level].copy()
    pdf_generator = BarrierMeasuresPDF()

    for _, row in filtered_df.iterrows():
        level = row["alert_level"]
        css_level = _level_class(level)
        growth_value = float(row["growth_rate"] or 0)
        growth_label = f"{growth_value:.1f}%"
        if growth_value > 0:
            growth_label = f"+{growth_label}"

        st.markdown(f"<div class=\"authority-alert-card {css_level}\"><div class=\"authority-alert-top\"><div><div class=\"authority-alert-badge {css_level}\">{'Non lue' if int(row['is_read']) == 0 else 'Lue'} • {level}</div><div class=\"authority-alert-title\">{row['disease']}</div><div class=\"authority-alert-meta\">Observation source: {row['province']} • {row['zone_sante']} • Semaine {int(row['week'])}/{int(row['year'])}</div></div><div class=\"authority-alert-meta\">Emission: {row['created_at']}</div></div><div class=\"authority-alert-stats\"><div class=\"authority-alert-stat\"><strong>{int(row['current_cases']):,}</strong><span>Cas actuels</span></div><div class=\"authority-alert-stat\"><strong>{int(row['predicted_cases']):,}</strong><span>Projection</span></div><div class=\"authority-alert-stat\"><strong>{growth_label}</strong><span>Croissance</span></div></div><div class=\"authority-alert-meta\" style=\"font-size:.86rem;color:#566f88\">{row['message']}</div></div>", unsafe_allow_html=True)

        action_col, pdf_col = st.columns([0.8, 1.2], gap="large")
        with action_col:
            if int(row["is_read"]) == 0 and st.button("Marquer comme lue", key=f"read_{int(row['notif_id'])}", use_container_width=True):
                auth.mark_notification_read(int(row["notif_id"]))
                st.rerun()
        with pdf_col:
            try:
                pdf_bytes = pdf_generator.generate_alert_pdf(disease=row["disease"], province=row["province"], zone_sante=row["zone_sante"], current_cases=int(row["current_cases"]), predicted_cases=int(row["predicted_cases"]), growth_rate=float(row["growth_rate"]), alert_level=level, r2_score=0.816)
                st.download_button("Telecharger les mesures barrieres (PDF)", pdf_bytes, file_name=f"alerte_{row['disease']}_{int(row['week'])}_{int(row['year'])}.pdf", mime="application/pdf", key=f"pdf_{int(row['id'])}", use_container_width=True)
            except Exception:
                pass


if __name__ == "__main__":
    main()
