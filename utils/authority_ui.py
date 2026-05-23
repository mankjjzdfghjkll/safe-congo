import sqlite3
from pathlib import Path
from typing import List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND, render_sidebar_active_button

__all__ = [
    "apply_authority_theme",
    "render_authority_sidebar",
    "render_authority_hero",
    "render_authority_kpis",
    "authority_section_label",
    "authority_panel_title",
    "make_plotly_layout",
    "load_historical_province",
    "alerts_for_user",
    "alert_delivery_health",
]


AUTHORITY_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
[data-testid="stSidebarNav"]{display:none}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.stApp{background:linear-gradient(180deg,#edf6ff 0%,#e7f2ff 48%,#f7fbff 100%)!important}
[data-testid="stAppViewContainer"] .main .block-container{max-width:1160px!important;padding-top:1.45rem!important;padding-bottom:1.4rem!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#eff7ff 100%)!important;border-right:1px solid rgba(176,208,233,.55)!important;box-shadow:3px 0 18px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] *{color:#0f2542!important}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.86)!important;color:#0a5fab!important;border:1px solid #c8dff0!important;border-radius:12px!important;padding:9px 13px!important;font-weight:700!important;font-size:.8rem!important;transition:all .22s ease!important;width:100%!important;justify-content:flex-start!important;box-shadow:0 8px 22px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] .stButton>button:hover{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;transform:translateX(4px)!important;box-shadow:0 10px 22px rgba(10,95,171,.22)!important}
[data-testid="stSidebar"] .stButton>button:focus-visible,[data-testid="stSidebar"] .stButton>button:active{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important;transform:translateX(2px)!important;box-shadow:0 0 0 3px rgba(26,162,226,.18),0 10px 22px rgba(10,95,171,.22)!important}
.stButton>button,.stDownloadButton>button{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border:0!important;border-radius:10px!important;padding:8px 12px!important;font-weight:800!important;font-size:.78rem!important;box-shadow:0 8px 18px rgba(10,95,171,.22)!important;transition:all .22s ease!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 12px 22px rgba(10,95,171,.28)!important}
.authority-sidebar-user-card{margin:10px 6px 12px;padding:13px 13px 11px;border-radius:16px;background:linear-gradient(180deg,#ffffff 0%,#eef7ff 100%);border:1px solid #d8e9f6;box-shadow:0 10px 22px rgba(10,60,120,.08)}
.authority-sidebar-role{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:rgba(5,150,105,.08);color:#047857!important;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase}
.authority-sidebar-role::before{content:'';width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#059669,#34d399)}
.authority-sidebar-name{margin-top:10px;font-family:'Sora',sans-serif;font-size:.95rem;line-height:1.35;color:#0f2542!important}
.authority-sidebar-meta{margin-top:6px;font-size:.76rem;line-height:1.55;color:#67839c!important}
.authority-shell{max-width:1160px;margin:0 auto;padding-bottom:10px}
.authority-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#0a5fab 0%,#0d80d8 52%,#1aa2e2 100%);border-radius:24px;padding:24px 24px 20px;box-shadow:0 18px 40px rgba(10,95,171,.18);margin:0 0 16px;animation:fadeIn .45s ease-out}
.authority-hero::before{content:'';position:absolute;inset:auto -10% -58% auto;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%)}
.authority-eyebrow{display:inline-flex;align-items:center;gap:8px;padding:6px 11px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.26);font-size:.64rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#fff}
.authority-eyebrow-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#fff,#dcfce7)}
.authority-title{font-family:'Sora',sans-serif;font-size:2rem;line-height:1.08;color:#fff;margin:14px 0 8px;max-width:760px}
.authority-subtitle{max-width:760px;color:rgba(255,255,255,.9);font-size:.92rem;line-height:1.65;margin:0}
.authority-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.authority-chip{padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);font-size:.7rem;font-weight:700;color:#fff;transition:transform .2s ease,background .2s ease}
.authority-chip:hover{transform:translateY(-2px);background:rgba(255,255,255,.18)}
.authority-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:0 0 16px}
.authority-kpi-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e2edf8;border-radius:18px;padding:16px 14px;box-shadow:0 10px 24px rgba(15,23,42,.06);position:relative;overflow:hidden;animation:fadeIn .55s ease-out;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.authority-kpi-card:hover{transform:translateY(-4px);box-shadow:0 18px 32px rgba(10,95,171,.10);border-color:#cfe3f4}
.authority-kpi-card::before{content:'';position:absolute;left:18px;right:18px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent-soft))}
.authority-kpi-label{font-size:.68rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#6b7f99;margin-bottom:8px}
.authority-kpi-value{font-family:'Sora',sans-serif;font-size:1.55rem;line-height:1;color:#0f172a;margin-bottom:7px}
.authority-kpi-delta{display:inline-flex;align-items:center;gap:6px;padding:4px 9px;border-radius:999px;background:var(--pill);font-size:.68rem;font-weight:700;color:var(--accent)}
.authority-kpi-copy{margin-top:8px;font-size:.8rem;line-height:1.58;color:#6b7f99}
.authority-section-label{display:flex;align-items:center;gap:10px;margin:22px 0 12px;font-size:.68rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#8aa0b8}
.authority-section-label::after{content:'';flex:1;height:1px;background:#dbe8f5}
.authority-panel{background:rgba(255,255,255,.94);border:1px solid rgba(180,208,232,.55);border-radius:18px;padding:14px;box-shadow:0 10px 24px rgba(15,23,42,.05);margin-bottom:14px;animation:fadeIn .6s ease-out;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.authority-panel:hover{transform:translateY(-3px);box-shadow:0 18px 30px rgba(10,95,171,.08);border-color:rgba(135,186,226,.75)}
.authority-panel-title{font-family:'Sora',sans-serif;font-size:.98rem;color:#0f3f73;margin:0 0 12px}
.authority-support-copy{margin:-2px 0 12px;font-size:.8rem;line-height:1.62;color:#68819a}
.authority-grid-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.authority-grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.authority-mini-card{padding:12px;border-radius:12px;background:linear-gradient(180deg,#ffffff,#f4f9ff);border:1px solid #e1edf9;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.authority-mini-card:hover{transform:translateY(-3px);box-shadow:0 12px 22px rgba(10,95,171,.08);border-color:#cfe3f4}
.authority-mini-card h4{margin:0 0 6px;font-size:.84rem;color:#103d6f}
.authority-mini-card p{margin:0;color:#6b7f99;font-size:.79rem;line-height:1.56}
.authority-highlight{padding:12px 14px;border-radius:14px;background:linear-gradient(135deg,#f1f8ff,#eef7ff);border:1px solid rgba(160,200,232,.6);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.authority-highlight:hover{transform:translateY(-3px);box-shadow:0 12px 22px rgba(10,95,171,.08);border-color:rgba(120,182,226,.65)}
.authority-highlight strong{display:block;color:#0a4a8a;font-size:.9rem;margin-bottom:3px}
.authority-highlight span{font-size:.79rem;line-height:1.56;color:#62758b}
.authority-empty-state{padding:14px;border-radius:14px;background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border:1px dashed #c8dff0;color:#5f7992;font-size:.79rem;line-height:1.58}
.authority-alert-card{border-radius:16px;padding:14px 14px 12px;background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #deebf7;box-shadow:0 8px 18px rgba(15,23,42,.06);margin-bottom:12px;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.authority-alert-card:hover{transform:translateY(-3px);box-shadow:0 16px 24px rgba(10,95,171,.08)}
.authority-alert-card.critique{border-color:rgba(239,68,68,.3);background:linear-gradient(180deg,#fff5f5 0%,#fff9f9 100%)}
.authority-alert-card.haute{border-color:rgba(249,115,22,.28);background:linear-gradient(180deg,#fff8f3 0%,#fffdfb 100%)}
.authority-alert-card.moderee{border-color:rgba(245,158,11,.28);background:linear-gradient(180deg,#fffdf0 0%,#fffef9 100%)}
.authority-alert-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap;margin-bottom:10px}
.authority-alert-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;font-size:.64rem;font-weight:800;letter-spacing:1.2px;text-transform:uppercase}
.authority-alert-badge.critique{background:rgba(239,68,68,.12);color:#b91c1c}
.authority-alert-badge.haute{background:rgba(249,115,22,.12);color:#c2410c}
.authority-alert-badge.moderee,.authority-alert-badge.info{background:rgba(245,158,11,.14);color:#a16207}
.authority-alert-title{font-family:'Sora',sans-serif;font-size:.97rem;color:#163e68;margin:0 0 4px}
.authority-alert-meta{font-size:.77rem;line-height:1.54;color:#69829b}
.authority-alert-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0}
.authority-alert-stat{padding:10px;border-radius:12px;background:rgba(255,255,255,.75);border:1px solid #e2edf8}
.authority-alert-stat strong{display:block;font-family:'Sora',sans-serif;font-size:.95rem;color:#0f172a;margin-bottom:3px}
.authority-alert-stat span{font-size:.66rem;letter-spacing:1px;text-transform:uppercase;color:#7c92a8;font-weight:800}
.authority-status-chip{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border-radius:999px;border:1px solid #cde2f4;background:#eff8ff;font-size:.7rem;font-weight:700;color:#0a5fab;margin-bottom:14px}
.authority-status-chip.dot-ok::before,.authority-status-chip.dot-warn::before{content:'';width:8px;height:8px;border-radius:50%}
.authority-status-chip.dot-ok::before{background:#16a34a}
.authority-status-chip.dot-warn::before{background:#f59e0b}
[data-testid="stExpander"]{border:1px solid rgba(180,208,232,.7)!important;border-radius:18px!important;background:linear-gradient(180deg,rgba(255,255,255,.97) 0%,rgba(246,251,255,.97) 100%)!important;box-shadow:0 10px 24px rgba(15,23,42,.05)!important;overflow:hidden!important;margin-bottom:12px!important}
[data-testid="stExpander"] details{border-radius:18px!important}
[data-testid="stExpander"] summary{padding:.25rem 0!important;font-weight:800!important;color:#103d6f!important}
[data-testid="stExpander"] summary:hover{color:#0a5fab!important}
[data-testid="stDataFrame"]{border-radius:16px!important;overflow:hidden!important;border:1px solid #e2edf8!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#f2f8ff;border:1px solid #d7e7f6;border-radius:999px;padding:9px 14px;font-weight:700;color:#0f4d8c}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important}
@media (max-width: 1100px){.authority-grid-2,.authority-grid-3,.authority-alert-stats{grid-template-columns:1fr}}
@media (max-width: 720px){.authority-hero{padding:18px 16px}.authority-title{font-size:1.45rem}.authority-kpi-grid{grid-template-columns:1fr}.authority-panel{padding:12px}}
</style>
"""


def apply_authority_theme() -> None:
    st.markdown(AUTHORITY_THEME, unsafe_allow_html=True)


def render_authority_sidebar(user: dict, auth, active_item: int) -> None:
    unread = auth.get_unread_count(user["id"])
    badge = f" ({unread})" if unread > 0 else ""
    with st.sidebar:
        st.markdown(PUBLIC_SIDEBAR_BRAND, unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="authority-sidebar-user-card">
  <div class="authority-sidebar-role">Autorite sanitaire</div>
  <div class="authority-sidebar-name">{user['full_name']}</div>
  <div class="authority-sidebar-meta">Province: {user.get('province', '—')}<br/>Zone de sante: {user.get('zone_sante', '—')}<br/>{unread} notification(s) non lue(s)</div>
</div>
""",
            unsafe_allow_html=True,
        )
        render_sidebar_active_button(active_item)
        if st.button("  Mon tableau de bord", use_container_width=True, key=f"authority_dashboard_{active_item}"):
            st.switch_page("pages/authority_dashboard.py")
        if st.button(f"  Mes alertes{badge}", use_container_width=True, key=f"authority_alerts_{active_item}"):
            st.switch_page("pages/authority_alerts.py")
        st.markdown("---")
        if st.button("  Retour accueil", use_container_width=True, key=f"authority_home_{active_item}"):
            st.switch_page("pages/home.py")
        if st.button("  Deconnexion", use_container_width=True, key=f"authority_logout_{active_item}"):
            st.session_state.user = None
            st.switch_page("pages/auth.py")


def render_authority_hero(title: str, subtitle: str = "", chips: Optional[list] = None, eyebrow: str = "Tableau de veille sanitaire") -> None:
    chip_markup = "".join(f'<span class="authority-chip">{chip}</span>' for chip in (chips or []))
    chip_container = f'<div class="authority-chip-row">{chip_markup}</div>' if chip_markup else ""
    st.markdown(
        f"""
<div class="authority-shell">
  <div class="authority-hero">
    <div class="authority-eyebrow"><span class="authority-eyebrow-dot"></span>{eyebrow}</div>
    <div class="authority-title">{title}</div>
    <div class="authority-subtitle">{subtitle}</div>
    {chip_container}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_authority_kpis(cards: List[dict]) -> None:
    markup = []
    for card in cards:
        accent = card.get("accent", "#0a5fab")
        accent_soft = card.get("accent_soft", accent + "33")
        pill = card.get("pill", accent + "1A")
        markup.append(
            f"""
<div class="authority-kpi-card" style="--accent:{accent};--accent-soft:{accent_soft};--pill:{pill}">
  <div class="authority-kpi-label">{card['label']}</div>
  <div class="authority-kpi-value">{card['value']}</div>
  <div class="authority-kpi-delta">{card['delta']}</div>
  <div class="authority-kpi-copy">{card['copy']}</div>
</div>
"""
        )
    st.markdown(f'<div class="authority-kpi-grid">{"".join(markup)}</div>', unsafe_allow_html=True)


def authority_section_label(text: str) -> None:
    st.markdown(f'<div class="authority-section-label">{text}</div>', unsafe_allow_html=True)


def authority_panel_title(title: str) -> None:
    st.markdown(f'<div class="authority-panel-title">{title}</div>', unsafe_allow_html=True)


def make_plotly_layout(fig: go.Figure, title: Optional[str] = None) -> go.Figure:
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=52 if title else 18, b=16),
        font=dict(family="Manrope", color="#17314f"),
        title_font=dict(family="Sora", size=14, color="#0f3f73"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(255,255,255,.68)", bordercolor="rgba(185,212,234,.65)", borderwidth=1),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="rgba(10,95,171,.18)", font=dict(color="#15304d")),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="rgba(151,195,228,.22)", zeroline=False, automargin=True)
    return fig


def load_historical_province(province: str) -> pd.DataFrame:
    root = Path(__file__).parent.parent
    for name in ["donnees_agregees_nettoyees.csv", "aggregated_data_clean.csv", "aggregated_data.csv"]:
        candidate = root / "data" / "processed" / name
        if not candidate.exists():
            continue
        try:
            frame = pd.read_csv(candidate)
        except Exception:
            continue
        if "PROVINCE" in frame.columns and province:
            return frame.loc[frame["PROVINCE"].astype(str).str.casefold() == province.casefold()].copy()
        return frame.copy()
    return pd.DataFrame()


def alerts_for_user(db_path: Path, user_id: int) -> pd.DataFrame:
    query = """
        SELECT
            a.id,
            COALESCE(a.disease, 'Inconnue') AS disease,
            COALESCE(a.province, '—') AS province,
            COALESCE(a.zone_sante, '—') AS zone_sante,
            COALESCE(a.week, 0) AS week,
            COALESCE(a.year, 0) AS year,
            COALESCE(a.current_cases, 0) AS current_cases,
            COALESCE(a.predicted_cases, 0) AS predicted_cases,
            COALESCE(a.growth_rate, 0) AS growth_rate,
            UPPER(TRIM(COALESCE(a.alert_level, 'INFO'))) AS alert_level,
            COALESCE(a.message, 'Aucun message detaille') AS message,
            COALESCE(a.created_at, n.created_at) AS created_at,
            COALESCE(n.is_read, 0) AS is_read,
            n.id AS notif_id
        FROM notifications n
        JOIN alerts a ON a.id = n.alert_id
        WHERE n.user_id = ?
        ORDER BY n.created_at DESC
    """
    expected_cols = [
        "id", "disease", "province", "zone_sante", "week", "year", "current_cases",
        "predicted_cases", "growth_rate", "alert_level", "message", "created_at", "is_read", "notif_id",
    ]
    try:
        conn = sqlite3.connect(str(db_path))
        frame = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        if frame.empty:
            return pd.DataFrame(columns=expected_cols)
        frame = frame.drop_duplicates(subset=["notif_id"], keep="first")
        frame["alert_level"] = frame["alert_level"].replace({
            "MODERATE": "MODEREE",
            "MODERE": "MODEREE",
            "HIGH": "HAUTE",
            "CRITICAL": "CRITIQUE",
        })
        return frame
    except Exception:
        return pd.DataFrame(columns=expected_cols)


def alert_delivery_health(db_path: Path, user_id: int) -> dict:
    status = {
        "ok": True,
        "notification_count": 0,
        "linked_alert_count": 0,
        "unread_count": 0,
        "message": "Canal d'alerte operationnel.",
    }
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id=?", (user_id,))
        notification_count = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0", (user_id,))
        unread_count = int(cur.fetchone()[0] or 0)
        cur.execute(
            """
            SELECT COUNT(*)
            FROM notifications n
            JOIN alerts a ON a.id = n.alert_id
            WHERE n.user_id=?
            """,
            (user_id,),
        )
        linked_alert_count = int(cur.fetchone()[0] or 0)
        conn.close()
        status.update(
            {
                "notification_count": notification_count,
                "linked_alert_count": linked_alert_count,
                "unread_count": unread_count,
            }
        )
        if linked_alert_count < notification_count:
            status["ok"] = False
            status["message"] = "Certaines notifications ne sont pas liees a une alerte detaillee."
        return status
    except Exception:
        status["ok"] = False
        status["message"] = "Verification du canal d'alerte indisponible pour le moment."
        return status