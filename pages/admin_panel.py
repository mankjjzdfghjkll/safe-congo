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
    panel_title,
    recent_entries_frame,
    render_admin_inbox_expander,
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


def _system_pulse_chart(entries_df: pd.DataFrame, alerts_df: pd.DataFrame, users_df: pd.DataFrame) -> go.Figure:
    entries = prepare_periodic_entries(entries_df)
    alerts = prepare_periodic_alerts(alerts_df)
    if entries.empty and alerts.empty:
        return empty_state_figure("Pulse systeme", "Le systeme attend encore des signaux recents pour composer ce pulse.", make_plotly_layout)

    entry_counts = entries.groupby("period", as_index=False).size().rename(columns={"size": "entries"}) if not entries.empty else pd.DataFrame(columns=["period", "entries"])
    alert_counts = alerts.groupby("period", as_index=False).size().rename(columns={"size": "alerts"}) if not alerts.empty and "period" in alerts.columns else pd.DataFrame(columns=["period", "alerts"])
    pulse = entry_counts.merge(alert_counts, on="period", how="outer").fillna(0)
    pulse = pulse.sort_values("period").tail(12)
    if pulse.empty:
        return empty_state_figure("Pulse systeme", "Aucune semaine consolidee disponible.", make_plotly_layout)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=pulse["period"],
            y=pulse["entries"],
            name="Saisies",
            marker_color="rgba(10,95,171,.84)",
            hovertemplate="<b>%{x}</b><br>Saisies: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pulse["period"],
            y=pulse["alerts"],
            name="Alertes",
            mode="lines+markers",
            line=dict(color="#f59e0b", width=3, shape="spline"),
            marker=dict(size=8, color="#ffffff", line=dict(color="#f59e0b", width=2)),
            hovertemplate="<b>%{x}</b><br>Alertes: %{y}<extra></extra>",
        )
    )
    fig.update_layout(hovermode="x unified")
    return make_plotly_layout(fig, "Pulse systeme")


