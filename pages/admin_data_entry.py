import sqlite3
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

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
)
from utils.auth import AuthSystem, require_auth
from utils.navigation import switch_to_home_page
from src.pdf_generator import BarrierMeasuresPDF


PROVINCES = [
    "Kinshasa", "Kongo Central", "Kwango", "Kwilu", "Mai-Ndombe", "Equateur", "Sud-Ubangi",
    "Nord-Ubangi", "Mongala", "Tshopo", "Bas-Uele", "Haut-Uele", "Ituri", "Nord-Kivu",
    "Sud-Kivu", "Maniema", "Tanganyika", "Haut-Lomami", "Lualaba", "Haut-Katanga",
    "Lomami", "Sankuru", "Kasai", "Kasai Central", "Kasai Oriental",
]

MALADIES = [
    "Paludisme", "Cholera", "Rougeole", "Mpox", "Ebola", "Meningite", "Fievre jaune",
    "Rage", "Typhoide", "Peste", "Trypanosomiase", "Leishmaniose", "Poliomyelite",
    "Coqueluche", "Tetanos", "Hepatite A", "Hepatite B", "Hepatite E", "Diarrhee", "IRA",
    "Malnutrition", "Autre",
]


def _sorted_unique(values) -> List[str]:
    cleaned = {
        str(value).strip()
        for value in values
        if pd.notna(value) and str(value).strip() and str(value).strip().lower() != "nan"
    }
    return sorted(cleaned, key=lambda item: item.casefold())


@st.cache_data(show_spinner=False)
def _reference_catalog() -> pd.DataFrame:
    reference_df = aggregated_csv_frame().copy()
    if reference_df.empty:
        return pd.DataFrame(columns=["MALADIE", "PROVINCE", "ZONE_SANTE"])

    rename_map = {}
    for column in reference_df.columns:
        normalized = column.strip().upper()
        if normalized in {"MALADIE", "PROVINCE", "ZONE_SANTE"}:
            rename_map[column] = normalized
    reference_df = reference_df.rename(columns=rename_map)

    for required in ["MALADIE", "PROVINCE", "ZONE_SANTE"]:
        if required not in reference_df.columns:
            reference_df[required] = None

    return reference_df[["MALADIE", "PROVINCE", "ZONE_SANTE"]].drop_duplicates()


def _disease_options(reference_df: pd.DataFrame, entries_df: pd.DataFrame) -> List[str]:
    sources = list(MALADIES)
    if "MALADIE" in reference_df.columns:
        sources.extend(reference_df["MALADIE"].tolist())
    if not entries_df.empty and "disease" in entries_df.columns:
        sources.extend(entries_df["disease"].tolist())
    return _sorted_unique(sources)


def _province_options(reference_df: pd.DataFrame, entries_df: pd.DataFrame) -> List[str]:
    sources = list(PROVINCES)
    if "PROVINCE" in reference_df.columns:
        sources.extend(reference_df["PROVINCE"].tolist())
    if not entries_df.empty and "province" in entries_df.columns:
        sources.extend(entries_df["province"].tolist())
    return _sorted_unique(sources)


def _zone_options(reference_df: pd.DataFrame, entries_df: pd.DataFrame, province: str) -> List[str]:
    sources = []
    if not reference_df.empty and province:
        matches = reference_df.loc[reference_df["PROVINCE"].astype(str).str.casefold() == province.casefold(), "ZONE_SANTE"]
        sources.extend(matches.tolist())
    if not entries_df.empty and province:
        matches = entries_df.loc[entries_df["province"].astype(str).str.casefold() == province.casefold(), "zone_sante"]
        sources.extend(matches.tolist())
    return _sorted_unique(sources)


