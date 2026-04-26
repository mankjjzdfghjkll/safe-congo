import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem

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
[data-testid="collapsedControl"]{display:none!important}

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
.auth-page{display:grid;grid-template-columns:1.05fr .95fr;min-height:100vh;gap:0;border-radius:28px;overflow:hidden;box-shadow:0 28px 80px rgba(10,60,120,.14);margin:16px;animation:fadeUp .5s ease-out}
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
.auth-right{background:#ffffff;padding:52px 48px;display:flex;flex-direction:column;justify-content:center}
.ar-back{display:inline-flex;align-items:center;gap:7px;font-size:.8rem;font-weight:700;color:#5a8aaa;cursor:pointer;margin-bottom:34px;border:none;background:none;padding:0;text-decoration:none;transition:color .2s}
.ar-back:hover{color:#0a84d0}
.ar-back svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.ar-kicker{display:inline-block;padding:6px 12px;border-radius:999px;background:#eef7ff;border:1px solid #c8dff0;font-size:.68rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#1a6db5;margin-bottom:12px}
.ar-title{font-family:'Sora',sans-serif;font-size:1.85rem;font-weight:800;color:#0a2040;letter-spacing:-.5px;margin-bottom:8px}
.ar-sub{font-size:.9rem;color:#6a8da8;line-height:1.64;margin-bottom:28px}

.no-account{background:linear-gradient(135deg,#f0f9ff 0%,#e8f4fd 100%);border:1px solid #c8dff0;border-radius:18px;padding:20px 22px;margin-top:22px}
.nac-label{font-size:.7rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#5a9ac0;margin-bottom:8px}
.nac-title{font-size:1rem;font-weight:800;color:#0a2040;margin-bottom:6px}
.nac-copy{font-size:.84rem;color:#6a8da8;line-height:1.58;margin-bottom:12px}
.nac-perks{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.nac-perk{padding:5px 10px;border-radius:999px;background:#fff;border:1px solid #c8e4f5;font-size:.72rem;font-weight:700;color:#1a6db5}

.register-success{background:linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%);border:1px solid #6ee7b7;border-radius:16px;padding:18px 20px;text-align:center}
.reg-s-ico{font-size:2rem;margin-bottom:8px}
.reg-s-t{font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:#065f46;margin-bottom:6px}
.reg-s-c{font-size:.86rem;color:#047857;line-height:1.58}

@media(max-width:860px){.auth-page{grid-template-columns:1fr;margin:8px}.auth-left{padding:32px 24px}.auth-right{padding:32px 24px}.al-headline{font-size:2rem}.al-headline em{font-size:1.7rem}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PROVINCES = [
    "Kinshasa","Kongo Central","Kwango","Kwilu","Mai-Ndombe",
    "Equateur","Sud-Ubangi","Nord-Ubangi","Mongala","Tshopo",
    "Bas-Uele","Haut-Uele","Ituri","Nord-Kivu","Sud-Kivu",
    "Maniema","Tanganyika","Haut-Lomami","Lualaba","Haut-Katanga",
    "Lomami","Sankuru","Kasai","Kasai Central","Kasai Oriental",
]

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
  <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
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
  <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="white" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
  </polyline>
  <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="white" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
    <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
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
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Detection precoce</div><div class="al-feat-c">Signaux d\'alerte sur 26 provinces en temps reel.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Analyse intelligente</div><div class="al-feat-c">Tendances, visualisations et previsions fiables.</div></div></div>'
            f'<div class="al-feat"><div class="al-feat-ico"><svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3Z"/><path d="m9.5 12 1.8 1.8 3.2-3.6"/></svg></div><div class="al-feat-text"><div class="al-feat-t">Acces securise</div><div class="al-feat-c">Espace personnel protege, role adapte.</div></div></div>'
            f'</div>'

            # stats
            f'<div class="al-stats">'
            f'<div class="al-stat"><div class="al-stat-v">26</div><div class="al-stat-k">Provinces</div></div>'
            f'<div class="al-stat"><div class="al-stat-v">516</div><div class="al-stat-k">Zones</div></div>'
            f'<div class="al-stat"><div class="al-stat-v">24/7</div><div class="al-stat-k">Alerte</div></div>'
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
        st.markdown(
            '<div style="background:#fff;border-radius:26px;padding:52px 46px;min-height:86vh;'
            'box-shadow:0 22px 58px rgba(10,60,120,.10)">',
            unsafe_allow_html=True,
        )

        # back button
        if st.button("← Retour à l'accueil", key="auth_back"):
            st.session_state.auth_view = None
            st.switch_page("app.py")

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

            with st.form("login_form_page"):
                username = st.text_input("Nom d'utilisateur", placeholder="Votre identifiant")
                password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
                submitted = st.form_submit_button("Se connecter →", use_container_width=True)

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

                with st.form("register_form_page"):
                    c1, c2 = st.columns(2)
                    with c1:
                        r_username  = st.text_input("Identifiant *", placeholder="ex: dr.kabongo")
                        r_nom       = st.text_input("Nom *")
                        r_prenom    = st.text_input("Prénom *")
                        r_email     = st.text_input("Email *")
                    with c2:
                        r_password  = st.text_input("Mot de passe *", type="password")
                        r_confirm   = st.text_input("Confirmer *", type="password")
                        r_telephone = st.text_input("Téléphone *")
                        r_province  = st.selectbox("Province *", PROVINCES)
                    r_zone = st.text_input("Zone de santé *", placeholder="Votre zone de santé")
                    reg_submit = st.form_submit_button("Soumettre ma demande →", use_container_width=True)

                if reg_submit:
                    if all([r_username, r_password, r_confirm, r_nom, r_prenom, r_email, r_telephone, r_province, r_zone]):
                        if r_password != r_confirm:
                            st.error("Les mots de passe ne correspondent pas.")
                        elif len(r_password) < 6:
                            st.error("Mot de passe trop court (minimum 6 caractères).")
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
                    '<div style="margin-top:16px;padding:12px 14px;border-radius:12px;background:#f0f8ff;border:1px solid #c8dff0">'
                    '<p style="font-size:.76rem;color:#5a8aaa;margin:0;line-height:1.6">'
                    'Déjà inscrit ? Utilisez le bouton <strong>Retour</strong> ci-dessus puis connectez-vous.'
                    '</p></div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

main()
