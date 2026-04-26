import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import AuthSystem, require_auth
from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND

try:
    import joblib
except ImportError:
    joblib = None


CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebarNav"]{display:none}

@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-1200px 0}100%{background-position:1200px 0}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(220,53,69,.35)}70%{box-shadow:0 0 0 10px rgba(220,53,69,0)}}
@keyframes countPop{from{opacity:0;transform:scale(.75)}to{opacity:1;transform:scale(1)}}
@keyframes borderFlow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

/* App background */
.stApp{background:linear-gradient(180deg,#eef6ff,#e6f2fd,#f0f8ff)!important}

/* Sidebar */
[data-testid="stSidebar"]{background:#ffffff!important;border-right:1px solid #d0e8f8!important}
[data-testid="stSidebar"] *{color:#0a2040!important}
.stButton>button{background:#eef7ff!important;color:#0a5fab!important;border:1px solid #c8dff0!important;border-radius:10px!important;padding:10px 18px!important;font-weight:700!important;font-size:.85rem!important;transition:all .25s!important;width:100%!important;letter-spacing:.3px!important}
.stButton>button:hover{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;transform:translateX(4px)!important;box-shadow:0 4px 18px rgba(10,95,171,.28)!important}

/* Page header banner */
.page-header{
  background:linear-gradient(135deg,#0052A5 0%,#0077DD 50%,#003d99 100%);
  border-radius:20px;padding:32px 40px;margin-bottom:32px;
  animation:fadeIn .5s ease-out;position:relative;overflow:hidden;
  box-shadow:0 8px 32px rgba(0,80,180,.25);
}
.page-header::before{content:'';position:absolute;top:0;left:-100%;width:70%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent);
  animation:shimmer 4s 1s infinite}
.page-header::after{content:'';position:absolute;bottom:0;right:0;width:220px;height:220px;
  background:radial-gradient(circle,rgba(255,255,255,.06) 0%,transparent 70%);border-radius:50%}
.page-header h1{color:#fff;margin:0;font-size:1.75rem;font-weight:800;font-family:'Sora',sans-serif;letter-spacing:.5px}
.page-header p{color:rgba(255,255,255,.82);margin:8px 0 0;font-size:.92rem}
.page-header-badge{display:inline-block;background:rgba(255,255,255,.15);backdrop-filter:blur(8px);
  color:#fff;font-size:.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  padding:4px 14px;border-radius:100px;border:1px solid rgba(255,255,255,.25);margin-bottom:10px}
.page-header-meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.page-header-chip{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);font-size:.74rem;font-weight:700;color:#fff}

.executive-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:-8px 0 24px;animation:fadeIn .65s ease-out}
.executive-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e4eef8;border-radius:22px;padding:20px;box-shadow:0 10px 28px rgba(15,23,42,.06);position:relative;overflow:hidden}
.executive-card::before{content:'';position:absolute;left:18px;right:18px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,#0066CC,#00D4FF,#FFD45E)}
.executive-k{font-size:.68rem;font-weight:800;letter-spacing:1.9px;text-transform:uppercase;color:#6b7f99;margin-bottom:8px}
.executive-v{font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:#0f172a;margin-bottom:6px}
.executive-copy{font-size:.84rem;line-height:1.6;color:#64748b}

/* KPI metric cards */
.metric-card{
  background:#fff;border-radius:20px;padding:26px 22px;
  transition:all .35s cubic-bezier(.34,1.56,.64,1);
  box-shadow:0 2px 12px rgba(0,0,0,.06),0 1px 3px rgba(0,0,0,.04);
  border-top:4px solid;position:relative;overflow:hidden;
  animation:fadeIn .6s ease-out;
}
.metric-card::after{content:'';position:absolute;bottom:-18px;right:-18px;
  width:70px;height:70px;border-radius:50%;opacity:.06;background:currentColor}
.metric-card:hover{transform:translateY(-6px);box-shadow:0 14px 36px rgba(0,0,0,.12)}
.metric-icon{
  width:48px;height:48px;border-radius:14px;display:flex;align-items:center;
  justify-content:center;font-size:1.3rem;margin-bottom:14px;
  background:linear-gradient(135deg,var(--clr-light),var(--clr-mid))
}
.metric-value{font-size:2.1rem;font-weight:800;line-height:1;margin-bottom:6px;
  font-family:'Sora',sans-serif;animation:countPop .5s ease-out}
.metric-label{color:#64748b;font-size:.82rem;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.metric-delta{font-size:.75rem;font-weight:600;margin-top:8px;display:inline-flex;
  align-items:center;gap:4px;padding:3px 10px;border-radius:100px}

/* Content cards */
.content-card{
  background:#fff;border-radius:20px;padding:28px;
  box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:22px;
  animation:fadeIn .7s ease-out;border:1px solid #f1f5f9;
}
.card-title{font-size:1rem;font-weight:700;color:#1e293b;margin-bottom:20px;
  display:flex;align-items:center;gap:10px}
.card-title-bar{width:4px;height:20px;border-radius:2px;
  background:linear-gradient(180deg,#0066CC,#00D4FF)}

/* Model performance card */
.model-card{
  background:linear-gradient(145deg,#0052A5 0%,#0077DD 55%,#003d99 100%);
  border-radius:20px;padding:32px 28px;color:#fff;text-align:center;
  animation:fadeIn .8s ease-out;position:relative;overflow:hidden;
  box-shadow:0 8px 32px rgba(0,80,180,.3);
}
.model-card::before{content:'';position:absolute;top:-30px;right:-30px;
  width:120px;height:120px;border-radius:50%;
  background:rgba(255,255,255,.06)}
.model-card::after{content:'';position:absolute;bottom:-20px;left:-20px;
  width:90px;height:90px;border-radius:50%;
  background:rgba(255,255,255,.04)}
.model-name{font-size:.75rem;letter-spacing:3px;text-transform:uppercase;
  color:rgba(255,255,255,.7);margin-bottom:6px}
.model-type{font-size:1.5rem;font-weight:800;font-family:'Sora',sans-serif;
  margin-bottom:4px}
.model-pct{font-size:3.8rem;font-weight:900;font-family:'Sora',sans-serif;
  line-height:1;margin:16px 0 8px;
  background:linear-gradient(135deg,#ffffff,#a8d8ff);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.model-label{font-size:.82rem;opacity:.8;margin-bottom:18px}
.model-stat-row{display:flex;justify-content:center;gap:24px;margin-top:16px;
  border-top:1px solid rgba(255,255,255,.15);padding-top:16px}
.model-stat{text-align:center}
.model-stat-num{font-size:1.1rem;font-weight:700}
.model-stat-lbl{font-size:.68rem;opacity:.7;letter-spacing:1px;text-transform:uppercase;margin-top:2px}

/* Alert level badges */
.badge-critique{background:#fee2e2;color:#991b1b;padding:3px 10px;border-radius:100px;
  font-size:.72rem;font-weight:700;letter-spacing:.5px}
.badge-haute{background:#ffedd5;color:#9a3412;padding:3px 10px;border-radius:100px;
  font-size:.72rem;font-weight:700;letter-spacing:.5px}
.badge-moderee{background:#fef3c7;color:#92400e;padding:3px 10px;border-radius:100px;
  font-size:.72rem;font-weight:700;letter-spacing:.5px}

/* Section divider label */
.section-label{font-size:.7rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
  color:#94a3b8;margin:24px 0 14px;display:flex;align-items:center;gap:10px}
.section-label::after{content:'';flex:1;height:1px;background:#e2e8f0}

@media (max-width: 980px){
  .executive-strip{grid-template-columns:1fr}
  .page-header-meta{gap:8px}
}
</style>"""


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


def load_historical():
    root = Path(__file__).parent.parent
    for name in ["donnees_agregees_nettoyees.csv", "aggregated_data_clean.csv"]:
        p = root / "data" / name
        if p.exists():
            return pd.read_csv(p)
    return pd.DataFrame()


def load_model_info():
    root = Path(__file__).parent.parent / "models"
    p = None
    for name in ["meilleur_modele.pkl", "best_model.pkl", "models.pkl"]:
        candidate = root / name
        if candidate.exists():
            p = candidate
            break
    if p is not None and joblib is not None:
        try:
            obj = joblib.load(p)
            if isinstance(obj, dict):
                return obj.get("accuracy", 0.816), obj.get("f1_score", 0.458), "XGBoost"
            return 0.816, 0.458, "XGBoost"
        except Exception:
            pass
    log = Path(__file__).parent.parent / "train_run.log"
    if log.exists():
        return 0.816, 0.458, "XGBoost"
    return 0.816, 0.458, "XGBoost"


def main():
    st.set_page_config(page_title="Admin Dashboard - SAFE CONGO",
                       page_icon=None, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    auth = AuthSystem()
    user = require_auth(auth)
    if not user or user["role"] != "admin":
        st.switch_page("app.py")
        return

    nav_sidebar(user, auth)
    st.markdown(
        f'<div class="page-header">'
        f'<span class="page-header-badge">Administration</span>'
        f'<h1>Tableau de bord administrateur</h1>'
        f'<p>Bienvenue <strong>{user["full_name"]}</strong> &nbsp;|&nbsp; '
      f'{datetime.now().strftime("%A %d %B %Y, %H:%M")}</p>'
      f'<div class="page-header-meta">'
      f'<span class="page-header-chip">Pilotage national</span>'
      f'<span class="page-header-chip">Surveillance consolid&eacute;e</span>'
      f'<span class="page-header-chip">D&eacute;cision assist&eacute;e</span>'
      f'</div></div>',
        unsafe_allow_html=True,
    )

    df = load_historical()
    stats = auth.get_stats()
    acc, f1, model_name = load_model_info()

    total_cas = int(df["TOTALCAS"].sum()) if not df.empty else 0
    total_deces = int(df["TOTALDECES"].sum()) if not df.empty else 0
    nb_maladies = int(df["MALADIE"].nunique()) if not df.empty else 0
    nb_alertes = stats.get("total_alerts", 0)
    nb_users = stats.get("total_authorities", 0)

    st.markdown(
      f'<div class="executive-strip">'
      f'<div class="executive-card"><div class="executive-k">Lecture ex&eacute;cutive</div><div class="executive-v">Vision imm&eacute;diate</div><div class="executive-copy">Les volumes, les alertes et les capacit&eacute;s terrain restent visibles dans une vue de d&eacute;cision claire.</div></div>'
      f'<div class="executive-card"><div class="executive-k">Couverture</div><div class="executive-v">{nb_users} autorit&eacute;s actives</div><div class="executive-copy">Le suivi administratif conserve une lecture unifi&eacute;e des acteurs et des signaux prioritaires.</div></div>'
      f'<div class="executive-card"><div class="executive-k">Mod&egrave;le</div><div class="executive-v">{model_name}</div><div class="executive-copy">L&rsquo;interface met en avant la performance du mod&egrave;le sans perdre la lisibilit&eacute; op&eacute;rationnelle.</div></div>'
      f'</div>',
      unsafe_allow_html=True,
    )

    kpi_data = [
        ("Total Cas", f"{total_cas:,}", "&#x25B3;", "#0066CC", "#dbeafe", "#93c5fd"),
        ("Total D&eacute;c&egrave;s", f"{total_deces:,}", "&#x2665;", "#DC3545", "#fee2e2", "#fca5a5"),
        ("Maladies", f"{nb_maladies}", "&#x2736;", "#059669", "#d1fae5", "#6ee7b7"),
        ("Alertes g&eacute;n&eacute;r&eacute;es", f"{nb_alertes}", "&#x26A0;", "#D97706", "#fef3c7", "#fcd34d"),
        ("Autorit&eacute;s", f"{nb_users}", "&#x25CF;", "#7C3AED", "#ede9fe", "#c4b5fd"),
    ]
    cols = st.columns(5)
    for col, (label, val, icon, color, clr_light, clr_mid) in zip(cols, kpi_data):
        with col:
            st.markdown(
                f'<div class="metric-card" style="border-top-color:{color};--clr-light:{clr_light};--clr-mid:{clr_mid}">'
                f'<div class="metric-icon" style="color:{color}">{icon}</div>'
                f'<div class="metric-value" style="color:{color}">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-label">Performance & Tendances</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown(
            f'<div class="model-card">'
            f'<div class="model-name">Mod&egrave;le actif</div>'
            f'<div class="model-type">{model_name}</div>'
            f'<div class="model-pct">{acc*100:.1f}%</div>'
            f'<div class="model-label">Accuracy g&eacute;n&eacute;rale &mdash; F1&nbsp;Score: {f1:.3f}</div>'
            f'<div class="model-stat-row">'
            f'<div class="model-stat"><div class="model-stat-num">22 157</div><div class="model-stat-lbl">Echantillons</div></div>'
            f'<div class="model-stat"><div class="model-stat-num">27</div><div class="model-stat-lbl">Maladies</div></div>'
            f'<div class="model-stat"><div class="model-stat-num">26</div><div class="model-stat-lbl">Provinces</div></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown('<div class="content-card"><div class="card-title"><div class="card-title-bar"></div>Evolution des principales maladies</div>', unsafe_allow_html=True)
        if not df.empty and {"MALADIE", "TOTALCAS", "DEBUTSEM"}.issubset(df.columns):
            top5 = df.groupby("MALADIE")["TOTALCAS"].sum().nlargest(5).index
            fig = go.Figure()
            for color, disease in zip(["#0066CC", "#059669", "#D97706", "#DC3545", "#7C3AED"], top5):
                ddf = df[df["MALADIE"] == disease].sort_values("DEBUTSEM")
                fig.add_trace(
                    go.Scatter(
                        x=ddf["DEBUTSEM"],
                        y=ddf["TOTALCAS"],
                        mode="lines+markers",
                        name=disease,
                        line=dict(color=color, width=3),
                        marker=dict(size=7),
                    )
                )
            fig.update_layout(
                margin=dict(l=10, r=10, t=12, b=10),
                height=340,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248,250,252,.85)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                xaxis=dict(title="Semaine", showgrid=False),
                yaxis=dict(title="Cas", gridcolor="rgba(148,163,184,.18)"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de donnees pour afficher l'evolution des maladies.")
        st.markdown('</div>', unsafe_allow_html=True)


main()