def _reference_lists(reference_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if reference_df.empty:
        empty_frame = pd.DataFrame()
        return empty_frame, empty_frame, empty_frame

    diseases_df = pd.DataFrame({"Maladie": _sorted_unique(reference_df.get("MALADIE", []))})
    provinces_df = pd.DataFrame({"Province": _sorted_unique(reference_df.get("PROVINCE", []))})
    zones_df = pd.DataFrame({"Zone de sante": _sorted_unique(reference_df.get("ZONE_SANTE", []))})
    return diseases_df, provinces_df, zones_df


def _filtered_zones(reference_df: pd.DataFrame, selected_province: str) -> pd.DataFrame:
    if reference_df.empty:
        return pd.DataFrame(columns=["Zone de sante"])

    filtered_df = reference_df
    if selected_province and selected_province != "Toutes les provinces":
        filtered_df = filtered_df.loc[
            filtered_df["PROVINCE"].astype(str).str.casefold() == selected_province.casefold()
        ]
    return pd.DataFrame({"Zone de sante": _sorted_unique(filtered_df.get("ZONE_SANTE", []))})


def _reference_export_name(prefix: str, selected_province: str, extension: str) -> str:
    suffix = "toutes_provinces" if not selected_province or selected_province == "Toutes les provinces" else _normalize_location(selected_province)
    return f"{prefix}_{suffix}.{extension}"


def _alert_destination_provinces(auth: AuthSystem, province_options: List[str]) -> List[str]:
    authority_provinces = [authority.get("province") for authority in auth.get_all_authorities() if authority.get("province")]
    return _sorted_unique(list(province_options) + authority_provinces)


def _normalize_location(value: str) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in ascii_only.lower() if ch.isalnum())


def _recipient_ids_for_target(auth: AuthSystem, target_mode: str, province: str, target_province: str) -> tuple[List[int], str]:
    authorities = auth.get_all_authorities()

    if target_mode == "Toutes les provinces":
        recipient_ids = [authority["id"] for authority in authorities]
        return recipient_ids, "toutes les provinces"

    destination_label = target_province if target_mode == "Province ciblee" and target_province else province
    normalized_destination = _normalize_location(destination_label)
    recipient_ids = [
        authority["id"]
        for authority in authorities
        if _normalize_location(authority.get("province")) == normalized_destination
    ]
    return recipient_ids, destination_label


def generate_alert(
    auth: AuthSystem,
    disease: str,
    province: str,
    zone: str,
    week: int,
    year: int,
    total_cases: int,
    target_mode: str,
    target_province: str,
):
    conn = sqlite3.connect(str(auth.db_path))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT total_cases, week, year
        FROM epidemiological_data
        WHERE disease=?
          AND province=?
          AND zone_sante=?
          AND (year < ? OR (year = ? AND week < ?))
        ORDER BY year DESC, week DESC
        LIMIT 1
        """,
        (disease, province, zone, year, year, week),
    )
    row = cursor.fetchone()
    prev = int(row[0]) if row else None

    if prev is None:
        growth = 0.0
        level = "NOUVELLE_DONNEE"
        predicted = int(total_cases)
        msg = f"Nouvelle saisie admin enregistree pour {disease} a {zone}, {province}, semaine {week}/{year}."
    else:
        growth = ((total_cases - prev) / prev * 100) if prev > 0 else (100.0 if total_cases > 0 else 0.0)
        if growth > 50:
            level = "CRITIQUE"
        elif growth > 25:
            level = "HAUTE"
        elif growth >= 10:
            level = "MODEREE"
        else:
            level = "INFO"

        predicted = max(int(round(total_cases * (1 + max(growth, 0) / 100))), int(total_cases))
        if growth >= 0:
            msg = f"Saisie admin recensee avec une evolution de {growth:.1f}% par rapport a la periode precedente."
        else:
            msg = f"Saisie admin recensee avec un recul de {abs(growth):.1f}% par rapport a la periode precedente."

    cursor.execute(
        """
        INSERT INTO alerts (disease, province, zone_sante, week, year, current_cases, predicted_cases, growth_rate, alert_level, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (disease, province, zone, week, year, total_cases, predicted, growth, level, msg),
    )
    alert_id = cursor.lastrowid

    recipient_ids, destination_label = _recipient_ids_for_target(auth, target_mode, province, target_province)

    notification_message = f"{msg} Diffusion vers: {destination_label}. Observation source: {province} / {zone}."
    for uid in recipient_ids:
        cursor.execute(
            "INSERT INTO notifications (user_id, alert_id, title, message) VALUES (?, ?, ?, ?)",
            (uid, alert_id, f"ALERTE {level} - {disease}", notification_message),
        )
    conn.commit()
    conn.close()
    return level, growth, len(recipient_ids), destination_label


