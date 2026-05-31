import pandas as pd
import joblib
import numpy as np
import streamlit as st
import unicodedata
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

from utils.admin_ui import (
    apply_admin_theme,
    alerts_frame,
    make_plotly_layout,
    panel_title,
    recent_entries_frame,
    reference_catalog_frame,
    render_admin_hero,
    render_admin_sidebar,
    render_kpi_cards,
    section_label,
)
from utils.auth import AuthSystem, require_auth
from utils.chart_helpers import empty_state_figure
from utils.navigation import switch_to_home_page
from src.config import MODEL_RESULT_FILTERS
from src.config import TRAINING_CONFIG
from src.alert_system import AlertSystem

# --- CONFIGURATION & PATHS ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_SUMMARY_PATH = ROOT_DIR / "models" / "evaluation" / "model_performance_summary.csv"
MODELS_PATH = ROOT_DIR / "models" / "trained" / "models.pkl"
DEFAULT_FORECAST_DATE = datetime.now().date()
REFERENCE_HISTORY_CANDIDATES = [
    ROOT_DIR / "data" / "processed" / "donnees_agregees_nettoyees.csv",
    ROOT_DIR / "data" / "processed" / "aggregated_data_clean.csv",
]
MIN_ACCEPTABLE_R2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))
MIN_HISTORY_WEEKS = int(TRAINING_CONFIG.get("history_weeks", 4))

# --- HELPERS ---

def _normalize_text(value: str) -> str:
    if not value: return ""
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.casefold().split())


def _province_token(value: str) -> str:
    ascii_only = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in ascii_only.lower() if ch.isalnum())

def _sorted_unique(values) -> list[str]:
    cleaned = {
        str(value).strip()
        for value in values
        if pd.notna(value) and str(value).strip() and str(value).strip().lower() != "nan"
    }
    return sorted(cleaned, key=lambda item: item.casefold())

@st.cache_data(show_spinner=False)
def _global_weighted_r2() -> float:
    if not MODEL_SUMMARY_PATH.exists():
        return 0.0
    try:
        summary_df = pd.read_csv(MODEL_SUMMARY_PATH, encoding="utf-8-sig")
        if "R² (Best)" not in summary_df.columns:
            return 0.0

        r2_values = pd.to_numeric(summary_df["R² (Best)"], errors="coerce")
        if "Total cas" in summary_df.columns:
            weights = pd.to_numeric(summary_df["Total cas"], errors="coerce").fillna(0.0)
        else:
            weights = pd.Series(np.ones(len(summary_df)), index=summary_df.index, dtype=float)

        valid_mask = r2_values.notna() & weights.notna()
        if not valid_mask.any():
            return 0.0

        r2_values = r2_values.loc[valid_mask]
        weights = weights.loc[valid_mask].clip(lower=1.0)
        return float(np.average(r2_values, weights=weights))
    except Exception:
        return 0.0

@st.cache_data(show_spinner=False)
def _available_model_diseases() -> set[str]:
    return {_normalize_text(name) for name in _load_prediction_models().keys()}

def _has_prediction_model(disease: str) -> bool:
    return _normalize_text(disease) in _available_model_diseases()

def _eligible_model_diseases() -> set[str]:
    global_r2 = _global_weighted_r2()
    if global_r2 < MIN_ACCEPTABLE_R2:
        return set()
    return _available_model_diseases()

# Diseases present in the reference CSV but excluded from the form:
# These have no trained model (insufficient historical data in the training set).
_NO_MODEL_DISEASES: frozenset[str] = frozenset({
    "chikungunya",
    "diphterie",
    "dracunculose",
})

@st.cache_data(show_spinner=False)
def _dropped_by_r2() -> set[str]:
    """Return normalized disease names from the model summary with R\u00b2(Best) < MIN_ACCEPTABLE_R2."""
    if not MODEL_SUMMARY_PATH.exists():
        return set()
    try:
        df = pd.read_csv(MODEL_SUMMARY_PATH, encoding="utf-8-sig")
        r2 = pd.to_numeric(df.get("R\u00b2 (Best)", pd.Series(dtype=float)), errors="coerce")
        return {_normalize_text(d) for d in df.loc[r2 < MIN_ACCEPTABLE_R2, "Maladie"].dropna()}
    except Exception:
        return set()

def _excluded_diseases() -> frozenset[str]:
    """Union of no-model diseases and R\u00b2-dropped diseases."""
    return _NO_MODEL_DISEASES | _dropped_by_r2()


def _all_disease_options(reference_df: pd.DataFrame, entries_df: pd.DataFrame) -> list[str]:
    sources = []
    if "MALADIE" in reference_df.columns:
        sources.extend(reference_df["MALADIE"].tolist())
    elif not entries_df.empty and "disease" in entries_df.columns:
        sources.extend(entries_df["disease"].tolist())
    excluded = _excluded_diseases()
    return [d for d in _sorted_unique(sources) if _normalize_text(d) not in excluded]

def _reference_history_count(reference_df: pd.DataFrame, disease: str, province: str = "", zone: str = "") -> int:
    if reference_df.empty or "MALADIE" not in reference_df.columns:
        return 0

    mask = reference_df["MALADIE"].astype(str).map(_normalize_text) == _normalize_text(disease)
    if province and "PROVINCE" in reference_df.columns:
        mask &= reference_df["PROVINCE"].astype(str).map(_normalize_text) == _normalize_text(province)
    if zone and "ZONE_SANTE" in reference_df.columns:
        mask &= reference_df["ZONE_SANTE"].astype(str).map(_normalize_text) == _normalize_text(zone)
    return int(mask.sum())

