import streamlit as st
import pandas as pd
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem, require_auth
from src.pdf_generator import BarrierMeasuresPDF
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@700;900&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebarNav"]{display:none}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-1200px 0}100%{background-position:1200px 0}}
@keyframes pulseRed{0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,.4)}70%{box-shadow:0 0 0 12px rgba(220,38,38,0)}}
@keyframes countPop{from{opacity:0;transform:scale(.75)}to{opacity:1;transform:scale(1)}}
.stApp{background:#f0f4f9!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#080c18 0%,#0d1830 60%,#060b16 100%)!important;border-right:1px solid rgba(0,212,255,.15)!important}
[data-testid="stSidebar"] *{color:#e0eaff!important}
.stButton>button{background:linear-gradient(135deg,#0a3a7a,#0066CC)!important;color:#fff!important;border:none!important;border-radius:10px!important;padding:10px 18px!important;font-weight:600!important;font-size:.85rem!important;transition:all .3s!important;width:100%!important}
.stButton>button:hover{background:linear-gradient(135deg,#0066CC,#004499)!important;transform:translateX(4px)!important;box-shadow:0 4px 18px rgba(0,102,204,.4)!important}
.page-header{background:linear-gradient(135deg,#991b1b 0%,#DC2626 50%,#7f1d1d 100%);border-radius:20px;padding:32px 40px;margin-bottom:32px;animation:fadeIn .5s ease-out;position:relative;overflow:hidden;box-shadow:0 8px 32px rgba(180,0,0,.25)}
.page-header::before{content:'';position:absolute;top:0;left:-100%;width:70%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent);animation:shimmer 4s 1s infinite}
.page-header h1{color:#fff;margin:0;font-size:1.75rem;font-weight:800;font-family:'Orbitron',sans-serif;letter-spacing:1px}
.page-header p{color:rgba(255,255,255,.82);margin:8px 0 0;font-size:.92rem}
.page-header-badge{display:inline-block;background:rgba(255,255,255,.15);backdrop-filter:blur(8px);color:#fff;font-size:.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:4px 14px;border-radius:100px;border:1px solid rgba(255,255,255,.25);margin-bottom:10px}
.page-header-meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.page-header-chip{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);font-size:.74rem;font-weight:700;color:#fff}
.metric-card{background:#fff;border-radius:20px;padding:26px 22px;transition:all .35s cubic-bezier(.34,1.56,.64,1);box-shadow:0 2px 12px rgba(0,0,0,.06);border-top:4px solid;position:relative;overflow:hidden;animation:fadeIn .6s ease-out}
.metric-card:hover{transform:translateY(-6px);box-shadow:0 14px 36px rgba(0,0,0,.12)}
.metric-icon{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:14px;background:linear-gradient(135deg,var(--clr-light),var(--clr-mid))}
.metric-value{font-size:2.1rem;font-weight:800;line-height:1;margin-bottom:6px;font-family:'Orbitron',sans-serif;animation:countPop .5s ease-out}
.metric-label{color:#64748b;font-size:.82rem;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.alert-summary-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:18px 0 24px;animation:fadeIn .65s ease-out}
.alert-summary-card{background:#fff;border:1px solid #e8edf5;border-radius:22px;padding:20px;box-shadow:0 10px 28px rgba(15,23,42,.06)}
.alert-summary-k{font-size:.68rem;font-weight:800;letter-spacing:1.9px;text-transform:uppercase;color:#6b7f99;margin-bottom:8px}
.alert-summary-v{font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:800;color:#0f172a;margin-bottom:6px}
.alert-summary-copy{font-size:.84rem;line-height:1.6;color:#64748b}
.filter-shell{background:#fff;border:1px solid #e8edf5;border-radius:18px;padding:14px 18px;margin:8px 0 18px;box-shadow:0 8px 22px rgba(15,23,42,.05)}
.alert-card{border-radius:18px;padding:22px 26px;margin:14px 0;position:relative;overflow:hidden;animation:fadeIn .4s ease-out}
.alert-card::before{content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);animation:shimmer 5s 2s infinite}
.alert-card-badge{display:inline-flex;align-items:center;gap:6px;font-size:.72rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:100px;background:rgba(255,255,255,.2);margin-bottom:10px}
.alert-card-title{font-size:1.15rem;font-weight:800;margin-bottom:8px;letter-spacing:.3px}
.alert-card-detail{font-size:.88rem;line-height:1.75;opacity:.9}
.alert-card-stats{display:flex;gap:20px;margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,.2)}
.alert-stat-item{text-align:center}
.alert-stat-num{font-size:1.2rem;font-weight:800}
.alert-stat-lbl{font-size:.68rem;opacity:.75;text-transform:uppercase;letter-spacing:1px}
.ac-critique{background:linear-gradient(135deg,#7f1d1d,#DC2626);color:#fff;box-shadow:0 6px 24px rgba(220,38,38,.3);animation:pulseRed 3s infinite}
.ac-haute{background:linear-gradient(135deg,#7c2d12,#EA580C);color:#fff;box-shadow:0 6px 24px rgba(234,88,12,.25)}
.ac-moderee{background:linear-gradient(135deg,#713f12,#CA8A04);color:#fff;box-shadow:0 6px 20px rgba(202,138,4,.2)}
.section-label{font-size:.7rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#94a3b8;margin:24px 0 14px;display:flex;align-items:center;gap:10px}
.section-label::after{content:'';flex:1;height:1px;background:#e2e8f0}

@media (max-width: 980px){
    .alert-summary-strip{grid-template-columns:1fr}
    .page-header-meta{gap:8px}
}
</style>"""


SHIELD_SVG = PUBLIC_SIDEBAR_BRAND

def nav_sidebar(user, auth):
    unread = auth.get_unread_count(user["id"])
    badge  = f" ({unread})" if unread > 0 else ""
    with st.sidebar:
        st.markdown(SHIELD_SVG, unsafe_allow_html=True)
        st.markdown(f"**{user['full_name']}**  \n*{user.get('province','—')}*")
        st.markdown("---")
        if st.button("  Mon tableau de bord", use_container_width=True):
            st.switch_page("pages/authority_dashboard.py")
        if st.button(f"  Mes alertes{badge}", use_container_width=True):
            st.switch_page("pages/authority_alerts.py")
        st.markdown("---")
        if st.button("  Deconnexion", use_container_width=True):
            st.session_state.user = None
            st.switch_page("app.py")


def main():
    st.set_page_config(page_title="Alertes - SAFE CONGO",
                       page_icon=None, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "autorite_sanitaire":
        st.switch_page("app.py")
        return

    nav_sidebar(user, auth)
    province = user.get("province", "")

    st.markdown(
        f'<div class="page-header">'
        f'<span class="page-header-badge">Surveillance active</span>'
        f'<h1>Alertes &Eacute;pid&eacute;miologiques</h1>'
        f'<p>Province&nbsp;: <strong>{province}</strong> &mdash; '
        f'Zone&nbsp;: <strong>{user.get("zone_sante","—")}</strong></p>'
        f'<div class="page-header-meta">'
        f'<span class="page-header-chip">Lecture d&rsquo;urgence</span>'
        f'<span class="page-header-chip">Filtrage rapide</span>'
        f'<span class="page-header-chip">Mesures barri&egrave;res</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Load alerts
    try:
        conn = sqlite3.connect(str(auth.db_path))
        alerts = pd.read_sql_query(
            "SELECT a.id, a.disease, a.province, a.zone_sante, a.week, a.year, "
            "a.current_cases, a.predicted_cases, a.growth_rate, a.alert_level, "
            "a.message, a.created_at, "
            "COALESCE(n.is_read,0) as is_read, COALESCE(n.id,-1) as notif_id "
            "FROM alerts a "
            "LEFT JOIN notifications n ON a.id=n.alert_id AND n.user_id=? "
            "WHERE a.province=? ORDER BY a.created_at DESC",
            conn, params=(user["id"], province),
        )
        conn.close()
    except Exception:
        alerts = pd.DataFrame()

    if alerts.empty:
        st.info("Aucune alerte pour votre province pour l'instant.")
        return

    critique  = alerts[alerts["alert_level"] == "CRITIQUE"]
    haute     = alerts[alerts["alert_level"] == "HAUTE"]
    moderee   = alerts[alerts["alert_level"] == "MODEREE"]

    kpi_alerts = [
        ("Critiques",  len(critique), "#DC2626", "#fee2e2", "#fca5a5"),
        ("Hautes",     len(haute),    "#EA580C", "#ffedd5", "#fdba74"),
        ("Mod&eacute;r&eacute;es", len(moderee), "#CA8A04", "#fef3c7", "#fcd34d"),
    ]
    c1, c2, c3 = st.columns(3)
    for col, (label, nb, color, clr_light, clr_mid) in zip([c1,c2,c3], kpi_alerts):
        with col:
            st.markdown(
                f'<div class="metric-card" style="border-top-color:{color};--clr-light:{clr_light};--clr-mid:{clr_mid}">'
                f'<div class="metric-icon" style="color:{color}">&#x26A0;</div>'
                f'<div class="metric-value" style="color:{color}">{nb}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="alert-summary-strip">'
        f'<div class="alert-summary-card"><div class="alert-summary-k">Lecture</div><div class="alert-summary-v">Vue prioris&eacute;e</div><div class="alert-summary-copy">Les alertes sont hi&eacute;rarchis&eacute;es pour attirer l&rsquo;attention sur les niveaux qui demandent une d&eacute;cision rapide.</div></div>'
        f'<div class="alert-summary-card"><div class="alert-summary-k">Province</div><div class="alert-summary-v">{province}</div><div class="alert-summary-copy">L&rsquo;interface replace votre territoire dans un cadre plus propre, plus lisible et plus professionnel.</div></div>'
        f'<div class="alert-summary-card"><div class="alert-summary-k">Action</div><div class="alert-summary-v">PDF & mesures</div><div class="alert-summary-copy">Chaque alerte s&rsquo;accompagne d&rsquo;un acc&egrave;s direct aux mesures barri&egrave;res pour soutenir la r&eacute;ponse terrain.</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
    filter_opt = st.radio("Filtrer :", ["Toutes", "CRITIQUE", "HAUTE", "MODEREE"],
                          horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)
    filtered = alerts if filter_opt == "Toutes" else alerts[alerts["alert_level"] == filter_opt]

    pdf_gen = BarrierMeasuresPDF()

    for _, row in filtered.iterrows():
        level = row["alert_level"]
        cls   = {"CRITIQUE": "ac-critique", "HAUTE": "ac-haute"}.get(level, "ac-moderee")
        unread_dot = "&#x1F534;&nbsp;" if not row["is_read"] else "&#x2705;&nbsp;"
        growth_arrow = "&#x2197;" if row["growth_rate"] > 0 else "&#x2198;"

        st.markdown(
            f'<div class="alert-card {cls}">'
            f'<div class="alert-card-badge">{unread_dot}ALERTE {level}</div>'
            f'<div class="alert-card-title">{row["disease"]}</div>'
            f'<div class="alert-card-detail">'
            f'&#x1F4CD; {row["province"]} &mdash; {row["zone_sante"]}&nbsp;&nbsp;'
            f'&#x1F4C5; Semaine&nbsp;{int(row["week"])}&nbsp;/&nbsp;{int(row["year"])}'
            f'</div>'
            f'<div class="alert-card-stats">'
            f'<div class="alert-stat-item"><div class="alert-stat-num">{int(row["current_cases"]):,}</div><div class="alert-stat-lbl">Cas actuels</div></div>'
            f'<div class="alert-stat-item"><div class="alert-stat-num">{int(row["predicted_cases"]):,}</div><div class="alert-stat-lbl">Pr&eacute;diction</div></div>'
            f'<div class="alert-stat-item"><div class="alert-stat-num">{growth_arrow}&nbsp;{row["growth_rate"]:.1f}%</div><div class="alert-stat-lbl">Croissance</div></div>'
            f'</div>'
            f'<div style="margin-top:12px;font-size:.85rem;opacity:.88">{row["message"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if not row["is_read"] and row["notif_id"] != -1:
                if st.button("Marquer comme lue", key=f"rd_{row['notif_id']}"):
                    auth.mark_notification_read(int(row["notif_id"]))
                    st.rerun()

        with col_b:
            try:
                pdf_bytes = pdf_gen.generate_alert_pdf(
                    disease=row["disease"],
                    province=row["province"],
                    zone_sante=row["zone_sante"],
                    current_cases=int(row["current_cases"]),
                    predicted_cases=int(row["predicted_cases"]),
                    growth_rate=float(row["growth_rate"]),
                    alert_level=level,
                    r2_score=0.816,
                )
                st.download_button(
                    "Mesures barrieres (PDF)", pdf_bytes,
                    file_name=f"alerte_{row['disease']}_{row['week']}_{row['year']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{row['id']}",
                )
            except Exception:
                pass


main()
