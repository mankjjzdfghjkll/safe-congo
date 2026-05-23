import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem
from utils.navigation import switch_to_home_page

st.set_page_config(
    page_title="Accès - SAFE CONGO",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stSidebarNav"]{display:none}
[data-testid="collapsedControl"]{
  display:flex!important;
  visibility:visible!important;
  opacity:1!important;
  color:#0b4d95!important;
  background:rgba(255,255,255,.96)!important;
  border:1px solid rgba(11,77,149,.16)!important;
  border-radius:14px!important;
  box-shadow:0 10px 28px rgba(15,23,42,.12)!important;
}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}

.stApp{background:linear-gradient(135deg,#eef6ff 0%,#e2f0fb 50%,#eef8ff 100%)!important}

/* ─── inputs ──────────────────────────────────────────── */
.stTextInput>div>div>input{
  border-radius:10px!important;
  border:1.5px solid #c8dff0!important;
  padding:12px 14px!important;
  background:#ffffff!important;
  color:#0a2040!important;
  font-size:.92rem!important;
  transition:border-color .2s,box-shadow .2s!important;
}
.stTextInput>div>div>input:focus{
  border-color:#0a84d0!important;
  box-shadow:0 0 0 3px rgba(10,132,208,.12)!important;
}
.stTextInput label,.stSelectbox label{
  color:#3a6080!important;font-weight:700!important;font-size:.84rem!important;
}
.stSelectbox>div>div{
  border-radius:10px!important;
  border:1.5px solid #c8dff0!important;
  background:#ffffff!important;
}

/* ─── buttons ─────────────────────────────────────────── */
.stButton>button{
  background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
  color:#fff!important;border:none!important;
  border-radius:12px!important;padding:13px 24px!important;
  font-weight:800!important;font-size:.9rem!important;
  letter-spacing:.4px!important;width:100%!important;
  box-shadow:0 6px 20px rgba(10,95,171,.28)!important;
  transition:all .25s!important;
}
.stButton>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 10px 28px rgba(10,95,171,.36)!important;
}
.stFormSubmitButton>button{
  background:#0a5fab!important;
  background-image:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
  color:#fff!important;
  border:none!important;
  border-radius:12px!important;
  padding:13px 24px!important;
  font-weight:800!important;
  font-size:.9rem!important;
  letter-spacing:.4px!important;
  width:100%!important;
  opacity:1!important;
  box-shadow:0 6px 20px rgba(10,95,171,.28)!important;
  transition:all .25s!important;
}
.stFormSubmitButton>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 10px 28px rgba(10,95,171,.36)!important;
}