def _coverage_chart(users_df: pd.DataFrame) -> go.Figure:
    if users_df.empty or "role" not in users_df.columns:
        return empty_state_figure("Couverture institutionnelle", "Aucune presence utilisateur consolidee.", make_plotly_layout)

    active_df = users_df.copy()
    if "is_active" in active_df.columns:
        active_df = active_df.loc[active_df["is_active"] == 1]
    role_df = active_df.groupby("role", as_index=False).size().rename(columns={"size": "count"})
    if role_df.empty:
        return empty_state_figure("Couverture institutionnelle", "Aucun compte actif a cartographier.", make_plotly_layout)

    fig = go.Figure(
        go.Pie(
            labels=role_df["role"],
            values=role_df["count"],
            hole=0.66,
            marker=dict(colors=["#0a5fab", "#34d399", "#fcd116", "#a78bfa"]),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Comptes: %{value}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Couverture institutionnelle")


def _recent_login_table(users_df: pd.DataFrame) -> pd.DataFrame:
    if users_df.empty:
        return pd.DataFrame()
    table_df = users_df.copy()
    table_df["Nom complet"] = table_df["nom"].fillna("") + " " + table_df["prenom"].fillna("")
    if "last_login" in table_df.columns:
        table_df = table_df.sort_values("last_login", ascending=False, na_position="last")
    if "is_active" in table_df.columns:
        table_df["Statut"] = table_df["is_active"].map({1: "Actif", 0: "Inactif"}).fillna("Inconnu")
    else:
        table_df["Statut"] = "Actif"
    return table_df[["Nom complet", "username", "role", "province", "last_login", "Statut"]].rename(
        columns={
            "username": "Identifiant",
            "role": "Role",
            "province": "Province",
            "last_login": "Derniere connexion",
        }
    )


def _render_action_ribbon() -> None:
    st.markdown(
        """
<div class="admin-grid-3">
  <div class="admin-mini-card"><h4>Executif national</h4><p>Basculer vers la lecture macro des courbes, de la pression territoriale et des signaux critiques.</p></div>
  <div class="admin-mini-card"><h4>Saisie et IA</h4><p>Declencher une nouvelle projection terrain sans quitter la couche de commandement.</p></div>
  <div class="admin-mini-card"><h4>Gouvernance utilisateurs</h4><p>Ouvrir ou restreindre le maillage institutionnel selon la pression operationnelle du moment.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ouvrir le dashboard", use_container_width=True, key="panel_to_dashboard"):
            st.switch_page("pages/admin_dashboard.py")
    with col2:
        if st.button("Lancer une prediction", use_container_width=True, key="panel_to_entry"):
            st.switch_page("pages/admin_data_entry.py")
    with col3:
        if st.button("Piloter les comptes", use_container_width=True, key="panel_to_users"):
            st.switch_page("pages/admin_users.py")


def main() -> None:
    st.set_page_config(page_title="Centre de pilotage | SAFE CONGO", layout="wide")
    apply_admin_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        st.stop()

    render_admin_sidebar(user, active_item=4, show_logo=False)
    _, admin_unread = admin_notifications_snapshot(auth, user["id"])
    render_admin_hero(
        title="Centre de pilotage systeme",
        subtitle="Une vue de supervision qui rassemble rythme de production, pression d'alerte, disponibilite du reseau et raccourcis d'action dans une seule salle de controle.",
        chips=["Commandement central", "Vue temps court", "Actions rapides"],
        eyebrow="Pilotage systeme",
        notification_count=admin_unread,
    )

    entries_df = recent_entries_frame(auth.db_path)
    alerts_df = alerts_frame(auth.db_path)
    users_df = users_frame(auth)
    db_size_kb = Path(auth.db_path).stat().st_size / 1024 if Path(auth.db_path).exists() else 0

    prepared_alerts = prepare_periodic_alerts(alerts_df)
    active_users = int((users_df["is_active"] == 1).sum()) if not users_df.empty and "is_active" in users_df.columns else len(users_df)
    peak_growth = prepared_alerts["growth_rate"].max() if not prepared_alerts.empty else 0.0

    render_kpi_cards(
        [
            {
                "label": "Base systeme",
                "value": f"{db_size_kb:,.0f} Ko",
                "delta": "Empreinte locale",
                "copy": "Lecture instantanee de la taille actuelle du socle SQLite utilise en exploitation.",
                "accent": "#0a5fab",
                "accent_soft": "#49acef",
                "pill": "rgba(10,95,171,.12)",
            },
            {
                "label": "Comptes actifs",
                "value": f"{active_users}",
                "delta": "Reseau disponible",
                "copy": "Presence immediate des operateurs et administrateurs capables d'agir dans la plateforme.",
                "accent": "#059669",
                "accent_soft": "#34d399",
                "pill": "rgba(5,150,105,.12)",
            },
            {
                "label": "Alertes recentes",
                "value": f"{len(alerts_df)}",
                "delta": f"Pic {peak_growth:.1f}%",
                "copy": "Le centre retient la densite d'alertes et la pointe de croissance la plus haute sur la fenetre recente.",
                "accent": "#d97706",
                "accent_soft": "#fcd116",
                "pill": "rgba(217,119,6,.12)",
            },
            {
                "label": "Production recente",
                "value": f"{len(entries_df)}",
                "delta": "Fenetre 200 lignes",
                "copy": "Le volume de saisies reelles permet de sentir le rythme de remontee terrain et admin.",
                "accent": "#7c3aed",
                "accent_soft": "#a78bfa",
                "pill": "rgba(124,58,237,.12)",
            },
            {
                "label": "Notifications admin",
                "value": f"{admin_unread}",
                "delta": "Suivi diffusion",
                "copy": "Les confirmations de diffusion et retours systeme restent a portee depuis le centre de pilotage.",
                "accent": "#ce1126",
                "accent_soft": "#f87171",
                "pill": "rgba(206,17,38,.12)",
            },
        ]
    )

    render_admin_inbox_expander(
        auth,
        user["id"],
        key_prefix="admin_panel_inbox",
        unread_count=admin_unread,
        title="Messagerie admin",
        intro="Les confirmations de diffusion et retours systeme restent accessibles ici sans quitter la salle de controle.",
        limit=6,
    )

    st.markdown(
        f"""
<div class="admin-grid-3">
  <div class="admin-mini-card"><h4>Pression actuelle</h4><p>{'Escalade active' if peak_growth >= 30 else 'Sous tension' if peak_growth >= 10 else 'Sous controle'} avec un pic de croissance mesure a <strong>{peak_growth:.1f}%</strong>.</p></div>
  <div class="admin-highlight"><strong>Socle unifie</strong><span>Cette page reprend le meme langage visuel que le dashboard executif pour eviter toute rupture de lecture.</span></div>
  <div class="admin-mini-card"><h4>Navigation tactique</h4><p>Chaque bloc privilegie une information courte, puis une action directe vers la bonne page admin.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )

    section_label("Supervision temps court")
    main_col, side_col = st.columns([1.25, 0.95], gap="large")
    with main_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_system_pulse_chart(entries_df, alerts_df, users_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Connexions et disponibilite")
        logins_df = _recent_login_table(users_df)
        if logins_df.empty:
            st.info("Aucune connexion recente disponible dans la base.")
        else:
            st.dataframe(logins_df.head(15), use_container_width=True, hide_index=True, height=340)
        st.markdown("</div>", unsafe_allow_html=True)

    with side_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_coverage_chart(users_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Actions rapides")
        _render_action_ribbon()
        st.markdown("</div>", unsafe_allow_html=True)

    section_label("Veille operationnelle")
    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    panel_title("Dernieres alertes pour arbitrage")
    if alerts_df.empty:
        st.info("Aucune alerte disponible dans la base.")
    else:
        view_df = prepared_alerts.copy().sort_values(["year", "week"], ascending=False) if {"year", "week"}.issubset(prepared_alerts.columns) else prepared_alerts.copy()
        if {"year", "week"}.issubset(view_df.columns):
            view_df["Periode"] = view_df["year"].astype(str) + "-S" + view_df["week"].astype(str).str.zfill(2)
        view_df["growth_rate"] = view_df["growth_rate"].map(lambda value: f"{value:.1f}%")
        st.dataframe(
            view_df.rename(
                columns={
                    "disease": "Maladie",
                    "province": "Province",
                    "zone_sante": "Zone",
                    "alert_level": "Niveau",
                    "growth_rate": "Croissance",
                    "current_cases": "Cas actuels",
                    "predicted_cases": "Projection",
                    "message": "Message",
                }
            )[
                [
                    "Maladie",
                    "Province",
                    "Zone",
                    "Periode",
                    "Cas actuels",
                    "Projection",
                    "Croissance",
                    "Niveau",
                    "Message",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=360,
        )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()