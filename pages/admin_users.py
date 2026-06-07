import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.admin_ui import (
    admin_notifications_snapshot,
    apply_admin_theme,
    make_plotly_layout,
    panel_title,
    reference_catalog_frame,
    render_admin_hero,
    render_admin_sidebar,
    render_kpi_cards,
    section_label,
    users_frame,
)
from utils.auth import AuthSystem, require_auth
from utils.chart_helpers import empty_state_figure
from utils.navigation import switch_to_home_page


def _sorted_unique(values) -> list[str]:
    cleaned = {
        str(value).strip()
        for value in values
        if pd.notna(value) and str(value).strip() and str(value).strip().lower() != "nan"
    }
    return sorted(cleaned, key=lambda item: item.casefold())


def _province_options(reference_df: pd.DataFrame, users_df: pd.DataFrame) -> list[str]:
    sources = []
    if not reference_df.empty and "PROVINCE" in reference_df.columns:
        sources.extend(reference_df["PROVINCE"].tolist())
    if not users_df.empty and "province" in users_df.columns:
        sources.extend(users_df["province"].tolist())
    return _sorted_unique(sources)


def _zone_options(reference_df: pd.DataFrame, users_df: pd.DataFrame, province: str) -> list[str]:
    sources = []
    if province and not reference_df.empty and {"PROVINCE", "ZONE_SANTE"}.issubset(reference_df.columns):
        sources.extend(
            reference_df.loc[
                reference_df["PROVINCE"].astype(str).str.casefold() == province.casefold(),
                "ZONE_SANTE",
            ].tolist()
        )
    if province and not users_df.empty and {"province", "zone_sante"}.issubset(users_df.columns):
        sources.extend(
            users_df.loc[
                users_df["province"].astype(str).str.casefold() == province.casefold(),
                "zone_sante",
            ].tolist()
        )
    return _sorted_unique(sources)


