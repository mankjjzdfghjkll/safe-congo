import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import AuthSystem, require_auth
from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebarNav"]{display:none}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-1200px 0}100%{background-position:1200px 0}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(0,102,204,.3)}70%{box-shadow:0 0 0 10px rgba(0,102,204,0)}}
@keyframes countPop{from{opacity:0;transform:scale(.75)}to{opacity:1;transform:scale(1)}}
.stApp{background:linear-gradient(180deg,#eef6ff,#e6f2fd,#f0f8ff)!important}
[data-testid="stSidebar"]{background:#ffffff!important;border-right:1px solid #d0e8f8!important}
[data-testid="stSidebar"] *{color:#0a2040!important}
.stButton>button{background:#eef7ff!important;color:#0a5fab!important;border:1px solid #c8dff0!important;border-radius:10px!important;padding:10px 18px!important;font-weight:700!important;font-size:.85rem!important;transition:all .25s!important;width:100%!important}
.stButton>button:hover{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;transform:translateX(4px)!important;box-shadow:0 4px 18px rgba(10,95,171,.28)!important}
.page-header{background:linear-gradient(135deg,#0052A5 0%,#0077DD 50%,#003d99 100%);border-radius:20px;padding:32px 40px;margin-bottom:32px;animation:fadeIn .5s ease-out;position:relative;overflow:hidden;box-shadow:0 8px 32px rgba(0,120,80,.25)}
.page-header::before{content:'';position:absolute;top:0;left:-100%;width:70%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent);animation:shimmer 4s 1s infinite}
.page-header h1{color:#fff;margin:0;font-size:1.75rem;font-weight:800;font-family:'Sora',sans-serif;letter-spacing:.5px}
.page-header p{color:rgba(255,255,255,.82);margin:8px 0 0;font-size:.92rem}
.page-header-badge{display:inline-block;background:rgba(255,255,255,.15);backdrop-filter:blur(8px);color:#fff;font-size:.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:4px 14px;border-radius:100px;border:1px solid rgba(255,255,255,.25);margin-bottom:10px}
.page-header-meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.page-header-chip{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);font-size:.74rem;font-weight:700;color:#fff}
.metric-card{background:#fff;border-radius:20px;padding:26px 22px;transition:all .35s cubic-bezier(.34,1.56,.64,1);box-shadow:0 2px 12px rgba(0,0,0,.06);border-top:4px solid;position:relative;overflow:hidden;animation:fadeIn .6s ease-out}
.metric-card:hover{transform:translateY(-6px);box-shadow:0 14px 36px rgba(0,0,0,.12)}
.metric-icon{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:14px;background:linear-gradient(135deg,var(--clr-light),var(--clr-mid))}
.metric-value{font-size:2.1rem;font-weight:800;line-height:1;margin-bottom:6px;font-family:'Sora',sans-serif;animation:countPop .5s ease-out}
.metric-label{color:#64748b;font-size:.82rem;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.summary-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:-8px 0 24px;animation:fadeIn .65s ease-out}
.summary-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e4eef8;border-radius:22px;padding:20px;box-shadow:0 10px 28px rgba(15,23,42,.06);position:relative;overflow:hidden}
.summary-card::before{content:'';position:absolute;left:18px;right:18px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,#00A86B,#00D4A0,#7dd3fc)}
.summary-k{font-size:.68rem;font-weight:800;letter-spacing:1.9px;text-transform:uppercase;color:#6b7f99;margin-bottom:8px}
.summary-v{font-family:'Sora',sans-serif;font-size:1.02rem;font-weight:800;color:#0f172a;margin-bottom:6px}
.summary-copy{font-size:.84rem;line-height:1.6;color:#64748b}
.content-card{background:#fff;border-radius:20px;padding:28px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:22px;animation:fadeIn .7s ease-out;border:1px solid #f1f5f9}
.card-title{font-size:1rem;font-weight:700;color:#1e293b;margin-bottom:20px;display:flex;align-items:center;gap:10px}
.card-title-bar{width:4px;height:20px;border-radius:2px;background:linear-gradient(180deg,#00A86B,#00D4A0)}
.notif-unread{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-left:4px solid #00A86B;border-radius:14px;padding:16px 18px;margin:10px 0;box-shadow:0 2px 8px rgba(0,168,107,.1)}
.notif-read{background:#f8fafc;border-left:4px solid #cbd5e1;border-radius:14px;padding:14px 18px;margin:8px 0;opacity:.8}
.notif-title{font-weight:700;font-size:.9rem;color:#1e293b;margin-bottom:4px}
.notif-msg{font-size:.83rem;color:#475569;line-height:1.5}
.notif-date{font-size:.72rem;color:#94a3b8;margin-top:6px}
.section-label{font-size:.7rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#94a3b8;margin:24px 0 14px;display:flex;align-items:center;gap:10px}
.section-label::after{content:'';flex:1;height:1px;background:#e2e8f0}

@media (max-width: 980px){
    .summary-strip,.metric-card{grid-template-columns:1fr}
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


def load_historical(province):
    root = Path(__file__).parent.parent
    for name in ["donnees_agregees_nettoyees.csv", "aggregated_data_clean.csv"]:
        p = root / "data" / name
        if p.exists():
            df = pd.read_csv(p)
            if "PROVINCE" in df.columns:
                return df[df["PROVINCE"].str.lower() == province.lower()]
            return df
    return pd.DataFrame()


def main():
    st.set_page_config(page_title="Tableau de bord - SAFE CONGO",
                       page_icon=None, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "autorite_sanitaire":
        st.switch_page("app.py")
        return

    nav_sidebar(user, auth)
    province   = user.get("province", "—")
    zone_sante = user.get("zone_sante", "—")

    st.markdown(
        f'<div class="page-header">'
        f'<span class="page-header-badge">Autorit&eacute; sanitaire</span>'
        f'<h1>Tableau de bord</h1>'
        f'<p>Bienvenue <strong>{user["full_name"]}</strong> &nbsp;|&nbsp; '
        f'Province&nbsp;: <strong>{province}</strong> &mdash; Zone&nbsp;: <strong>{zone_sante}</strong></p>'
        f'<div class="page-header-meta">'
        f'<span class="page-header-chip">Veille locale</span>'
        f'<span class="page-header-chip">Priorit&eacute; terrain</span>'
        f'<span class="page-header-chip">Acc&egrave;s autoris&eacute;</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    df       = load_historical(province)
    unread   = auth.get_unread_count(user["id"])
    notifs   = auth.get_notifications(user["id"], unread_only=False)

    # KPIs
    try:
        conn = sqlite3.connect(str(auth.db_path))
        prov_df = pd.read_sql_query(
            "SELECT SUM(total_cases) tc, SUM(total_deaths) td, COUNT(*) n "
            "FROM epidemiological_data WHERE province=?", conn, params=(province,)
        )
        alerts_df = pd.read_sql_query(
            "SELECT COUNT(*) n FROM alerts WHERE province=?", conn, params=(province,)
        )
        conn.close()
        prov_cases  = int(prov_df["tc"].iloc[0] or 0)
        prov_deaths = int(prov_df["td"].iloc[0] or 0)
        prov_alerts = int(alerts_df["n"].iloc[0] or 0)
    except Exception:
        prov_cases = prov_deaths = prov_alerts = 0

    st.markdown(
        f'<div class="summary-strip">'
        f'<div class="summary-card"><div class="summary-k">Situation</div><div class="summary-v">{province}</div><div class="summary-copy">Votre tableau concentre les signaux utiles de votre province dans une lecture plus claire et plus professionnelle.</div></div>'
        f'<div class="summary-card"><div class="summary-k">Vigilance</div><div class="summary-v">{prov_alerts} alertes</div><div class="summary-copy">Les alertes et notifications critiques restent visibles pour orienter la r&eacute;ponse rapidement.</div></div>'
        f'<div class="summary-card"><div class="summary-k">Terrain</div><div class="summary-v">{zone_sante}</div><div class="summary-copy">La zone de sant&eacute; est replac&eacute;e au centre d&rsquo;une interface plus nette et plus rassurante.</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    kpi_data = [
        ("Cas enregistr&eacute;s", f"{prov_cases:,}",  "&#x25B3;", "#0066CC", "#dbeafe", "#93c5fd"),
        ("D&eacute;c&egrave;s",    f"{prov_deaths:,}", "&#x2665;", "#DC3545", "#fee2e2", "#fca5a5"),
        ("Alertes",                f"{prov_alerts}",   "&#x26A0;", "#D97706", "#fef3c7", "#fcd34d"),
        ("Nouvelles notifs",       f"{unread}",        "&#x25CF;", "#059669", "#d1fae5", "#6ee7b7"),
    ]
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, val, icon, color, clr_light, clr_mid) in zip([c1,c2,c3,c4], kpi_data):
        with col:
            st.markdown(
                f'<div class="metric-card" style="border-top-color:{color};--clr-light:{clr_light};--clr-mid:{clr_mid}">'
                f'<div class="metric-icon" style="color:{color}">{icon}</div>'
                f'<div class="metric-value" style="color:{color}">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-label">Notifications &amp; &Eacute;volution</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="content-card"><div class="card-title"><div class="card-title-bar"></div>Derni&egrave;res notifications</div>', unsafe_allow_html=True)
        if notifs:
            shown = 0
            for n in notifs[:8]:
                cls  = "notif-unread" if not n["is_read"] else "notif-read"
                dot  = "&#x1F534; " if not n["is_read"] else "&#x2705; "
                st.markdown(
                    f'<div class="{cls}">'
                    f'<div class="notif-title">{dot}{n["title"]}</div>'
                    f'<div class="notif-msg">{n["message"][:130]}</div>'
                    f'<div class="notif-date">{n["created_at"]}</div></div>',
                    unsafe_allow_html=True,
                )
                if not n["is_read"]:
                    if st.button("Marquer lue", key=f"rd_{n['id']}"):
                        auth.mark_notification_read(n["id"])
                        st.rerun()
                shown += 1
            if auth.get_unread_count(user["id"]) > 0:
                if st.button("Tout marquer comme lu", use_container_width=True):
                    auth.mark_all_notifications_read(user["id"])
                    st.rerun()
        else:
            st.info("Aucune notification.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="content-card"><div class="card-title"><div class="card-title-bar"></div>&Eacute;volution dans votre province</div>', unsafe_allow_html=True)
        if not df.empty and "MALADIE" in df.columns and "TOTALCAS" in df.columns:
            top3 = df.groupby("MALADIE")["TOTALCAS"].sum().nlargest(3).index
            fig  = go.Figure()
            colors_list = ["#0066CC", "#DC3545", "#00A86B"]
            for i, disease in enumerate(top3):
                ddf = df[df["MALADIE"] == disease]
                x_col = "DEBUTSEM" if "DEBUTSEM" in ddf.columns else ddf.columns[0]
                ddf = ddf.sort_values(x_col)
                fig.add_trace(go.Scatter(
                    x=ddf[x_col], y=ddf["TOTALCAS"], name=disease,
                    mode="lines+markers",
                    line=dict(color=colors_list[i % 3], width=2),
                    marker=dict(size=5),
                ))
            fig.update_layout(
                height=300, hovermode="x unified",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0,r=0,t=10,b=0),
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Donnees historiques non disponibles pour cette province.")
        if st.button("Voir toutes mes alertes", use_container_width=True):
            st.switch_page("pages/authority_alerts.py")
        st.markdown("</div>", unsafe_allow_html=True)


main()
