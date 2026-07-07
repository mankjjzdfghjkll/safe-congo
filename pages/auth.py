import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem

st.set_page_config(
    page_title="Accès - SAFE CONGO",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "province_selection" not in st.session_state:
    st.session_state.province_selection = None

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
  width:38px!important;
  height:38px!important;
  min-width:38px!important;
  min-height:38px!important;
  align-items:center!important;
  justify-content:center!important;
  padding:0!important;
  border:2px solid rgba(10,95,171,.32)!important;
  border-radius:12px!important;
  box-shadow:0 10px 24px rgba(10,60,120,.16)!important;
}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important;stroke:#0b4d95!important;width:21px!important;height:21px!important}
.stApp{background:
  linear-gradient(135deg,rgba(255,255,255,.54) 0%,rgba(255,255,255,0) 30%),
  radial-gradient(circle at 8% 12%,rgba(26,162,226,.16),transparent 30%),
  radial-gradient(circle at 96% 8%,rgba(10,95,171,.14),transparent 26%),
  linear-gradient(135deg,#eef6ff 0%,#e6f2fd 48%,#f0f8ff 100%)!important}
.block-container{padding-top:18px!important;padding-bottom:18px!important;max-width:1380px!important}

/* --- OPTIMISATION DU FORMULAIRE ET CENTRAGE --- */
[data-testid="stForm"] {
  background: linear-gradient(180deg,#ffffff 0%,#f8fbfd 100%) !important;
  border: 1px solid #d7e6ed !important;
  border-radius: 20px !important;
  padding: 26px 26px 22px 26px !important;
  box-shadow: 0 18px 45px rgba(10,60,120,.08) !important;
  margin: 0 auto !important;
  max-width: 480px !important;
}

/* Rapprochement des champs à l'intérieur du formulaire */
[data-testid="stForm"] [data-testid="stVerticalBlock"]{
  gap: 0.85rem !important;
}

.stTextInput>div>div>input{
  border-radius:12px!important;
  border:1.5px solid #c8dce6!important;
  padding:13px 14px!important;
  background:#ffffff!important;
  color:#0a2040!important;
  font-size:.92rem!important;
  transition:border-color .2s,box-shadow .2s!important;
}
.stTextInput input[type="password"]{
  -webkit-text-security:disc!important;
  text-security:disc!important;
}
.stTextInput input[type="text"][aria-label*="Mot de passe"],
.stTextInput input[type="text"][aria-label*="Confirmer"]{
  -webkit-text-security:none!important;
  text-security:none!important;
}
.stTextInput button[aria-label*="password"],
.stTextInput button[aria-label*="Password"],
.stTextInput button[aria-label*="mot de passe"]{
  color:#0a5fab!important;
  background:#eef7ff!important;
  border:1px solid #c8dce6!important;
  border-radius:10px!important;
}
.stTextInput>div>div>input:focus{
  border-color:#0a84d0!important;
  box-shadow:0 0 0 3px rgba(10,132,208,.12)!important;
}
.stTextInput label,.stSelectbox label{
  color:#26465b!important;font-weight:800!important;font-size:.82rem!important;
  margin-bottom: 2px !important;
}
.stSelectbox>div>div{
  border-radius:12px!important;
  border:1.5px solid #c8dce6!important;
  background:#ffffff!important;
}

/* Boutons */
.stButton>button, .stFormSubmitButton>button{
  background:linear-gradient(135deg,#083f73 0%,#0a5fab 50%,#1aa2e2 100%)!important;
  color:#fff!important;border:1px solid rgba(255,255,255,.16)!important;
  border-radius:14px!important;padding:12px 24px!important;
  font-weight:800!important;font-size:.94rem!important;
  letter-spacing:.3px!important;width:auto!important;
  min-width:240px!important;
  max-width:320px!important;
  box-shadow:0 14px 34px rgba(10,95,171,.24)!important;
  transition:all .25s ease!important;
  margin-top: 14px !important;
}
.stFormSubmitButton>button {
  margin-top: 8px !important;
  min-width: 240px !important;
  width: 240px !important;
  max-width: 240px !important;
  padding: 13px 20px !important;
  border-radius: 14px !important;
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
.stButton>button:hover, .stFormSubmitButton>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 16px 38px rgba(10,95,171,.30)!important;
  filter:saturate(1.06)!important;
}
/* Structure globale */
.auth-page{display:grid;grid-template-columns:1.05fr .95fr;min-height:calc(100vh - 34px);gap:0;border-radius:26px;overflow:hidden;box-shadow:0 32px 90px rgba(10,60,120,.16);width:min(96vw,1320px);margin:16px auto;animation:fadeUp .5s ease-out;background:rgba(255,255,255,.84);backdrop-filter:blur(22px);border:1px solid rgba(255,255,255,.6)}
.auth-left{background:linear-gradient(145deg,#083f73 0%,#0a5fab 52%,#1aa2e2 100%);padding:52px 44px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;border-radius:24px;box-shadow:inset 0 1px 0 rgba(255,255,255,.18),0 24px 60px rgba(10,60,120,.20)}
.auth-left-dots{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.1) 1px,transparent 1px);background-size:24px 24px;pointer-events:none}
.auth-left-glow{position:absolute;inset:0;background:radial-gradient(ellipse at 80% 10%,rgba(255,255,255,.16),transparent 36%),radial-gradient(ellipse at 10% 90%,rgba(7,52,95,.30),transparent 30%);pointer-events:none}
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
.al-feat-t{font-size:.88rem;font-weight:800;color:#fff;margin-bottom:2px}
.al-feat-c{font-size:.77rem;color:rgba(255,255,255,.72);line-height:1.46}
.al-stats{display:flex;gap:10px;flex-wrap:wrap}
.al-stat{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.2);border-radius:12px;padding:10px 14px;text-align:center}
.al-stat-v{font-family:'Sora',sans-serif;font-size:1.15rem;font-weight:800;color:#fff}
.al-stat-k{font-size:.6rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:rgba(255,255,255,.68);margin-top:2px}
.al-visual{display:flex;justify-content:center;margin:18px 0}

/* Colonne Droite Contenu */
.auth-right{background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%);padding:52px 48px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;border-radius:24px;border:1px solid rgba(200,226,245,.82);box-shadow:0 24px 60px rgba(10,60,120,.08)}
.auth-right::before{content:"";position:absolute;inset:-30% 12% auto auto;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(10,95,171,.08),rgba(10,95,171,0) 70%);pointer-events:none}
.auth-right::after{content:"";position:absolute;inset:auto auto -20% -12%;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(26,162,226,.08),rgba(26,162,226,0) 72%);pointer-events:none}
.auth-right > *{width:min(100%,480px);position:relative;z-index:1} /* Aligné sur la taille idéale du formulaire */
.ar-title{font-family:'Sora',sans-serif;font-size:1.85rem;font-weight:800;color:#0a2040;letter-spacing:-.5px;margin-bottom:8px;text-align:center}
.ar-sub{font-size:.9rem;color:#6a8da8;line-height:1.64;margin-bottom:28px;text-align:center}

.auth-form-shell{background:linear-gradient(180deg,rgba(255,255,255,.98) 0%,rgba(247,251,252,.98) 100%);border:1px solid #d7e6ed;border-radius:20px;padding:24px 22px 20px;box-shadow:0 18px 42px rgba(15,74,99,.08);margin:0 auto 14px auto;max-width:480px}
.auth-form-topline{display:flex;justify-content:between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.auth-form-chip{display:inline-flex;align-items:center;gap:8px;padding:7px 12px;border-radius:999px;background:#ffffff;border:1px solid #d7e8f5;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase;color:#0a5fab}
.auth-form-chip-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2)}
.auth-form-mini{font-size:.74rem;font-weight:700;color:#7a98b2}
.auth-form-note{margin:-2px 0 18px;font-size:.82rem;line-height:1.65;color:#6f8ca6}
.auth-register-note{margin-bottom:16px;padding:13px 14px;border-radius:14px;background:linear-gradient(135deg,#eef7ff,#f7fbff);border:1px solid #d3e6f4;font-size:.8rem;line-height:1.65;color:#517386;max-width:480px}
.auth-register-hero{margin:0 auto 16px auto;max-width:480px;padding:20px 22px;border-radius:20px;background:linear-gradient(135deg,#083f73 0%,#0a5fab 52%,#1aa2e2 100%);box-shadow:0 20px 50px rgba(10,95,171,.20);color:#fff}
.auth-register-hero-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 11px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.22);font-size:.68rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px}
.auth-register-hero .ar-title{color:#fff!important;text-align:left!important;margin-bottom:8px!important}
.auth-register-hero .ar-sub{color:rgba(255,255,255,.9)!important;text-align:left!important;margin-bottom:0!important}
.auth-register-section{margin:0 auto 16px auto;max-width:480px;padding:18px 20px;border-radius:18px;background:#ffffff;border:1px solid #d7e6ed;box-shadow:0 12px 32px rgba(15,74,99,.06)}
.auth-register-section-title{font-size:.95rem;font-weight:800;color:#0a2040;margin-bottom:6px}
.auth-register-section-sub{font-size:.8rem;line-height:1.6;color:#6f8ca6}
.register-success{background:linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%);border:1px solid #6ee7b7;border-radius:16px;padding:18px 20px;text-align:center;max-width:480px}

@media(max-width:980px){.auth-page{grid-template-columns:1fr;margin:10px;min-height:auto}.auth-left{padding:34px 28px;border-radius:26px 26px 0 0}.auth-right{padding:34px 28px}.auth-right>*{width:100%}.al-headline{font-size:2.15rem}.al-headline em{font-size:1.8rem}}

/* Polish final */
.auth-register-hero{position:relative;overflow:hidden}
.auth-register-hero::before{content:"";position:absolute;inset:auto -20% -40% auto;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.2),rgba(255,255,255,0) 72%);pointer-events:none}
.auth-register-section{position:relative;overflow:hidden}
.auth-register-section::after{content:"";position:absolute;right:-18px;top:-18px;width:70px;height:70px;border-radius:50%;background:radial-gradient(circle,rgba(10,95,171,.08),rgba(10,95,171,0) 70%);pointer-events:none}
.stTextInput>div>div>input:hover{border-color:#0a84d0!important}
.stSelectbox>div>div:hover{border-color:#0a84d0!important}
.auth-register-section{backdrop-filter:blur(6px)}
.auth-switch-text{margin:16px auto 0;text-align:center;color:#607d8f;font-size:.86rem;font-weight:700}
.auth-switch-text a{color:#0a5fab!important;text-decoration:none!important;font-weight:900;border-bottom:1px solid rgba(10,95,171,.28)}
.auth-switch-text a:hover{color:#083f73!important;border-bottom-color:#083f73}
.auth-home-row{display:flex;justify-content:center;margin:14px auto 0}
.auth-home-button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 18px;border-radius:999px;background:#eef7ff;border:1px solid #c9e2f3;color:#0a5fab!important;text-decoration:none!important;font-size:.84rem;font-weight:900;box-shadow:0 10px 24px rgba(10,95,171,.09)}
.auth-home-button:hover{background:#ffffff;border-color:#0a84d0;color:#083f73!important;box-shadow:0 14px 30px rgba(10,95,171,.14)}
.auth-trust-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}
.auth-trust-item{padding:10px;border-radius:14px;background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.18);color:#fff}
.auth-trust-item strong{display:block;font:800 .86rem 'Sora',sans-serif;color:#fff}
.auth-trust-item span{display:block;margin-top:3px;font-size:.66rem;font-weight:700;color:rgba(255,255,255,.72);text-transform:uppercase;letter-spacing:.8px}
.field-section-label{max-width:480px;margin:4px auto 10px;padding:0 2px;color:#26465b;font-size:.76rem;font-weight:900;letter-spacing:1.2px;text-transform:uppercase}
@media(max-width:720px){.auth-trust-grid{grid-template-columns:1fr}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DEFAULT_PROVINCES = [
    "Kinshasa","Kongo Central","Kwango","Kwilu","Mai-Ndombe",
    "Equateur","Sud-Ubangi","Nord-Ubangi","Mongala","Tshopo",
    "Bas-Uele","Haut-Uele","Ituri","Nord-Kivu","Sud-Kivu",
    "Maniema","Tanganyika","Haut-Lomami","Lualaba","Haut-Katanga",
    "Lomami","Sankuru","Kasai","Kasai Central","Kasai Oriental",
]

PROVINCE_TO_ZONES = {}
try:
    df_geo = pd.read_csv("data/processed/donnees_agregees_nettoyees.csv")
    provinces_from_data = []
    seen = set()
    for p in df_geo["PROVINCE"].dropna():
        p_clean = str(p).strip()
        if p_clean and p_clean.lower() != "nan" and p_clean not in seen:
            provinces_from_data.append(p_clean)
            seen.add(p_clean)
    PROVINCES = provinces_from_data

    for province in PROVINCES:
        zones = df_geo[df_geo["PROVINCE"] == province]["ZONE_SANTE"].dropna().unique()
        zones = [str(z).strip() for z in zones if str(z).strip() and str(z).strip().lower() != "nan"]
        PROVINCE_TO_ZONES[province] = sorted(zones)
except Exception:
    PROVINCES = DEFAULT_PROVINCES
    PROVINCE_TO_ZONES = {}

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

def on_province_change():
    st.session_state.province_selection = st.session_state.register_province_unique
    st.session_state.register_zone_unique = ""
    st.session_state.zone_manual = ""


def main():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    auth_action = st.query_params.get("auth_action")
    if auth_action in {"login", "register"}:
        st.session_state.auth_view = auth_action
        st.query_params.clear()
    if "register_success" not in st.session_state:
        st.session_state.register_success = False

    auth = AuthSystem()

    # --- Aucune gestion de paramètre view ---

    if st.session_state.user is not None:
        u = st.session_state.user
        if u["role"] == "admin":
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.switch_page("pages/authority_dashboard.py")
        return

    col_left, col_right = st.columns([1.05, 0.95])

    with col_left:
        st.markdown(
            f'<div class="auth-left">'
            f'<div class="auth-left-dots"></div>'
            f'<div class="auth-left-glow"></div>'
            f'<div class="auth-left-inner">'
            f'<div class="al-logo">{SHIELD_SVG}<div><div class="al-name">SAFE CONGO</div><div class="al-tag">Veille sanitaire nationale</div></div></div>'
            f'<div class="al-headline">Espace sécurisé <em>de veille.</em></div>'
            f'<div class="al-sub">Connectez-vous ou demandez un accès pour suivre les alertes, les données et les décisions sanitaires depuis une interface contrôlée.</div>'
            f'<div class="al-features">'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Lecture rapide</div><div class="al-feat-c">Un accès direct aux signaux utiles, sans parcours inutile.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Pilotage sanitaire</div><div class="al-feat-c">Tableaux de bord, alertes et suivi territorial regroupés.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3Z"/><path d="m9.5 12 1.8 1.8 3.2-3.6"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Accès maîtrisé</div><div class="al-feat-c">Chaque compte est associé à un rôle et à une zone de responsabilité.</div></div></div>'
            f'</div>'
            f'<div class="auth-trust-grid">'
            f'<div class="auth-trust-item"><strong>Privé</strong><span>Session</span></div>'
            f'<div class="auth-trust-item"><strong>Rôles</strong><span>Accès</span></div>'
            f'<div class="auth-trust-item"><strong>RDC</strong><span>Veille</span></div>'
            f'</div>'
            f'</div>'
            f'<div class="al-visual" style="position:relative;z-index:2;margin-top:28px;opacity:.82">{VISUAL_SVG}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_right:
        mode = st.session_state.auth_view or "login"

        # Show success message coming from a recent registration, once
        if "register_message" in st.session_state:
            st.success(st.session_state.pop("register_message"))

        if mode == "login":
            st.markdown(
                '<div class="ar-title">Bon retour</div>'
                '<div class="ar-sub">Renseignez vos identifiants pour ouvrir votre espace de surveillance et accéder aux outils autorisés.</div>',
                unsafe_allow_html=True,
            )

            # Formulaire unifié et centré
            with st.form("login_form_page"):
                st.markdown(
                    """<div class="auth-form-chip" style="margin-bottom:12px;"><span class="auth-form-chip-dot"></span>Session privée</div>
<div class="auth-form-note" style="font-size:0.85rem; margin-bottom:16px;">Utilisez l'identifiant ou l'adresse email associée à votre compte SAFE CONGO.</div>""",
                    unsafe_allow_html=True,
                )
                # Préremplissage si fourni après création de compte
                username = st.text_input(
                    "Identifiant ou email",
                    value=st.session_state.get("prefill_username", ""),
                    placeholder="ex: autorite_kinshasa",
                    label_visibility="visible",
                    key="login_username",
                )
                password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe", label_visibility="visible")
                # Bouton de connexion centré et plus léger visuellement
                _, b2, _ = st.columns([1, 2, 1])
                with b2:
                    submitted = st.form_submit_button("Ouvrir mon espace", use_container_width=False)

            st.markdown(
                '<div class="auth-switch-text">Pas de compte ? <a href="/auth?auth_action=register" target="_self">Créer mon accès</a></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="auth-home-row"><a class="auth-home-button" href="/" target="_self">Retour à l’accueil</a></div>',
                unsafe_allow_html=True,
            )
            if submitted:
                if username and password:
                    user = auth.authenticate(username, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects ou compte désactivé.")
                else:
                    st.warning("Veuillez remplir tous les champs.")
        else:
            # --- AFFICHAGE DU FORMULAIRE D'INSCRIPTION ---
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
                    '<div class="auth-register-hero">'
                    '<div class="auth-register-hero-badge">Demande d\'accès</div>'
                    '<div class="ar-title">Créer un accès autorité</div>'
                    '<div class="ar-sub">Renseignez vos informations professionnelles pour rejoindre le dispositif de surveillance SAFE CONGO.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="auth-register-section">'
                    '<div class="auth-register-section-title">Fiche de demande</div>'
                    '<div class="auth-register-section-sub">Les champs marqués d\'un astérisque sont obligatoires. Choisissez un identifiant simple et un mot de passe d\'au moins 8 caractères.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="field-section-label">Identité et contact</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    r_username = st.text_input("Identifiant *", placeholder="ex: dr.kabongo")
                    r_nom = st.text_input("Nom *")
                    r_prenom = st.text_input("Prénom *")
                    r_email = st.text_input("Email *")
                with c2:
                    r_password = st.text_input("Mot de passe *", type="password")
                    r_confirm = st.text_input("Confirmer *", type="password")
                    r_telephone = st.text_input("Téléphone *")
                    st.markdown('<div class="field-section-label" style="margin-top:10px">Affectation sanitaire</div>', unsafe_allow_html=True)
                    
                    try:
                        idx = PROVINCES.index(st.session_state.province_selection) if st.session_state.province_selection in PROVINCES else None
                    except ValueError:
                        idx = None

                    r_province = st.selectbox(
                        "Province *",
                        PROVINCES,
                        index=idx,
                        placeholder="Choisissez une province",
                        key="register_province_unique",
                        on_change=on_province_change
                    )

                    if r_province is not None:
                        zone_list = PROVINCE_TO_ZONES.get(r_province, [])
                        if zone_list:
                            r_zone = st.selectbox(
                                "Zone de santé *",
                                zone_list,
                                index=None,
                                placeholder="Choisissez une zone de santé",
                                key="register_zone_unique"
                            )
                        else:
                            st.warning(f"Aucune zone trouvée pour '{r_province}'.")
                            r_zone = st.text_input("Zone de santé *", placeholder="Ex: Kalonda Est", key="zone_manual")
                    else:
                        r_zone = st.text_input("Zone de santé *", disabled=True, placeholder="Sélectionnez d'abord une province")

                _, submit_col, _ = st.columns([1, 1.35, 1])
                with submit_col:
                    reg_submit = st.button(
                        "Soumettre ma demande",
                        key="register_submit_button",
                        use_container_width=True,
                    )

                st.markdown(
                    '<div class="auth-switch-text">Déjà inscrit ? <a href="/auth?auth_action=login" target="_self">Revenir à la connexion</a></div>',
                    unsafe_allow_html=True,
                )

                if reg_submit:
                    required_fields = [r_username, r_password, r_confirm, r_nom, r_prenom, r_email, r_telephone, r_province, r_zone]
                    if all(required_fields):
                        if r_password != r_confirm:
                            st.error("Les mots de passe ne correspondent pas.")
                        elif len(r_password) < 8:
                            st.error("Mot de passe trop court (minimum 8 caractères).")
                        else:
                            ok, msg = auth.register_authority(
                                r_username, r_password, r_nom, r_prenom,
                                r_email, r_telephone, r_province, r_zone,
                            )
                            if ok:
                              # Redirect to login and prefill username for convenience
                              st.session_state.auth_view = "login"
                              st.session_state.prefill_username = r_username
                              st.session_state.register_message = "Compte créé avec succès. Connectez-vous avec vos identifiants."
                              st.rerun()
                            else:
                                st.error(msg)
                    else:
                        st.markdown(
                            '<div style="padding:12px 14px; border-radius:12px; background:#fff7ed; border:1px solid #fdba74; color:#7c2d12; font-weight:700; font-size:0.95rem; text-align:center;">Veuillez remplir tous les champs obligatoires (*).</div>',
                            unsafe_allow_html=True,
                        )


if __name__ == "__main__":
    main()