def _disease_options(reference_df: pd.DataFrame, entries_df: pd.DataFrame) -> list[str]:
    options = _all_disease_options(reference_df, entries_df)
    eligible = _eligible_model_diseases()
    return [d for d in options if _normalize_text(d) in eligible] if eligible else options

def _disease_options_for_scope(reference_df: pd.DataFrame, entries_df: pd.DataFrame, province: str = "", zone: str = "", require_model: bool = False, min_history_weeks: int = 0) -> list[str]:
    options = _all_disease_options(reference_df, entries_df)
    if province and not reference_df.empty:
        d_col = next((c for c in reference_df.columns if _normalize_text(c) in ["maladie", "disease"]), None)
        p_col = next((c for c in reference_df.columns if _normalize_text(c) == "province"), None)
        z_col = next((c for c in reference_df.columns if _normalize_text(c) in ["zone_sante", "zonesante"]), None)
        if d_col and p_col:
            mask = reference_df[p_col].astype(str).map(_normalize_text) == _normalize_text(province)
            if zone and z_col:
                mask &= reference_df[z_col].astype(str).map(_normalize_text) == _normalize_text(zone)
            options = _sorted_unique(reference_df.loc[mask, d_col].tolist())

    if require_model:
        eligible = _eligible_model_diseases()
        options = [d for d in options if _normalize_text(d) in eligible] if eligible else []
    if min_history_weeks > 0:
        options = [
            d for d in options
            if _reference_history_count(reference_df, d, province, zone) >= min_history_weeks
        ]
    return options

def _province_options(reference_df: pd.DataFrame, entries_df: pd.DataFrame) -> list[str]:
    sources = []
    if "PROVINCE" in reference_df.columns: sources.extend(reference_df["PROVINCE"].tolist())
    elif not entries_df.empty and "province" in entries_df.columns: sources.extend(entries_df["province"].tolist())
    return _sorted_unique(sources)

def _zone_options(reference_df: pd.DataFrame, province: str) -> list[str]:
    if not province or reference_df.empty: return []
    norm_p = _normalize_text(province)
    p_col = next((c for c in reference_df.columns if _normalize_text(c) == "province"), None)
    z_col = next((c for c in reference_df.columns if _normalize_text(c) in ["zone_sante", "zonesante"]), None)
    if not p_col or not z_col: return []
    mask = reference_df[p_col].astype(str).map(_normalize_text) == norm_p
    zones = reference_df.loc[mask, z_col].dropna().unique().tolist()
    return sorted([str(z).strip() for z in zones], key=lambda x: x.casefold())

# --- DATA LOADING ---

@st.cache_resource(show_spinner=False)
def _load_prediction_models() -> dict[str, dict]:
    if not MODELS_PATH.exists(): return {}
    try:
        data = joblib.load(MODELS_PATH)
        return data.get("best_models", {})
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def _reference_history_frame() -> pd.DataFrame:
    expected = ["DEBUTSEM", "MALADIE", "PROVINCE", "ZONE_SANTE", "TOTALCAS", "TOTALDECES"]
    for path in REFERENCE_HISTORY_CANDIDATES:
        if not path.exists(): continue
        try:
            df = pd.read_csv(path)
            rename = {c: c.strip().upper() for c in df.columns if c.strip().upper() in expected}
            df = df.rename(columns=rename)
            if all(col in df.columns for col in expected):
                df["DEBUTSEM"] = pd.to_datetime(df["DEBUTSEM"], errors="coerce")
                df["TOTALCAS"] = pd.to_numeric(df["TOTALCAS"], errors="coerce").fillna(0.0)
                df = df.dropna(subset=["DEBUTSEM"])
                return df[expected]
        except Exception: continue
    return pd.DataFrame(columns=expected)

@st.cache_data(show_spinner=False)
def _disease_code_lookup() -> dict[str, int]:
    df = _reference_history_frame()
    if df.empty: return {}
    diseases = sorted({str(v).strip() for v in df["MALADIE"].dropna() if str(v).strip()})
    return {_normalize_text(d): i for i, d in enumerate(diseases)}

# --- PREDICTION LOGIC ---

def _history_series_for_location(auth: AuthSystem, disease: str, province: str = None, zone: str = None) -> pd.DataFrame:
    ref_df = _reference_history_frame()
    norm_d = _normalize_text(disease)
    
    # Filter Reference
    mask = ref_df["MALADIE"].astype(str).map(_normalize_text) == norm_d
    if province and zone:
        mask &= (ref_df["PROVINCE"].astype(str).map(_normalize_text) == _normalize_text(province))
        mask &= (ref_df["ZONE_SANTE"].astype(str).map(_normalize_text) == _normalize_text(zone))
    base_history = ref_df.loc[mask, ["DEBUTSEM", "TOTALCAS"]].copy() if not ref_df.empty else pd.DataFrame(columns=["DEBUTSEM", "TOTALCAS"])

    # Filter Database (Admin entries)
    conn = auth._get_connection()
    try:
        sql = "SELECT week, year, total_cases, total_deaths FROM epidemiological_data WHERE disease = ?"
        params = [disease]
        if province and zone:
            sql += " AND province = ? AND zone_sante = ?"
            params.extend([province, zone])
        admin_raw = pd.read_sql_query(sql, conn, params=params)
    finally: conn.close()

    if not admin_raw.empty:
        iso = admin_raw["year"].astype(int).astype(str) + "-W" + admin_raw["week"].astype(int).astype(str).str.zfill(2) + "-1"
        admin_raw["DEBUTSEM"] = pd.to_datetime(iso, format="%G-W%V-%u", errors="coerce")
        admin_raw["TOTALCAS"] = pd.to_numeric(admin_raw["total_cases"], errors="coerce")
        admin_hist = admin_raw.dropna(subset=["DEBUTSEM", "TOTALCAS"])[["DEBUTSEM", "TOTALCAS"]]
    else: admin_hist = pd.DataFrame(columns=["DEBUTSEM", "TOTALCAS"])

    combined = pd.concat([base_history, admin_hist], ignore_index=True)
    if combined.empty: return combined
    return combined.groupby("DEBUTSEM", as_index=False)["TOTALCAS"].sum().sort_values("DEBUTSEM").reset_index(drop=True)

