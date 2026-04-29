import streamlit as st
from pathlib import Path
import inspect
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Impact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "impact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
.stApp{background:linear-gradient(180deg,#eef6ff 0%,#e6f2fd 52%,#f0f8ff 100%)!important}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1180px}
.impact-hero{background:linear-gradient(135deg,#0b5a97 0%,#1193ca 56%,#53c0db 100%);border-radius:32px;padding:52px 56px;position:relative;overflow:hidden;box-shadow:0 26px 60px rgba(11,90,151,.2);margin-bottom:24px}
.impact-hero::after{content:'';position:absolute;right:-80px;bottom:-120px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.22),transparent 70%)}
.hero-kicker{display:inline-block;padding:6px 16px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#f7fbff;font-size:.72rem;font-weight:800;letter-spacing:2.4px;text-transform:uppercase}
.hero-title{font-family:'Sora',sans-serif;font-size:2.8rem;color:#fff;line-height:1.08;margin:18px 0 14px;max-width:760px}
.hero-sub{max-width:700px;color:rgba(247,251,255,.88);font-size:1rem;line-height:1.82;margin:0}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:18px;margin:22px 0}
.kpi-card{background:rgba(255,255,255,.88);border:1px solid rgba(166,204,233,.58);border-radius:24px;padding:24px;box-shadow:0 16px 38px rgba(35,91,150,.08)}
.kpi-num{font-family:'Sora',sans-serif;font-size:2rem;color:#0f5d93;margin-bottom:6px}
.kpi-label{font-size:.78rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:800;color:#5e86a3}
.kpi-desc{margin-top:10px;color:#67839d;font-size:.85rem;line-height:1.65}
.section-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:22px;margin-bottom:22px}
.section-card{background:rgba(255,255,255,.88);border:1px solid rgba(166,204,233,.58);border-radius:28px;padding:30px 32px;box-shadow:0 18px 40px rgba(35,91,150,.08)}
.section-title{font-family:'Sora',sans-serif;font-size:1.25rem;color:#0f4f7d;margin:0 0 14px}
.section-copy,.section-card li{color:#4e647e;font-size:.96rem;line-height:1.82}
.section-card ul{margin:14px 0 0;padding-left:18px}
.disease-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:18px}
.disease-tag{padding:12px 14px;border-radius:16px;background:linear-gradient(135deg,#ffffff,#edf8ff);border:1px solid rgba(166,204,233,.5);font-size:.82rem;font-weight:700;color:#195b8a;text-align:center}
.metric-row{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.metric-label{width:165px;flex-shrink:0;color:#4e647e;font-size:.86rem;font-weight:700}
.metric-track{flex:1;height:12px;border-radius:999px;background:#ddeefa;overflow:hidden}
.metric-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#1483d6,#63c9e7)}
.metric-val{width:54px;text-align:right;font-family:'Sora',sans-serif;color:#1483d6;font-size:.82rem}
.zone-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:18px}
.zone-card{padding:20px;border-radius:22px;background:linear-gradient(180deg,#ffffff,#edf8ff);border:1px solid rgba(166,204,233,.5)}
.zone-card h4{margin:0 0 8px;color:#0f4f7d;font-size:.95rem}
.zone-card p{margin:0;color:#64809b;font-size:.84rem;line-height:1.7}
@media (max-width: 900px){.impact-hero{padding:38px 24px}.hero-title{font-size:2.15rem}.section-grid{grid-template-columns:1fr}.section-card{padding:24px}.metric-row{align-items:flex-start;flex-direction:column}.metric-label,.metric-val{width:auto}}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)
render_public_sidebar(**SIDEBAR_KWARGS)

st.markdown(
    """
    <div class="impact-hero">
      <div class="hero-kicker">Preuves & resultats</div>
      <div class="hero-title">Un impact lisible, national et directement utile a la decision sanitaire.</div>
      <p class="hero-sub">Ici, la promesse devient mesure. SAFE CONGO consolide l'information epidemiologique, en extrait des signaux puissants et la transforme en indices de pilotage que les autorites peuvent mobiliser avec confiance.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-num">27 671</div><div class="kpi-label">observations traitees</div><div class="kpi-desc">Une base dense qui nourrit la robustesse des signaux epidemiologiques.</div></div>
      <div class="kpi-card"><div class="kpi-num">81.6%</div><div class="kpi-label">precision analytique</div><div class="kpi-desc">Une performance suffisamment solide pour soutenir des arbitrages rapides.</div></div>
      <div class="kpi-card"><div class="kpi-num">26</div><div class="kpi-label">provinces couvertes</div><div class="kpi-desc">Une lecture nationale qui n'oublie aucun territoire de la RDC.</div></div>
      <div class="kpi-card"><div class="kpi-num">517</div><div class="kpi-label">zones de sante</div><div class="kpi-desc">Un maillage territorial fin pour des alertes plus justes.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-grid">
      <div class="section-card">
        <h3 class="section-title">Pathologies prioritaires sous veille active</h3>
        <p class="section-copy">SAFE CONGO surveille un portefeuille de maladies prioritaires qui couvre les risques epidemiques, les maladies a propagation rapide et les signaux de tension sanitaire recurrente.</p>
        <div class="disease-grid">
          <div class="disease-tag">Cholera</div><div class="disease-tag">Mpox</div><div class="disease-tag">Ebola</div><div class="disease-tag">Rougeole</div><div class="disease-tag">Meningite</div><div class="disease-tag">Paludisme</div>
          <div class="disease-tag">Fievre typhoide</div><div class="disease-tag">Tuberculose</div><div class="disease-tag">COVID-19</div><div class="disease-tag">Dengue</div><div class="disease-tag">Fievre jaune</div><div class="disease-tag">IRA severe</div>
        </div>
      </div>
      <div class="section-card">
        <h3 class="section-title">Ce que signifient vraiment ces chiffres</h3>
        <p class="section-copy">Ils montrent qu'une plateforme bien pensee peut faire gagner en lucidite institutionnelle, en vitesse de lecture et en credibilite technique. L'impact n'est pas decoratif: il change la qualite de la reponse.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Lecture des performances</h3>
      <div class="metric-row"><div class="metric-label">Precision globale</div><div class="metric-track"><div class="metric-fill" style="width:81.6%"></div></div><div class="metric-val">81.6%</div></div>
      <div class="metric-row"><div class="metric-label">F1-score macro</div><div class="metric-track"><div class="metric-fill" style="width:45.8%"></div></div><div class="metric-val">45.8%</div></div>
      <div class="metric-row"><div class="metric-label">Couverture nationale</div><div class="metric-track"><div class="metric-fill" style="width:100%"></div></div><div class="metric-val">100%</div></div>
      <div class="metric-row"><div class="metric-label">Disponibilite systeme</div><div class="metric-track"><div class="metric-fill" style="width:99.5%"></div></div><div class="metric-val">99.5%</div></div>
      <p class="section-copy">Le modele XGBoost a ete optimize pour privilegier l'utilite operationnelle: assez sensible pour detecter l'inhabituel, assez stable pour eviter le bruit inutile dans la decision.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Carte d'intensite territoriale</h3>
      <div class="zone-grid">
        <div class="zone-card"><h4>Zone Est</h4><p>Nord-Kivu, Sud-Kivu, Ituri, Maniema et Tanganyika font l'objet d'une attention renforcee en raison de leur sensibilite epidemiologique et logistique.</p></div>
        <div class="zone-card"><h4>Zone Centrale</h4><p>Kinshasa, Kongo Central, Kwango, Kwilu, Mai-Ndombe et Kasai structurent le coeur de pilotage et de remontée des signaux.</p></div>
        <div class="zone-card"><h4>Zone Nord</h4><p>Equateur, Sud-Ubangi, Nord-Ubangi, Mongala, Tshopo, Bas-Uele et Haut-Uele composent un ensemble ou l'anticipation territoriale reste determinante.</p></div>
        <div class="zone-card"><h4>Zone Sud</h4><p>Haut-Katanga, Lualaba, Haut-Lomami, Lomami, Sankuru et Tanganyika prolongent la couverture nationale avec des profils de risques distincts.</p></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
