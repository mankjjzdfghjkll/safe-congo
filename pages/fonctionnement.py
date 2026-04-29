import streamlit as st
from pathlib import Path
import inspect
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Fonctionnement — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "fonctionnement"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
.stApp{background:linear-gradient(180deg,#eef6ff 0%,#e6f2fd 52%,#f0f8ff 100%)!important}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1180px}
.flow-hero{background:linear-gradient(135deg,#124f8d 0%,#1979bf 54%,#5fb8ea 100%);border-radius:32px;padding:52px 56px;position:relative;overflow:hidden;box-shadow:0 26px 60px rgba(18,79,141,.2);margin-bottom:24px}
.flow-hero::after{content:'';position:absolute;left:-80px;bottom:-130px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 72%)}
.hero-kicker{display:inline-block;padding:6px 16px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#f7fbff;font-size:.72rem;font-weight:800;letter-spacing:2.4px;text-transform:uppercase}
.hero-title{font-family:'Sora',sans-serif;font-size:2.8rem;color:#fff;line-height:1.08;margin:18px 0 14px;max-width:760px}
.hero-sub{max-width:720px;color:rgba(247,251,255,.88);font-size:1rem;line-height:1.82;margin:0}
.timeline{margin:24px 0}
.step-card{position:relative;padding:0 0 20px 68px;margin-bottom:22px}
.step-card::before{content:'';position:absolute;left:21px;top:48px;bottom:-14px;width:2px;background:linear-gradient(180deg,#6bbdf0,rgba(107,189,240,0))}
.step-card.last::before{display:none}
.step-num{position:absolute;left:0;top:0;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#124f8d,#47a8e7);color:#fff;font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 14px 28px rgba(18,79,141,.22)}
.step-body{background:rgba(255,255,255,.88);border:1px solid rgba(166,204,233,.58);border-radius:24px;padding:22px 24px;box-shadow:0 16px 38px rgba(35,91,150,.08)}
.step-title{font-family:'Sora',sans-serif;color:#124f8d;font-size:1.04rem;margin:0 0 8px}
.step-desc{color:#4e647e;font-size:.94rem;line-height:1.78;margin:0}
.step-tag{display:inline-block;margin-top:12px;padding:5px 10px;border-radius:999px;background:#e7f5ff;color:#1979bf;font-size:.72rem;font-weight:800;letter-spacing:1.1px;text-transform:uppercase}
.section-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;margin:22px 0}
.section-card{background:rgba(255,255,255,.88);border:1px solid rgba(166,204,233,.58);border-radius:28px;padding:30px 32px;box-shadow:0 18px 40px rgba(35,91,150,.08)}
.section-title{font-family:'Sora',sans-serif;font-size:1.2rem;color:#124f8d;margin:0 0 14px}
.section-copy,.section-card li{color:#4e647e;font-size:.95rem;line-height:1.82}
.section-card ul{margin:14px 0 0;padding-left:18px}
.badge-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px}
.badge{padding:16px;border-radius:20px;text-align:center;font-weight:800;font-size:.9rem}
.badge small{display:block;font-size:.75rem;font-weight:700;opacity:.8;margin-top:6px;line-height:1.55}
.badge-red{background:#fff1f1;color:#b42318;border:1px solid #f5b7b1}
.badge-orange{background:#fff5eb;color:#b54708;border:1px solid #f9c78f}
.badge-blue{background:#edf8ff;color:#156fb5;border:1px solid #b8dcf7}
.tech-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-top:18px}
.tech-card{padding:18px;border-radius:20px;background:linear-gradient(180deg,#ffffff,#edf8ff);border:1px solid rgba(166,204,233,.5)}
.tech-name{font-weight:800;color:#124f8d;font-size:.92rem;margin-bottom:6px}
.tech-role{color:#67839d;font-size:.8rem;line-height:1.6}
@media (max-width: 900px){.flow-hero{padding:38px 24px}.hero-title{font-size:2.15rem}.section-grid{grid-template-columns:1fr}.step-card{padding-left:58px}.section-card{padding:24px}}
</style>"""

steps = [
    ("01", "Collecte cadree", "Les donnees de terrain sont saisies avec une structure claire: territoire, maladie, volumes, severite et evolution constatee.", "Entree normalisee"),
    ("02", "Validation de confiance", "Chaque enregistrement est verifie, horodate et inscrit dans une chaine de traçabilite qui reduit les zones d'ombre.", "Qualite des donnees"),
    ("03", "Lecture predictive", "Le moteur analytique compare le present a l'historique, calcule les tendances et isole les comportements epidemiologiques inhabituels.", "XGBoost pilote"),
    ("04", "Graduation du risque", "Le systeme traduit la complexite en niveaux d'alerte lisibles pour faciliter la priorisation et la mobilisation.", "Priorisation rapide"),
    ("05", "Diffusion instantanee", "Les autorites concernees reçoivent des signaux contextualises avec localisation, gravite et mesures recommandees.", "Notification utile"),
    ("06", "Suivi executable", "Des rapports et syntheses sont generes pour prolonger l'analyse dans les reunions, les cellules de crise et les equipes terrain.", "Rapport activable"),
]

st.markdown(CSS, unsafe_allow_html=True)
render_public_sidebar(**SIDEBAR_KWARGS)

st.markdown(
    """
    <div class="flow-hero">
      <div class="hero-kicker">Mecanique intelligente</div>
      <div class="hero-title">Une chaine de decision fluide, du terrain jusqu'au signal d'alerte.</div>
      <p class="hero-sub">SAFE CONGO fonctionne comme une salle de pilotage silencieuse: il capte, ordonne, analyse et restitue. L'objectif est simple: donner a chaque acteur sanitaire une lecture plus nette, plus rapide et plus exploitable.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

for index, (num, title, desc, tag) in enumerate(steps):
    classes = "step-card last" if index == len(steps) - 1 else "step-card"
    st.markdown(
        f"""
        <div class="{classes}">
          <div class="step-num">{num}</div>
          <div class="step-body">
            <div class="step-title">{title}</div>
            <p class="step-desc">{desc}</p>
            <span class="step-tag">{tag}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="section-grid">
      <div class="section-card">
        <h3 class="section-title">Niveaux d'alerte</h3>
        <div class="badge-row">
          <div class="badge badge-red">Critique<small>Croissance > 200% et intervention immediate</small></div>
          <div class="badge badge-orange">Haute<small>Croissance 100 a 200% et mobilisation rapide</small></div>
          <div class="badge badge-blue">Moderee<small>Croissance 50 a 100% et surveillance renforcee</small></div>
        </div>
      </div>
      <div class="section-card">
        <h3 class="section-title">Ce que la plateforme apporte vraiment</h3>
        <p class="section-copy">Elle reduit la friction entre information, interpretation et action. Au lieu d'un simple tableau de chiffres, l'utilisateur accede a une narration du risque, lisible et directement exploitable.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Socle technologique</h3>
      <div class="tech-grid">
        <div class="tech-card"><div class="tech-name">Python 3</div><div class="tech-role">Pilote l'orchestration applicative et les traitements analytiques.</div></div>
        <div class="tech-card"><div class="tech-name">Streamlit</div><div class="tech-role">Offre une experience web rapide, lisible et operationnelle.</div></div>
        <div class="tech-card"><div class="tech-name">XGBoost</div><div class="tech-role">Repere les signaux faibles et soutient la prediction du risque.</div></div>
        <div class="tech-card"><div class="tech-name">SQLite</div><div class="tech-role">Garantit un stockage simple, solide et traçable.</div></div>
        <div class="tech-card"><div class="tech-name">Pandas</div><div class="tech-role">Met les donnees en forme pour l'analyse et la restitution.</div></div>
        <div class="tech-card"><div class="tech-name">ReportLab</div><div class="tech-role">Transforme les alertes en rapports distribuables.</div></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