def _role_chart(users_df: pd.DataFrame) -> go.Figure:
    if users_df.empty or "role" not in users_df.columns:
        return empty_state_figure("Structure des roles", "Aucun portefeuille de roles disponible.", make_plotly_layout)
    role_df = users_df.groupby("role", as_index=False).size().rename(columns={"size": "count"})
    fig = go.Figure(
        go.Pie(
            labels=role_df["role"],
            values=role_df["count"],
            hole=0.68,
            marker=dict(colors=["#0a5fab", "#34d399", "#a78bfa", "#fcd116"]),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Comptes: %{value}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Structure des roles")


def _province_chart(users_df: pd.DataFrame) -> go.Figure:
    if users_df.empty or "province" not in users_df.columns:
        return empty_state_figure("Couverture provinciale", "Aucune couverture territoriale disponible.", make_plotly_layout)
    chart_df = (
        users_df.loc[users_df["role"] == "autorite_sanitaire"]
        .groupby("province", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=True)
        .tail(10)
    )
    if chart_df.empty:
        return empty_state_figure("Couverture provinciale", "Aucune autorite sanitaire active a afficher.", make_plotly_layout)
    fig = go.Figure(
        go.Bar(
            x=chart_df["count"],
            y=chart_df["province"],
            orientation="h",
            marker=dict(color=chart_df["count"], colorscale=[[0, "#dbeafe"], [0.5, "#49acef"], [1, "#0a5fab"]]),
            text=chart_df["count"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Comptes: %{x}<extra></extra>",
        )
    )
    return make_plotly_layout(fig, "Couverture provinciale")


def _status_chart(users_df: pd.DataFrame) -> go.Figure:
    if users_df.empty or "is_active" not in users_df.columns:
        return empty_state_figure("Etat des comptes", "Aucun statut de compte consolide.", make_plotly_layout)
    chart_df = (
        users_df.assign(statut=users_df["is_active"].map({1: "Actif", 0: "Inactif"}).fillna("Inconnu"))
        .groupby(["role", "statut"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    fig = go.Figure()
    for statut, color in [("Actif", "#059669"), ("Inactif", "#ce1126"), ("Inconnu", "#94a3b8")]:
        subset = chart_df.loc[chart_df["statut"] == statut]
        if subset.empty:
            continue
        fig.add_trace(
            go.Bar(
                x=subset["role"],
                y=subset["count"],
                name=statut,
                marker_color=color,
                hovertemplate="<b>%{x}</b><br>" + statut + ": %{y}<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    return make_plotly_layout(fig, "Etat des comptes")


def _registry_table(users_df: pd.DataFrame) -> pd.DataFrame:
    if users_df.empty:
        return pd.DataFrame()
    table_df = users_df.copy()
    table_df["Nom complet"] = table_df["nom"].fillna("") + " " + table_df["prenom"].fillna("")
    table_df["Statut"] = table_df["is_active"].map({1: "Actif", 0: "Inactif"}).fillna("Inactif")
    return table_df.rename(
        columns={
            "username": "Identifiant",
            "role": "Role",
            "province": "Province",
            "zone_sante": "Zone de sante",
            "created_at": "Cree le",
            "last_login": "Derniere connexion",
        }
    )[
        [
            "Nom complet",
            "Identifiant",
            "Role",
            "Province",
            "Zone de sante",
            "Statut",
            "Cree le",
            "Derniere connexion",
        ]
    ]


def main() -> None:
    st.set_page_config(page_title="Utilisateurs | SAFE CONGO", layout="wide")
    apply_admin_theme()
    st.markdown(
        """
<style>
    @media (max-width: 1180px) {
        div[data-testid="stHorizontalBlock"] { gap: .85rem !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        [data-testid="stTabs"] [role="tablist"] { flex-wrap: wrap; gap: .45rem; }
    }
    @media (max-width: 760px) {
        .admin-form-banner, .admin-highlight, .admin-mini-card { padding: .95rem !important; }
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

    render_admin_sidebar(user, active_item=3, show_logo=False)
    _, admin_unread = admin_notifications_snapshot(auth, user["id"])
    render_admin_hero(
        title="Gouvernance des utilisateurs",
        subtitle="Une lecture claire du maillage institutionnel, des comptes actifs et des operations d'ouverture ou de remise en service des acces terrain.",
        chips=["Activation guidee", "Cycle de vie des comptes", "Couverture territoriale"],
        eyebrow="Utilisateurs",
        notification_count=admin_unread,
        auth=auth,
        user_id=user["id"],
        inbox_key_prefix="admin_users_inbox",
        inbox_limit=8,
    )

    users_df = users_frame(auth)
    reference_df = reference_catalog_frame()
    province_choices = _province_options(reference_df, users_df)
    active_count = int((users_df["is_active"] == 1).sum()) if not users_df.empty and "is_active" in users_df.columns else len(users_df)
    inactive_count = int((users_df["is_active"] == 0).sum()) if not users_df.empty and "is_active" in users_df.columns else 0
    authority_count = int((users_df["role"] == "autorite_sanitaire").sum()) if not users_df.empty and "role" in users_df.columns else 0
    covered_provinces = users_df["province"].dropna().nunique() if not users_df.empty and "province" in users_df.columns else 0

    render_kpi_cards(
        [
            {
                "label": "Comptes actifs",
                "value": f"{active_count}",
                "delta": "Capacite immediate",
                "copy": "Nombre de comptes actuellement capables d'agir dans la plateforme sans reactivation prealable.",
                "accent": "#0a5fab",
                "accent_soft": "#49acef",
                "pill": "rgba(10,95,171,.12)",
            },
            {
                "label": "Autorites terrain",
                "value": f"{authority_count}",
                "delta": "Maillage sanitaire",
                "copy": "Le coeur du reseau territorial reste mesure via les autorites sanitaires effectivement provisionnees.",
                "accent": "#059669",
                "accent_soft": "#34d399",
                "pill": "rgba(5,150,105,.12)",
            },
            {
                "label": "Comptes inactifs",
                "value": f"{inactive_count}",
                "delta": "A remettre en service",
                "copy": "Lecture rapide des comptes suspendus qui peuvent freiner une montee en charge regionale.",
                "accent": "#ce1126",
                "accent_soft": "#f87171",
                "pill": "rgba(206,17,38,.12)",
            },
            {
                "label": "Provinces couvertes",
                "value": f"{covered_provinces}",
                "delta": "Presence institutionnelle",
                "copy": "Empreinte territoriale totale visible a partir des comptes actuellement connus dans la base.",
                "accent": "#d97706",
                "accent_soft": "#fcd116",
                "pill": "rgba(217,119,6,.12)",
            },
        ]
    )

    st.markdown(
        """
<div class="admin-grid-3">
  <div class="admin-mini-card"><h4>Lecture simple</h4><p>Les graphiques absorbent leurs titres et la page ne repete plus les memes libelles avant chaque visuel.</p></div>
  <div class="admin-highlight"><strong>Flux honnete</strong><span>La creation rapide provisionne des autorites sanitaires, et la reactivation est maintenant reelle cote backend.</span></div>
  <div class="admin-mini-card"><h4>Decision rapide</h4><p>En un coup d'oeil, vous voyez les roles, les provinces couvertes et les comptes a remettre en service.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )

    section_label("Cartographie institutionnelle")
    top_left, top_right = st.columns([1.05, 0.95], gap="large")
    with top_left:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_role_chart(users_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_status_chart(users_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with top_right:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        st.plotly_chart(_province_chart(users_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    panel_title("Registre des comptes")
    registry_df = _registry_table(users_df)
    if registry_df.empty:
        st.markdown('<div class="admin-empty-state">Aucun utilisateur enregistre.</div>', unsafe_allow_html=True)
    else:
        st.dataframe(registry_df.head(40), use_container_width=True, hide_index=True, height=360)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    panel_title("Operations de gouvernance")
    tab1, tab2, tab3 = st.tabs(["Provisionner", "Suspendre", "Reactiver"])

    with tab1:
        st.markdown(
            """
<div class="admin-form-banner">
  <strong>Provisionnement guide</strong>
  <span>Ce flux rapide cree soit un administrateur, soit une autorite sanitaire, selon le besoin de gouvernance et de terrain.</span>
</div>
""",
            unsafe_allow_html=True,
        )
        create_admin_tab, create_authority_tab = st.tabs(["Creer un admin", "Creer une autorite sanitaire"])

        with create_admin_tab:
            st.markdown('<div class="admin-highlight" style="margin-bottom:12px"><strong>Compte administrateur</strong><span>Acces central a la gouvernance, au pilotage et aux operations systeme. Le rattachement province / zone est aussi renseigne ici et la liste des zones suit directement la province choisie.</span></div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                admin_username = st.text_input("Identifiant admin", key="create_admin_username")
                admin_nom = st.text_input("Nom", key="create_admin_nom")
                admin_prenom = st.text_input("Prenom", key="create_admin_prenom")
                admin_province = st.selectbox("Province", [""] + province_choices, index=0, key="create_admin_province")
            with col2:
                admin_email = st.text_input("Email", key="create_admin_email")
                admin_password = st.text_input("Mot de passe initial", type="password", key="create_admin_password")
                admin_telephone = st.text_input("Telephone", key="create_admin_telephone")
                admin_zone = st.selectbox(
                    "Zone de sante",
                    [""] + _zone_options(reference_df, users_df, admin_province),
                    index=0,
                    key=f"create_admin_zone_{admin_province or 'none'}",
                )
            submitted_admin = st.button("Creer l'administrateur", use_container_width=True, key="create_admin_submit")
            if submitted_admin:
                if not all([admin_username, admin_nom, admin_prenom, admin_email, admin_password, admin_province, admin_zone]):
                    st.error("Tous les champs sont obligatoires pour creer un administrateur.")
                else:
                    ok, message = auth.register_user(
                        admin_username,
                        admin_password,
                        admin_nom,
                        admin_prenom,
                        admin_email,
                        admin_telephone,
                        "admin",
                        admin_province,
                        admin_zone,
                    )
                    if ok:
                        st.success("Administrateur cree avec succes.")
                        st.rerun()
                    else:
                        st.error(message)

        with create_authority_tab:
            st.markdown('<div class="admin-highlight" style="margin-bottom:12px"><strong>Autorite sanitaire</strong><span>Compte terrain rattache a une province et une zone de sante pour recevoir et traiter les alertes ciblees. La liste des zones se recharge automatiquement selon la province choisie.</span></div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                authority_username = st.text_input("Identifiant autorite", key="create_authority_username")
                authority_nom = st.text_input("Nom", key="create_authority_nom")
                authority_prenom = st.text_input("Prenom", key="create_authority_prenom")
                authority_email = st.text_input("Email", key="create_authority_email")
            with col2:
                authority_password = st.text_input("Mot de passe initial", type="password", key="create_authority_password")
                authority_telephone = st.text_input("Telephone", key="create_authority_telephone")
                authority_province = st.selectbox("Province", [""] + province_choices, index=0, key="create_authority_province")
                authority_zone = st.selectbox(
                    "Zone de sante",
                    [""] + _zone_options(reference_df, users_df, authority_province),
                    index=0,
                    key=f"create_authority_zone_{authority_province or 'none'}",
                )
            submitted_authority = st.button("Creer l'autorite sanitaire", use_container_width=True, key="create_authority_submit")
            if submitted_authority:
                if not all([authority_username, authority_nom, authority_prenom, authority_email, authority_password, authority_province, authority_zone]):
                    st.error("Tous les champs sont obligatoires pour creer une autorite sanitaire.")
                else:
                    ok, message = auth.register_user(
                        authority_username,
                        authority_password,
                        authority_nom,
                        authority_prenom,
                        authority_email,
                        authority_telephone,
                        "autorite_sanitaire",
                        authority_province,
                        authority_zone,
                    )
                    if ok:
                        st.success("Autorite sanitaire creee avec succes.")
                        st.rerun()
                    else:
                        st.error(message)

    with tab2:
        actifs = users_df[(users_df.get("is_active", 1) == 1) & (users_df["username"] != "admin")].copy() if not users_df.empty else pd.DataFrame()
        if actifs.empty:
            st.markdown('<div class="admin-empty-state">Aucun utilisateur actif a suspendre.</div>', unsafe_allow_html=True)
        else:
            actifs["Libelle"] = actifs["nom"].fillna("") + " " + actifs["prenom"].fillna("") + " (" + actifs["username"] + ")"
            with st.form("disable_user_form"):
                selection = st.selectbox("Compte a suspendre", actifs["Libelle"], index=None)
                disable_submit = st.form_submit_button("Suspendre ce compte", use_container_width=True)
            if disable_submit and selection:
                selected_row = actifs.loc[actifs["Libelle"] == selection].iloc[0]
                st.markdown(
                    f"""
<div class="admin-highlight">
  <strong>{selected_row['nom']} {selected_row['prenom']}</strong>
  <span>Province: {selected_row['province']} | Zone: {selected_row['zone_sante']} | Role: {selected_row['role']}</span>
</div>
""",
                    unsafe_allow_html=True,
                )
                ok, message = auth.delete_user(int(selected_row["id"]))
                if ok:
                    st.success("Utilisateur suspendu.")
                    st.rerun()
                else:
                    st.error(message)
            elif disable_submit:
                st.warning("Choisissez d'abord un compte a suspendre.")

    with tab3:
        inactifs = users_df[(users_df.get("is_active", 1) == 0) & (users_df["username"] != "admin")].copy() if not users_df.empty else pd.DataFrame()
        if inactifs.empty:
            st.markdown('<div class="admin-empty-state">Aucun utilisateur inactif a reactiver.</div>', unsafe_allow_html=True)
        else:
            inactifs["Libelle"] = inactifs["nom"].fillna("") + " " + inactifs["prenom"].fillna("") + " (" + inactifs["username"] + ")"
            with st.form("reactivate_user_form"):
                selection = st.selectbox("Compte a reactiver", inactifs["Libelle"], index=None)
                reactivate_submit = st.form_submit_button("Reactiver ce compte", use_container_width=True)
            if reactivate_submit and selection:
                selected_row = inactifs.loc[inactifs["Libelle"] == selection].iloc[0]
                st.markdown(
                    f"""
<div class="admin-highlight">
  <strong>Remise en service prete</strong>
  <span>{selected_row['nom']} {selected_row['prenom']} sera remis en circulation pour {selected_row['province']} / {selected_row['zone_sante']}.</span>
</div>
""",
                    unsafe_allow_html=True,
                )
                ok, message = auth.reactivate_user(int(selected_row["id"]))
                if ok:
                    st.success("Utilisateur reactive.")
                    st.rerun()
                else:
                    st.error(message)
            elif reactivate_submit:
                st.warning("Choisissez d'abord un compte a reactiver.")
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()