/* ─── tabs ────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"]{
  background:#f0f8ff;border:1px solid #c8dff0;
  border-radius:14px;padding:5px;gap:6px;
}
.stTabs [data-baseweb="tab"]{
  border-radius:10px;padding:9px 22px;
  font-weight:700;color:#5a7a99!important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
  color:#fff!important;
  box-shadow:0 6px 18px rgba(10,95,171,.22)!important;
}

.stMarkdown p,.stMarkdown label,.stMarkdown{color:#3a6080!important}

@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{transform:scale(1);opacity:.6}50%{transform:scale(1.15);opacity:1}}
@keyframes ecgDraw{0%{stroke-dashoffset:90}60%{stroke-dashoffset:0}80%{stroke-dashoffset:0}100%{stroke-dashoffset:90}}

/* ─── layout ──────────────────────────────────────────── */
.auth-page{display:grid;grid-template-columns:1.05fr .95fr;min-height:calc(100vh - 34px);gap:0;border-radius:28px;overflow:hidden;box-shadow:0 28px 80px rgba(10,60,120,.14);width:min(96vw,1320px);margin:16px auto;animation:fadeUp .5s ease-out}
.auth-left{background:linear-gradient(160deg,#0a5fab 0%,#0d80d8 55%,#1aa2e2 100%);padding:52px 44px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.auth-left-dots{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.1) 1px,transparent 1px);background-size:24px 24px;pointer-events:none}
.auth-left-glow{position:absolute;inset:0;background:radial-gradient(ellipse at 80% 10%,rgba(255,255,255,.14),transparent 36%),radial-gradient(ellipse at 10% 90%,rgba(0,30,80,.18),transparent 28%);pointer-events:none}
.auth-left-inner{position:relative;z-index:2}

.al-logo{display:flex;align-items:center;gap:14px;margin-bottom:42px}
.al-shield{width:44px;height:52px;animation:float 5s ease-in-out infinite;filter:drop-shadow(0 4px 12px rgba(0,0,0,.22))}
.al-name{font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;letter-spacing:2.2px;color:#fff;text-transform:uppercase}
.al-tag{font-size:.62rem;font-weight:700;letter-spacing:1.5px;color:rgba(255,255,255,.72);text-transform:uppercase;margin-top:2px}

.al-headline{font-family:'Sora',sans-serif;font-size:2.8rem;font-weight:800;line-height:1.08;letter-spacing:-1.2px;color:#ffffff;margin-bottom:16px}
.al-headline em{font-style:normal;display:block;color:rgba(255,255,255,.68);font-size:2.3rem}
.al-sub{font-size:.94rem;line-height:1.72;color:rgba(255,255,255,.8);max-width:400px;margin-bottom:34px}

.al-features{display:grid;gap:12px;margin-bottom:36px}
.al-feat{display:flex;align-items:center;gap:13px;padding:14px 16px;border-radius:16px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18)}
.al-feat-ico{width:38px;height:38px;border-radius:11px;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.al-feat-ico svg{width:18px;height:18px;stroke:rgba(255,255,255,.95);fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.al-feat-text{}
.al-feat-t{font-size:.88rem;font-weight:800;color:#fff;margin-bottom:2px}
.al-feat-c{font-size:.77rem;color:rgba(255,255,255,.72);line-height:1.46}

.al-stats{display:flex;gap:10px;flex-wrap:wrap}
.al-stat{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.2);border-radius:12px;padding:10px 14px;text-align:center}
.al-stat-v{font-family:'Sora',sans-serif;font-size:1.15rem;font-weight:800;color:#fff}
.al-stat-k{font-size:.6rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:rgba(255,255,255,.68);margin-top:2px}

.al-visual{display:flex;justify-content:center;margin:18px 0}

/* ─── right panel ─────────────────────────────────────── */
.auth-right{background:#ffffff;padding:52px 48px;display:flex;flex-direction:column;justify-content:center;align-items:center}
.auth-right > *{width:min(100%,560px)}
.ar-back{display:inline-flex;align-items:center;gap:7px;font-size:.8rem;font-weight:700;color:#5a8aaa;cursor:pointer;margin-bottom:34px;border:none;background:none;padding:0;text-decoration:none;transition:color .2s}
.ar-back:hover{color:#0a84d0}
.ar-back svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.ar-kicker{display:inline-block;padding:6px 12px;border-radius:999px;background:#eef7ff;border:1px solid #c8dff0;font-size:.68rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#1a6db5;margin-bottom:12px}
.ar-title{font-family:'Sora',sans-serif;font-size:1.85rem;font-weight:800;color:#0a2040;letter-spacing:-.5px;margin-bottom:8px}
.ar-sub{font-size:.9rem;color:#6a8da8;line-height:1.64;margin-bottom:28px}
.auth-form-shell{background:linear-gradient(180deg,#fbfdff 0%,#f4faff 100%);border:1px solid #d8e9f6;border-radius:22px;padding:22px 20px 18px;box-shadow:0 10px 28px rgba(10,60,120,.05);margin:0 auto 14px auto;max-width:560px}
.auth-form-topline{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.auth-form-chip{display:inline-flex;align-items:center;gap:8px;padding:7px 12px;border-radius:999px;background:#ffffff;border:1px solid #d7e8f5;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase;color:#0a5fab}
.auth-form-chip-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2)}
.auth-form-mini{font-size:.74rem;font-weight:700;color:#7a98b2}
.auth-form-note{margin:-2px 0 18px;font-size:.82rem;line-height:1.65;color:#6f8ca6}
.auth-form-helper{margin-top:12px;padding:12px 14px;border-radius:14px;background:linear-gradient(180deg,#ffffff 0%,#f8fcff 100%);border:1px dashed #c8dff0;font-size:.77rem;line-height:1.6;color:#67839c}
.auth-section-note{margin-top:16px;padding:12px 14px;border-radius:14px;background:#f0f8ff;border:1px solid #c8dff0;font-size:.78rem;line-height:1.6;color:#5a8aaa}
.auth-register-note{margin-bottom:16px;padding:13px 14px;border-radius:14px;background:linear-gradient(135deg,#eef7ff,#f7fbff);border:1px solid #d3e6f4;font-size:.8rem;line-height:1.65;color:#62819c}
.auth-access-split{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;max-width:560px;margin:0 auto 16px auto}
.auth-access-card{padding:14px 15px;border-radius:16px;border:1px solid #d6e6f4;background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%);box-shadow:0 8px 22px rgba(10,60,120,.05)}
.auth-access-card strong{display:block;font-size:.72rem;letter-spacing:1.2px;text-transform:uppercase;color:#0a5fab;margin-bottom:6px}
.auth-access-card span{display:block;font-size:.8rem;line-height:1.58;color:#64809a}
.auth-access-card.admin{background:linear-gradient(180deg,#f8fbff 0%,#eef6ff 100%)}
[data-testid="stForm"]{background:linear-gradient(180deg,#ffffff 0%,#fbfdff 100%);border:1px solid #d8e9f6;border-radius:22px;padding:18px 18px 10px;box-shadow:0 12px 28px rgba(10,60,120,.05);margin:0 auto 12px auto;max-width:560px}
[data-testid="stForm"] [data-testid="stVerticalBlock"]{gap:.35rem}
.stFormSubmitButton{max-width:560px;margin:0 auto}
.auth-form-helper,.auth-section-note,.auth-register-note,.register-success{max-width:560px;margin-left:auto;margin-right:auto}

.no-account{background:linear-gradient(135deg,#f0f9ff 0%,#e8f4fd 100%);border:1px solid #c8dff0;border-radius:18px;padding:20px 22px;margin:22px auto 0 auto;max-width:560px}
.nac-label{font-size:.7rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#5a9ac0;margin-bottom:8px}
.nac-title{font-size:1rem;font-weight:800;color:#0a2040;margin-bottom:6px}
.nac-copy{font-size:.84rem;color:#6a8da8;line-height:1.58;margin-bottom:12px}
.nac-perks{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.nac-perk{padding:5px 10px;border-radius:999px;background:#fff;border:1px solid #c8e4f5;font-size:.72rem;font-weight:700;color:#1a6db5}

.register-success{background:linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%);border:1px solid #6ee7b7;border-radius:16px;padding:18px 20px;text-align:center}
.reg-s-ico{font-size:2rem;margin-bottom:8px}
.reg-s-t{font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:#065f46;margin-bottom:6px}
.reg-s-c{font-size:.86rem;color:#047857;line-height:1.58}

@media(max-width:860px){
  .auth-page{grid-template-columns:1fr;margin:8px}
  .auth-left{padding:32px 24px;min-height:auto!important}
  .auth-right{padding:32px 24px}
  .al-headline{font-size:2rem}
  .al-headline em{font-size:1.7rem}
  .block-container{padding-left:1rem!important;padding-right:1rem!important;padding-top:.75rem!important}
  [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:1rem!important}
  [data-testid="column"]{width:100%!important;flex:1 1 100%!important;min-width:100%!important}
  [data-testid="stForm"]{padding:16px 14px 10px!important}
  .auth-form-shell,.auth-form-helper,.auth-section-note,.auth-register-note,.register-success,.no-account,.stFormSubmitButton,.auth-access-split{max-width:100%!important}
  .auth-access-split{grid-template-columns:1fr!important}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DATASET_GEO_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "donnees_agregees_nettoyees.csv"
REQUIRED_GEO_COLUMNS = {"PROVINCE", "ZONE_SANTE"}


def _clean_geo_value(value):
    if pd.isna(value):
        return ""
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() == "nan":
        return ""
    return cleaned


# Source unique des provinces et zones: dataset géographique
df_geo = pd.DataFrame()
PROVINCES = []
ZONES_BY_PROVINCE = {}
GEO_DATA_ERROR = ""

try:
    df_geo = pd.read_csv(DATASET_GEO_PATH)
    if not REQUIRED_GEO_COLUMNS.issubset(df_geo.columns):
        missing = REQUIRED_GEO_COLUMNS.difference(set(df_geo.columns))
        raise ValueError(f"Colonnes manquantes dans le dataset: {', '.join(sorted(missing))}")

    province_order = []
    zones_by_province = {}
    for raw_province, raw_zone in df_geo[["PROVINCE", "ZONE_SANTE"]].itertuples(index=False, name=None):
        province = _clean_geo_value(raw_province)
        zone = _clean_geo_value(raw_zone)
        if not province or not zone:
            continue
        if province not in zones_by_province:
            zones_by_province[province] = set()
            province_order.append(province)
        zones_by_province[province].add(zone)

    PROVINCES = province_order
    ZONES_BY_PROVINCE = {
        province: sorted(zones_by_province[province], key=lambda item: item.casefold())
        for province in province_order
    }
except Exception as exc:
    GEO_DATA_ERROR = str(exc)

SHIELD_SVG = """<svg width="44" height="52" viewBox="0 0 110 128" xmlns="http://www.w3.org/2000/svg" class="al-shield">
  <defs>
    <linearGradient id="asg1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(255,255,255,.94)"/>
      <stop offset="58%" stop-color="rgba(180,230,255,.78)"/>
      <stop offset="100%" stop-color="rgba(120,190,240,.56)"/>
    </linearGradient>
  </defs>
  <circle cx="55" cy="64" r="44" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="1" stroke-dasharray="6 5">
    <animateTransform attributeName="transform" type="rotate" from="0 55 64" to="360 55 64" dur="20s" repeatCount="indefinite"/>
  </circle>
  <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#asg1)"/>
  <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="rgba(255,255,255,.52)" stroke-width="1.8"/>
  <rect x="46" y="64" width="18" height="5" rx="2.2" fill="white"/>
  <rect x="52" y="57" width="6" height="19" rx="2.2" fill="white"/>
  <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".6s" repeatCount="indefinite"/>
  </polyline>
</svg>"""

VISUAL_SVG = """<svg width="130" height="150" viewBox="0 0 110 128" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <defs>
    <linearGradient id="vis1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(255,255,255,.88)"/>
      <stop offset="100%" stop-color="rgba(160,220,255,.54)"/>
    </linearGradient>
    <filter id="vgf" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <circle cx="55" cy="64" r="50" fill="none" stroke="rgba(255,255,255,.16)" stroke-width=".9" stroke-dasharray="5 4">
    <animateTransform attributeName="transform" type="rotate" from="0 55 64" to="360 55 64" dur="24s" repeatCount="indefinite"/>
  </circle>
  <circle cx="55" cy="64" r="38" fill="none" stroke="rgba(255,255,255,.28)" stroke-width=".8">
    <animate attributeName="r" values="38;56" dur="2.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".5;0" dur="2.8s" repeatCount="indefinite"/>
  </circle>
  <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#vis1)" filter="url(#vgf)"/>
  <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="rgba(255,255,255,.44)" stroke-width="1.6"/>
  <rect x="46" y="64" width="18" height="5" rx="2.2" fill="white" opacity=".95"/>
  <rect x="52" y="57" width="6" height="19" rx="2.2" fill="white" opacity=".95"/>
  <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".6s" repeatCount="indefinite"/>
  </polyline>
</svg>"""


def main():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    if "register_success" not in st.session_state:
        st.session_state.register_success = False

    auth = AuthSystem()
    db_snapshot = auth.database_snapshot()
    province_count = len(PROVINCES)
    zone_count = sum(len(zones) for zones in ZONES_BY_PROVINCE.values())
    user_count = int(db_snapshot.get("users_total", 0))

    # Already logged in → route to dashboard
    if st.session_state.user is not None:
        u = st.session_state.user
        if u["role"] == "admin":
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.switch_page("pages/authority_dashboard.py")
        return

    col_left, col_right = st.columns([1.05, 0.95])

    # ── LEFT PANEL ───────────────────────────────────────────────────────
    with col_left:
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#0a5fab 0%,#0d80d8 55%,#1aa2e2 100%);'
            f'border-radius:26px;padding:52px 44px;min-height:86vh;position:relative;overflow:hidden;'
            f'box-shadow:0 22px 58px rgba(10,95,171,.26)">'

            # dots + glow overlay (pure CSS, no JS)
            f'<div style="position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.1) 1px,transparent 1px);background-size:24px 24px;pointer-events:none;border-radius:26px"></div>'
            f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 80% 10%,rgba(255,255,255,.14),transparent 36%),radial-gradient(ellipse at 10% 90%,rgba(0,30,80,.18),transparent 28%);pointer-events:none;border-radius:26px"></div>'

            # logo
            f'<div style="position:relative;z-index:2">'
            f'<div class="al-logo">'
            f'{SHIELD_SVG}'
            f'<div><div class="al-name">SAFE CONGO</div><div class="al-tag">Veille sanitaire nationale</div></div>'
            f'</div>'

            # headline
            f'<div class="al-headline">Votre espace<em>de veille.</em></div>'
            f'<div class="al-sub">Accedez en toute securite a votre tableau de bord de surveillance epidemiologique.</div>'

            # features
            f'<div class="al-features">'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Detection precoce</div><div class="al-feat-c">Lecture des signaux sur {province_count} provinces chargees dans le referentiel.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Analyse territoriale</div><div class="al-feat-c">Suivi structure autour de {zone_count} zones de sante disponibles dans la base de reference.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3Z"/><path d="m9.5 12 1.8 1.8 3.2-3.6"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Acces securise</div><div class="al-feat-c">Connexion reservee aux comptes actifs deja presents dans la base locale.</div></div></div>'
            f'</div>'

            # stats
            f'<div class="al-stats">'
            f'<div class="al-stat"><div class="al-stat-v">{province_count}</div><div class="al-stat-k">Provinces</div></div>'
            f'<div class="al-stat"><div class="al-stat-v">{zone_count}</div><div class="al-stat-k">Zones</div></div>'
            f'<div class="al-stat"><div class="al-stat-v">{user_count}</div><div class="al-stat-k">Comptes</div></div>'
            f'</div>'
            f'</div>'

            # centered visual
            f'<div class="al-visual" style="position:relative;z-index:2;margin-top:28px;opacity:.82">'
            f'{VISUAL_SVG}'
            f'</div>'

            f'</div>',
            unsafe_allow_html=True,
        )

    # ── RIGHT PANEL ──────────────────────────────────────────────────────
    with col_right:
        # back button
        if st.button("← Retour à l'accueil", key="auth_back"):
            st.session_state.auth_view = None
            switch_to_home_page()

        # kicker
        mode = st.session_state.auth_view or "login"
        kicker = "Connexion" if mode == "login" else "Créer un compte"
        st.markdown(f'<div class="ar-kicker">{kicker}</div>', unsafe_allow_html=True)

        if mode == "login":
            st.markdown(
                '<div class="ar-title">Bon retour parmi nous</div>'
                '<div class="ar-sub">Connectez-vous pour accéder à votre espace de surveillance et de pilotage sanitaire.</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="auth-form-shell">'
                '<div class="auth-form-topline">'
                '<div class="auth-form-chip"><span class="auth-form-chip-dot"></span>Connexion securisee</div>'
                '<div class="auth-form-mini">Acces reserve aux comptes autorises</div>'
                '</div>'
              '<div class="auth-form-note">Renseignez vos identifiants pour ouvrir votre espace de suivi epidemiologique.</div>'
              '</div>',
                unsafe_allow_html=True,
            )

            if db_snapshot.get("database_exists"):
                st.markdown(
                    f'<div class="auth-section-note">Base locale detectee: <b>{db_snapshot.get("users_total", 0)}</b> compte(s), <b>{db_snapshot.get("alerts_total", 0)}</b> alerte(s), <b>{db_snapshot.get("entries_total", 0)}</b> saisie(s) terrain et <b>{db_snapshot.get("prediction_runs_total", 0)}</b> prevision(s) historisee(s). Taille courante: <b>{db_snapshot.get("database_size_kb", 0)}</b> Ko.</div>',
                    unsafe_allow_html=True,
                )

            with st.form("login_form_page"):
                username = st.text_input("Nom d'utilisateur ou email", placeholder="Votre identifiant ou email")
                password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
                submitted = st.form_submit_button("Acceder a mon espace", use_container_width=True)

            st.markdown(
                '<div class="auth-form-helper">Utilisez l\'identifiant transmis lors de la creation du compte. En cas de perte d\'acces, passez par votre coordination ou l\'administration de la plateforme.</div>'
              ,
                unsafe_allow_html=True,
            )

            if submitted:
                if username and password:
                    user = auth.authenticate(username, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        diagnostic = auth.diagnose_login_attempt(username)
                        if diagnostic.get("status") == "disabled":
                            st.error("Compte trouve, mais desactive. Demandez sa reactivation a l'administration.")
                        elif diagnostic.get("status") == "password_mismatch":
                            st.error("Compte reconnu, mais mot de passe incorrect. Vous pouvez utiliser votre identifiant ou votre email.")
                        elif diagnostic.get("status") == "not_found":
                            st.error("Aucun compte correspondant n'a ete trouve dans la base locale.")
                        else:
                            st.error("Connexion impossible pour le moment. Verifiez vos identifiants puis reessayez.")
                else:
                    st.warning("Veuillez remplir tous les champs.")

            # No account invitation
            st.markdown(
                '<div class="no-account">'
                '<div class="nac-label">Pas encore de compte ?</div>'
                '<div class="nac-title">Rejoignez la plateforme nationale</div>'
                '<div class="nac-copy">En tant qu\'autorité sanitaire de votre province ou zone de santé, vous pouvez demander un accès pour suivre les alertes et contribuer à la surveillance.</div>'
                '<div class="nac-perks">'
                '<span class="nac-perk">Tableau de bord dédié</span>'
                '<span class="nac-perk">Alertes en temps réel</span>'
                '<span class="nac-perk">Suivi provincial</span>'
                '<span class="nac-perk">Accès sécurisé</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button("Créer mon accès maintenant", key="switch_to_register"):
                st.session_state.auth_view = "register"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            # Register view
            if st.session_state.register_success:
                st.markdown(
                    '<div class="register-success">'
                    '<div class="reg-s-ico">✅</div>'
                    '<div class="reg-s-t">Compte créé avec succès !</div>'
                    '<div class="reg-s-c">Votre demande d\'accès a été soumise. Vous pouvez maintenant vous connecter avec vos identifiants.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.session_state.register_success = False
                if st.button("Me connecter maintenant →", key="go_login_after_reg"):
                    st.session_state.auth_view = "login"
                    st.rerun()
            else:
                st.markdown(
                    '<div class="ar-title">Créez votre accès</div>'
                    '<div class="ar-sub">Renseignez vos informations pour rejoindre la plateforme de surveillance sanitaire nationale.</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="auth-register-note">Chaque demande est rattachee a une province et a une zone de sante afin de garantir un acces adapte au bon niveau de responsabilite.</div>'
                  '<div class="auth-access-split">'
                  '<div class="auth-access-card"><strong>Acces public</strong><span>Cette page sert a demander un compte d\'autorite sanitaire rattache a une province et une zone de sante.</span></div>'
                  '<div class="auth-access-card admin"><strong>Compte admin</strong><span>Les administrateurs SAFE CONGO sont crees uniquement depuis la gouvernance interne par un autre administrateur.</span></div>'
                  '</div>'
                    '<div class="auth-form-shell">'
                    '<div class="auth-form-topline">'
                    '<div class="auth-form-chip"><span class="auth-form-chip-dot"></span>Nouvel acces</div>'
                    '<div class="auth-form-mini">Informations verifiees avant activation</div>'
                    '</div>'
                  '<div class="auth-form-note">Completez ce formulaire avec vos informations professionnelles pour soumettre votre demande d\'acces.</div>'
                  '</div>',
                    unsafe_allow_html=True,
                )

                provinces_options = [""] + PROVINCES if PROVINCES else [""]

                if GEO_DATA_ERROR:
                    st.warning("Le dataset géographique n'a pas pu être chargé.")
                c1, c2 = st.columns(2)
                with c1:
                  r_username = st.text_input("Identifiant *", placeholder="ex: dr.kabongo", key="register_username")
                  r_nom = st.text_input("Nom *", key="register_nom")
                  r_prenom = st.text_input("Prénom *", key="register_prenom")
                  r_email = st.text_input("Email *", key="register_email")
                with c2:
                  r_password = st.text_input("Mot de passe *", type="password", key="register_password")
                  r_confirm = st.text_input("Confirmer *", type="password", key="register_confirm")
                  r_telephone = st.text_input("Téléphone *", key="register_telephone")

                current_province = st.selectbox(
                  "Province *",
                  options=provinces_options,
                  key="register_province_dynamic",
                  format_func=lambda value: "Sélectionnez une province" if value == "" else value,
                )

                filtered_zones = ZONES_BY_PROVINCE.get(current_province, []) if current_province else []
                if current_province and not filtered_zones:
                  st.warning("Aucune zone de santé trouvée pour cette province dans le dataset.")

                zone_options = [""] + filtered_zones if current_province else [""]
                r_zone = st.selectbox(
                  "Zone de santé *",
                  options=zone_options,
                  index=0,
                  key=f"register_zone_form_{current_province or 'none'}",
                  format_func=lambda value: (
                    "Choisissez d'abord une province" if not current_province else "Sélectionnez une zone de santé" if value == "" else value
                  ),
                  disabled=not current_province,
                )

                st.markdown(
                  '<div class="auth-form-helper">Les champs marques d\'un asterisque sont obligatoires. Votre demande pourra etre activee apres verification des informations fournies.</div>',
                  unsafe_allow_html=True,
                )
                reg_submit = st.button("Soumettre ma demande", use_container_width=True, key="register_authority_submit")

                if reg_submit:
                  if all([r_username, r_password, r_confirm, r_nom, r_prenom, r_email, r_telephone, current_province, r_zone]):
                    if r_password != r_confirm:
                      st.error("Les mots de passe ne correspondent pas.")
                    elif len(r_password) < 6:
                      st.error("Mot de passe trop court (minimum 6 caractères).")
                    else:
                      ok, msg = auth.register_authority(
                        r_username,
                        r_password,
                        r_nom,
                        r_prenom,
                        r_email,
                        r_telephone,
                        current_province,
                        r_zone,
                      )
                      if ok:
                        st.session_state.register_success = True
                        st.rerun()
                      else:
                        st.error(msg)
                  else:
                    st.warning("Veuillez remplir tous les champs obligatoires (*).")

                st.markdown(
                  '<div class="auth-section-note">Deja inscrit ? Revenez simplement a la connexion pour acceder a votre espace des que votre compte est actif.</div>',
                  unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
