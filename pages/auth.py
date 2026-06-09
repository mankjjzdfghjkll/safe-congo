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
  border:1px solid rgba(11,77,149,.16)!important;
  border-radius:14px!important;
  box-shadow:0 10px 28px rgba(15,23,42,.12)!important;
}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
.stApp{background:linear-gradient(135deg,#eef6ff 0%,#e2f0fb 50%,#eef8ff 100%)!important}

/* --- OPTIMISATION DU FORMULAIRE ET CENTRAGE --- */
[data-testid="stForm"] {
  background: #ffffff !important;
  border: 1px solid #d8e9f6 !important;
  border-radius: 24px !important;
  padding: 30px 28px 24px 28px !important;
  box-shadow: 0 16px 40px rgba(10,60,120,.06) !important;
  margin: 0 auto !important;
  max-width: 480px !important;
}

/* Rapprochement des champs à l'intérieur du formulaire */
[data-testid="stForm"] [data-testid="stVerticalBlock"]{
  gap: 0.85rem !important;
}

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
  margin-bottom: 2px !important;
}
.stSelectbox>div>div{
  border-radius:10px!important;
  border:1.5px solid #c8dff0!important;
  background:#ffffff!important;
}

/* Boutons */
.stButton>button, .stFormSubmitButton>button{
  background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
  color:#fff!important;border:none!important;
  border-radius:12px!important;padding:14px 24px!important;
  font-weight:800!important;font-size:.92rem!important;
  letter-spacing:.4px!important;width:100%!important;
  box-shadow:0 6px 20px rgba(10,95,171,.24)!important;
  transition:all .25s!important;
  margin-top: 10px !important;
}
.stButton>button:hover, .stFormSubmitButton>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 10px 28px rgba(10,95,171,.32)!important;
}

