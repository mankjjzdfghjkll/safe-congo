import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem, require_auth
from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND

SHIELD_SVG = PUBLIC_SIDEBAR_BRAND

SHIELD_SVG = """<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
@keyframes floatUp{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes textGlow{0%,100%{text-shadow:0 0 10px rgba(0,212,255,.4)}50%{text-shadow:0 0 20px rgba(0,212,255,.8),0 0 40px rgba(0,102,204,.6)}}
.sidebar-logo-wrap{display:flex;flex-direction:column;align-items:center;padding:28px 0 16px;position:relative}
.sidebar-logo-glow{position:absolute;width:110px;height:110px;top:20px;border-radius:50%;background:radial-gradient(circle,rgba(0,102,204,.35) 0%,transparent 70%);animation:floatUp 4s ease-in-out infinite}
.sidebar-logo-svg{position:relative;z-index:2;animation:floatUp 4s ease-in-out infinite;filter:drop-shadow(0 0 14px rgba(0,212,255,.5)) drop-shadow(0 4px 12px rgba(0,0,0,.6))}
.sidebar-brand{font-family:'Orbitron',sans-serif;font-size:1.05rem;font-weight:900;letter-spacing:3px;color:#fff!important;text-align:center;margin-top:12px;animation:textGlow 3s ease-in-out infinite;text-transform:uppercase}
.sidebar-tagline{font-size:.65rem;letter-spacing:2px;text-align:center;color:rgba(0,212,255,.7)!important;text-transform:uppercase;margin-top:3px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#080c18 0%,#0d1830 60%,#060b16 100%)!important;border-right:1px solid rgba(0,212,255,.15)!important}
</style>
<div class="sidebar-logo-wrap">
    <div class="sidebar-logo-glow"></div>
    <svg class="sidebar-logo-svg" width="80" height="95" viewBox="0 0 120 145" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="sidebarShieldGrad" x1="0%" y1="0%" x2="100%" y2="120%">
                <stop offset="0%" stop-color="#9BE9FF"/>
                <stop offset="34%" stop-color="#1795FF"/>
                <stop offset="70%" stop-color="#0058B8"/>
                <stop offset="100%" stop-color="#051A46"/>
            </linearGradient>
            <linearGradient id="sidebarShieldGloss" x1="20%" y1="0%" x2="72%" y2="62%">
                <stop offset="0%" stop-color="rgba(255,255,255,.46)"/>
                <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
            </linearGradient>
            <linearGradient id="sidebarRingGold" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FFF1A1"/>
                <stop offset="45%" stop-color="#FFD45E"/>
                <stop offset="100%" stop-color="#A86B0B"/>
            </linearGradient>
            <linearGradient id="sidebarWaveYellow" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#FFD447"/><stop offset="40%" stop-color="#FFF59D"/><stop offset="70%" stop-color="#FFCA28"/><stop offset="100%" stop-color="#FFD447"/><animateTransform attributeName="gradientTransform" type="translate" values="-0.8 0;0.8 0;-0.8 0" dur="3.2s" repeatCount="indefinite"/></linearGradient>
            <linearGradient id="sidebarWaveBlue" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#0077C8"/><stop offset="38%" stop-color="#2DB6FF"/><stop offset="68%" stop-color="#0099E5"/><stop offset="100%" stop-color="#0077C8"/><animateTransform attributeName="gradientTransform" type="translate" values="0.8 0;-0.8 0;0.8 0" dur="3.4s" repeatCount="indefinite"/></linearGradient>
            <linearGradient id="sidebarWaveRed" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#A90D1F"/><stop offset="42%" stop-color="#FF4D5F"/><stop offset="72%" stop-color="#CE1126"/><stop offset="100%" stop-color="#A90D1F"/><animateTransform attributeName="gradientTransform" type="translate" values="-0.6 0;0.6 0;-0.6 0" dur="2.9s" repeatCount="indefinite"/></linearGradient>
            <filter id="sidebarShadow" x="-30%" y="-30%" width="170%" height="170%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3.4" result="blur"/>
                <feOffset dx="0" dy="5" result="offset"/>
                <feFlood flood-color="rgba(5,22,58,.34)"/>
                <feComposite in2="offset" operator="in"/>
                <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="sidebarGlow" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="2.1" result="blur"/>
                <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        </defs>
        <ellipse cx="60" cy="70" rx="48" ry="48" fill="none" stroke="rgba(0,102,204,.12)" stroke-width="1" stroke-dasharray="3 7">
            <animateTransform attributeName="transform" type="rotate" from="0 60 70" to="360 60 70" dur="18s" repeatCount="indefinite"/>
        </ellipse>
        <ellipse cx="60" cy="70" rx="55" ry="55" fill="none" stroke="rgba(0,212,255,.18)" stroke-width="1.2" stroke-dasharray="6 4">
            <animateTransform attributeName="transform" type="rotate" from="0 60 70" to="-360 60 70" dur="22s" repeatCount="indefinite"/>
        </ellipse>
        <g>
            <circle cx="60" cy="70" r="45" fill="rgba(255,255,255,.22)"/>
            <circle cx="60" cy="70" r="44" fill="url(#sidebarShieldGrad)" filter="url(#sidebarShadow)"/>
            <circle cx="60" cy="70" r="44" fill="url(#sidebarShieldGloss)" opacity=".5"/>
            <circle cx="60" cy="70" r="48" fill="none" stroke="url(#sidebarRingGold)" stroke-width="2.4" opacity=".94"/>
            <circle cx="60" cy="70" r="36" fill="none" stroke="rgba(255,255,255,.18)" stroke-width="1.1"/>
        </g>
        <g opacity=".56">
            <line x1="60" y1="15" x2="60" y2="21" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="60" y1="119" x2="60" y2="125" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="7" y1="70" x2="13" y2="70" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="107" y1="70" x2="113" y2="70" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
        </g>
        <g>
            <animateTransform attributeName="transform" type="rotate" from="0 60 70" to="360 60 70" dur="14s" repeatCount="indefinite"/>
            <circle cx="60" cy="23" r="2.5" fill="#00E1FF"/>
            <circle cx="107" cy="70" r="1.8" fill="#9FE9FF" opacity=".88"/>
            <circle cx="60" cy="117" r="2.1" fill="#64C8FF" opacity=".74"/>
            <circle cx="13" cy="70" r="1.7" fill="#5FB8FF" opacity=".74"/>
        </g>
        <g>
            <path d="M60 38 L79 49 L79 73 Q79 92 60 103 Q41 92 41 73 L41 49 Z" fill="rgba(4,21,60,.24)" transform="translate(1.5,4)"/>
            <path d="M60 38 L79 49 L79 73 Q79 92 60 103 Q41 92 41 73 L41 49 Z" fill="rgba(255,255,255,.06)"/>
            <path d="M60 38 L79 49 L79 73 Q79 92 60 103 Q41 92 41 73 L41 49 Z" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="1"/>
        </g>
        <g filter="url(#sidebarGlow)">
            <path d="M31 70 H44 L49 58 L55 83 L60 69 L68 69 L73 54 L79 80 L84 70 H89" fill="none" stroke="#00EEFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="140" stroke-dashoffset="140">
                <animate attributeName="stroke-dashoffset" values="140;0;0;140" dur="4.2s" repeatCount="indefinite"/>
            </path>
        </g>
        <g>
            <circle cx="60" cy="51" r="5.4" fill="url(#sidebarWaveYellow)"/>
            <path d="M60 58 C66 58 71 62 71 69 V79 C71 82 68.5 84 65.5 84 H54.5 C51.5 84 49 82 49 79 V69 C49 62 54 58 60 58 Z" fill="url(#sidebarWaveBlue)"/>
            <rect x="57" y="58" width="6" height="26" rx="3" fill="url(#sidebarWaveRed)"/>
        </g>
        <circle cx="60" cy="70" r="28" fill="none" stroke="rgba(0,235,255,.26)" stroke-width="1.1">
            <animate attributeName="r" values="28;44" dur="3.2s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values=".55;0" dur="3.2s" repeatCount="indefinite"/>
        </circle>
    </svg>
    <div class="sidebar-brand">SAFE CONGO</div>
    <div class="sidebar-tagline">Surveillance &#8226; RDC</div>
</div>"""

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*{font-family:'Inter',sans-serif}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebarNav"]{display:none}
@keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-1000px 0}100%{background-position:1000px 0}}
@keyframes shieldPulse{0%,100%{filter:drop-shadow(0 6px 18px rgba(0,102,204,.6));transform:scale(1)}50%{filter:drop-shadow(0 10px 28px rgba(0,102,204,.9));transform:scale(1.06)}}
.stApp{background:linear-gradient(135deg,#f0f2f5,#e8ecf1)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e)}
[data-testid="stSidebar"] *{color:#fff!important}
.page-header{background:linear-gradient(135deg,#0066CC,#004D99);border-radius:20px;padding:28px 36px;margin-bottom:28px;animation:fadeIn .6s ease-out;position:relative;overflow:hidden}
.page-header::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.15),transparent);animation:shimmer 3s infinite}
.page-header h1{color:#fff;margin:0;font-size:1.8rem}
.page-header p{color:rgba(255,255,255,.85);margin:6px 0 0}
.content-card{background:#fff;border-radius:18px;padding:24px;box-shadow:0 3px 12px rgba(0,0,0,.07);margin-bottom:20px;animation:fadeIn .7s ease-out}
.metric-card{background:#fff;border-radius:18px;padding:22px;text-align:center;transition:all .3s;box-shadow:0 3px 12px rgba(0,0,0,.07);border-left:4px solid;animation:fadeIn .6s ease-out}
.metric-card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
.metric-icon{font-size:2.2rem;margin-bottom:8px}
.metric-value{font-size:1.9rem;font-weight:700;margin:6px 0}
.metric-label{color:#666;font-size:.88rem;font-weight:500}
.stButton>button{background:linear-gradient(135deg,#0066CC,#004D99);color:#fff;border:none;border-radius:12px;padding:10px 24px;font-weight:600;transition:all .3s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 5px 20px rgba(0,102,204,.35)}
.stTextInput>div>div>input{border-radius:12px;border:1px solid #e0e0e0;padding:12px 16px}
.stSelectbox>div>div{border-radius:12px}
</style>"""

PROVINCES = [
    "Kinshasa","Kongo Central","Kwango","Kwilu","Mai-Ndombe",
    "Equateur","Sud-Ubangi","Nord-Ubangi","Mongala","Tshopo",
    "Bas-Uele","Haut-Uele","Ituri","Nord-Kivu","Sud-Kivu",
    "Maniema","Tanganyika","Haut-Lomami","Lualaba","Haut-Katanga",
    "Lomami","Sankuru","Kasai","Kasai Central","Kasai Oriental",
]


SHIELD_SVG = PUBLIC_SIDEBAR_BRAND

def nav_sidebar(user, auth):
    with st.sidebar:
        st.markdown(SHIELD_SVG, unsafe_allow_html=True)
        st.markdown(f"**{user['full_name']}**  \n*Administrateur*")
        st.markdown("---")
        if st.button("  Tableau de bord",   use_container_width=True): st.switch_page("pages/admin_dashboard.py")
        if st.button("  Saisie donnees",     use_container_width=True): st.switch_page("pages/admin_data_entry.py")
        if st.button("  Utilisateurs",        use_container_width=True): st.switch_page("pages/admin_users.py")
        st.markdown("---")
        if st.button("  Deconnexion",         use_container_width=True):
            st.session_state.user = None
            st.switch_page("app.py")


def main():
    st.set_page_config(page_title="Utilisateurs - SAFE CONGO",
                       page_icon=None, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        st.switch_page("app.py")
        return

    nav_sidebar(user, auth)

    st.markdown(
        '<div class="page-header"><h1>Gestion des Utilisateurs</h1>'
        "<p>Administrez les comptes des autorites sanitaires.</p></div>",
        unsafe_allow_html=True,
    )

    users = auth.get_all_users()
    admins    = [u for u in users if u["role"] == "admin"]
    autorites = [u for u in users if u["role"] == "autorite_sanitaire"]
    actifs    = [u for u in autorites if u["is_active"]]

    c1, c2, c3 = st.columns(3)
    for col, label, val, icon, color in [
        (c1, "Total utilisateurs", len(users),    "&#x25CF;", "#0066CC"),
        (c2, "Autorites actives",  len(actifs),   "&#x25B3;", "#00A86B"),
        (c3, "Administrateurs",    len(admins),   "&#x25A0;", "#FFC107"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card" style="border-left-color:{color}">'
                f'<div class="metric-icon">{icon}</div>'
                f'<div class="metric-value" style="color:{color}">{val}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Liste des utilisateurs", "Ajouter une autorite"])

    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if users:
            rows = []
            for u in users:
                rows.append({
                    "Nom complet":  f"{u['nom']} {u['prenom']}",
                    "Username":     u["username"],
                    "Role":         u["role"],
                    "Province":     u.get("province", "—"),
                    "Zone":         u.get("zone_sante", "—"),
                    "Email":        u.get("email", "—"),
                    "Statut":       "Actif" if u["is_active"] else "Desactive",
                    "Derniere connexion": u.get("last_login", "—"),
                    "id":           u["id"],
                })
            df = pd.DataFrame(rows)
            display_df = df.drop(columns=["id"])
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Desactiver un utilisateur")
            non_admin_users = [u for u in users if u["username"] != "admin" and u["is_active"]]
            if non_admin_users:
                selected = st.selectbox(
                    "Choisir un utilisateur",
                    [u["username"] for u in non_admin_users],
                )
                if st.button("Desactiver", use_container_width=True):
                    uid = next(u["id"] for u in non_admin_users if u["username"] == selected)
                    ok, msg = auth.delete_user(uid)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Aucun utilisateur a desactiver.")
        else:
            st.info("Aucun utilisateur enregistre.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            with c1:
                n_username  = st.text_input("Nom d\'utilisateur *")
                n_nom       = st.text_input("Nom *")
                n_prenom    = st.text_input("Prenom *")
                n_email     = st.text_input("Email *")
            with c2:
                n_password  = st.text_input("Mot de passe *", type="password")
                n_telephone = st.text_input("Telephone *")
                n_province  = st.selectbox("Province *", PROVINCES)
                n_zone      = st.text_input("Zone de sante *")
            add_sub = st.form_submit_button("Creer le compte", use_container_width=True)

        if add_sub:
            if all([n_username, n_password, n_nom, n_prenom, n_email, n_telephone, n_province, n_zone]):
                ok, msg = auth.register_authority(
                    n_username, n_password, n_nom, n_prenom,
                    n_email, n_telephone, n_province, n_zone,
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")
        st.markdown("</div>", unsafe_allow_html=True)


main()
