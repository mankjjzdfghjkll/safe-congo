import streamlit as st
import pandas as pd
import sys
import logging
import warnings
from pathlib import Path
from urllib.parse import quote

from src.config import MODEL_RESULT_FILTERS

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs" / "app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

PROCESSED_DATA_CANDIDATES = [
  Path(__file__).parent / "data" / "processed" / "donnees_agregees_nettoyees.csv",
  Path(__file__).parent / "data" / "processed" / "aggregated_data.csv",
]
MODEL_SUMMARY_CANDIDATES = [
  Path(__file__).parent / "models" / "evaluation" / "model_performance_summary.csv",
]
MIN_ACCEPTABLE_R2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))


@st.cache_data(show_spinner=False)
def _home_reference_metrics() -> dict[str, int]:
    metrics = {"diseases": 0, "provinces": 0, "zones": 0, "observations": 0}
    for candidate in PROCESSED_DATA_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            frame = pd.read_csv(candidate)
        except Exception:
            continue

        normalized_columns = {column: column.strip().upper() for column in frame.columns}
        frame = frame.rename(columns=normalized_columns)

        disease_col = next((column for column in ["MALADIE", "DISEASE"] if column in frame.columns), None)
        province_col = next((column for column in ["PROVINCE", "PROV"] if column in frame.columns), None)
        zone_col = next((column for column in ["ZONE_SANTE", "ZS"] if column in frame.columns), None)

        metrics["observations"] = int(len(frame.index))
        if disease_col:
            metrics["diseases"] = int(frame[disease_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())
        if province_col:
            metrics["provinces"] = int(frame[province_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())
        if zone_col:
            metrics["zones"] = int(frame[zone_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())
        break

    for candidate in MODEL_SUMMARY_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            summary_df = pd.read_csv(candidate, encoding="utf-8-sig")
        except Exception:
            continue

        if "R² (Best)" in summary_df.columns:
            r2_values = pd.to_numeric(summary_df["R² (Best)"], errors="coerce")
            metrics["diseases"] = int(r2_values.ge(MIN_ACCEPTABLE_R2).fillna(False).sum())
            break

    return metrics


def _home_surface_context(auth) -> dict[str, int]:
    reference_metrics = _home_reference_metrics()
    snapshot = auth.database_snapshot() if hasattr(auth, "database_snapshot") else {}
    snapshot = snapshot or {}
    return {
        "diseases": int(reference_metrics.get("diseases", 0)),
        "provinces": int(reference_metrics.get("provinces", 0)),
        "zones": int(reference_metrics.get("zones", 0)),
        "observations": int(reference_metrics.get("observations", 0)),
        "users_total": int(snapshot.get("users_total", 0)),
        "alerts_total": int(snapshot.get("alerts_total", 0)),
        "entries_total": int(snapshot.get("entries_total", 0)),
    }

st.set_page_config(
    page_title="SAFE CONGO - Surveillance Epidemiologique",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
* { font-family: 'Manrope', sans-serif; box-sizing: border-box; }
/* #MainMenu { visibility: hidden; } */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  color: #0b4d95 !important;
  background: rgba(255,255,255,.96) !important;
  border: 1px solid rgba(11,77,149,.16) !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 28px rgba(15,23,42,.12) !important;
}
[data-testid="collapsedControl"] svg {
  fill: #0b4d95 !important;
}
[data-testid="stSidebarNav"] { display: none; }


/* ─── MAIN BG LIGHT BLUE ────────────────────────────────────────────── */
html, body, .stApp, .main, .block-container {
  background: linear-gradient(180deg, #eef6ff 0%, #e6f2fd 52%, #f0f8ff 100%) !important;
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
  height: auto !important;
  box-sizing: border-box;
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
  overflow-y: auto !important;
}
.stApp:after, .main:after, .block-container:after, body:after, html:after {
  display: none !important;
  content: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Supprime l’espace vide au-dessus et en dessous */
.block-container, .main, .stApp > div:first-child, .stApp > div:last-child {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* ─── GLOW BUTTON ANIMATION ─────────────────────────────────────────── */
.stButton > button {
  position: relative;
  z-index: 1;
  overflow: hidden;
}
.stButton > button::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 12px;
  box-shadow: 0 0 0 0 rgba(26,162,226,0.0);
  transition: box-shadow .28s cubic-bezier(.22,1,.36,1);
  z-index: -1;
}
.stButton > button:hover::after {
  box-shadow: 0 0 16px 4px rgba(26,162,226,0.18), 0 0 32px 8px rgba(11,77,149,0.12);
}

:root {
    --primary: #0066CC;
    --primary-dark: #004D99;
    --primary-glow: rgba(0,102,204,.7);
    --cyan: #00D4FF;
    --danger: #DC3545;
    --warning: #FFC107;
    --success: #00A86B;
    --dark: #0a0e1a;
    --dark2: #111827;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes shimmer {
    0%   { background-position: -1200px 0; }
    100% { background-position:  1200px 0; }
}
@keyframes floatUp {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-8px); }
}
@keyframes orbitRing {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes orbitRingRev {
    from { transform: rotate(0deg); }
    to   { transform: rotate(-360deg); }
}
@keyframes glow {
    0%,100% { opacity:.4; r:44; }
    50%     { opacity:1;  r:48; }
}
@keyframes scanLine {
    0%   { transform: translateY(-60px); opacity:0; }
    10%  { opacity:.8; }
    90%  { opacity:.8; }
    100% { transform: translateY(60px); opacity:0; }
}
@keyframes heartbeat {
    0%   { stroke-dashoffset: 200; }
    100% { stroke-dashoffset: 0; }
}
@keyframes particleFloat {
    0%   { transform: translate(0,0);   opacity:1; }
    100% { transform: translate(var(--tx),var(--ty)); opacity:0; }
}
@keyframes ripple {
    0%   { transform: scale(.6); opacity:.7; }
    100% { transform: scale(2.2); opacity:0; }
}
@keyframes textGlow {
    0%,100% { text-shadow: 0 0 10px rgba(0,212,255,.4), 0 0 20px rgba(0,102,204,.3); }
    50%     { text-shadow: 0 0 20px rgba(0,212,255,.8), 0 0 40px rgba(0,102,204,.6), 0 0 60px rgba(0,102,204,.3); }
}
@keyframes countUp {
    from { opacity:0; transform:scale(.8); }
    to   { opacity:1; transform:scale(1); }
}
@keyframes borderSpin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes slideInUp {
    from { opacity:0; transform:translateY(40px); }
    to   { opacity:1; transform:translateY(0); }
}

/* stApp already set above */

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #eef6ff 0%, #e6f2fd 52%, #f0f8ff 100%) !important;
  border-right: 1px solid rgba(117,171,215,.32);
  box-shadow: 2px 0 18px rgba(10,60,140,.07);
}
[data-testid="stSidebar"] * { color: #0a2c5a !important; }
[data-testid="stSidebar"] .stMarkdown { color: #0a2c5a; }
[data-testid="stSidebar"] .stButton > button {
  background: #eef7ff !important;
  border: 1px solid #c8e2f5 !important;
  border-radius: 12px !important;
  min-height: 42px !important;
  box-shadow: none !important;
  color: #0a4a8a !important;
  font-size: .86rem !important;
  font-weight: 700 !important;
  letter-spacing: .2px !important;
  text-align: left !important;
  justify-content: flex-start !important;
  padding: 0 16px !important;
  transition: all .22s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  transform: translateX(4px) !important;
  border-color: #0a84d0 !important;
  background: linear-gradient(135deg, #dff0ff, #eaf6ff) !important;
  box-shadow: 0 4px 16px rgba(10,132,208,.14) !important;
}
[data-testid="stSidebar"] .stButton > button:focus-visible,
[data-testid="stSidebar"] .stButton > button:active {
  background: linear-gradient(135deg, #083f73 0%, #0a5fab 52%, #1aa2e2 100%) !important;
  color: #ffffff !important;
  border-color: #0a5fab !important;
  box-shadow: 0 0 0 3px rgba(26,162,226,.18), 0 10px 24px rgba(10,95,171,.22) !important;
  transform: translateX(2px) !important;
}

/* ─── SIDEBAR LOGO ─────────────────────────────────────────────────────── */
.sidebar-logo-wrap {
    display: flex; flex-direction: column; align-items: center;
    padding: 16px 14px 8px; position: relative;
    margin: 4px 8px 0;
    border-radius: 18px;
    background: transparent;
}
.sidebar-logo-glow {
    position: absolute; width: 95px; height: 95px; top: 6px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(10,85,184,.28) 0%, transparent 70%);
    animation: floatUp 4s ease-in-out infinite;
    z-index: 0;
}
.sidebar-logo-svg {
    position: relative; z-index: 2;
    animation: floatUp 4s ease-in-out infinite;
    filter: drop-shadow(0 6px 14px rgba(10,60,120,.24));
}
.sidebar-brand {
    font-family: 'Sora', sans-serif;
    font-size: .86rem; font-weight: 800; letter-spacing: 1.6px;
    color: #0a2c5a !important; text-align: center;
    margin-top: 10px;
    text-transform: uppercase;
}
.sidebar-tagline {
    font-size: .64rem; letter-spacing: .8px; text-align: center;
    color: #7a9ab8 !important;
    text-transform: none; margin-top: 2px; font-weight: 600;
}
.hero-subtitle {
    font-size: 1rem; letter-spacing: 4px; text-transform: uppercase;
    color: rgba(0,212,255,.8); font-weight: 500;
    animation: slideInUp .8s ease-out .4s both;
    margin-bottom: 28px;
}
.hero-divider {
    width: 80px; height: 2px; margin: 0 auto 28px;
    background: linear-gradient(90deg, transparent, #00D4FF, transparent);
    animation: slideInUp .8s ease-out .5s both;
}

.hero-stats {
    display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
    animation: slideInUp .8s ease-out .6s both;
}
.hero-stat {
    text-align: center;
}
.hero-stat-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem; font-weight: 900;
    color: #00D4FF;
    animation: textGlow 3s ease-in-out infinite;
}
.hero-stat-label {
    font-size: .7rem; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,.5); margin-top: 2px;
}

/* ─── FEATURE CARDS ─────────────────────────────────────────────────────── */
.feat-card {
    background: rgba(255,255,255,.04); border-radius: 18px; padding: 24px 20px;
    text-align: center; transition: all .35s;
    border: 1px solid rgba(0,212,255,.12);
    backdrop-filter: blur(8px);
    animation: fadeIn .9s ease-out;
    position: relative; overflow: hidden;
}
.feat-card::before {
    content:''; position:absolute; inset:0;
    background: linear-gradient(135deg, rgba(0,212,255,.05), transparent);
    opacity:0; transition: opacity .35s;
}
.feat-card:hover { transform: translateY(-8px); border-color: rgba(0,212,255,.4);
    box-shadow: 0 12px 40px rgba(0,102,204,.25); }
.feat-card:hover::before { opacity:1; }
.feat-icon { font-size: 2.6rem; margin-bottom: 10px; }
.feat-label { font-weight: 700; color: #e0eaff; font-size: .95rem; }
.feat-desc  { font-size: .78rem; color: rgba(160,180,220,.7); margin-top: 5px; }

/* ─── FORM / CARD ───────────────────────────────────────────────────────── */
.form-wrapper {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(0,212,255,.15);
    border-radius: 24px; padding: 36px;
    backdrop-filter: blur(12px);
    box-shadow: 0 20px 60px rgba(0,0,0,.4);
    animation: fadeIn .7s ease-out;
}

.stButton > button {
    background: linear-gradient(135deg, #0066CC, #004D99) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    padding: 12px 24px !important; font-weight: 700 !important;
    transition: all .3s !important; width: 100% !important;
    letter-spacing: 1px !important;
    box-shadow: 0 4px 20px rgba(0,102,204,.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,102,204,.5) !important;
}
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid rgba(0,212,255,.2) !important;
    padding: 12px 16px !important;
    background: rgba(255,255,255,.06) !important;
    color: #e0eaff !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,.15) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(160,180,220,.5) !important; }
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1px solid rgba(0,212,255,.2) !important;
    background: rgba(255,255,255,.06) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px; padding: 8px 20px; font-weight: 600;
    color: rgba(160,200,255,.7) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#0066CC,#004D99) !important;
    color:#fff !important;
}
.stMarkdown p, .stMarkdown label, .stMarkdown { color: #374151 !important; }

/* ─── LOGIN FORM OVERRIDES (white bg) ──────────────────────────────── */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #d1d5db !important;
    padding: 12px 16px !important;
    background: #fff !important;
    color: #111827 !important;
    font-size: .95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0066CC !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,.12) !important;
}
.stTextInput label { color: #374151 !important; font-weight: 600 !important; font-size: .88rem !important; }
.stSelectbox label { color: #374151 !important; font-weight: 600 !important; font-size: .88rem !important; }
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #d1d5db !important;
    background: #fff !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 10px;
  background: #f3f8ff;
  border: 1px solid #dde9f8;
  border-radius: 16px;
  padding: 6px;
}
.stTabs [data-baseweb="tab"] { border-radius: 12px; padding: 10px 24px; font-weight: 700; color: #6b7280 !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,#0066CC,#004D99) !important; color:#fff !important; box-shadow: 0 10px 22px rgba(0,102,204,.18) !important; }

.auth-shell {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255,255,255,.97) 0%, rgba(241,249,255,.98) 100%);
  border: 1px solid rgba(77, 142, 198, .18);
  border-radius: 34px;
  padding: 20px;
  box-shadow: 0 26px 60px rgba(52, 106, 163, .10), 0 0 0 1px rgba(255,255,255,.84) inset;
}
.auth-shell::before {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: 30px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(11,77,149,.34), rgba(111,206,244,.36), rgba(255,255,255,.18));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
.auth-shell::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top right, rgba(74,177,228,.14), transparent 30%),
    radial-gradient(circle at bottom left, rgba(8,82,144,.08), transparent 24%),
    linear-gradient(180deg, rgba(255,255,255,.24), transparent 46%);
  pointer-events: none;
}
.auth-shell-head {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1.15fr .85fr;
  gap: 18px;
  margin-bottom: 16px;
  padding: 22px 20px 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f2f9ff 70%, #eef7ff 100%);
  border: 1px solid #d5e8f7;
  border-radius: 28px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.88);
  text-align: center;
  align-items: center;
}
.auth-shell-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.22rem;
  font-weight: 800;
  letter-spacing: -.2px;
  color: #10345f !important;
  margin-bottom: 10px;
}
.auth-shell-copy {
  color: #5f7492 !important;
  font-size: .92rem;
  line-height: 1.76;
  max-width: 560px;
  margin: 0 auto;
}
.auth-shell-statbox {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.auth-shell-stat {
  background: linear-gradient(180deg, #ffffff 0%, #edf8ff 100%);
  border: 1px solid #d7eaf9;
  border-radius: 20px;
  padding: 15px 14px;
  box-shadow: 0 12px 26px rgba(72, 128, 184, .07);
}
.auth-shell-stat-k {
  font-size: .66rem;
  font-weight: 800;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: #6d87a7 !important;
  margin-bottom: 6px;
}
.auth-shell-stat-v {
  font-family: 'Sora', sans-serif;
  font-size: .98rem;
  font-weight: 800;
  color: #0b4d95 !important;
}
.auth-panel {
  background: linear-gradient(180deg, #ffffff 0%, #f8fcff 100%);
  border: 1px solid rgba(71, 136, 194, .14);
  border-radius: 28px;
  padding: 30px 28px 24px;
  box-shadow: 0 18px 34px rgba(72, 127, 184, .08);
}
.auth-kicker {
  display: inline-block;
  font-size: .68rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #0b4d95 !important;
  background: linear-gradient(135deg, #ebf7ff 0%, #f6fbff 100%);
  border: 1px solid #cfe8fa;
  border-radius: 999px;
  padding: 6px 12px;
  margin-bottom: 10px;
  margin-left: auto;
  margin-right: auto;
}
.auth-panel-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.22rem;
  font-weight: 800;
  color: #11355e !important;
  margin: 0 0 6px;
  letter-spacing: .5px;
  text-align: center;
}
.auth-panel-sub {
  color: #5f7490 !important;
  font-size: .9rem;
  line-height: 1.6;
  margin-bottom: 16px;
  text-align: center;
}
.auth-inline-note {
  color: #4f6886 !important;
  background: linear-gradient(135deg, #f7fcff 0%, #edf8ff 100%);
  border: 1px solid #d8ebf9;
  border-radius: 16px;
  padding: 12px 14px;
  font-size: .82rem;
  line-height: 1.6;
  margin: 10px 0 6px;
  text-align: center;
}
.trust-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 14px 0 8px;
  justify-content: center;
}
.trust-pill {
  font-size: .74rem;
  font-weight: 700;
  color: #17477d !important;
  background: linear-gradient(135deg, #eff8ff 0%, #f8fcff 100%);
  border: 1px solid #d7ebfb;
  border-radius: 999px;
  padding: 7px 12px;
}
.auth-mini-note {
  color: #94a3b8 !important;
  font-size: .75rem;
  margin-top: 8px;
  line-height: 1.5;
  text-align: center;
}
.auth-feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 22px;
}
.auth-feature-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  border: 1px solid rgba(0, 102, 204, .12);
  border-radius: 22px;
  padding: 20px;
  min-height: 184px;
  box-shadow: 0 16px 36px rgba(15, 23, 42, .07);
}
.auth-feature-card::before {
  content: "";
  position: absolute;
  left: 16px;
  right: 16px;
  top: 0;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #0066CC, #00D4FF, #FFD447);
}
.auth-feature-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff8dd 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  margin-bottom: 14px;
}
.auth-feature-icon svg {
  width: 24px;
  height: 24px;
  stroke: #0b4d95;
  fill: none;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.auth-feature-title {
  color: #0f172a !important;
  font-size: .95rem;
  font-weight: 800;
  letter-spacing: .4px;
  margin-bottom: 8px;
  text-align: center;
}
.auth-feature-copy {
  color: #64748b !important;
  font-size: .84rem;
  line-height: 1.62;
  text-align: center;
}
.bridge-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  max-width: 1160px;
  margin: 10px auto 22px;
}
.bridge-shell {
  max-width: 1160px;
  margin: 6px auto 20px;
}
.bridge-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 16px;
  text-align: center;
}
.bridge-titleline {
  color: #0f172a !important;
  font-family: 'Sora', sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -.4px;
  text-align: center;
}
.bridge-subline {
  color: #64748b !important;
  font-size: .92rem;
  line-height: 1.7;
  max-width: 640px;
  text-align: center;
  margin: 0 auto;
}
.bridge-tag {
  padding: 10px 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff8dd 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .74rem;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  white-space: nowrap;
  margin: 0 auto;
}
.bridge-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  border: 1px solid rgba(0, 102, 204, .12);
  border-radius: 22px;
  padding: 22px;
  min-height: 190px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, .07);
  text-align: center;
}
.bridge-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top right, rgba(0,212,255,.10), transparent 36%);
  pointer-events: none;
}
.bridge-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff4cc 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  margin: 0 auto 14px;
}
.bridge-icon svg {
  width: 26px;
  height: 26px;
  stroke: #0b4d95;
  fill: none;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.bridge-title {
  color: #0f172a !important;
  font-size: .98rem;
  font-weight: 800;
  letter-spacing: .5px;
  margin-bottom: 8px;
}
.bridge-copy {
  color: #64748b !important;
  font-size: .86rem;
  line-height: 1.64;
}
.entry-shell {
  max-width: 1120px;
  margin: 10px auto 0;
}
.entry-head {
  text-align: center;
  margin: 0 auto 20px;
  max-width: 760px;
}
.entry-kicker {
  display: inline-block;
  padding: 7px 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff8dd 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .72rem;
  font-weight: 800;
  letter-spacing: 1.7px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.entry-title {
  color: #0f172a !important;
  font-family: 'Sora', sans-serif;
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -.5px;
  margin-bottom: 10px;
}
.entry-copy {
  color: #64748b !important;
  font-size: .95rem;
  line-height: 1.7;
}
.entry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 16px auto 22px;
}
.entry-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid rgba(71, 136, 194, .14);
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 18px 34px rgba(72, 127, 184, .08);
  text-align: center;
}
.entry-card-title {
  color: #0f172a !important;
  font-size: .98rem;
  font-weight: 800;
  margin-bottom: 8px;
}
.entry-card-copy {
  color: #64748b !important;
  font-size: .84rem;
  line-height: 1.62;
}
.auth-stage {
  max-width: 920px;
  margin: 6px auto 0;
}
.auth-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.auth-mode-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .74rem;
  font-weight: 800;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar compact logo SVG ───────────────────────────────────────────────
