import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND, render_sidebar_active_button


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
[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#eff7ff 100%)!important;border-right:1px solid rgba(176,208,233,.55)!important;box-shadow:3px 0 18px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] *{color:#0f2542!important}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.86)!important;color:#0a5fab!important;border:1px solid #c8dff0!important;border-radius:16px!important;padding:11px 16px!important;font-weight:700!important;font-size:.86rem!important;transition:all .25s ease!important;width:100%!important;justify-content:flex-start!important;box-shadow:0 8px 22px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] .stButton>button:hover{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;transform:translateX(4px)!important;box-shadow:0 10px 22px rgba(10,95,171,.22)!important}
[data-testid="stSidebar"] .stButton>button:focus-visible,[data-testid="stSidebar"] .stButton>button:active{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important;transform:translateX(2px)!important;box-shadow:0 0 0 3px rgba(26,162,226,.18),0 10px 22px rgba(10,95,171,.22)!important}

.authority-sidebar-user-card{margin:12px 6px 16px;padding:16px 16px 14px;border-radius:20px;background:linear-gradient(180deg,#ffffff 0%,#eef7ff 100%);border:1px solid #d8e9f6;box-shadow:0 12px 28px rgba(10,60,120,.08)}
.authority-sidebar-role{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:rgba(5,150,105,.08);color:#047857!important;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase}
.authority-sidebar-role::before{content:'';width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#059669,#34d399)}
.authority-sidebar-name{margin-top:10px;font-family:'Sora',sans-serif;font-size:.95rem;line-height:1.35;color:#0f2542!important}
.authority-sidebar-meta{margin-top:6px;font-size:.76rem;line-height:1.55;color:#67839c!important}

.authority-shell{max-width:1320px;margin:0 auto;padding-bottom:24px}
.authority-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#046c96 0%,#0e7490 54%,#22c55e 100%);border-radius:34px;padding:34px 36px 30px;box-shadow:0 26px 60px rgba(6,95,140,.18);margin:0 0 24px;animation:fadeIn .45s ease-out}
.authority-hero::before{content:'';position:absolute;inset:auto -10% -58% auto;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%)}
.authority-eyebrow{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.26);font-size:.7rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}
.authority-eyebrow-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#fff,#dcfce7)}
.authority-title{font-family:'Sora',sans-serif;font-size:2.15rem;line-height:1.04;color:#fff;margin:16px 0 10px;max-width:760px}
.authority-subtitle{max-width:760px;color:rgba(255,255,255,.88);font-size:.97rem;line-height:1.74;margin:0}
.authority-chip-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.authority-chip{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);font-size:.74rem;font-weight:700;color:#fff}

.authority-kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin:0 0 26px}
.authority-kpi-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e2edf8;border-radius:24px;padding:22px 20px;box-shadow:0 12px 32px rgba(15,23,42,.06);position:relative;overflow:hidden;animation:fadeIn .55s ease-out}
.authority-kpi-card::before{content:'';position:absolute;left:20px;right:20px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent-soft))}
.authority-kpi-label{font-size:.72rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#6b7f99;margin-bottom:10px}
.authority-kpi-value{font-family:'Sora',sans-serif;font-size:2rem;line-height:1;color:#0f172a;margin-bottom:8px}
.authority-kpi-delta{display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:999px;background:var(--pill);font-size:.74rem;font-weight:700;color:var(--accent)}
.authority-kpi-copy{margin-top:10px;font-size:.84rem;line-height:1.6;color:#6b7f99}

.authority-section-label{display:flex;align-items:center;gap:10px;margin:30px 0 16px;font-size:.72rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#8aa0b8}
.authority-section-label::after{content:'';flex:1;height:1px;background:#dbe8f5}
.authority-panel{background:rgba(255,255,255,.92);border:1px solid rgba(180,208,232,.55);border-radius:28px;padding:24px;box-shadow:0 12px 30px rgba(15,23,42,.05);margin-bottom:22px;animation:fadeIn .6s ease-out}
.authority-panel-title{font-family:'Sora',sans-serif;font-size:1rem;color:#0f3f73;margin:0 0 14px}
.authority-support-copy{margin:-4px 0 18px;font-size:.84rem;line-height:1.7;color:#68819a}
.authority-grid-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.authority-grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.authority-mini-card{padding:18px;border-radius:20px;background:linear-gradient(180deg,#ffffff,#f4f9ff);border:1px solid #e1edf9}
.authority-mini-card h4{margin:0 0 8px;font-size:.95rem;color:#103d6f}
.authority-mini-card p{margin:0;color:#6b7f99;font-size:.84rem;line-height:1.64}
.authority-highlight{padding:16px 18px;border-radius:20px;background:linear-gradient(135deg,#eefcf7,#eef7ff);border:1px solid rgba(160,200,232,.6)}
.authority-highlight strong{display:block;color:#0a4a8a;font-size:1rem;margin-bottom:4px}
.authority-highlight span{font-size:.84rem;line-height:1.65;color:#62758b}
.authority-empty-state{padding:18px 18px;border-radius:18px;background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border:1px dashed #c8dff0;color:#5f7992;font-size:.84rem;line-height:1.7}

.authority-alert-card{border-radius:22px;padding:22px 22px 18px;background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #deebf7;box-shadow:0 12px 28px rgba(15,23,42,.06);margin-bottom:16px}
.authority-alert-card.critique{border-color:rgba(239,68,68,.3);background:linear-gradient(180deg,#fff5f5 0%,#fff9f9 100%)}
.authority-alert-card.haute{border-color:rgba(249,115,22,.28);background:linear-gradient(180deg,#fff8f3 0%,#fffdfb 100%)}
.authority-alert-card.moderee{border-color:rgba(245,158,11,.28);background:linear-gradient(180deg,#fffdf0 0%,#fffef9 100%)}
.authority-alert-top{display:flex;justify-content:space-between;gap:14px;align-items:flex-start;flex-wrap:wrap;margin-bottom:12px}
.authority-alert-badge{display:inline-flex;align-items:center;gap:8px;padding:7px 12px;border-radius:999px;font-size:.7rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase}
.authority-alert-badge.critique{background:rgba(239,68,68,.12);color:#b91c1c}
.authority-alert-badge.haute{background:rgba(249,115,22,.12);color:#c2410c}
.authority-alert-badge.moderee,.authority-alert-badge.info{background:rgba(245,158,11,.14);color:#a16207}
.authority-alert-badge.nouvelle_donnee{background:rgba(10,95,171,.12);color:#0a5fab}
.authority-alert-title{font-family:'Sora',sans-serif;font-size:1.05rem;color:#163e68;margin:0 0 6px}
.authority-alert-meta{font-size:.82rem;line-height:1.65;color:#69829b}
.authority-alert-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:16px 0}
.authority-alert-stat{padding:14px;border-radius:16px;background:rgba(255,255,255,.75);border:1px solid #e2edf8}
.authority-alert-stat strong{display:block;font-family:'Sora',sans-serif;font-size:1.05rem;color:#0f172a;margin-bottom:4px}
.authority-alert-stat span{font-size:.73rem;letter-spacing:1.1px;text-transform:uppercase;color:#7c92a8;font-weight:800}

[data-testid="stDataFrame"]{border-radius:18px!important;overflow:hidden!important;border:1px solid #e2edf8!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#f2f8ff;border:1px solid #d7e7f6;border-radius:999px;padding:9px 14px;font-weight:700;color:#0f4d8c}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important}

@media (max-width: 1100px){.authority-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.authority-grid-2,.authority-grid-3,.authority-alert-stats{grid-template-columns:1fr}}
@media (max-width: 720px){.authority-hero{padding:28px 22px}.authority-title{font-size:1.72rem}.authority-kpi-grid{grid-template-columns:1fr}}
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
        if st.button("  Mon tableau de bord", use_container_width=True):
            st.switch_page("pages/authority_dashboard.py")
        if st.button(f"  Mes alertes{badge}", use_container_width=True):
            st.switch_page("pages/authority_alerts.py")
        st.markdown("---")
        if st.button("  Retour accueil", use_container_width=True):
            st.switch_page("pages/home.py")
        if st.button("  Deconnexion", use_container_width=True):
            st.session_state.user = None
            st.switch_page("pages/auth.py")


def render_authority_hero(title: str, subtitle: str, chips: Iterable[str], eyebrow: str = "Autorite sanitaire") -> None:
    chip_markup = "".join(f'<span class="authority-chip">{chip}</span>' for chip in chips)
    st.markdown(
        f"""
<div class="authority-shell">
  <div class="authority-hero">
    <div class="authority-eyebrow"><span class="authority-eyebrow-dot"></span>{eyebrow}</div>
    <div class="authority-title">{title}</div>
    <p class="authority-subtitle">{subtitle}</p>
    <div class="authority-chip-row">{chip_markup}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_authority_kpis(cards: List[dict]) -> None:
    markup = []
    for card in cards:
        markup.append(
            f"""
<div class="authority-kpi-card" style="--accent:{card['accent']};--accent-soft:{card['accent_soft']};--pill:{card['pill']}">
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
        margin=dict(l=18, r=18, t=50 if title else 20, b=18),
        font=dict(family="Manrope", color="#17314f"),
        title_font=dict(family="Sora", size=15, color="#0f3f73"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(151,195,228,.22)", zeroline=False)
    return fig


def load_historical_province(province: str) -> pd.DataFrame:
    root = Path(__file__).parent.parent
    for name in ["donnees_agregees_nettoyees.csv", "aggregated_data_clean.csv", "aggregated_data.csv"]:
        candidate = root / "data" / name
        if candidate.exists():
            try:
                frame = pd.read_csv(candidate)
            except Exception:
                continue
            if "PROVINCE" in frame.columns:
                return frame.loc[frame["PROVINCE"].astype(str).str.casefold() == province.casefold()].copy()
            return frame.copy()
    return pd.DataFrame()


def alerts_for_user(db_path: Path, user_id: int) -> pd.DataFrame:
    query = """
        SELECT a.id, a.disease, a.province, a.zone_sante, a.week, a.year,
               a.current_cases, a.predicted_cases, a.growth_rate, a.alert_level,
               a.message, a.created_at, n.is_read, n.id AS notif_id
        FROM notifications n
        JOIN alerts a ON a.id = n.alert_id
        WHERE n.user_id = ?
        ORDER BY a.created_at DESC
    """
    try:
        conn = sqlite3.connect(str(db_path))
        frame = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return frame
    except Exception:
        return pd.DataFrame()