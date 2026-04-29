import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.admin_ui import (
    apply_admin_theme,
    make_plotly_layout,
    panel_title,
    render_admin_hero,
    render_admin_sidebar,
    render_kpi_cards,
    users_frame,
)
from utils.auth import AuthSystem, require_auth
from utils.navigation import switch_to_home_page


PROVINCES = [
    "Kinshasa", "Kongo Central", "Kwango", "Kwilu", "Mai-Ndombe", "Equateur", "Sud-Ubangi",
    "Nord-Ubangi", "Mongala", "Tshopo", "Bas-Uele", "Haut-Uele", "Ituri", "Nord-Kivu",
    "Sud-Kivu", "Maniema", "Tanganyika", "Haut-Lomami", "Lualaba", "Haut-Katanga",
    "Lomami", "Sankuru", "Kasai", "Kasai Central", "Kasai Oriental",
]


def _role_chart(users_df: pd.DataFrame) -> go.Figure:
    if users_df.empty:
        users_df = pd.DataFrame({"role": ["aucun"], "count": [0]})
    else:
        users_df = users_df.groupby("role", as_index=False).size().rename(columns={"size": "count"})
    fig = go.Figure(go.Pie(labels=users_df["role"], values=users_df["count"], hole=0.58, marker=dict(colors=["#0a5fab", "#49acef", "#f9c74f", "#a78bfa"])))
    return make_plotly_layout(fig, "Structure des roles")


def _province_chart(users_df: pd.DataFrame) -> go.Figure:
    if users_df.empty or "province" not in users_df:
        chart_df = pd.DataFrame({"province": ["Aucune donnee"], "count": [0]})
    else:
        chart_df = users_df.loc[users_df["role"] == "autorite_sanitaire"].groupby("province", as_index=False).size().rename(columns={"size": "count"}).sort_values("count", ascending=True).tail(10)
    fig = go.Figure(go.Bar(x=chart_df["count"], y=chart_df["province"], orientation="h", marker_color="#1aa2e2"))
    return make_plotly_layout(fig, "Couverture provinciale")


def main() -> None:
    st.set_page_config(page_title="Utilisateurs - SAFE CONGO", page_icon=None, layout="wide")
    apply_admin_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        return

    render_admin_sidebar(user, active_item=3)
    render_admin_hero(
        "Gouvernance des utilisateurs",
        "Une interface admin concue pour suivre la densite institutionnelle, ouvrir des acces propres et maitriser le cycle de vie des comptes terrain.",
        ["Activation guidee", "Couverture territoriale", "Controle d'acces"],
    )

    users_df = users_frame(auth)
    admins = users_df.loc[users_df["role"] == "admin"] if not users_df.empty else pd.DataFrame()
    authorities = users_df.loc[users_df["role"] == "autorite_sanitaire"] if not users_df.empty else pd.DataFrame()
    active_authorities = authorities.loc[authorities["is_active"] == 1] if not authorities.empty else pd.DataFrame()

    render_kpi_cards(
        [
            {"label": "Utilisateurs totaux", "value": str(len(users_df)), "delta": "Population systeme", "copy": "La plateforme suit tous les comptes sans perdre la distinction entre administration centrale et terrain.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.1)"},
            {"label": "Autorites actives", "value": str(len(active_authorities)), "delta": "Presence operationnelle", "copy": "Ce chiffre reflete le reseau capable de recevoir et traiter les alertes en condition reelle.", "accent": "#059669", "accent_soft": "#34d399", "pill": "rgba(5,150,105,.12)"},
            {"label": "Administrateurs", "value": str(len(admins)), "delta": "Gouvernance centrale", "copy": "Les profils admin pilotent les arbitrages de qualite, de creation de compte et de supervision systeme.", "accent": "#d97706", "accent_soft": "#f9c74f", "pill": "rgba(217,119,6,.12)"},
            {"label": "Provinces couvertes", "value": str(active_authorities["province"].nunique()) if not active_authorities.empty else "0", "delta": "Maillage territorial", "copy": "Le nombre de provinces couvertes aide a distinguer profondeur locale et zones encore a renforcer.", "accent": "#7c3aed", "accent_soft": "#a78bfa", "pill": "rgba(124,58,237,.12)"},
        ]
    )

    chart_col, coverage_col = st.columns(2, gap="large")
    with chart_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Repartition des roles")
        st.plotly_chart(_role_chart(users_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with coverage_col:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Presence provinciale")
        st.plotly_chart(_province_chart(users_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    tab_roster, tab_create, tab_govern = st.tabs(["Registre", "Creer une autorite", "Gouvernance"])

    with tab_roster:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Registre des comptes")
        if users_df.empty:
            st.info("Aucun utilisateur enregistre.")
        else:
            roster = users_df.copy()
            roster["Nom complet"] = roster["nom"].fillna("") + " " + roster["prenom"].fillna("")
            roster["Statut"] = roster["is_active"].map({1: "Actif", 0: "Desactive"})
            display_df = roster[["Nom complet", "username", "role", "province", "zone_sante", "email", "last_login", "Statut"]].rename(columns={"username": "Identifiant", "role": "Role", "province": "Province", "zone_sante": "Zone", "email": "Email", "last_login": "Derniere connexion"})
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_create:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Creation guidee d'une autorite sanitaire")
        with st.form("create_authority_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Identifiant")
                nom = st.text_input("Nom")
                prenom = st.text_input("Prenom")
                email = st.text_input("Email")
            with col2:
                password = st.text_input("Mot de passe initial", type="password")
                telephone = st.text_input("Telephone")
                province = st.selectbox("Province", PROVINCES)
                zone = st.text_input("Zone de sante")
            submitted = st.form_submit_button("Creer l'autorite", use_container_width=True)

        if submitted:
            ok, message = auth.register_authority(username, password, nom, prenom, email, telephone, province, zone)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_govern:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Cycle de vie des comptes")
        active_non_admin = []
        if not users_df.empty:
            active_non_admin = users_df.loc[(users_df["username"] != "admin") & (users_df["is_active"] == 1), ["id", "username", "nom", "prenom"]].to_dict("records")
        if active_non_admin:
            labels = [f"{record['username']} - {record['nom']} {record['prenom']}" for record in active_non_admin]
            selected_label = st.selectbox("Compte a desactiver", labels)
            if st.button("Desactiver le compte", use_container_width=True):
                selected_record = active_non_admin[labels.index(selected_label)]
                ok, message = auth.delete_user(selected_record["id"])
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("Aucun compte actif supplementaire a desactiver.")

        st.markdown(
            """
<div class="admin-grid-3">
  <div class="admin-mini-card"><h4>Activation guidee</h4><p>Chaque nouveau compte doit etre rattache a une province et une zone pour garantir un routage d'alerte pertinent.</p></div>
  <div class="admin-mini-card"><h4>Desactivation propre</h4><p>La suppression logique preserve l'historique et empeche la perte de contexte sur les traces de connexion et de notification.</p></div>
  <div class="admin-mini-card"><h4>Lecture institutionnelle</h4><p>Le mix des profils aide a detecter les trous de couverture ou les surcharges admin par rapport au terrain.</p></div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