SHIELD_SIDEBAR = """
<div class="sidebar-logo-wrap">
  <div class="sidebar-logo-glow"></div>
  <svg class="sidebar-logo-svg" width="84" height="94" viewBox="0 0 124 140"
       xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="sig1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="rgba(255,255,255,.92)"/>
        <stop offset="58%" stop-color="rgba(180,230,255,.74)"/>
        <stop offset="100%" stop-color="rgba(100,180,240,.52)"/>
      </linearGradient>
      <filter id="sigf" x="-28%" y="-28%" width="156%" height="156%">
        <feGaussianBlur stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <!-- Rotating orbit rings -->
    <circle cx="55" cy="64" r="50" fill="none" stroke="rgba(10,85,184,.14)" stroke-width="1" stroke-dasharray="6 5">
      <animateTransform attributeName="transform" type="rotate" from="0 55 64" to="360 55 64" dur="22s" repeatCount="indefinite"/>
    </circle>
    <circle cx="55" cy="64" r="40" fill="none" stroke="rgba(10,85,184,.24)" stroke-width="1">
      <animate attributeName="r" values="40;58" dur="2.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;0" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#sig1)" filter="url(#sigf)"/>
    <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="1.6"/>
    <rect x="46" y="64" width="18" height="5" rx="2.2" fill="white"/>
    <rect x="52" y="57" width="6" height="19" rx="2.2" fill="white"/>
    <!-- Sinusoid waves - RDC colors -->
    <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
    </polyline>
    <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
    </polyline>
    <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".6s" repeatCount="indefinite"/>
    </polyline>
    <g transform="translate(15 104)">
      <rect x="0" y="0" width="94" height="22" rx="11" fill="rgba(255,255,255,.06)" stroke="rgba(126,198,241,.18)"/>
      <text x="47" y="15.8" text-anchor="middle" fill="rgba(200,230,255,.92)" style="font-family:'Sora',sans-serif;font-size:11px;font-weight:700;letter-spacing:1.55px">SAFE CONGO</text>
    </g>
  </svg>
  <div class="sidebar-brand">SAFE CONGO</div>
  <div class="sidebar-tagline">Veille sanitaire nationale</div>
</div>
"""