def _entry_mix_chart(entries_df: pd.DataFrame) -> go.Figure:
    chart_df = entries_df.copy()
    if chart_df.empty:
        chart_df = pd.DataFrame({"disease": ["Aucune donnee"], "total_cases": [0]})
    else:
        chart_df = chart_df.groupby("disease", as_index=False)["total_cases"].sum().sort_values("total_cases", ascending=False).head(8)
    fig = go.Figure(go.Bar(x=chart_df["disease"], y=chart_df["total_cases"], marker_color="#0a5fab"))
    return make_plotly_layout(fig, "Maladies les plus saisies")


def _province_chart(entries_df: pd.DataFrame) -> go.Figure:
    province_df = entries_df.copy()
    if province_df.empty:
        province_df = pd.DataFrame({"province": ["Aucune donnee"], "total_cases": [0]})
    else:
        province_df = province_df.groupby("province", as_index=False)["total_cases"].sum().sort_values("total_cases", ascending=True).tail(8)
    fig = go.Figure(go.Bar(x=province_df["total_cases"], y=province_df["province"], orientation="h", marker_color="#49acef"))
    return make_plotly_layout(fig, "Charge recente par province")


def main() -> None:
    st.set_page_config(page_title="Saisie Donnees - SAFE CONGO", page_icon=None, layout="wide")
    apply_admin_theme()

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        return

    render_admin_sidebar(user, active_item=2)
    render_admin_hero(
        "Saisie & intelligence epidemiologique",
        "Un espace de production admin qui combine formulaire, verification, recentrage territorial et declenchement intelligent des alertes.",
        ["Saisie haute confiance", "Alertes automatiques", "Traite prioritaire"],
    )

    entries_df = recent_entries_frame(auth.db_path)
    alerts_df = alerts_frame(auth.db_path)
    reference_df = _reference_catalog()
    disease_options = _disease_options(reference_df, entries_df)
    province_options = _province_options(reference_df, entries_df)
    destination_options = _alert_destination_provinces(auth, province_options)
    latest_week = f"S{datetime.now().isocalendar()[1]}-{datetime.now().year}"
    render_kpi_cards(
        [
            {"label": "Saisies recentes", "value": str(len(entries_df)), "delta": "Fenetre de 200 lignes", "copy": "La page garde une vision immediate des entrees les plus fraiches pour detecter les anomalies de cadence.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.1)"},
            {"label": "Alertes emises", "value": str(len(alerts_df)), "delta": "Signal compare au precedent", "copy": "Toute hausse significative est transformee en notification exploitable pour les autorites concernees.", "accent": "#d97706", "accent_soft": "#f9c74f", "pill": "rgba(217,119,6,.12)"},
            {"label": "Semaine active", "value": latest_week, "delta": "Cadence courante", "copy": "Le repere hebdomadaire cadre la saisie et structure l'analyse longitudinale par territoire.", "accent": "#059669", "accent_soft": "#34d399", "pill": "rgba(5,150,105,.12)"},
            {"label": "Provinces touchees", "value": str(entries_df["province"].nunique()) if not entries_df.empty else "0", "delta": "Couverture territoriale", "copy": "Le nombre de provinces remontees mesure la largeur de la capture sur la fenetre recente.", "accent": "#7c3aed", "accent_soft": "#a78bfa", "pill": "rgba(124,58,237,.12)"},
        ]
    )

    diseases_reference_df, provinces_reference_df, _ = _reference_lists(reference_df)
    reference_filter_options = ["Toutes les provinces"] + provinces_reference_df["Province"].tolist() if not provinces_reference_df.empty else ["Toutes les provinces"]
    tab_form, tab_intel, tab_reference = st.tabs(["Nouvelle saisie", "Lecture recente", "Referentiel dataset"])

    with tab_form:
        left_col, right_col = st.columns([1.15, 0.85], gap="large")
        with left_col:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Formulaire admin prioritaire")
            with st.form("admin_entry_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    disease = st.selectbox("Maladie", disease_options, accept_new_options=True)
                    province = st.selectbox("Province", province_options, accept_new_options=True)
                    zone = st.selectbox(
                        "Zone de sante",
                        _zone_options(reference_df, entries_df, province) or [""],
                        index=None,
                        placeholder="Choisir ou saisir une zone",
                        accept_new_options=True,
                    )
                with c2:
                    week = st.number_input("Semaine", min_value=1, max_value=53, value=datetime.now().isocalendar()[1])
                    year = st.number_input("Annee", min_value=2020, max_value=2035, value=datetime.now().year)
                    cases = st.number_input("Cas", min_value=0, value=0)
                    deaths = st.number_input("Deces", min_value=0, value=0)
                target_mode = st.radio("Diffuser l'alerte vers", ["Province de la saisie", "Province ciblee", "Toutes les provinces"], horizontal=True)
                target_province = ""
                if target_mode == "Province ciblee":
                    target_province = st.selectbox("Province destinataire", destination_options, index=0 if destination_options else None, placeholder="Choisir la province qui recevra l'alerte")
                submitted = st.form_submit_button("Enregistrer la saisie", use_container_width=True)

            st.caption("Les suggestions de maladie, province et zone de sante sont alimentees par le dataset et les saisies deja en base.")

            if submitted:
                zone_value = (zone or "").strip()
                if not disease or not province or not zone_value:
                    st.warning("Renseignez la maladie, la province et la zone de sante.")
                elif target_mode == "Province ciblee" and not target_province:
                    st.warning("Choisissez la province destinataire de l'alerte.")
                else:
                    try:
                        conn = sqlite3.connect(str(auth.db_path))
                        cursor = conn.cursor()
                        letalite = (deaths / cases * 100) if cases else 0
                        cursor.execute(
                            """
                            INSERT INTO epidemiological_data
                            (disease, week, year, province, zone_sante, total_cases, total_deaths, incidence_rate, mortality_rate, entered_by)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (disease, week, year, province, zone_value, cases, deaths, cases / 100000 if cases else 0, letalite, user["id"]),
                        )
                        conn.commit()
                        conn.close()
                        st.success("Saisie admin enregistree avec succes.")
                        alert_result = generate_alert(auth, disease, province, zone_value, int(week), int(year), int(cases), target_mode, target_province)
                        if alert_result:
                            level, growth, recipient_count, destination_label = alert_result
                            if recipient_count == 0:
                                st.error(f"Alerte {level} creee, mais aucune autorite sanitaire active ne correspond a la destination {destination_label}. Activez un compte autorite ou choisissez une autre destination.")
                            else:
                                st.warning(f"Alerte {level} declenchee automatiquement avec une croissance de {growth:.1f}% et diffusee a {recipient_count} autorite(s) vers {destination_label}.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Impossible d'enregistrer la saisie : {exc}")
            st.markdown("</div>", unsafe_allow_html=True)

        with right_col:
            st.markdown(
                """
<div class="admin-panel">
  <div class="admin-panel-title">Cadre de verification</div>
  <div class="admin-grid-3">
    <div class="admin-mini-card"><h4>Signal propre</h4><p>Verifier la coherence entre cas, deces et territoire avant validation pour proteger la fiabilite du tableau national.</p></div>
        <div class="admin-mini-card"><h4>Diffusion ciblee</h4><p>L'admin choisit desormais si l'alerte doit partir a la province observee, a une autre province precise ou a toutes les autorites actives.</p></div>
    <div class="admin-mini-card"><h4>Trace immediate</h4><p>La nouvelle ligne rejoint instantanement les vues de lecture recente et les indicateurs du dashboard executif.</p></div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    with tab_intel:
        section_label("Lecture de production")
        chart_left, chart_right = st.columns(2, gap="large")
        with chart_left:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Maladies les plus saisies")
            st.plotly_chart(_entry_mix_chart(entries_df), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with chart_right:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Territoires les plus charges")
            st.plotly_chart(_province_chart(entries_df), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Journal recent de production")
        if entries_df.empty:
            st.info("Aucune saisie recente disponible.")
        else:
            view_df = entries_df.rename(
                columns={
                    "disease": "Maladie",
                    "province": "Province",
                    "zone_sante": "Zone",
                    "week": "Semaine",
                    "year": "Annee",
                    "total_cases": "Cas",
                    "total_deaths": "Deces",
                    "entry_date": "Horodatage",
                }
            )
            st.dataframe(view_df.head(30), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_reference:
        section_label("Catalogue dataset")
        selected_reference_province = st.selectbox("Filtrer les zones de sante par province", reference_filter_options, index=0)
        filtered_zones_df = _filtered_zones(reference_df, selected_reference_province)
        export_pdf = BarrierMeasuresPDF().generate_reference_catalog_pdf(
            diseases_reference_df["Maladie"].tolist() if not diseases_reference_df.empty else [],
            provinces_reference_df["Province"].tolist() if not provinces_reference_df.empty else [],
            filtered_zones_df["Zone de sante"].tolist() if not filtered_zones_df.empty else [],
            None if selected_reference_province == "Toutes les provinces" else selected_reference_province,
        )
        export_csv = pd.concat(
            [
                diseases_reference_df.assign(Categorie="Maladie", Valeur=diseases_reference_df.get("Maladie")),
                provinces_reference_df.assign(Categorie="Province", Valeur=provinces_reference_df.get("Province")),
                filtered_zones_df.assign(Categorie="Zone de sante", Valeur=filtered_zones_df.get("Zone de sante")),
            ],
            ignore_index=True,
        )[["Categorie", "Valeur"]]
        st.markdown(
            f"""
<div class="admin-panel">
  <div class="admin-support-copy">Ce referentiel liste toutes les valeurs uniques detectees dans le dataset detaille utilise pour alimenter la saisie: <strong>{len(diseases_reference_df)}</strong> maladies, <strong>{len(provinces_reference_df)}</strong> provinces et <strong>{len(filtered_zones_df)}</strong> zones de sante pour le filtre courant.</div>
</div>
""",
            unsafe_allow_html=True,
        )

        export_col1, export_col2 = st.columns(2)
        with export_col1:
            st.download_button(
                "Exporter le referentiel en PDF",
                data=export_pdf,
                file_name=_reference_export_name("referentiel_safe_congo", selected_reference_province, "pdf"),
                mime="application/pdf",
                use_container_width=True,
            )
        with export_col2:
            st.download_button(
                "Exporter le referentiel en CSV",
                data=export_csv.to_csv(index=False).encode("utf-8"),
                file_name=_reference_export_name("referentiel_safe_congo", selected_reference_province, "csv"),
                mime="text/csv",
                use_container_width=True,
            )

        ref_col1, ref_col2, ref_col3 = st.columns(3, gap="large")
        with ref_col1:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Toutes les maladies")
            if diseases_reference_df.empty:
                st.info("Aucune maladie detectee dans le dataset.")
            else:
                st.dataframe(diseases_reference_df, use_container_width=True, hide_index=True, height=520)
            st.markdown("</div>", unsafe_allow_html=True)

        with ref_col2:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Toutes les provinces")
            if provinces_reference_df.empty:
                st.info("Aucune province detectee dans le dataset.")
            else:
                st.dataframe(provinces_reference_df, use_container_width=True, hide_index=True, height=520)
            st.markdown("</div>", unsafe_allow_html=True)

        with ref_col3:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Toutes les zones de sante")
            if filtered_zones_df.empty:
                st.info("Aucune zone de sante detectee dans le dataset.")
            else:
                st.dataframe(filtered_zones_df, use_container_width=True, hide_index=True, height=520)
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