/* Structure globale */
.auth-page{display:grid;grid-template-columns:1.05fr .95fr;min-height:calc(100vh - 34px);gap:0;border-radius:28px;overflow:hidden;box-shadow:0 28px 80px rgba(10,60,120,.14);width:min(96vw,1320px);margin:16px auto;animation:fadeUp .5s ease-out}
.auth-left{background:linear-gradient(160deg,#0a5fab 0%,#0d80d8 55%,#1aa2e2 100%);padding:52px 44px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;border-radius:26px 0 0 26px}
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
.al-feat-t{font-size:.88rem;font-weight:800;color:#fff;margin-bottom:2px}
.al-feat-c{font-size:.77rem;color:rgba(255,255,255,.72);line-height:1.46}
.al-stats{display:flex;gap:10px;flex-wrap:wrap}
.al-stat{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.2);border-radius:12px;padding:10px 14px;text-align:center}
.al-stat-v{font-family:'Sora',sans-serif;font-size:1.15rem;font-weight:800;color:#fff}
.al-stat-k{font-size:.6rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:rgba(255,255,255,.68);margin-top:2px}
.al-visual{display:flex;justify-content:center;margin:18px 0}

/* Colonne Droite Contenu */
.auth-right{background:#ffffff;padding:52px 48px;display:flex;flex-direction:column;justify-content:center;align-items:center}
.auth-right > *{width:min(100%,480px)} /* Aligné sur la taille idéale du formulaire */
.ar-kicker{display:inline-block;padding:6px 12px;border-radius:999px;background:#eef7ff;border:1px solid #c8dff0;font-size:.68rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#1a6db5;margin-bottom:12px}
.ar-title{font-family:'Sora',sans-serif;font-size:1.85rem;font-weight:800;color:#0a2040;letter-spacing:-.5px;margin-bottom:8px;text-align:center}
.ar-sub{font-size:.9rem;color:#6a8da8;line-height:1.64;margin-bottom:28px;text-align:center}

.auth-form-shell{background:linear-gradient(180deg,#fbfdff 0%,#f4faff 100%);border:1px solid #d8e9f6;border-radius:22px;padding:22px 20px 18px;box-shadow:0 10px 28px rgba(10,60,120,.05);margin:0 auto 14px auto;max-width:480px}
.auth-form-topline{display:flex;justify-content:between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.auth-form-chip{display:inline-flex;align-items:center;gap:8px;padding:7px 12px;border-radius:999px;background:#ffffff;border:1px solid #d7e8f5;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase;color:#0a5fab}
.auth-form-chip-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2)}
.auth-form-mini{font-size:.74rem;font-weight:700;color:#7a98b2}
.auth-form-note{margin:-2px 0 18px;font-size:.82rem;line-height:1.65;color:#6f8ca6}
.auth-form-helper{margin:12px auto 0 auto;padding:12px 14px;border-radius:14px;background:linear-gradient(180deg,#ffffff 0%,#f8fcff 100%);border:1px dashed #c8dff0;font-size:.77rem;line-height:1.6;color:#67839c;max-width:480px}
.auth-section-note{margin-top:16px;padding:12px 14px;border-radius:14px;background:#f0f8ff;border:1px solid #c8dff0;font-size:.78rem;line-height:1.6;color:#5a8aaa;max-width:480px}
.auth-register-note{margin-bottom:16px;padding:13px 14px;border-radius:14px;background:linear-gradient(135deg,#eef7ff,#f7fbff);border:1px solid #d3e6f4;font-size:.8rem;line-height:1.65;color:#62819c;max-width:480px}
.no-account{background:linear-gradient(135deg,#f0f9ff 0%,#e8f4fd 100%);border:1px solid #c8dff0;border-radius:18px;padding:20px 22px;margin:22px auto 0 auto;max-width:480px}
.nac-label{font-size:.7rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#5a9ac0;margin-bottom:8px}
.nac-title{font-size:1rem;font-weight:800;color:#0a2040;margin-bottom:6px}
.nac-copy{font-size:.84rem;color:#6a8da8;line-height:1.58;margin-bottom:12px}
.nac-perks{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.nac-perk{padding:5px 10px;border-radius:999px;background:#fff;border:1px solid #c8e4f5;font-size:.72rem;font-weight:700;color:#1a6db5}
.register-success{background:linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%);border:1px solid #6ee7b7;border-radius:16px;padding:18px 20px;text-align:center;max-width:480px}

@media(max-width:980px){.auth-page{grid-template-columns:1fr;margin:10px;min-height:auto}.auth-left{padding:34px 28px;border-radius:26px 26px 0 0}.auth-right{padding:34px 28px}.auth-right>*{width:100%}.al-headline{font-size:2.15rem}.al-headline em{font-size:1.8rem}}
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

def main():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    if "register_success" not in st.session_state:
        st.session_state.register_success = False

    auth = AuthSystem()

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
            f'<div class="al-headline">Votre espace <em>de veille.</em></div>'
            f'<div class="al-sub">Accédez en toute sécurité à votre tableau de bord de surveillance épidémiologique.</div>'
            f'<div class="al-features">'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Détection précoce</div><div class="al-feat-c">Signaux consolidés pour une lecture rapide et utile.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Analyse intelligente</div><div class="al-feat-c">Tendances, visualisations et prévisions fiables.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3Z"/><path d="m9.5 12 1.8 1.8 3.2-3.6"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Accès sécurisé</div><div class="al-feat-c">Espace personnel protégé, rôle adapté.</div></div></div>'
            f'</div>'
            f'<div class="al-stats">'
            f'<div class="al-stat"><div class="al-stat-v">Privé</div><div class="al-stat-k">Accès</div></div>'
            f'<div class="al-stat"><div class="al-stat-v">Guidée</div><div class="al-stat-k">Lecture</div></div>'
            f'<div class="al-stat"><div class="al-stat-v">Active</div><div class="al-stat-k">Veille</div></div>'
            f'</div>'
            f'</div>'
            f'<div class="al-visual" style="position:relative;z-index:2;margin-top:28px;opacity:.82">{VISUAL_SVG}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_right:
        if st.button("← Retour à l'accueil", key="auth_back"):
            st.session_state.auth_view = None
            switch_to_home_page()

        mode = st.session_state.auth_view or "login"
        kicker = "Connexion" if mode == "login" else "Créer un compte"
        st.markdown(f'<div style="text-align: center;"><div class="ar-kicker">{kicker}</div></div>', unsafe_allow_html=True)

        if mode == "login":
            st.markdown(
                '<div class="ar-title">Bon retour parmi nous</div>'
                '<div class="ar-sub">Connectez-vous pour accéder à votre espace de surveillance et de pilotage sanitaire.</div>',
                unsafe_allow_html=True,
            )
            
            # Formulaire unifié et centré
            with st.form("login_form_page"):
                st.markdown(
                    '<div class="auth-form-chip" style="margin-bottom:12px;"><span class="auth-form-chip-dot"></span>Connexion sécurisée</div>'
                    '<div class="auth-form-note" style="font-size:0.85rem; margin-bottom:16px;">Renseignez vos identifiants pour ouvrir votre espace de suivi épidémiologique.</div>',
                    unsafe_allow_html=True
                )
                username = st.text_input("Nom d'utilisateur", placeholder="Votre identifiant", label_visibility="visible")
                password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe", label_visibility="visible")
                submitted = st.form_submit_button("Accéder à mon espace", use_container_width=True)

            st.markdown(
                '<div class="auth-form-helper">Utilisez l\'identifiant transmis lors de la création du compte. En cas de perte d\'accès, passez par votre coordination ou l\'administration de la plateforme.</div>',
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
                    '<div class="auth-register-note">Chaque demande est rattachée à une province et à une zone de santé afin de garantir un accès adapté au bon niveau de responsabilité.</div>'
                    '<div class="auth-form-shell">'
                    '<div class="auth-form-topline">'
                    '<div class="auth-form-chip"><span class="auth-form-chip-dot"></span>Nouvel accès</div>'
                    '<div class="auth-form-mini">Informations vérifiées avant activation</div>'
                    '</div>'
                    '<div class="auth-form-note">Complétez ce formulaire avec vos informations professionnelles pour soumettre votre demande d\'accès.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

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

                with st.form("register_form_submit_part"):
                    reg_submit = st.form_submit_button("Soumettre ma demande", use_container_width=True)

                st.markdown(
                    '<div class="auth-form-helper">Les champs marqués d\'un astérisque sont obligatoires. Votre demande pourra être activée après vérification des informations fournies.</div>',
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
                                st.session_state.register_success = True
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        st.warning("Veuillez remplir tous les champs obligatoires (*).")

                st.markdown(
                    '<div class="auth-section-note">Déjà inscrit ? Revenez simplement à la connexion pour accéder à votre espace dès que votre compte est actif.</div>',
                    unsafe_allow_html=True,
                )

if __name__ == "__main__":
    main()