def _svg_data_uri(svg: str) -> str:
    return f"data:image/svg+xml;utf8,{quote(svg)}"


RDC_FLAG_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600">
  <defs>
    <linearGradient id="flagBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1697F6"/>
      <stop offset="100%" stop-color="#0055B8"/>
    </linearGradient>
    <linearGradient id="flagShine" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.04"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="900" height="600" rx="26" fill="url(#flagBlue)"/>
  <polygon points="-120,600 40,600 1020,0 860,0" fill="#FCD116"/>
  <polygon points="-60,600 100,600 960,0 800,0" fill="#CE1126"/>
  <polygon points="126,72 140,114 184,114 148,140 162,184 126,158 90,184 104,140 68,114 112,114" fill="#FCD116" transform="translate(126 128) scale(1.34) translate(-126 -128)"/>
  <rect x="0" y="0" width="900" height="600" fill="url(#flagShine)"/>
</svg>
"""

SIDEBAR_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 124 140">
  <defs>
    <linearGradient id="sigimg1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.92"/>
      <stop offset="58%" stop-color="#b4e6ff" stop-opacity="0.74"/>
      <stop offset="100%" stop-color="#64b4f0" stop-opacity="0.52"/>
    </linearGradient>
    <filter id="sigimgf" x="-28%" y="-28%" width="156%" height="156%">
      <feGaussianBlur stdDeviation="2.8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <circle cx="55" cy="64" r="50" fill="none" stroke="#0a55b8" stroke-opacity="0.14" stroke-width="1" stroke-dasharray="6 5"/>
  <circle cx="55" cy="64" r="40" fill="none" stroke="#0a55b8" stroke-opacity="0.24" stroke-width="1"/>
  <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#sigimg1)" filter="url(#sigimgf)"/>
  <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="#ffffff" stroke-opacity="0.5" stroke-width="1.6"/>
  <rect x="46" y="64" width="18" height="5" rx="2.2" fill="#ffffff"/>
  <rect x="52" y="57" width="6" height="19" rx="2.2" fill="#ffffff"/>
  <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin="0.3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin="0.6s" repeatCount="indefinite"/>
  </polyline>
  <g transform="translate(15 104)">
    <rect x="0" y="0" width="94" height="22" rx="11" fill="#ffffff" fill-opacity="0.06" stroke="#7ec6f1" stroke-opacity="0.18"/>
    <text x="47" y="15.8" text-anchor="middle" fill="#c8e6ff" font-family="Sora, sans-serif" font-size="11" font-weight="700" letter-spacing="1.55">SAFE CONGO</text>
  </g>
</svg>
"""

HERO_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 124 140">
  <defs>
    <linearGradient id="heroimg1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.98"/>
      <stop offset="58%" stop-color="#c2ecff" stop-opacity="0.82"/>
      <stop offset="100%" stop-color="#69bdf3" stop-opacity="0.62"/>
    </linearGradient>
    <filter id="heroimgf" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3.1" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <circle cx="55" cy="64" r="50" fill="none" stroke="#d9f1ff" stroke-opacity="0.32" stroke-width="1.1" stroke-dasharray="6 5"/>
  <circle cx="55" cy="64" r="40" fill="none" stroke="#d9f1ff" stroke-opacity="0.42" stroke-width="1.1"/>
  <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#heroimg1)" filter="url(#heroimgf)"/>
  <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="#ffffff" stroke-opacity="0.58" stroke-width="1.7"/>
  <rect x="46" y="64" width="18" height="5" rx="2.2" fill="#ffffff"/>
  <rect x="52" y="57" width="6" height="19" rx="2.2" fill="#ffffff"/>
  <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin="0.3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin="0.6s" repeatCount="indefinite"/>
  </polyline>
</svg>
"""

RDC_FLAG_DATA_URI = _svg_data_uri(RDC_FLAG_SVG)
SIDEBAR_LOGO_DATA_URI = _svg_data_uri(SIDEBAR_LOGO_SVG)
HERO_LOGO_DATA_URI = _svg_data_uri(HERO_LOGO_SVG)

# ── Hero logo (large, for login page) ─────────────────────────────────────
SHIELD_HERO = """
<div class="hero-logo-container">
  <svg width="160" height="190" viewBox="0 0 160 190"
       xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
    <defs>
      <linearGradient id="hg1" x1="0%" y1="0%" x2="100%" y2="130%">
        <stop offset="0%"   stop-color="#80E0FF"/>
        <stop offset="40%"  stop-color="#0088FF"/>
        <stop offset="100%" stop-color="#003080"/>
      </linearGradient>
      <linearGradient id="hg2" x1="0%" y1="0%" x2="60%" y2="100%">
        <stop offset="0%"  stop-color="rgba(255,255,255,.5)"/>
        <stop offset="70%" stop-color="rgba(255,255,255,0)"/>
      </linearGradient>
      <radialGradient id="hglow" cx="50%" cy="50%" r="50%">
        <stop offset="0%"  stop-color="rgba(0,136,255,.35)"/>
        <stop offset="100%" stop-color="rgba(0,136,255,0)"/>
      </radialGradient>
      <filter id="hf" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="4" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="hf2" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="2"/>
      </filter>
    </defs>

    <!-- Pulsing background glow -->
    <ellipse cx="80" cy="95" rx="70" ry="70" fill="url(#hglow)">
      <animate attributeName="rx" values="60;80;60" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="60;80;60" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;1;.5" dur="3s" repeatCount="indefinite"/>
    </ellipse>

    <!-- Outer orbit ring 1 -->
    <g>
      <animateTransform attributeName="transform" type="rotate"
        from="0 80 95" to="360 80 95" dur="10s" repeatCount="indefinite"/>
      <ellipse cx="80" cy="95" rx="74" ry="74"
               fill="none" stroke="rgba(0,212,255,.35)" stroke-width="1.2"
               stroke-dasharray="8 6"/>
      <circle cx="154" cy="95" r="4" fill="#00D4FF" opacity=".9"/>
      <circle cx="6"   cy="95" r="3" fill="#00D4FF" opacity=".6"/>
    </g>

    <!-- Outer orbit ring 2 (reverse) -->
    <g>
      <animateTransform attributeName="transform" type="rotate"
        from="0 80 95" to="-360 80 95" dur="15s" repeatCount="indefinite"/>
      <ellipse cx="80" cy="95" rx="82" ry="82"
               fill="none" stroke="rgba(0,102,204,.25)" stroke-width=".8"
               stroke-dasharray="3 9"/>
      <circle cx="80" cy="13" r="3" fill="#0088FF" opacity=".8"/>
    </g>

    <!-- Shield drop shadow (blur layer) -->
    <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"
          fill="rgba(0,60,160,.5)" filter="url(#hf2)"
          transform="translate(4,8)"/>

    <!-- Shield main body -->
    <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"
          fill="url(#hg1)"/>

    <!-- 3D highlight overlay -->
    <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"
          fill="url(#hg2)" opacity=".5"/>

    <!-- Inner shield bevel -->
    <path d="M80 24 L130 50 L130 96 Q130 138 80 164 Q30 138 30 96 L30 50 Z"
          fill="none" stroke="rgba(255,255,255,.22)" stroke-width="2"/>

    <!-- Animated scan line -->
    <clipPath id="shieldClip">
      <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"/>
    </clipPath>
    <g clip-path="url(#shieldClip)">
      <rect x="18" y="0" width="124" height="3"
            fill="rgba(0,212,255,.6)" rx="1">
        <animateTransform attributeName="transform" type="translate"
          values="0,20; 0,160" dur="2.8s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;.9;.9;0" dur="2.8s" repeatCount="indefinite"/>
      </rect>
    </g>

    <!-- Cross shape -->
    <rect x="65" y="76" width="30" height="10" rx="3" fill="white" opacity=".95"/>
    <rect x="73" y="68" width="14" height="26" rx="3" fill="white" opacity=".95"/>

    <!-- ECG / heartbeat line -->
    <polyline
      points="32,81 42,81 47,62 53,100 58,81 65,81"
      fill="none" stroke="#00D4FF" stroke-width="2.2"
      stroke-linecap="round" stroke-linejoin="round"
      stroke-dasharray="90" stroke-dashoffset="90">
      <animate attributeName="stroke-dashoffset"
        values="90;0;0;90" dur="3.2s" repeatCount="indefinite"/>
    </polyline>
    <polyline
      points="95,81 102,81 107,62 113,100 118,81 128,81"
      fill="none" stroke="#00D4FF" stroke-width="2.2"
      stroke-linecap="round" stroke-linejoin="round"
      stroke-dasharray="90" stroke-dashoffset="90">
      <animate attributeName="stroke-dashoffset"
        values="90;0;0;90" dur="3.2s" begin="0.3s" repeatCount="indefinite"/>
    </polyline>

    <!-- Ripple circles -->
    <circle cx="80" cy="95" r="55" fill="none"
            stroke="rgba(0,212,255,.5)" stroke-width="1.5">
      <animate attributeName="r"      values="55;90" dur="2.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".6;0"  dur="2.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="80" cy="95" r="55" fill="none"
            stroke="rgba(0,102,204,.4)" stroke-width="1">
      <animate attributeName="r"      values="55;90" dur="2.5s" begin="1.25s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;0"  dur="2.5s" begin="1.25s" repeatCount="indefinite"/>
    </circle>

    <!-- Corner accent dots -->
    <circle cx="80"  cy="12"  r="3.5" fill="#00D4FF"/>
    <circle cx="142" cy="42"  r="2.5" fill="#60CFFF" opacity=".8"/>
    <circle cx="18"  cy="42"  r="2.5" fill="#60CFFF" opacity=".8"/>
    <circle cx="18"  cy="98"  r="2"   fill="#0088FF" opacity=".6"/>
    <circle cx="142" cy="98"  r="2"   fill="#0088FF" opacity=".6"/>

    <!-- Floating particles -->
    <g opacity=".8">
      <circle cx="20" cy="50" r="1.8" fill="#00D4FF">
        <animate attributeName="cy" values="50;20" dur="4s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="4s" repeatCount="indefinite"/>
      </circle>
      <circle cx="140" cy="70" r="1.5" fill="#60CFFF">
        <animate attributeName="cy" values="70;30" dur="5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="5s" begin="1s" repeatCount="indefinite"/>
      </circle>
      <circle cx="50" cy="160" r="1.2" fill="#00D4FF">
        <animate attributeName="cy" values="160;130" dur="3.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;.8;0" dur="3.5s" begin=".5s" repeatCount="indefinite"/>
      </circle>
      <circle cx="110" cy="155" r="1.5" fill="#4FC3F7">
        <animate attributeName="cy" values="155;125" dur="4.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="4.5s" begin="2s" repeatCount="indefinite"/>
      </circle>
    </g>
  </svg>
</div>
"""


# ── Hero section – standalone HTML (bypasses Streamlit markdown sanitizer) ──
HERO_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#eef6ff;font-family:'Manrope',sans-serif;min-height:100%;overflow-x:hidden}
/* ── ANIMATIONS ────────────────────────────────── */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes blockGlow{0%,100%{box-shadow:0 10px 38px rgba(26,162,226,.13);}50%{box-shadow:0 24px 64px rgba(26,162,226,.22);}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{transform:scale(1);opacity:.7}50%{transform:scale(1.18);opacity:1}}
@keyframes ecgDraw{0%{stroke-dashoffset:90}60%{stroke-dashoffset:0}80%{stroke-dashoffset:0}100%{stroke-dashoffset:90}}
@keyframes ripple{0%{r:40;opacity:.55}100%{r:64;opacity:0}}

/* ── BASE ───────────────────────────────────────── */
.shell{padding:10px 18px 0}

/* ── NAVBAR ─────────────────────────────────────── */
.navbar{display:flex;align-items:center;justify-content:space-between;padding:13px 22px;border-radius:18px;background:#ffffff;border:1px solid #d0e8f8;box-shadow:0 4px 22px rgba(10,70,140,.08);margin-bottom:18px;animation:fadeUp .45s ease-out}
.nav-brand{display:flex;align-items:center;gap:12px}
.nav-shield{width:38px;height:44px;animation:float 4.5s ease-in-out infinite;flex-shrink:0}
.nav-name{font-family:'Sora',sans-serif;font-size:.95rem;font-weight:800;letter-spacing:2px;color:#0a2c5a;text-transform:uppercase;line-height:1.2}
.nav-sub{font-size:.62rem;font-weight:700;letter-spacing:1.4px;color:#5a9ac0;text-transform:uppercase;margin-top:2px}
.nav-pills{display:flex;gap:7px;flex-wrap:wrap}
.nav-pill{padding:7px 14px;border-radius:999px;background:#eef7ff;border:1px solid #c8e2f5;font-size:.72rem;font-weight:700;color:#1a6db5;letter-spacing:.3px;white-space:nowrap}

/* ── HERO ───────────────────────────────────────── */
.hero{position:relative;overflow:hidden;border-radius:26px;background:linear-gradient(135deg,#0a5fab 0%,#0d80d8 52%,#1aa2e2 100%);padding:48px 46px 42px;margin-bottom:16px;box-shadow:0 22px 58px rgba(10,95,171,.24),0 2px 0 rgba(255,255,255,.14) inset;animation:fadeUp .55s ease-out .06s both}
.hero,.hero *{color:#ffffff}
.hero-dots{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.11) 1px,transparent 1px);background-size:26px 26px;pointer-events:none}
.hero-glow{position:absolute;inset:0;background:radial-gradient(ellipse at 78% 18%,rgba(255,255,255,.16),transparent 34%),radial-gradient(ellipse at 12% 82%,rgba(0,40,100,.22),transparent 30%);pointer-events:none}
.hero-inner{position:relative;z-index:2;display:grid;grid-template-columns:1fr auto;gap:40px;align-items:center}
.hero-kicker{display:inline-flex;align-items:center;gap:7px;padding:7px 13px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);font-size:.7rem;font-weight:800;letter-spacing:1.7px;color:rgba(255,255,255,.95);text-transform:uppercase;margin-bottom:16px}
.kicker-dot{width:7px;height:7px;border-radius:50%;background:#72f5c0;animation:pulse 2.2s ease-in-out infinite}
.hero-title{font-family:'Sora',sans-serif;font-size:3.2rem;font-weight:800;line-height:1.06;letter-spacing:-1.4px;color:#ffffff;margin-bottom:14px}
.hero-title em{font-style:normal;display:block;color:rgba(255,255,255,.72);font-size:2.7rem}
.hero-sub{font-size:.95rem;line-height:1.72;color:rgba(255,255,255,.8);max-width:460px;margin-bottom:26px}
.hero-stats{display:flex;gap:14px;flex-wrap:wrap}
.hstat{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:11px 16px;text-align:center;min-width:80px}
.hstat-v{font-family:'Sora',sans-serif;font-size:1.3rem;font-weight:800;color:#ffffff}
.hstat-k{font-size:.62rem;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;color:rgba(255,255,255,.68);margin-top:3px}
.hero-proof{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:18px;max-width:740px}
.hero-proof-card{padding:13px 14px;border-radius:16px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);backdrop-filter:blur(8px)}
.hero-proof-k{font-size:.66rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,.68)}
.hero-proof-v{margin-top:6px;font-size:.88rem;line-height:1.45;color:#fff;font-weight:700}
.hero-visual{animation:float 5.5s ease-in-out infinite;filter:drop-shadow(0 18px 36px rgba(0,0,0,.16))}

/* ── CARDS ──────────────────────────────────────── */
.section-head{margin:0 0 32px 0;animation:fadeUp .8s cubic-bezier(.22,1,.36,1);}
.section-label{font-size:.7rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#3a7ebf;padding-left:2px}
.cards-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin:44px 0 40px 0;animation:fadeUp .8s cubic-bezier(.22,1,.36,1);}
.card{background:#ffffff;border:1px solid #d0e8f8;border-radius:22px;padding:32px 28px;box-shadow:0 8px 32px rgba(10,60,120,.09);position:relative;overflow:hidden;transition:transform .28s,box-shadow .28s;animation:fadeUp .65s ease-out both}
.card:nth-child(1){animation-delay:.08s}.card:nth-child(2){animation-delay:.16s}.card:nth-child(3){animation-delay:.24s}
.card::after{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:22px 22px 0 0}
.c1::after{background:linear-gradient(90deg,#0a84d0,#38b6e8)}.c2::after{background:linear-gradient(90deg,#0b9e6e,#3ec99a)}.c3::after{background:linear-gradient(90deg,#f57c00,#ffb74d)}
.card:hover{transform:translateY(-8px) scale(1.03);box-shadow:0 24px 64px rgba(26,162,226,.18),0 0 0 4px #e6f2fd;animation:blockGlow 1.8s infinite alternate;}
.c-ico{width:50px;height:50px;border-radius:15px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.ci-b{background:#e6f4fd}.ci-g{background:#e6f8f0}.ci-o{background:#fff3e0}
.c-title{font-family:'Sora',sans-serif;font-size:.98rem;font-weight:800;color:#0a2040;margin-bottom:8px}
.c-copy{font-size:.84rem;line-height:1.66;color:#5a7a99}
.c-tag{display:inline-block;margin-top:11px;padding:5px 10px;border-radius:999px;font-size:.67rem;font-weight:800;letter-spacing:.9px;text-transform:uppercase}
.ct-b{background:#e6f4fd;color:#1268b0}.ct-g{background:#e6f8f0;color:#0b7a52}.ct-o{background:#fff3e0;color:#c05800}

/* ── STEPS ──────────────────────────────────────── */
.steps-wrap{background:#ffffff;border:1px solid #d0e8f8;border-radius:22px;padding:34px 34px 34px;margin:56px 0 0 0;box-shadow:0 8px 32px rgba(10,60,120,.09);animation:fadeUp 1.1s cubic-bezier(.22,1,.36,1);}
.steps-title{font-family:'Sora',sans-serif;font-size:1.35rem;font-weight:800;color:#0a2c5a;text-align:center;margin-bottom:18px;}
.steps-sub{font-size:.98rem;color:#7a9ab8;text-align:center;margin-bottom:44px;}
.steps-row{display:flex;align-items:flex-start;gap:54px;}
.step{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;box-shadow:0 8px 32px rgba(26,162,226,.11);transition:box-shadow .22s,transform .18s;}
.step:hover{box-shadow:0 16px 48px rgba(26,162,226,.18),0 0 0 4px #e6f2fd;transform:translateY(-4px) scale(1.03);animation:blockGlow 1.8s infinite alternate;}
.step-line{flex:.42;height:2px;margin-top:23px;background:linear-gradient(90deg,#b8d8f0,#8ebfde)}
.step-num{width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2);color:#fff;font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:11px;box-shadow:0 6px 18px rgba(10,95,171,.26)}
.step-t{font-size:.9rem;font-weight:800;color:#0a2040;margin-bottom:5px}
.step-c{font-size:.78rem;color:#7a9ab8;line-height:1.56;max-width:150px}

.home-top-inner{padding:55px 40px;max-width:1200px;margin:0 auto}
.home-top-grid{display:grid;grid-template-columns:1fr 1.2fr;gap:60px;align-items:center}
.home-top-identity{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.home-flag-img{width:94px;height:auto;flex:0 0 auto;border-radius:14px;box-shadow:0 10px 22px rgba(10,85,184,.14),0 0 0 1px rgba(255,255,255,.82) inset;filter:drop-shadow(0 4px 10px rgba(10,85,184,.12));animation:float 6.4s ease-in-out infinite}
.home-top-copy{display:flex;flex-direction:column;gap:20px;justify-content:center}
.home-top-copy-inner{padding-top:12px}
.home-top-title{font-size:32px;font-weight:800;color:#0a5fab;font-family:'Sora',sans-serif;margin-bottom:12px;line-height:1.2}
.home-top-desc{font-size:14px;color:#666;font-family:'Manrope',sans-serif;line-height:1.7;max-width:450px;margin-bottom:16px}
.home-top-badges{display:flex;gap:30px;flex-wrap:wrap}
.home-logo-wrap{position:relative;width:286px;height:322px;display:flex;align-items:center;justify-content:center;animation:float 5.5s ease-in-out infinite;filter:drop-shadow(0 22px 48px rgba(0,0,0,.26))}
.home-logo-glow{width:244px;height:244px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.26) 0%,transparent 70%)}
.home-logo-img{position:relative;z-index:1;width:238px;height:270px;display:block}
.home-steps-row{gap:32px}
.home-impact-shell{padding:82px 40px;background:linear-gradient(180deg,#eef6ff 0%,#f6fbff 46%,#edf6ff 100%);position:relative;overflow:hidden;border-top:1px solid rgba(26,162,226,.18);border-bottom:1px solid rgba(26,162,226,.14);animation:fadeUp .9s cubic-bezier(.22,1,.36,1) both}
.home-impact-inner{max-width:1200px;margin:0 auto;position:relative;z-index:1}
.home-impact-head{display:grid;grid-template-columns:1.1fr .9fr;gap:22px;align-items:end;margin-bottom:30px}
.home-impact-desc{font-size:16px;color:#587691;font-family:'Manrope',sans-serif;line-height:1.8;max-width:650px}
.home-impact-aside{justify-self:end;width:100%;max-width:360px;padding:22px 24px;border-radius:24px;background:linear-gradient(145deg,#0c4e91,#1176c0);box-shadow:0 20px 48px rgba(10,95,171,.22);border:1px solid rgba(255,255,255,.10);animation:fadeUp .95s .12s cubic-bezier(.22,1,.36,1) both, float 5.5s ease-in-out infinite;transition:transform .22s ease,box-shadow .22s ease}
.home-impact-aside,.home-impact-aside *{color:#ffffff!important}
.home-blue-card,.home-blue-card *{color:#ffffff!important}
.home-impact-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-bottom:20px}
.home-impact-bottom{display:grid;grid-template-columns:1.08fr .92fr;gap:22px;align-items:stretch}

@media(max-width:860px){
  .hero{padding:34px 26px 30px}
  .hero-inner{grid-template-columns:1fr;gap:24px}
  .hero-title{font-size:2.35rem}
  .hero-title em{font-size:1.95rem}
  .hero-proof{grid-template-columns:1fr}
}

@media (max-width: 1100px){
  .home-top-inner{padding:42px 24px}
  .home-top-grid,.home-impact-head,.home-impact-bottom{grid-template-columns:1fr!important;gap:24px!important}
  .home-top-copy-inner{padding-top:0}
  .home-top-badges{gap:14px}
  .home-impact-shell{padding:58px 24px}
  .home-impact-aside{justify-self:stretch;max-width:none}
  .home-impact-stats{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
  .home-steps-row{flex-direction:column;gap:14px!important;align-items:stretch}
  .steps-wrap{padding:28px 22px 24px}
  .step{width:100%}
  .step-line{width:2px;height:26px;flex:none;margin:0 auto;background:linear-gradient(180deg,#b8d8f0,#8ebfde)}
}

@media (max-width: 700px){
  .hero{padding:28px 18px 24px}
  .hero-kicker{font-size:.62rem;letter-spacing:1.3px;padding:6px 11px}
  .hero-title{font-size:1.95rem;letter-spacing:-.8px}
  .hero-title em{font-size:1.55rem}
  .hero-sub{font-size:.9rem;max-width:none;margin-bottom:18px}
  .hero-stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
  .hstat{min-width:0;padding:10px 12px}
  .home-top-inner{padding:34px 16px}
  .home-top-identity{gap:14px;align-items:flex-start}
  .home-flag-img{width:76px}
  .home-top-title{font-size:26px;margin-bottom:10px}
  .home-top-desc{font-size:13px;max-width:none;margin-bottom:12px}
  .home-top-badges{gap:10px;flex-direction:column;align-items:flex-start}
  .hero-visual{padding:8px 0 0 0!important}
  .home-logo-wrap{width:100%;height:auto;min-height:232px}
  .home-logo-glow{width:190px;height:190px}
  .home-logo-img{width:184px;height:208px}
  .cards-grid{margin-top:18px!important}
  .steps-title{font-size:1.2rem}
  .steps-sub{font-size:.92rem;margin-bottom:20px}
  .home-impact-shell{padding:42px 16px}
  .home-impact-desc{font-size:14px;max-width:none}
  .home-impact-stats{grid-template-columns:1fr}
}

@media (max-width: 900px){
  div[data-testid="stHorizontalBlock"]{gap:.8rem!important}
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}
}

/* ── FOOTER ─────────────────────────────────────── */

</style></head><body>
<div class="shell">

  <!-- DRAPEAU RDC AVANT HEADER -->
  <!-- DRAPEAU + HEADER HARMONISÉS -->
  <div style="background:linear-gradient(135deg,#eef6ff 0%,#f0f8ff 50%,rgba(245,251,255,.8) 100%);padding:0;position:relative;overflow:hidden">
    <!-- Accent bar avec couleurs RDC -->
    <div style="height:6px;background:linear-gradient(90deg,#0055B8 0%,#FCD116 50%,#CE1126 100%)"></div>
    
    <!-- Contenu principal -->
    <div class="home-top-inner">
      <div class="home-top-grid">
        <!-- Colonne gauche: Drapeau + Info RDC -->
        <div class="home-top-identity">
          <!-- Drapeau compact -->
          <img class="home-flag-img" src="__RDC_FLAG_SRC__" alt="Drapeau de la Republique Democratique du Congo" />
          
          <!-- Infos RDC -->
          <div style="border-left:3px solid #0055B8;padding-left:20px">
            <div style="font-size:14px;font-weight:700;color:#0a5fab;font-family:'Sora',sans-serif;letter-spacing:1px;margin-bottom:4px">REPUBLIQUE DEMOCRATIQUE</div>
            <div style="font-size:14px;font-weight:700;color:#0a5fab;font-family:'Sora',sans-serif;letter-spacing:1px;margin-bottom:8px">DU CONGO</div>
            <div style="font-size:11px;color:#1aa2e2;font-family:'Manrope',sans-serif;font-weight:700;letter-spacing:1.5px">justice paix travail</div>
          </div>
        </div>
        
        <!-- Colonne droite: Header + Logo -->
        <div class="home-top-copy">
          
          <!-- Titre et description -->
          <div class="home-top-copy-inner">
            <div class="home-top-title">
              <span style="background:linear-gradient(135deg,#0a5fab 0%,#1aa2e2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">SAFE CONGO</span>
            </div>
            <div class="home-top-desc">
              Plateforme de surveillance épidémiologique pour la protection collective. Détection, analyse et réponse coordonnée aux menaces sanitaires en temps réel.
            </div>
            <div class="home-top-badges">
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:4px;height:20px;background:#0055B8;border-radius:2px"></div>
                <div style="font-size:12px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:700">Surveillance structuree</div>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:4px;height:20px;background:#CE1126;border-radius:2px"></div>
                <div style="font-size:12px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:700">Détection Rapide</div>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:4px;height:20px;background:#FCD116;border-radius:2px"></div>
                <div style="font-size:12px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:700">Action Immédiate</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- HERO -->
  <div class="hero">
    <div class="hero-dots"></div>
    <div class="hero-glow"></div>
    <div class="hero-inner">
      <div>
        <div class="hero-kicker"><span class="kicker-dot"></span>__HERO_KICKER__</div>
        <div class="hero-title">__HERO_TITLE_MAIN__<em>__HERO_TITLE_EMPHASIS__</em></div>
        <div class="hero-sub">__HERO_SUBTEXT__</div>
        <div class="hero-stats">
          <div class="hstat"><div class="hstat-v">__STAT_ONE_VALUE__</div><div class="hstat-k">__STAT_ONE_LABEL__</div></div>
          <div class="hstat"><div class="hstat-v">__STAT_TWO_VALUE__</div><div class="hstat-k">__STAT_TWO_LABEL__</div></div>
          <div class="hstat"><div class="hstat-v">__STAT_THREE_VALUE__</div><div class="hstat-k">__STAT_THREE_LABEL__</div></div>
          <div class="hstat"><div class="hstat-v">__STAT_FOUR_VALUE__</div><div class="hstat-k">__STAT_FOUR_LABEL__</div></div>
        </div>
        <div class="hero-proof">
          <div class="hero-proof-card"><div class="hero-proof-k">__PROOF_ONE_LABEL__</div><div class="hero-proof-v">__PROOF_ONE_VALUE__</div></div>
          <div class="hero-proof-card"><div class="hero-proof-k">__PROOF_TWO_LABEL__</div><div class="hero-proof-v">__PROOF_TWO_VALUE__</div></div>
          <div class="hero-proof-card"><div class="hero-proof-k">__PROOF_THREE_LABEL__</div><div class="hero-proof-v">__PROOF_THREE_VALUE__</div></div>
        </div>
      </div>
      <!-- Logo SAFE CONGO identique a la sidebar -->
      <div class="hero-visual" style="display:flex;align-items:center;justify-content:center;padding:18px 0 8px 20px">
        <div class="home-logo-wrap">
          <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">
            <div class="home-logo-glow"></div>
          </div>
          <img class="home-logo-img" src="__HERO_LOGO_SRC__" alt="Logo SAFE CONGO" />
        </div>
      </div>
    </div>
  </div>

  <!-- CARDS -->
  <div class="section-head" style="margin-bottom:0;animation:fadeUp .8s cubic-bezier(.22,1,.36,1);"><div class="section-label" style="font-size:1.1rem;letter-spacing:2.5px;color:#0a5fab;">Capacités clés de la plateforme</div></div>
  <div class="cards-grid" style="margin-top:30px;gap:36px;">
    <div class="card card-premium" style="background:linear-gradient(135deg,#fafdff 60%,#e6f2fd 100%);border-radius:36px;box-shadow:0 22px 70px 0 rgba(26,162,226,.13),0 0 0 10px #e6f2fd1a inset;border:2.5px solid #e0eaff;align-items:center;gap:28px;animation:fadeUp .7s cubic-bezier(.22,1,.36,1);position:relative;overflow:hidden;transition:box-shadow .22s,transform .22s;min-width:310px;max-width:400px;padding:38px 28px 32px 28px;">
      <span class="c-tag-float" style="position:absolute;top:18px;right:18px;background:linear-gradient(90deg,#e6f2fd 60%,#fafdff 100%);color:#0a5fab;border:1.2px solid #c8e2f5;font-size:.89rem;font-weight:800;border-radius:999px;padding:6px 14px;box-shadow:0 2px 12px #e6f2fd80;z-index:2;">Surveillance</span>
      <div style="display:flex;align-items:center;gap:18px;margin-top:18px;">
        <svg width="54" height="54" viewBox="0 0 54 54" fill="none" style="background:linear-gradient(135deg,#e6f2fd,#fafdff);border-radius:16px;box-shadow:0 0 0 6px #e6f2fd;">
          <circle cx="27" cy="27" r="20" stroke="#0a5fab" stroke-width="2.5" fill="#fafdff"/>
          <path d="M37 37L27 27L20 34" stroke="#1aa2e2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <animate attributeName="stroke-dasharray" values="0,40;40,0;0,40" dur="2.2s" repeatCount="indefinite"/>
          </path>
        </svg>
        <span style="font-size:1.19rem;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#0a5fab;font-family:'Sora',sans-serif;">Détection rapide</span>
      </div>
      <div style="font-size:1.04rem;color:#4a6a8a;font-family:'Manrope',sans-serif;text-align:center;margin:12px 0 0 0;">Identification précoce des signaux d'alerte épidémiologique sur l'ensemble du territoire national.</div>
    </div>
    <div class="card card-premium" style="background:linear-gradient(135deg,#f8fcff 60%,#e6f8f0 100%);border-radius:36px;box-shadow:0 22px 70px 0 rgba(11,158,110,.13),0 0 0 10px #e6f8f01a inset;border:2.5px solid #b8e8d5;align-items:center;gap:28px;animation:fadeUp .8s .1s cubic-bezier(.22,1,.36,1);position:relative;overflow:hidden;transition:box-shadow .22s,transform .22s;min-width:310px;max-width:400px;padding:38px 28px 32px 28px;">
      <span class="c-tag-float" style="position:absolute;top:18px;right:18px;background:linear-gradient(90deg,#e6f8f0 60%,#f8fcff 100%);color:#0b9e6e;border:1.2px solid #b8e8d5;font-size:.89rem;font-weight:800;border-radius:999px;padding:6px 14px;box-shadow:0 2px 12px #e6f8f080;z-index:2;">Analyse</span>
      <div style="display:flex;align-items:center;gap:18px;margin-top:18px;">
        <svg width="54" height="54" viewBox="0 0 54 54" fill="none" style="background:linear-gradient(135deg,#e6f8f0,#f8fcff);border-radius:16px;box-shadow:0 0 0 6px #e6f8f0;">
          <rect x="12" y="12" width="30" height="30" rx="10" stroke="#0b9e6e" stroke-width="2.5" fill="#f8fcff"/>
          <path d="M19 27h16M27 19v16" stroke="#1aa2e2" stroke-width="2.5"/>
        </svg>
        <span style="font-size:1.19rem;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#0b9e6e;font-family:'Sora',sans-serif;">Analyse intelligente</span>
      </div>
      <div style="font-size:1.04rem;color:#4a6a8a;font-family:'Manrope',sans-serif;text-align:center;margin:12px 0 0 0;">Traitement et visualisation des données sanitaires pour une lecture claire des tendances et risques.</div>
    </div>
    <div class="card card-premium" style="background:linear-gradient(135deg,#fff7f8 60%,#fff3e0 100%);border-radius:36px;box-shadow:0 22px 70px 0 rgba(245,124,0,.13),0 0 0 10px #fff3e01a inset;border:2.5px solid #ffd6b8;align-items:center;gap:28px;animation:fadeUp .8s .2s cubic-bezier(.22,1,.36,1);position:relative;overflow:hidden;transition:box-shadow .22s,transform .22s;min-width:310px;max-width:400px;padding:38px 28px 32px 28px;">
      <span class="c-tag-float" style="position:absolute;top:18px;right:18px;background:linear-gradient(90deg,#fff7f8 60%,#fff3e0 100%);color:#f57c00;border:1.2px solid #ffd6b8;font-size:.89rem;font-weight:800;border-radius:999px;padding:6px 14px;box-shadow:0 2px 12px #fff3e080;z-index:2;">Pilotage</span>
      <div style="display:flex;align-items:center;gap:18px;margin-top:18px;">
        <svg width="54" height="54" viewBox="0 0 54 54" fill="none" style="background:linear-gradient(135deg,#fff7f8,#fff3e0);border-radius:16px;box-shadow:0 0 0 6px #fff3e0;">
          <polygon points="27,12 14,20 14,34 27,42 40,34 40,20" stroke="#f57c00" stroke-width="2.5" fill="#fff7f8"/>
          <path d="M23 30l4 4 8-8" stroke="#f57c00" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <animate attributeName="stroke-dasharray" values="0,24;24,0;0,24" dur="2.2s" repeatCount="indefinite"/>
          </path>
        </svg>
        <span style="font-size:1.19rem;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#f57c00;font-family:'Sora',sans-serif;">Réponse coordonnée</span>
      </div>
      <div style="font-size:1.04rem;color:#4a6a8a;font-family:'Manrope',sans-serif;text-align:center;margin:12px 0 0 0;">Alertes prioritaires et outils de pilotage pour mobiliser rapidement les ressources</div>
    </div>
  </div>
  <style>
    .cards-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 26px;
      margin: 24px 0 30px 0;
      justify-content: center;
      overflow-x: unset;
      padding-bottom: 0;
      scroll-behavior: unset;
    }
    .card {
      min-width: 220px;
      max-width: 340px;
      flex: 1 1 280px;
      background: linear-gradient(180deg,#fff 0%,#fafdff 100%);
      border-radius: 28px;
      box-shadow: 0 8px 32px rgba(10,95,171,.09);
      border: 1.5px solid #e0eaff;
      padding: 24px 14px 20px 14px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      transition: box-shadow .18s, transform .18s;
    }
    .card:hover {
      box-shadow: 0 16px 48px rgba(10,95,171,.16);
      transform: translateY(-4px) scale(1.03);
    }
    .c-title {
      font-size: 1.13rem;
      font-weight: 900;
      color: #0a2040;
      font-family: 'Sora',sans-serif;
      margin-bottom: 8px;
      letter-spacing: -.5px;
    }
    .c-copy {
      font-size: 0.97rem;
      color: #4a6a8a;
      font-family: 'Manrope',sans-serif;
      margin-bottom: 14px;
    }
    .c-tag {
      font-size: .89rem;
      font-weight: 800;
      border-radius: 999px;
      padding: 6px 14px;
      margin-top: auto;
      letter-spacing: 1.1px;
      background: #e6f2fd;
      color: #0a5fab;
      border: 1.2px solid #c8e2f5;
    }
    @media (max-width: 1100px) {
      .cards-grid { gap: 14px; }
      .card { min-width: 0; max-width: 99vw; padding: 12px 4px 12px 4px; }
    }
    @media (max-width: 900px) {
      .cards-grid { flex-direction: column; align-items: center; gap: 12px; }
      .card { width: 100%; min-width: 0; max-width: 600px; }
    }
    @media (max-width: 700px) {
      .cards-grid { flex-direction: column; gap: 10px; }
      .card { width: 100%; min-width: 0; max-width: 99vw; }
    }
  </style>
  </div>

  <!-- STEPS -->
  <div class="steps-wrap" style="margin-top:42px;">
    <div class="steps-title" style="font-size:1.5rem;letter-spacing:1.2px;">Du signal à la réponse</div>
    <div class="steps-sub" style="font-size:1.08rem;margin-bottom:30px;">Un processus structuré pour agir efficacement sur le terrain</div>
    <div class="steps-row home-steps-row" style="gap:32px;">
      <div class="step" style="animation:fadeUp .7s .1s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#0a5fab,#1aa2e2);box-shadow:0 6px 18px rgba(10,95,171,.26);font-size:1.2rem;">1</div>
        <div class="step-t">Signalement</div>
        <div class="step-c">Les autorités locales remontent les données de leur zone de santé.</div>
      </div>
      <div class="step-line"></div>
      <div class="step" style="animation:fadeUp .7s .2s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#0b9e6e,#3ec99a);box-shadow:0 6px 18px rgba(11,158,110,.18);font-size:1.2rem;">2</div>
        <div class="step-t">Analyse</div>
        <div class="step-c">La plateforme détecte les anomalies et produit des visualisations.</div>
      </div>
      <div class="step-line"></div>
      <div class="step" style="animation:fadeUp .7s .3s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#f57c00,#ffb74d);box-shadow:0 6px 18px rgba(245,124,0,.18);font-size:1.2rem;">3</div>
        <div class="step-t">Alerte</div>
        <div class="step-c">Les responsables sont notifiés avec les informations nécessaires.</div>
      </div>
      <div class="step-line"></div>
      <div class="step" style="animation:fadeUp .7s .4s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#0a5fab,#1aa2e2);box-shadow:0 6px 18px rgba(10,95,171,.26);font-size:1.2rem;">4</div>
        <div class="step-t">Réponse</div>
        <div class="step-c">Coordination et mobilisation des ressources pour une intervention.</div>
      </div>
    </div>
  </div>

  <!-- DRAPEAU RDC -->
  <!-- IMPACT SECTION -->
  <div class="home-impact-shell">
    <div style="position:absolute;inset:0;background:radial-gradient(circle at 10% 18%,rgba(0,85,184,.09),transparent 20%),radial-gradient(circle at 88% 24%,rgba(252,209,22,.12),transparent 18%),radial-gradient(circle at 50% 100%,rgba(26,162,226,.08),transparent 28%);pointer-events:none"></div>
    <div class="home-impact-inner">
      <div class="home-impact-head">
        <div>
          <div style="display:inline-flex;align-items:center;gap:8px;padding:8px 15px;border-radius:999px;background:rgba(255,255,255,.8);border:1px solid rgba(10,95,171,.10);box-shadow:0 6px 18px rgba(10,60,120,.05);font-size:.72rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#0a5fab;font-family:'Sora',sans-serif;margin-bottom:18px">
            <span style="width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0055B8,#1aa2e2)"></span>
            Impact national
          </div>
          <div style="font-size:38px;font-weight:800;color:#0a2040;margin-bottom:14px;font-family:'Sora',sans-serif;letter-spacing:-1px;line-height:1.08">
            Notre Impact pour la <span style="background:linear-gradient(135deg,#0a5fab,#1aa2e2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">Sante Publique</span>
          </div>
          <div class="home-impact-desc">Engagement continu vers une couverture sanitaire universelle en RDC, avec des donnees fiables, des signaux precoces et une coordination rapide entre les acteurs sanitaires.</div>
        </div>
        <div class="home-impact-aside">
          <div style="font-size:.72rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:rgba(255,255,255,.7);font-family:'Sora',sans-serif;margin-bottom:10px">Vision terrain</div>
          <div style="font-size:1rem;font-weight:700;color:#ffffff;font-family:'Sora',sans-serif;line-height:1.5;margin-bottom:10px">Une veille epidemiologique utile, lisible et actionnable au niveau national.</div>
          <div style="font-size:.82rem;color:rgba(255,255,255,.76);line-height:1.65;font-family:'Manrope',sans-serif">Le systeme transforme les signaux sanitaires en decisions plus rapides pour les zones de sante, les provinces et la coordination centrale.</div>
        </div>
      </div>

      <div class="home-impact-stats">
        <div style="position:relative;overflow:hidden;padding:28px 26px 24px;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#f6fbff 100%);border:1px solid rgba(10,95,171,.10);box-shadow:0 18px 40px rgba(10,60,120,.08);animation:fadeUp .9s .16s cubic-bezier(.22,1,.36,1) both, blockGlow 5.8s ease-in-out infinite;transition:transform .22s ease,box-shadow .22s ease">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#0055B8,#1aa2e2)"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px">
            <div style="width:54px;height:54px;border-radius:18px;background:linear-gradient(135deg,rgba(0,85,184,.10),rgba(26,162,226,.16));display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0a5fab" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15h3"/><path d="M7 11h6"/><path d="M7 7h10"/></svg>
            </div>
            <div style="font-size:.68rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#84a7c5;font-family:'Sora',sans-serif">Couverture</div>
          </div>
          <div style="font-size:52px;font-weight:800;background:linear-gradient(135deg,#0055B8,#1aa2e2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif;line-height:1;animation:pulse 2.8s ease-in-out infinite">__IMPACT_ONE_VALUE__</div>
          <div style="font-size:14px;color:#0a2040;font-family:'Sora',sans-serif;font-weight:800;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">__IMPACT_ONE_LABEL__</div>
          <div style="font-size:14px;color:#6a879f;font-family:'Manrope',sans-serif;line-height:1.7">__IMPACT_ONE_COPY__</div>
        </div>

        <div style="position:relative;overflow:hidden;padding:28px 26px 24px;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#fff7ef 100%);border:1px solid rgba(232,136,43,.18);box-shadow:0 18px 40px rgba(10,60,120,.08);animation:fadeUp .9s .28s cubic-bezier(.22,1,.36,1) both, blockGlow 6.2s ease-in-out infinite;transition:transform .22s ease,box-shadow .22s ease">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#de7f1f,#f2ad43)"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px">
            <div style="width:54px;height:54px;border-radius:18px;background:linear-gradient(135deg,rgba(222,127,31,.15),rgba(242,173,67,.22));display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#de7f1f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21c4.97-4.22 8-7.44 8-11a4 4 0 0 0-7-2.65A4 4 0 0 0 4 10c0 3.56 3.03 6.78 8 11Z"/></svg>
            </div>
            <div style="font-size:.68rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#c77a2d;font-family:'Sora',sans-serif">Population</div>
          </div>
          <div style="font-size:52px;font-weight:800;background:linear-gradient(135deg,#de7f1f,#f2ad43);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif;line-height:1;animation:pulse 3.1s ease-in-out infinite">__IMPACT_TWO_VALUE__</div>
          <div style="font-size:14px;color:#0a2040;font-family:'Sora',sans-serif;font-weight:800;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">__IMPACT_TWO_LABEL__</div>
          <div style="font-size:14px;color:#6a879f;font-family:'Manrope',sans-serif;line-height:1.7">__IMPACT_TWO_COPY__</div>
        </div>

        <div style="position:relative;overflow:hidden;padding:28px 26px 24px;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#f3fbf4 100%);border:1px solid rgba(54,153,88,.18);box-shadow:0 18px 40px rgba(10,60,120,.08);animation:fadeUp .9s .4s cubic-bezier(.22,1,.36,1) both, blockGlow 6.6s ease-in-out infinite;transition:transform .22s ease,box-shadow .22s ease">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#2d8a4a,#74bf6b)"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px">
            <div style="width:54px;height:54px;border-radius:18px;background:linear-gradient(135deg,rgba(45,138,74,.14),rgba(116,191,107,.20));display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2d8a4a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg>
            </div>
            <div style="font-size:.68rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#4d9b62;font-family:'Sora',sans-serif">Qualite</div>
          </div>
          <div style="font-size:52px;font-weight:800;background:linear-gradient(135deg,#2d8a4a,#74bf6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif;line-height:1;animation:pulse 3.4s ease-in-out infinite">__IMPACT_THREE_VALUE__</div>
          <div style="font-size:14px;color:#0a2040;font-family:'Sora',sans-serif;font-weight:800;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">__IMPACT_THREE_LABEL__</div>
          <div style="font-size:14px;color:#6a879f;font-family:'Manrope',sans-serif;line-height:1.7">__IMPACT_THREE_COPY__</div>
        </div>
      </div>

      <div class="home-impact-bottom">
        <div style="padding:30px 30px 28px;border-radius:26px;background:linear-gradient(135deg,#ffffff 0%,#f7fbff 100%);border:1px solid rgba(10,95,171,.10);box-shadow:0 16px 36px rgba(10,60,120,.07);animation:fadeUp .95s .52s cubic-bezier(.22,1,.36,1) both">
          <div style="font-size:.74rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#0a84d0;font-family:'Sora',sans-serif;margin-bottom:12px">Mission Sanitaire</div>
          <div style="font-size:24px;font-weight:800;color:#0a2040;font-family:'Sora',sans-serif;line-height:1.25;margin-bottom:12px">Transformer les donnees sanitaires en action concrete sur le terrain.</div>
          <div style="font-size:14px;color:#65839c;font-family:'Manrope',sans-serif;line-height:1.8;max-width:700px">Assurer une surveillance epidemiologique en temps reel, detecter rapidement les foyers de maladie et coordonner les interventions pour proteger la sante de tous les Congolais.</div>
        </div>
        <div class="home-blue-card" style="padding:26px 26px 24px;border-radius:26px;background:linear-gradient(160deg,#0c4e91,#1581cb);border:1px solid rgba(255,255,255,.08);box-shadow:0 20px 42px rgba(10,95,171,.22);animation:fadeUp .95s .66s cubic-bezier(.22,1,.36,1) both, float 6s ease-in-out infinite">
          <div style="font-size:.72rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:rgba(255,255,255,.68);font-family:'Sora',sans-serif;margin-bottom:10px">Lecture rapide</div>
          <div style="font-size:1.35rem;font-weight:800;color:#ffffff;font-family:'Sora',sans-serif;line-height:1.35;margin-bottom:16px">Une plateforme qui renforce la reactivite nationale face aux menaces sanitaires.</div>
          <div style="display:flex;gap:10px;flex-wrap:wrap">
            <span style="padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12);font-size:.72rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#ffffff">Surveillance continue</span>
            <span style="padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12);font-size:.72rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#ffffff">Coordination rapide</span>
            <span style="padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12);font-size:.72rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#ffffff">Couverture nationale</span>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>
</body></html>"""


def build_home_hero_html(auth) -> str:
    context = _home_surface_context(auth)
    html = HERO_HTML
    html = html.replace("__RDC_FLAG_SRC__", RDC_FLAG_DATA_URI)
    html = html.replace("__HERO_LOGO_SRC__", HERO_LOGO_DATA_URI)
    html = html.replace("__HERO_KICKER__", "Dispositif national de veille sanitaire")
    html = html.replace("__HERO_TITLE_MAIN__", "Veiller avec clarte")
    html = html.replace("__HERO_TITLE_EMPHASIS__", "agir avec coordination.")
    html = html.replace(
        "__HERO_SUBTEXT__",
        "SAFE CONGO facilite la lecture sanitaire nationale, l'orientation des autorites et la coordination des actions dans une interface claire, fiable et orientee decision.",
    )
    html = html.replace("__STAT_ONE_VALUE__", str(context.get("provinces", 0)))
    html = html.replace("__STAT_ONE_LABEL__", "Provinces")
    html = html.replace("__STAT_TWO_VALUE__", str(context.get("zones", 0)))
    html = html.replace("__STAT_TWO_LABEL__", "Zones")
    html = html.replace("__STAT_THREE_VALUE__", str(context.get("diseases", 0)))
    html = html.replace("__STAT_THREE_LABEL__", "Maladies retenues")
    html = html.replace("__STAT_FOUR_VALUE__", f"{context.get('observations', 0):,}".replace(",", " "))
    html = html.replace("__STAT_FOUR_LABEL__", "Observations")
    html = html.replace("__PROOF_ONE_LABEL__", "Orientation")
    html = html.replace(
        "__PROOF_ONE_VALUE__",
        "Un parcours lisible pour comprendre rapidement les priorites sanitaires.",
    )
    html = html.replace("__PROOF_TWO_LABEL__", "Coordination")
    html = html.replace(
        "__PROOF_TWO_VALUE__",
        "Une interface unifiee pour relier lecture terrain et action institutionnelle.",
    )
    html = html.replace("__PROOF_THREE_LABEL__", "Confiance")
    html = html.replace(
        "__PROOF_THREE_VALUE__",
        "Des reperes consolides pour soutenir des decisions rapides et responsables.",
    )
    html = html.replace("__IMPACT_ONE_VALUE__", str(context.get("provinces", 0)))
    html = html.replace("__IMPACT_ONE_LABEL__", "Provinces suivies")
    html = html.replace(
        "__IMPACT_ONE_COPY__",
        "Une couverture provinciale complete pour structurer la lecture nationale du risque sanitaire.",
    )
    html = html.replace("__IMPACT_TWO_VALUE__", str(context.get("zones", 0)))
    html = html.replace("__IMPACT_TWO_LABEL__", "Zones observees")
    html = html.replace(
        "__IMPACT_TWO_COPY__",
        "Une profondeur territoriale utile pour lire les tensions au plus pres des zones de sante.",
    )
    html = html.replace("__IMPACT_THREE_VALUE__", str(context.get("diseases", 0)))
    html = html.replace("__IMPACT_THREE_LABEL__", "Maladies retenues")
    html = html.replace(
        "__IMPACT_THREE_COPY__",
        "Les modeles retenus en production soutiennent une veille plus fiable et une priorisation plus responsable.",
    )
    return html

def sidebar_info():
  with st.sidebar:
    st.markdown(SHIELD_SIDEBAR, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(
      '<p style="font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:#5a9ac0;font-weight:800;padding:0 8px;margin-bottom:8px">Parcours editorial</p>',
      unsafe_allow_html=True,
    )
    st.markdown(
      """
      <style>
      [data-testid="stSidebar"] .stButton:nth-of-type(1) > button{
        text-align:center!important;
        justify-content:center!important;
        padding:0 12px!important;
      }
      </style>
      """,
      unsafe_allow_html=True,
    )

    if st.button("A propos de SAFE CONGO", use_container_width=True, key="nav_apropos"):
      st.switch_page("pages/apropos.py")
    if st.button("Perspective strategique", use_container_width=True, key="nav_mission"):
      st.switch_page("pages/notre_mission.py")
    if st.button("Impact national mesurable", use_container_width=True, key="nav_impact"):
      st.switch_page("pages/impact.py")
    if st.button("Mecanique intelligente", use_container_width=True, key="nav_fonc"):
      st.switch_page("pages/fonctionnement.py")
    if st.button("Alliance & coordination", use_container_width=True, key="nav_contact"):
      st.switch_page("pages/contact.py")

    st.markdown("---")
    st.markdown(
      '<p style="font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:#5a9ac0;font-weight:800;padding:0 8px;margin-bottom:8px">Liens officiels</p>',
      unsafe_allow_html=True,
    )
    st.markdown(
      '<p class="expander-info">'
      '<a class="info-link" href="https://www.minisanterdc.cd" target="_blank">Minist&egrave;re de la Sant&eacute;</a>'
      '<a class="info-link" href="https://www.who.int/fr" target="_blank">OMS</a>'
      '<a class="info-link" href="https://www.unicef.org/drcongo" target="_blank">UNICEF RDC</a>'
      '<a class="info-link" href="https://africacdc.org" target="_blank">Africa CDC</a>'
      '</p>',
      unsafe_allow_html=True,
    )


def show_login(auth):
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = None

    st.html(build_home_hero_html(auth))

    st.markdown(
        """
    <style>
      div[data-testid="stHorizontalBlock"] div[data-testid="column"] .stButton > button {
        min-height:60px;
        border-radius:18px;
        border:1px solid rgba(96,193,232,.24);
        font:800 1rem Sora,sans-serif;
        letter-spacing:.2px;
        transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
        box-shadow:0 14px 30px rgba(53,157,209,.10);
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"] .stButton > button:hover {
        transform:translateY(-2px);
        box-shadow:0 20px 38px rgba(53,157,209,.15);
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background:linear-gradient(135deg,#79d7f2 0%,#94e2f8 48%,#b7efff 100%);
        color:#1d6f9c;
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button:hover,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button:focus,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button:active {
        border-color:rgba(96,193,232,.28);
        background:linear-gradient(135deg,#6fd1ee 0%,#8eddF6 46%,#aeeafb 100%);
        color:#1d6f9c;
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button {
        background:#ffffff;
        color:#359bc8;
        border:2px solid rgba(96,193,232,.26);
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button:hover,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button:focus,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button:active {
        background:linear-gradient(135deg,#f2fbff 0%,#fbfeff 100%);
        color:#2c88b5;
        border-color:#78d2ee;
      }
      .home-footer-shell{
        width:100vw;
        margin:52px calc(50% - 50vw) 0;
        padding:0;
        border-radius:0;
        background:linear-gradient(135deg,#073d73 0%,#0a5ba8 44%,#1196d4 100%);
        border-top:1px solid rgba(197,235,255,.35);
        box-shadow:0 -14px 36px rgba(6,41,77,.26);
        overflow:hidden;
      }
      .home-footer-top{
        display:grid;
        grid-template-columns:1fr;
        gap:8px;
        padding:10px min(6vw,64px) 4px;
        background:radial-gradient(circle at top right,rgba(152,228,255,.24),transparent 44%);
      }
      .home-footer-badge{
        display:inline-flex;
        align-items:center;
        gap:6px;
        padding:4px 10px;
        border-radius:999px;
        background:rgba(255,255,255,.16);
        border:1px solid rgba(202,236,255,.45);
        color:#d7f2ff;
        font:800 .68rem Sora,sans-serif;
        letter-spacing:1.2px;
        text-transform:uppercase;
      }
      .home-footer-title{margin-top:4px;font:800 1rem/1.1 Sora,sans-serif;color:#ffffff}
      .home-footer-copy{margin-top:3px;color:#d7ecf9;font:600 .79rem/1.45 Manrope,sans-serif;max-width:760px}
      .home-footer-copy b{color:#ffffff}
      .home-footer-social-label{color:#d6efff;font:800 .69rem Sora,sans-serif;letter-spacing:.9px;text-transform:uppercase}
      .home-footer-socials{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px}
      .home-footer-social{
        display:flex;
        align-items:center;
        gap:8px;
        padding:5px 8px;
        border-radius:8px;
        background:rgba(255,255,255,.12);
        border:1px solid rgba(208,237,255,.38);
        color:#dff3ff;
        font:700 .69rem Manrope,sans-serif;
      }
      .home-footer-social svg{width:15px;height:15px;fill:#ffffff;flex:none}
      .home-footer-social strong{display:block;color:#ffffff;font:800 .68rem Sora,sans-serif}
      .home-footer-links{display:flex;gap:5px;flex-wrap:wrap;margin-top:4px}
      .home-footer-links a{
        color:#f2fbff;
        text-decoration:none;
        padding:4px 8px;
        border-radius:8px;
        background:rgba(255,255,255,.16);
        border:1px solid rgba(208,237,255,.38);
        font:800 .69rem Manrope,sans-serif;
        letter-spacing:.35px;
        text-transform:uppercase;
      }
      .home-footer-links a:hover{background:rgba(255,255,255,.24);border-color:rgba(224,244,255,.6)}
      .home-footer-bottom{
        display:flex;
        justify-content:space-between;
        gap:10px;
        flex-wrap:wrap;
        align-items:center;
        padding:5px min(6vw,64px) 6px;
        border-top:1px solid rgba(195,233,252,.34);
        background:rgba(2,28,58,.18);
      }
      .home-footer-bottom strong{color:#ffffff;font:800 .76rem Sora,sans-serif;letter-spacing:.8px;text-transform:uppercase}
      .home-footer-bottom span{color:#d8ecfb;font:700 .72rem/1.4 Manrope,sans-serif}
      @media(max-width:840px){
        .home-footer-socials{grid-template-columns:1fr}
      }
      .home-auth-shell{
        width:min(94vw,1020px);
        margin:12px auto 14px auto;
        padding:26px 24px;
        border-radius:30px;
        background:linear-gradient(180deg,#ffffff 0%,#f9fdff 100%);
        border:1px solid #dceef8;
        box-shadow:0 18px 38px rgba(53,157,209,.08);
      }
      .home-auth-grid{
        display:grid;
        grid-template-columns:1.04fr .96fr;
        gap:18px;
        align-items:stretch;
      }
      .home-auth-main{padding:4px 2px}
      .home-auth-badge{
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:8px 14px;
        border-radius:999px;
        background:#f2fbff;
        border:1px solid #d9eef8;
        color:#43a7d1;
        font:800 .74rem Sora,sans-serif;
        letter-spacing:1.4px;
        text-transform:uppercase;
      }
      .home-auth-title{
        margin-top:12px;
        font:800 1.72rem/1.2 Sora,sans-serif;
        color:#2a82b0;
      }
      .home-auth-copy{
        margin-top:9px;
        color:#68869b;
        font:600 .92rem/1.74 Manrope,sans-serif;
        max-width:620px;
      }
      .home-auth-points{display:grid;gap:7px;margin-top:10px}
      .home-auth-point{padding:9px 11px;border-radius:14px;background:#f8fdff;border:1px solid #e2f2fa;color:#69869b;font:600 .82rem/1.58 Manrope,sans-serif}
      .home-auth-point strong{display:block;margin-bottom:3px;color:#3798c6;font:800 .78rem Sora,sans-serif}
      .home-auth-side{
        padding:18px 16px;
        border-radius:20px;
        background:linear-gradient(150deg,#dff5ff 0%,#edfaff 100%);
        border:1px solid #d7edf8;
      }
      .home-auth-side h3{font:800 1.05rem/1.3 Sora,sans-serif;color:#2e86b3;margin-bottom:8px}
      .home-auth-side p{color:#6a879b;font:600 .86rem/1.64 Manrope,sans-serif;margin-bottom:10px}
      .home-auth-tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
      .home-auth-tags span{padding:6px 9px;border-radius:999px;background:#ffffff;border:1px solid #d8edf8;color:#4aa9d1;font:800 .66rem Manrope,sans-serif;letter-spacing:.55px;text-transform:uppercase}
      @media(max-width:900px){.home-auth-grid{grid-template-columns:1fr}}
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '''
    <style>
      div[data-testid="stHorizontalBlock"] div[data-testid="column"] .stButton > button {
        min-height:62px;
        border-radius:18px;
        border:1px solid rgba(10,95,171,.18);
        font:800 1rem Sora,sans-serif;
        letter-spacing:.2px;
        transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
        box-shadow:0 16px 36px rgba(10,95,171,.12);
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"] .stButton > button:hover {
        transform:translateY(-2px);
        box-shadow:0 22px 42px rgba(10,95,171,.18);
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background:linear-gradient(135deg,#083f73 0%,#0a5fab 48%,#1aa2e2 100%);
        color:#fff;
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button:hover,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button:focus,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2) .stButton > button:active {
        border-color:rgba(8,63,115,.24);
        background:linear-gradient(135deg,#07345f 0%,#0a5498 46%,#1595d3 100%);
        color:#fff;
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button {
        background:rgba(255,255,255,.96);
        color:#0a4e8f;
        border:2px solid rgba(13,111,188,.34);
      }
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button:hover,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button:focus,
      div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(3) .stButton > button:active {
        background:linear-gradient(135deg,#eef7ff 0%,#f7fbff 100%);
        color:#083f73;
        border-color:#0d6fbc;
      }
    </style>
    ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="home-auth-shell">
      <div class="home-auth-grid">
        <div class="home-auth-main">
          <div class="home-auth-badge">Acces securise</div>
          <div class="home-auth-title">Choisissez votre parcours en quelques secondes.</div>
          <div class="home-auth-copy">Une zone unique, claire et stable pour acceder a votre espace ou lancer une demande d'acces, sans perdre du temps dans la navigation.</div>
          <div class="home-auth-points">
            <div class="home-auth-point"><strong>Connexion immediate</strong>Entrez directement dans votre espace si votre compte est deja valide.</div>
            <div class="home-auth-point"><strong>Demande guidee</strong>Soumettez votre acces avec un formulaire simple pour les profils habilites.</div>
            <div class="home-auth-point"><strong>Parcours sans confusion</strong>Les deux actions critiques restent visibles au meme endroit du debut a la fin.</div>
          </div>
        </div>
        <div class="home-auth-side">
          <h3>Orientation rapide, decision facile.</h3>
          <p>Un coup d'oeil suffit pour savoir quoi faire: se connecter ou demander un acces.</p>
          <div class="home-auth-tags">
            <span>Connexion</span>
            <span>Demande d'acces</span>
            <span>Parcours simplifie</span>
            <span>Admin et autorites</span>
          </div>
        </div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, login_col, register_col, _ = st.columns([0.45, 1, 1, 0.45], gap="medium")
    with login_col:
        if st.button("Ouvrir mon espace", use_container_width=True, key="open_login_middle"):
            st.session_state.auth_view = "login"
            st.switch_page("pages/auth.py")
    with register_col:
        if st.button("Demander un acces", use_container_width=True, key="open_register_middle"):
            st.session_state.auth_view = "register"
            st.switch_page("pages/auth.py")

    st.markdown(
        """
    <div class="home-footer-shell">
      <div class="home-footer-top">
        <div>
          <div class="home-footer-badge">SAFE CONGO • RDC</div>
          <div class="home-footer-title">Veille sanitaire nationale</div>
          <div class="home-footer-copy">Restez connecte aux <b>canaux officiels</b> de SAFE CONGO pour la communication sanitaire publique et la diffusion des messages essentiels.</div>
        </div>
        <div>
          <div class="home-footer-social-label">Reseaux sociaux</div>
          <div class="home-footer-socials" style="margin-top:4px">
            <div class="home-footer-social">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 21v-8h2.7l.4-3h-3.1V8.1c0-.9.3-1.6 1.7-1.6H17V3.8c-.3 0-1.2-.1-2.4-.1-2.4 0-4 1.4-4 4.2V10H8v3h2.6v8h2.9Z"/></svg>
              <div><strong>Facebook</strong>Communication institutionnelle</div>
            </div>
            <div class="home-footer-social">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.9 3H21l-4.6 5.3L21.8 21h-4.3l-3.4-4.6L10 21H7.8l5-5.8L2.2 3h4.4l3 4.2L13.2 3h2.1l-4.6 5.2L18.9 3Z"/></svg>
              <div><strong>X</strong>Annonces rapides</div>
            </div>
            <div class="home-footer-social">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.5 12 4.5 12 4.5s-7 0-8.9.6A3 3 0 0 0 1 7.2 31.7 31.7 0 0 0 .5 12c0 1.6.2 3.2.5 4.8A3 3 0 0 0 3.1 19c1.9.5 8.9.5 8.9.5s7 0 8.9-.6a3 3 0 0 0 2.1-2.1c.3-1.6.5-3.2.5-4.8s-.2-3.2-.5-4.8ZM9.7 15.4V8.6l5.9 3.4-5.9 3.4Z"/></svg>
              <div><strong>YouTube</strong>Sensibilisation</div>
            </div>
            <div class="home-footer-social">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.9 8.5A1.4 1.4 0 1 1 7 5.7a1.4 1.4 0 0 1-.1 2.8ZM8.4 9.8H5.6V18h2.8V9.8Zm4.4 0H10V18h2.8v-4.3c0-2.4 3.1-2.6 3.1 0V18h2.8v-5.2c0-4-4.5-3.9-5.9-1.9V9.8Z"/></svg>
              <div><strong>LinkedIn</strong>Partenariats</div>
            </div>
          </div>
        </div>
      </div>
      <div style="padding:0 min(6vw,64px) 6px;">
        <div class="home-footer-social-label">Liens officiels</div>
        <div class="home-footer-links" style="margin-top:4px;">
          <a href="https://www.minisanterdc.cd" target="_blank">Ministere de la Sante</a>
          <a href="https://www.who.int/fr" target="_blank">OMS</a>
          <a href="https://www.unicef.org/drcongo" target="_blank">UNICEF RDC</a>
          <a href="https://africacdc.org" target="_blank">Africa CDC</a>
        </div>
      </div>
      <div class="home-footer-bottom">
        <strong>SAFE CONGO</strong>
        <span>Service de veille sanitaire disponible 24/24 • Republique Democratique du Congo</span>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )






    current_view = st.session_state.auth_view
    if current_view is None:
        return

    st.switch_page("pages/auth.py")


def main():
    from utils.auth import AuthSystem


    if "user" not in st.session_state:
        st.session_state.user = None

    auth = AuthSystem()
    sidebar_info()

    user = st.session_state.user
    if user is None:
        show_login(auth)
        return

    # Logged-in routing
    if user["role"] == "admin":
        st.switch_page("pages/admin_dashboard.py")
    else:
        st.switch_page("pages/authority_dashboard.py")


def run_hidden_navigation() -> None:
    from utils.navigation import register_navigation_pages

    nav_pages = {
      "home": st.Page("pages/home.py", title="Accueil", url_path="", default=True),
        "auth": st.Page("pages/auth.py", title="Authentification", url_path="auth"),
        "apropos": st.Page("pages/apropos.py", title="A propos", url_path="a-propos"),
        "mission": st.Page("pages/notre_mission.py", title="Notre mission", url_path="notre-mission"),
        "impact": st.Page("pages/impact.py", title="Impact", url_path="impact"),
        "fonctionnement": st.Page("pages/fonctionnement.py", title="Fonctionnement", url_path="fonctionnement"),
        "contact": st.Page("pages/contact.py", title="Contact", url_path="contact"),
        "admin_dashboard": st.Page("pages/admin_dashboard.py", title="Admin dashboard", url_path="admin-dashboard"),
        "admin_data_entry": st.Page("pages/admin_data_entry.py", title="Admin data entry", url_path="admin-data-entry"),
        "admin_users": st.Page("pages/admin_users.py", title="Admin users", url_path="admin-users"),
        "admin_panel": st.Page("pages/admin_panel.py", title="Admin panel", url_path="admin-panel"),
        "authority_dashboard": st.Page("pages/authority_dashboard.py", title="Authority dashboard", url_path="authority-dashboard"),
        "authority_alerts": st.Page("pages/authority_alerts.py", title="Authority alerts", url_path="authority-alerts"),
    }
    register_navigation_pages(nav_pages)
    st.session_state["_nav_pages"] = nav_pages
    current_page = st.navigation(list(nav_pages.values()), position="hidden")
    current_page.run()


if __name__ == "__main__":
    run_hidden_navigation()