def predict_cases_for_date(auth: AuthSystem, disease: str, province: str, zone: str, target_date):
    models = _load_prediction_models()
    normalized_d = _normalize_text(disease)
    
    # Resolve Model
    model_key = next((k for k in models.keys() if _normalize_text(k) == normalized_d), None)
    if not model_key: raise ValueError(f"Aucun modèle IA disponible pour {disease}.")
    
    model_info = models[model_key]
    global_r2 = _global_weighted_r2()
    if global_r2 < MIN_ACCEPTABLE_R2:
        raise ValueError(f"Modèle global trop imprécis (R² global={global_r2:.3f}).")

    # Features
    iso_year, week_num, _ = target_date.isocalendar()
    week_start = pd.Timestamp(datetime.fromisocalendar(iso_year, week_num, 1))
    
    location_hist = _history_series_for_location(auth, disease, province, zone)
    history_before_target = location_hist.loc[location_hist["DEBUTSEM"] < week_start].tail(MIN_HISTORY_WEEKS)
    if len(history_before_target) < MIN_HISTORY_WEEKS:
        raise ValueError(f"Historique insuffisant: au moins {MIN_HISTORY_WEEKS} semaines sont requises pour prédire cette zone.")

    recent = history_before_target["TOTALCAS"].tolist()
    lag_1_value, lag_2_value = recent[-1], recent[-2]
    ma_4_value = np.mean(recent)
    
    disease_code = _disease_code_lookup().get(normalized_d, 0)
    feat = pd.DataFrame([{
        "lag_1": lag_1_value, "lag_2": lag_2_value, "lag_3": recent[-3], "lag_4": recent[-4],
        "ma_2": np.mean(recent[-2:]), "ma_3": np.mean(recent[-3:]), "ma_4": ma_4_value,
        "growth_rate": np.clip((lag_1_value - lag_2_value)/lag_2_value if lag_2_value > 0 else 0, -5, 5),
        "week_rank": float(len(location_hist)), "month": float(week_start.month),
        "quarter": float((week_start.month-1)//3 + 1), "MALADIE_CODE": float(disease_code),
        "volatility_4w": np.std(recent), "trend": lag_1_value - ma_4_value,
    }])

    selected = list(model_info.get("features", []))
    for f in selected: 
        if f not in feat.columns: feat[f] = 0.0
    
    predicted = float(model_info["model"].predict(feat[selected])[0])
    if model_info.get("log_transform"):
        predicted = np.expm1(predicted)
    predicted = max(int(round(predicted)), 0)

    return {
        "disease": model_key, "week": week_num, "year": iso_year,
        "previous_cases": int(round(lag_1_value)), "predicted_cases": predicted, "r2": global_r2
    }


def _history_readiness(auth: AuthSystem, disease: str, province: str, zone: str, target_date):
    if not all([disease, province, zone, target_date]):
        return None

    iso_year, week_num, _ = target_date.isocalendar()
    week_start = pd.Timestamp(datetime.fromisocalendar(iso_year, week_num, 1))
    location_hist = _history_series_for_location(auth, disease, province, zone)
    history_before_target = location_hist.loc[location_hist["DEBUTSEM"] < week_start].tail(MIN_HISTORY_WEEKS).copy()
    available_weeks = len(history_before_target)
    weeks_list = [value.strftime("%d/%m/%Y") for value in history_before_target["DEBUTSEM"].tolist()]

    return {
        "target_week": week_num,
        "target_year": iso_year,
        "available_weeks": available_weeks,
        "ready": available_weeks >= MIN_HISTORY_WEEKS,
        "weeks_list": weeks_list,
    }

def _prediction_blocker(auth: AuthSystem, disease: str, province: str, zone: str, target_date):
    if not _has_prediction_model(disease):
        return f"Projection automatique non disponible pour {disease}."

    history_status = _history_readiness(auth, disease, province, zone, target_date)
    if history_status and not history_status["ready"]:
        visible_weeks = ", ".join(history_status["weeks_list"]) if history_status["weeks_list"] else "aucune"
        return (
            f"Historique insuffisant avant S{history_status['target_week']}/{history_status['target_year']} : "
            f"{history_status['available_weeks']} semaine(s) disponible(s) sur {MIN_HISTORY_WEEKS} requises. "
            f"Semaines trouvées : {visible_weeks}."
        )
    return None


def _observed_growth_rate(auth: AuthSystem, disease: str, province: str, zone: str, observed_date, observed_cases: int) -> float:
    if observed_date is None:
        return 0.0

    iso_year, week_num, _ = observed_date.isocalendar()
    week_start = pd.Timestamp(datetime.fromisocalendar(iso_year, week_num, 1))
    location_hist = _history_series_for_location(auth, disease, province, zone)
    previous_points = location_hist.loc[location_hist["DEBUTSEM"] < week_start].tail(1)
    if previous_points.empty:
        return 100.0 if observed_cases > 0 else 0.0

    previous_cases = float(previous_points.iloc[-1]["TOTALCAS"] or 0.0)
    if previous_cases <= 0:
        return 100.0 if observed_cases > 0 else 0.0
    return ((float(observed_cases) - previous_cases) / previous_cases) * 100.0


def _prediction_runs_frame(auth: AuthSystem) -> pd.DataFrame:
    runs = auth.get_prediction_runs(limit=200)
    return pd.DataFrame(runs) if runs else pd.DataFrame()

# --- ALERTS & NOTIFS ---

def _resolve_alert_recipients(auth: AuthSystem, mode: str, entry_province: str, target_province: str) -> tuple[list[int], str]:
    authorities = auth.get_all_authorities()
    if mode == "Toutes les provinces":
        ids = sorted({int(authority["id"]) for authority in authorities})
        return ids, "national"

    destination = entry_province if mode == "Province de la saisie" else target_province
    destination_token = _province_token(destination)
    ids = sorted(
        {
            int(authority["id"])
            for authority in authorities
            if _province_token(authority.get("province", "")) == destination_token
        }
    )
    return ids, destination


def _authority_visible_level(level: str) -> str:
    normalized = (level or "").upper().strip()
    if normalized in {"INFO", "NOUVELLE_DONNEE", ""}:
        return "FAIBLE"
    return normalized


def generate_prediction_alert(auth: AuthSystem, emitting_user: dict, disease: str, province: str, zone: str, week: int, year: int, prev: int, pred: int, mode: str, target_p: str, r2: float):
    conn = auth._get_connection()
    cursor = conn.cursor()

    growth = ((pred - prev) / prev * 100) if prev > 0 else (100.0 if pred > 0 else 0.0)
    # Classification OMS/IDSR : niveau basé sur cas prédits ET taux de croissance
    level = _authority_visible_level(AlertSystem.classify_alert_level(disease, pred, growth))

    recipient_ids, dest_label = _resolve_alert_recipients(auth, mode, province, target_p)
    if mode == "Province spécifique" and not target_p:
        conn.close()
        raise ValueError("Choisissez une province cible pour cette diffusion.")
    if not recipient_ids:
        conn.close()
        raise ValueError(f"Aucune autorite sanitaire active n'est rattachee a {dest_label or 'la province ciblee'}.")

    message = f"Prévision SAFE CONGO : {disease} à {zone} ({province}), S{week}/{year}. Dernier: {prev} cas, Projection: {pred} cas."

    cursor.execute("INSERT INTO alerts (disease, province, zone_sante, week, year, current_cases, predicted_cases, growth_rate, alert_level, message) VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (disease, province, zone, week, year, prev, pred, growth, level, message))
    alert_id = cursor.lastrowid

    notif_msg = f"{message} (R² global: {r2:.3f}). Zone cible : {dest_label}."
    for uid in recipient_ids:
        cursor.execute("INSERT INTO notifications (user_id, alert_id, title, message) VALUES (?,?,?,?)",
                       (uid, alert_id, f"ALERTE {level} - {disease}", notif_msg))

    admin_message = (
        f"Votre alerte {level} pour {disease} a bien ete diffusee vers {dest_label}. "
        f"{len(recipient_ids)} autorite(s) sanitaire(s) ciblee(s), projection {pred} cas contre {prev} observes."
    )
    cursor.execute(
        "INSERT INTO notifications (user_id, alert_id, title, message) VALUES (?,?,?,?)",
        (int(emitting_user["id"]), alert_id, f"Diffusion confirmee - {disease}", admin_message),
    )
    
    conn.commit()
    conn.close()
    return alert_id, level, growth, len(recipient_ids), dest_label


def generate_observed_entry_alert(
    auth: AuthSystem,
    emitting_user: dict,
    disease: str,
    province: str,
    zone: str,
    week: int,
    year: int,
    observed_cases: int,
    observed_deaths: int,
    mode: str = "Province de la saisie",
    target_province: str = "",
):
    conn = auth._get_connection()
    cursor = conn.cursor()

    growth = _observed_growth_rate(auth, disease, province, zone, datetime.fromisocalendar(year, week, 1).date(), observed_cases)
    level = _authority_visible_level(AlertSystem.classify_alert_level(disease, observed_cases, growth))
    recipient_ids, dest_label = _resolve_alert_recipients(auth, mode, province, target_province)
    message = (
        f"Nouveau signal terrain SAFE CONGO : {disease} a {zone} ({province}), "
        f"S{week}/{year}. Cas observes: {observed_cases}, deces observes: {observed_deaths}, croissance estimee: {growth:+.1f}%."
    )

    alert_id = None
    if recipient_ids:
        cursor.execute(
            "INSERT INTO alerts (disease, province, zone_sante, week, year, current_cases, predicted_cases, growth_rate, alert_level, message) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (disease, province, zone, week, year, observed_cases, observed_cases, growth, level, message),
        )
        alert_id = cursor.lastrowid
        notif_title = f"ALERTE {level} - {disease}"
        for uid in recipient_ids:
            cursor.execute(
                "INSERT INTO notifications (user_id, alert_id, title, message) VALUES (?,?,?,?)",
                (uid, alert_id, notif_title, message),
            )

    admin_message = (
        f"Votre saisie terrain pour {disease} a {zone} ({province}) a ete enregistree au niveau {level} et diffusee vers {len(recipient_ids)} autorite(s) sanitaire(s) pour {dest_label}."
        if recipient_ids
        else f"Votre saisie terrain pour {disease} a {zone} ({province}) a ete enregistree, mais aucune autorite active n'est rattachee a {dest_label or province}."
    )
    cursor.execute(
        "INSERT INTO notifications (user_id, alert_id, title, message) VALUES (?,?,?,?)",
        (int(emitting_user["id"]), alert_id, f"Saisie terrain confirmee - {disease}", admin_message),
    )

    conn.commit()
    conn.close()
    return alert_id, level, len(recipient_ids), (dest_label or province)
# --- CHARTS ---

def _entry_mix_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_state_figure(
            "Top maladies saisies",
            "Aucune remontee terrain disponible pour structurer cette vue.",
            make_plotly_layout,
        )
    df = df.groupby("disease")["total_cases"].sum().nlargest(8).reset_index()
    fig = go.Figure(go.Bar(x=df["disease"], y=df["total_cases"], marker_color="#0a5fab"))
    fig.update_layout(height=320)
    return make_plotly_layout(fig, "Top Maladies Saisies")

def _province_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_state_figure(
            "Top provinces",
            "Aucune couverture terrain recente pour comparer les provinces.",
            make_plotly_layout,
        )
    df = df.groupby("province")["total_cases"].sum().nlargest(8).reset_index()
    fig = go.Figure(go.Bar(x=df["total_cases"], y=df["province"], orientation="h", marker_color="#49acef"))
    fig.update_layout(height=320)
    return make_plotly_layout(fig, "Top Provinces (Cas)")

def _alert_destination_provinces(_auth: AuthSystem, province_options: List[str]) -> List[str]:
    return _sorted_unique(province_options)

# --- MAIN APP ---

def main() -> None:
    st.set_page_config(page_title="Pilotage - SAFE CONGO", layout="wide")
    apply_admin_theme()
    
    st.markdown("""
<style>
    .stSelectbox label, .stDateInput label, .stRadio label { font-weight: 700 !important; color: #475569 !important; font-size: 0.88rem !important; }
    button[kind="primary"] { width: 100% !important; background: linear-gradient(135deg, #0a5fab 0%, #49acef 100%) !important; border: none !important; padding: 0.8rem !important; border-radius: 0.8rem !important; font-weight: 700 !important; box-shadow: 0 4px 15px rgba(10,95,171,0.2) !important; }
    .context-box { background: linear-gradient(135deg,#eff7ff,#f8fbff); border: 1px solid rgba(160,200,232,.45); padding: 1rem 1.1rem; border-radius: 0.95rem; margin: .9rem 0 1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,.45); }
    .terrain-form-heading { margin: 0 0 1rem; }
    .terrain-form-kicker { display: inline-flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 999px; background: rgba(10,95,171,.08); color: #0a5fab; font-size: .68rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: .7rem; }
    .terrain-form-kicker::before { content: ''; width: 8px; height: 8px; border-radius: 50%; background: linear-gradient(135deg,#0a5fab,#49acef); }
    .terrain-form-title-lg { font-family: 'Sora', sans-serif; font-size: 1.5rem; line-height: 1.1; color: #0f3f73; margin: 0 0 .45rem; }
    .terrain-form-subtitle { font-size: .92rem; line-height: 1.7; color: #5d738d; margin: 0 0 .9rem; }
    .terrain-side-note { font-size: .88rem; line-height: 1.66; color: #556f8c; margin: 0; }
    .admin-panel [data-testid="stPlotlyChart"] { margin-top: .35rem; }
</style>
""", unsafe_allow_html=True)

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        switch_to_home_page()
        return

    render_admin_sidebar(user, active_item=2, show_logo=False)
    ref_df = reference_catalog_frame()
    ent_df = recent_entries_frame(auth.db_path)
    prediction_runs_df = _prediction_runs_frame(auth)
    recent_alerts = alerts_frame(auth.db_path)
    admin_unread = auth.get_unread_count(user["id"])
    available_target_provinces = _alert_destination_provinces(auth, _province_options(ref_df, ent_df))
    delivery_flash = st.session_state.pop("admin_delivery_flash", "")
    entry_flash = st.session_state.pop("admin_entry_flash", "")
    entry_warning_flash = st.session_state.pop("admin_entry_warning_flash", "")
    
    render_admin_hero(
        title="Pilotage strategique et prediction",
        subtitle="L'interface admin projette les cas a partir d'une date cible, controle la fiabilite globale du modele et diffuse des alertes sans casser la coherence du cockpit global.",
        chips=["Prediction guidee", "R2 global", "Diffusion ciblee"],
        eyebrow="Saisie et IA",
        notification_count=admin_unread,
        auth=auth,
        user_id=user["id"],
        inbox_key_prefix="admin_data_entry_inbox",
        inbox_limit=8,
    )
    if entry_flash:
        st.success(entry_flash)
    if entry_warning_flash:
        st.success(entry_warning_flash)
    if delivery_flash:
        st.success(delivery_flash)

    render_kpi_cards([
        {"label": "Saisies terrain", "value": str(len(ent_df)), "delta": "Donnees observees", "copy": "Les remontees terrain sont maintenant persistées dans la table epidemiologique sans melanger l'observe et la prevision.", "accent": "#0a5fab", "accent_soft": "#49acef", "pill": "rgba(10,95,171,.12)"},
        {"label": "Previsions recentes", "value": str(len(prediction_runs_df)), "delta": "Trace backend", "copy": "Chaque execution de prediction validee est historisee separement pour garder une piste d'audit claire.", "accent": "#2563eb", "accent_soft": "#60a5fa", "pill": "rgba(37,99,235,.12)"},
        {"label": "Alertes recentes", "value": str(len(recent_alerts)), "delta": "Diffusion active", "copy": "Chaque prediction transformee en alerte reste visible pour l'arbitrage et le suivi institutionnel.", "accent": "#d97706", "accent_soft": "#fcd116", "pill": "rgba(217,119,6,.12)"},
        {"label": "Provinces activables", "value": str(len(available_target_provinces)), "delta": "Referentiel national", "copy": "Le ciblage d'alerte s'appuie sur les provinces du referentiel sanitaire national.", "accent": "#d97706", "accent_soft": "#fcd116", "pill": "rgba(217,119,6,.12)"},
    ])

    section_label("Saisie terrain et prediction")
    tabs = st.tabs(["Saisie terrain", "Nouvelle prevision", "Historique", "Referentiel"])

    with tabs[0]:
        st.markdown(
            f"""
<div class="admin-form-hero">
    <div class="admin-form-banner">
        <div class="terrain-form-kicker">Collecte terrain</div>
        <div class="terrain-form-title-lg">Formulaire terrain prioritaire</div>
        <div class="terrain-form-subtitle">Cette zone sert a enregistrer des donnees observees propres, a verifier la diffusion d'alerte et a declencher la projection automatique seulement quand le contexte est exploitable.</div>
    </div>
    <div class="admin-form-stats">
        <div class="admin-form-stat"><strong>{len(ent_df)}</strong><span>Saisies terrain</span></div>
        <div class="admin-form-stat"><strong>{len(available_target_provinces)}</strong><span>Provinces cibles</span></div>
        <div class="admin-form-stat"><strong>{MIN_HISTORY_WEEKS}</strong><span>Semaines requises</span></div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        l, r = st.columns([1.3, 0.7], gap="large")
        with l:
            with st.container():
                st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
                selected_observed_province = st.selectbox(
                    "Province de saisie",
                    [""] + _province_options(ref_df, ent_df),
                    key="observed_province_selector",
                )
                observed_province = selected_observed_province
                current_observed_delivery_mode = st.session_state.get("observed_delivery_mode", "Province de la saisie")
                st.markdown('<div style="font-size:.78rem;color:#0f3f73;font-weight:800;margin:.35rem 0 .5rem">Diffusion de l\'alerte terrain</div>', unsafe_allow_html=True)
                delivery_col_1, delivery_col_2 = st.columns(2)
                with delivery_col_1:
                    if st.button(
                        "Autorite de la province de saisie",
                        key="observed_delivery_province_button",
                        type="primary" if current_observed_delivery_mode == "Province de la saisie" else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state["observed_delivery_mode"] = "Province de la saisie"
                        st.rerun()
                with delivery_col_2:
                    if st.button(
                        "Toutes les provinces",
                        key="observed_delivery_all_button",
                        type="primary" if current_observed_delivery_mode == "Toutes les provinces" else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state["observed_delivery_mode"] = "Toutes les provinces"
                        st.rerun()
                observed_delivery_mode = st.session_state.get("observed_delivery_mode", "Province de la saisie")
                observed_delivery_label = observed_province if observed_delivery_mode == "Province de la saisie" and observed_province else "toutes les provinces" if observed_delivery_mode == "Toutes les provinces" else "la province selectionnee"
                observed_zone_options = _zone_options(ref_df, observed_province)
                st.markdown(
                    f'<div class="context-box"><div style="font-size:0.72rem; color:#0369a1; font-weight:700;">SOURCE OBSERVEE</div><div style="font-size:1.02rem; font-weight:800;">{observed_province or "Choisissez une province"}</div><div style="margin-top:.35rem; color:#475569; font-size:.88rem;">Alerte terrain orientee vers <strong>{observed_delivery_label}</strong>. La date calcule automatiquement la semaine epidemiologique. Les champs cas et deces sont requis pour alimenter correctement l\'historique de prediction. La donnee est mise a jour si une observation existe deja pour la meme maladie, semaine, province et zone.</div></div>',
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                observed_date = c2.date_input("Date d'observation", value=datetime.now().date(), key="observed_date")
                c3, c4 = st.columns(2)
                observed_cases = c3.number_input("Cas observes", min_value=0, step=1, value=0, key="observed_cases")
                observed_deaths = c4.number_input("Deces observes", min_value=0, step=1, value=0, key="observed_deaths")
                observed_zone = st.selectbox("Zone de sante", [""] + observed_zone_options, key=f"observed_zone_{observed_province or 'none'}")
                observed_disease_options = _disease_options_for_scope(ref_df, ent_df, observed_province, observed_zone)
                observed_predictable_options = _disease_options_for_scope(
                    ref_df,
                    ent_df,
                    observed_province,
                    observed_zone,
                    require_model=True,
                    min_history_weeks=MIN_HISTORY_WEEKS,
                )
                observed_disease = c1.selectbox(
                    "Maladie observee",
                    [""] + observed_disease_options,
                    key=f"observed_disease_{observed_province or 'none'}_{observed_zone or 'none'}",
                )
                observed_forecast_date = observed_date + timedelta(days=7)
                observed_history_status = _history_readiness(
                    auth,
                    observed_disease,
                    observed_province,
                    observed_zone,
                    observed_forecast_date,
                )
                observed_prediction_issue = _prediction_blocker(
                    auth,
                    observed_disease,
                    observed_province,
                    observed_zone,
                    observed_forecast_date,
                )
                if observed_history_status:
                    if observed_history_status["ready"] and not observed_prediction_issue:
                        st.success(
                            f"Projection automatique prete pour S{observed_history_status['target_week']}/{observed_history_status['target_year']} : "
                            f"{observed_history_status['available_weeks']} semaines d'historique trouvees sur {MIN_HISTORY_WEEKS} requises ({', '.join(observed_history_status['weeks_list'])})."
                        )
                if observed_zone and observed_predictable_options:
                    st.caption(
                        "Projection automatique disponible pour : "
                        + ", ".join(observed_predictable_options[:12])
                        + ("..." if len(observed_predictable_options) > 12 else "")
                    )
                observed_submit = st.button("ENREGISTRER LA DONNEE TERRAIN", use_container_width=True, key="observed_entry_submit")

                if observed_submit:
                    if not all([observed_disease, selected_observed_province, observed_zone]):
                        st.error("Champs obligatoires manquants pour la saisie terrain.")
                    elif int(observed_cases) <= 0:
                        st.error("Le nombre de cas observes doit etre superieur a zero.")
                    else:
                        ok, result = auth.save_epidemiological_entry(
                            disease=observed_disease,
                            province=selected_observed_province,
                            zone_sante=observed_zone,
                            observed_date=observed_date,
                            total_cases=int(observed_cases),
                            total_deaths=int(observed_deaths),
                            entered_by=user["id"],
                        )
                        if ok:
                            forecast_date = observed_date + timedelta(days=7)
                            prediction_issue = _prediction_blocker(
                                auth,
                                result["disease"],
                                result["province"],
                                result["zone_sante"],
                                forecast_date,
                            )
                            if prediction_issue:
                                _, observed_level, observed_sent, observed_label = generate_observed_entry_alert(
                                    auth,
                                    user,
                                    result["disease"],
                                    result["province"],
                                    result["zone_sante"],
                                    result["week"],
                                    result["year"],
                                    int(observed_cases),
                                    int(observed_deaths),
                                    observed_delivery_mode,
                                )
                                st.session_state["admin_entry_flash"] = (
                                    f"Donnee terrain enregistree ({result['action']}) pour {result['disease']} a {result['zone_sante']} - "
                                    f"S{result['week']}/{result['year']}. Alerte terrain {observed_level} diffusee vers {observed_sent} autorite(s) pour {observed_label}."
                                )
                            else:
                                try:
                                    forecast = predict_cases_for_date(
                                        auth,
                                        result["disease"],
                                        result["province"],
                                        result["zone_sante"],
                                        forecast_date,
                                    )
                                    alert_id, lvl, gr, n_sent, lbl = generate_prediction_alert(
                                        auth,
                                        user,
                                        forecast["disease"],
                                        result["province"],
                                        result["zone_sante"],
                                        forecast["week"],
                                        forecast["year"],
                                        forecast["previous_cases"],
                                        forecast["predicted_cases"],
                                        observed_delivery_mode,
                                        "",
                                        forecast["r2"],
                                    )
                                    auth.record_prediction_run(
                                        disease=forecast["disease"],
                                        province=result["province"],
                                        zone_sante=result["zone_sante"],
                                        target_date=forecast_date,
                                        week=forecast["week"],
                                        year=forecast["year"],
                                        previous_cases=forecast["previous_cases"],
                                        predicted_cases=forecast["predicted_cases"],
                                        model_r2=forecast["r2"],
                                        delivery_mode=observed_delivery_mode,
                                        delivery_target=lbl,
                                        emitted_by=user["id"],
                                        alert_id=alert_id,
                                    )
                                    st.session_state["admin_entry_flash"] = (
                                        f"Donnee terrain enregistree ({result['action']}) pour {result['disease']} a {result['zone_sante']} - "
                                        f"S{result['week']}/{result['year']}. Projection automatique S{forecast['week']}/{forecast['year']} : "
                                        f"{forecast['predicted_cases']} cas ({gr:+.1f}%). Diffusion confirmee vers {n_sent} autorite(s) pour {lbl}."
                                    )
                                except Exception:
                                    _, observed_level, observed_sent, observed_label = generate_observed_entry_alert(
                                        auth,
                                        user,
                                        result["disease"],
                                        result["province"],
                                        result["zone_sante"],
                                        result["week"],
                                        result["year"],
                                        int(observed_cases),
                                        int(observed_deaths),
                                        observed_delivery_mode,
                                    )
                                    st.session_state["admin_entry_flash"] = (
                                        f"Donnee terrain enregistree ({result['action']}) pour {result['disease']} a {result['zone_sante']} - "
                                        f"S{result['week']}/{result['year']}. Projection indisponible, alerte terrain {observed_level} diffusee vers {observed_sent} autorite(s) pour {observed_label}."
                                    )
                            st.rerun()
                        else:
                            st.error(f"Erreur de sauvegarde: {result}")
                st.markdown("</div>", unsafe_allow_html=True)

        with r:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Repere operateur")
            st.markdown("<div class='terrain-side-note'>La saisie terrain repose sur la date, la maladie, la localisation, les cas et les deces observes. La semaine epidemiologique est deduite automatiquement, puis l'observation rejoint l'historique qui sert a la prediction.</div>", unsafe_allow_html=True)
            if not ent_df.empty:
                st.plotly_chart(_entry_mix_chart(ent_df), use_container_width=True, key="admin_entry_mix_chart_help")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Dernieres remontees")
            if ent_df.empty:
                st.markdown('<div class="admin-empty-state">Aucune donnee terrain enregistree pour le moment.</div>', unsafe_allow_html=True)
            else:
                latest_entries = ent_df.sort_values("entry_date", ascending=False).head(6).copy()
                latest_entries[["total_cases", "total_deaths"]] = latest_entries[["total_cases", "total_deaths"]].fillna("-")
                st.dataframe(latest_entries, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        l, r = st.columns([1.3, 0.7], gap="large")
        with l:
            with st.container():
                st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
                panel_title("Parametres d'analyse predictive")
                province = st.selectbox("Province source", [""] + _province_options(ref_df, ent_df), key="prediction_province_selector")
                mode = st.radio("Destinataires", ["Province de la saisie", "Province spécifique", "Toutes les provinces"], index=2, horizontal=True, key="prediction_delivery_mode")
                prediction_zone_options = _zone_options(ref_df, province)
                effective_destination = province if mode == "Province de la saisie" else (st.session_state.get("prediction_target_province") or "A choisir") if mode == "Province spécifique" else "Toutes les provinces"
                st.markdown(
                    f'<div class="context-box"><div style="font-size:0.72rem; color:#0369a1; font-weight:700;">PORTEE DE DIFFUSION</div><div style="font-size:1.02rem; font-weight:800;">{effective_destination}</div><div style="margin-top:.35rem; color:#475569; font-size:.88rem;">Le formulaire principal est maintenant soumis en bloc pour eviter les reruns a chaque champ. Seuls la province source et le mode de diffusion recalculent la vue.</div></div>',
                    unsafe_allow_html=True,
                )
                prediction_zone = st.selectbox("Zone de Sante", [""] + prediction_zone_options, key=f"prediction_zone_{province or 'none'}")
                prediction_disease_options = _disease_options_for_scope(
                    ref_df,
                    ent_df,
                    province,
                    prediction_zone,
                    require_model=True,
                    min_history_weeks=MIN_HISTORY_WEEKS,
                )
                if prediction_zone and prediction_disease_options:
                    st.caption(
                        "Maladies predictibles pour cette zone : "
                        + ", ".join(prediction_disease_options[:12])
                        + ("..." if len(prediction_disease_options) > 12 else "")
                    )
                elif prediction_zone:
                    st.caption("Aucune projection disponible actuellement pour cette zone.")

                with st.form("prediction_execution_form"):
                    c1, c2 = st.columns(2)
                    disease = c1.selectbox("Maladie", [""] + prediction_disease_options, key="prediction_disease")
                    date_input = c2.date_input("Date cible", value=DEFAULT_FORECAST_DATE, key="prediction_date")
                    iso_year, iso_w, _ = date_input.isocalendar()
                    st.caption(f"Semaine cible : **S{iso_w}/{iso_year}**")

                    if mode == "Province spécifique":
                        target_p = st.selectbox(
                            "Province cible",
                            [""] + available_target_provinces,
                            key="prediction_target_province",
                        )
                    else:
                        target_p = ""
                        st.markdown(
                            f'<div class="admin-form-note">Diffusion active : <strong>{effective_destination}</strong>. Aucun champ vide inutile n\'est affiche quand la cible est deja determinee par le mode choisi.</div>',
                            unsafe_allow_html=True,
                        )
                    predict_submit = st.form_submit_button("EXECUTER LA PREVISION", use_container_width=True)

                if predict_submit:
                    if not all([disease, province, prediction_zone]):
                        st.error("Champs obligatoires manquants.")
                    else:
                        with st.spinner("Analyse en cours..."):
                            prediction_issue = _prediction_blocker(auth, disease, province, prediction_zone, date_input)
                            if prediction_issue:
                                st.caption("Projection non disponible pour cette combinaison.")
                            else:
                                try:
                                    f = predict_cases_for_date(auth, disease, province, prediction_zone, date_input)
                                    alert_id, lvl, gr, n_sent, lbl = generate_prediction_alert(auth, user, f["disease"], province, prediction_zone, f["week"], f["year"], f["previous_cases"], f["predicted_cases"], mode, target_p, f["r2"])
                                    auth.record_prediction_run(
                                        disease=f["disease"],
                                        province=province,
                                        zone_sante=prediction_zone,
                                        target_date=date_input,
                                        week=f["week"],
                                        year=f["year"],
                                        previous_cases=f["previous_cases"],
                                        predicted_cases=f["predicted_cases"],
                                        model_r2=f["r2"],
                                        delivery_mode=mode,
                                        delivery_target=lbl,
                                        emitted_by=user["id"],
                                        alert_id=alert_id,
                                    )
                                    st.session_state["admin_delivery_flash"] = f"Alerte {lvl} emise. Projection: {f['predicted_cases']} cas ({gr:+.1f}%). Diffusion confirmee vers {n_sent} autorite(s) sanitaire(s) pour {lbl}. Le suivi est disponible dans la cloche de reception."
                                    st.rerun()
                                except Exception as e:
                                    st.caption("Projection indisponible actuellement.")
                st.markdown("</div>", unsafe_allow_html=True)

        with r:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            panel_title("Aide contextuelle")
            st.markdown(f"<div style='font-size:0.9rem; color:#475569;'>Les prévisions utilisent maintenant les {MIN_HISTORY_WEEKS} dernières semaines de données consolidées. Le score R² global est contrôlé au moment de l'exécution pour empêcher une projection peu fiable.</div>", unsafe_allow_html=True)
            if not ent_df.empty:
                st.plotly_chart(_entry_mix_chart(ent_df), use_container_width=True, key="admin_entry_mix_chart_prediction")
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Historique des donnees terrain")
        if ent_df.empty:
            st.markdown('<div class="admin-empty-state">Aucune donnee terrain enregistree pour le moment.</div>', unsafe_allow_html=True)
        else:
            history_entries = ent_df.sort_values("entry_date", ascending=False).copy()
            history_entries[["total_cases", "total_deaths"]] = history_entries[["total_cases", "total_deaths"]].fillna("-")
            st.dataframe(history_entries, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Historique recent des previsions")
        if prediction_runs_df.empty:
            st.markdown('<div class="admin-empty-state">Aucune prevision historisee pour le moment.</div>', unsafe_allow_html=True)
        else:
            st.dataframe(prediction_runs_df.sort_values("created_at", ascending=False), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
        panel_title("Referentiel province / zone")
        if not ref_df.empty:
            st.dataframe(ref_df[["PROVINCE", "ZONE_SANTE"]].drop_duplicates().sort_values(["PROVINCE", "ZONE_SANTE"]), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="admin-empty-state">Le referentiel province / zone est vide pour le moment.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
