import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.navigation import switch_to_home_page
from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND, render_sidebar_active_button


ADMIN_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
[data-testid="stSidebarNav"]{display:none}

@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-1200px 0}100%{background-position:1200px 0}}

.stApp{background:linear-gradient(180deg,#eef6ff 0%,#e7f2fc 48%,#f4f9ff 100%)!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#f4f9ff 100%)!important;border-right:1px solid rgba(176,208,233,.55)!important;box-shadow:3px 0 18px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] *{color:#0f2542!important}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.82)!important;color:#0a5fab!important;border:1px solid #c8dff0!important;border-radius:16px!important;padding:11px 16px!important;font-weight:700!important;font-size:.86rem!important;transition:all .25s ease!important;width:100%!important;justify-content:flex-start!important;box-shadow:0 8px 22px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] .stButton>button:hover{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;transform:translateX(4px)!important;box-shadow:0 10px 22px rgba(10,95,171,.22)!important}
[data-testid="stSidebar"] .stButton>button:focus-visible,[data-testid="stSidebar"] .stButton>button:active{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important;transform:translateX(2px)!important;box-shadow:0 0 0 3px rgba(26,162,226,.18),0 10px 22px rgba(10,95,171,.22)!important}

.admin-sidebar-user-card{margin:12px 6px 16px;padding:16px 16px 14px;border-radius:20px;background:linear-gradient(180deg,#ffffff 0%,#eef7ff 100%);border:1px solid #d8e9f6;box-shadow:0 12px 28px rgba(10,60,120,.08)}
.admin-sidebar-role{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:rgba(10,95,171,.08);color:#0a5fab!important;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase}
.admin-sidebar-role::before{content:'';width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2)}
.admin-sidebar-name{margin-top:10px;font-family:'Sora',sans-serif;font-size:.95rem;line-height:1.35;color:#0f2542!important}
.admin-sidebar-meta{margin-top:6px;font-size:.76rem;line-height:1.55;color:#67839c!important}
.admin-sidebar-separator{height:1px;background:linear-gradient(90deg,rgba(200,223,240,0),rgba(200,223,240,1),rgba(200,223,240,0));margin:14px 0 12px}

.admin-shell{max-width:1320px;margin:0 auto;padding-bottom:24px}
.admin-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#0b4d95 0%,#0f75cc 58%,#48acef 100%);border-radius:34px;padding:34px 36px 30px;box-shadow:0 26px 60px rgba(11,77,149,.22);margin:0 0 22px;animation:fadeIn .45s ease-out}
.admin-hero::before{content:'';position:absolute;inset:auto -10% -58% auto;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%)}
.admin-eyebrow{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.26);font-size:.7rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#fff}
.admin-eyebrow-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#fff,#cce8ff)}
.admin-title{font-family:'Sora',sans-serif;font-size:2.2rem;line-height:1.02;color:#fff;margin:16px 0 10px;max-width:760px}
.admin-subtitle{max-width:760px;color:rgba(255,255,255,.86);font-size:.97rem;line-height:1.74;margin:0}
.admin-chip-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.admin-chip{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);font-size:.74rem;font-weight:700;color:#fff}

.admin-kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin:0 0 26px}
.admin-kpi-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e2edf8;border-radius:24px;padding:22px 20px;box-shadow:0 12px 32px rgba(15,23,42,.06);position:relative;overflow:hidden;animation:fadeIn .55s ease-out}
.admin-kpi-card::before{content:'';position:absolute;left:20px;right:20px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent-soft))}
.admin-kpi-label{font-size:.72rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#6b7f99;margin-bottom:10px}
.admin-kpi-value{font-family:'Sora',sans-serif;font-size:2rem;line-height:1;color:#0f172a;margin-bottom:8px}
.admin-kpi-delta{display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:999px;background:var(--pill);font-size:.74rem;font-weight:700;color:var(--accent)}
.admin-kpi-copy{margin-top:10px;font-size:.84rem;line-height:1.6;color:#6b7f99}

.admin-section-label{display:flex;align-items:center;gap:10px;margin:30px 0 16px;font-size:.72rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#8aa0b8}
.admin-section-label::after{content:'';flex:1;height:1px;background:#dbe8f5}
.admin-panel{background:rgba(255,255,255,.9);border:1px solid rgba(180,208,232,.55);border-radius:28px;padding:24px;box-shadow:0 12px 30px rgba(15,23,42,.05);margin-bottom:22px;animation:fadeIn .6s ease-out}
.admin-panel-title{font-family:'Sora',sans-serif;font-size:1rem;color:#0f3f73;margin:0 0 14px}
.admin-note{font-size:.86rem;line-height:1.7;color:#62758b;margin:0}
.admin-grid-2{display:grid;grid-template-columns:1.3fr .9fr;gap:18px}
.admin-grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.admin-mini-card{padding:18px;border-radius:20px;background:linear-gradient(180deg,#ffffff,#f4f9ff);border:1px solid #e1edf9}
.admin-mini-card h4{margin:0 0 8px;font-size:.95rem;color:#103d6f}
.admin-mini-card p{margin:0;color:#6b7f99;font-size:.84rem;line-height:1.64}
.admin-highlight{padding:16px 18px;border-radius:20px;background:linear-gradient(135deg,#eff7ff,#e7f2ff);border:1px solid rgba(160,200,232,.6)}
.admin-highlight strong{display:block;color:#0a4a8a;font-size:1rem;margin-bottom:4px}
.admin-highlight span{font-size:.84rem;line-height:1.65;color:#62758b}
.admin-support-copy{margin:-4px 0 18px;font-size:.84rem;line-height:1.7;color:#68819a}
.admin-empty-state{padding:18px 18px;border-radius:18px;background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border:1px dashed #c8dff0;color:#5f7992;font-size:.84rem;line-height:1.7}

[data-testid="stDataFrame"]{border-radius:18px!important;overflow:hidden!important;border:1px solid #e2edf8!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#f2f8ff;border:1px solid #d7e7f6;border-radius:999px;padding:9px 14px;font-weight:700;color:#0f4d8c}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important}
.stTextInput>div>div>input,.stSelectbox>div>div,.stNumberInput>div>div>input{border-radius:14px!important;border:1px solid #d6e6f5!important}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{border-color:#0a5fab!important;box-shadow:0 0 0 3px rgba(26,162,226,.1)!important}

@media (max-width: 1100px){
  .admin-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .admin-grid-2,.admin-grid-3{grid-template-columns:1fr}
}
@media (max-width: 720px){
  .admin-hero{padding:28px 22px}
  .admin-title{font-size:1.75rem}
  .admin-kpi-grid{grid-template-columns:1fr}
}
</style>
"""


def apply_admin_theme() -> None:
    st.markdown(ADMIN_THEME, unsafe_allow_html=True)


def render_admin_sidebar(user: dict, active_item: int) -> None:
    with st.sidebar:
        st.markdown(PUBLIC_SIDEBAR_BRAND, unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="admin-sidebar-user-card">
  <div class="admin-sidebar-role">Administrateur</div>
  <div class="admin-sidebar-name">{user['full_name']}</div>
  <div class="admin-sidebar-meta">Console de supervision SAFE CONGO<br/>Acces central aux operations et a la gouvernance.</div>
</div>
<div class="admin-sidebar-separator"></div>
""",
            unsafe_allow_html=True,
        )
        render_sidebar_active_button(active_item)
        if st.button("  Tableau de bord executif", use_container_width=True):
            st.switch_page("pages/admin_dashboard.py")
        if st.button("  Saisie & intelligence", use_container_width=True):
            st.switch_page("pages/admin_data_entry.py")
        if st.button("  Gouvernance utilisateurs", use_container_width=True):
            st.switch_page("pages/admin_users.py")
        if st.button("  Centre de pilotage", use_container_width=True):
            st.switch_page("pages/admin_panel.py")
        st.markdown("---")
        if st.button("  Retour accueil", use_container_width=True):
            switch_to_home_page()
        if st.button("  Deconnexion", use_container_width=True):
            st.session_state.user = None
            st.switch_page("pages/auth.py")


def render_admin_hero(title: str, subtitle: str, chips: Iterable[str], eyebrow: str = "Administration") -> None:
    chip_markup = "".join(f'<span class="admin-chip">{chip}</span>' for chip in chips)
    st.markdown(
        f"""
<div class="admin-shell">
  <div class="admin-hero">
    <div class="admin-eyebrow"><span class="admin-eyebrow-dot"></span>{eyebrow}</div>
    <div class="admin-title">{title}</div>
    <p class="admin-subtitle">{subtitle}</p>
    <div class="admin-chip-row">{chip_markup}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kpi_cards(cards: List[dict]) -> None:
    markup = []
    for card in cards:
        markup.append(
            f"""
<div class="admin-kpi-card" style="--accent:{card['accent']};--accent-soft:{card['accent_soft']};--pill:{card['pill']}">
  <div class="admin-kpi-label">{card['label']}</div>
  <div class="admin-kpi-value">{card['value']}</div>
  <div class="admin-kpi-delta">{card['delta']}</div>
  <div class="admin-kpi-copy">{card['copy']}</div>
</div>
"""
        )
    st.markdown(f'<div class="admin-kpi-grid">{"".join(markup)}</div>', unsafe_allow_html=True)


def section_label(text: str) -> None:
    st.markdown(f'<div class="admin-section-label">{text}</div>', unsafe_allow_html=True)


def panel_title(title: str) -> None:
    st.markdown(f'<div class="admin-panel-title">{title}</div>', unsafe_allow_html=True)


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


def safe_read_sqlite(db_path: Path, query: str) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(db_path)
        frame = pd.read_sql_query(query, conn)
        conn.close()
        return frame
    except Exception:
        return pd.DataFrame()


def recent_entries_frame(db_path: Path) -> pd.DataFrame:
    return safe_read_sqlite(
        db_path,
        """
        SELECT disease, province, zone_sante, week, year, total_cases, total_deaths, entry_date
        FROM epidemiological_data
        ORDER BY entry_date DESC
        LIMIT 200
        """,
    )


def alerts_frame(db_path: Path) -> pd.DataFrame:
    return safe_read_sqlite(
        db_path,
        """
        SELECT disease, province, zone_sante, alert_level, growth_rate, current_cases, predicted_cases, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 200
        """,
    )


def users_frame(auth) -> pd.DataFrame:
    users = auth.get_all_users()
    return pd.DataFrame(users) if users else pd.DataFrame()


def aggregated_csv_frame() -> pd.DataFrame:
    root = Path(__file__).parent.parent
    for candidate in [
        root / "data" / "aggregated_data_clean.csv",
        root / "data" / "donnees_agregees_nettoyees.csv",
        root / "data" / "aggregated_data.csv",
    ]:
        if candidate.exists():
            try:
                return pd.read_csv(candidate)
            except Exception:
                return pd.DataFrame()
    return pd.DataFrame()
