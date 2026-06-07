import inspect
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.public_ui import apply_public_theme, get_public_reference_metrics, render_public_hero, render_public_steps
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Fonctionnement — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "fonctionnement"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

steps = [
    ("01", "Collecte cadree", "Les donnees de terrain sont saisies avec une structure claire: territoire, maladie, volumes, severite et evolution constatee.", "Entree normalisee"),
    ("02", "Validation de confiance", "Chaque enregistrement est verifie, horodate et inscrit dans une chaine de tracabilite qui reduit les zones d'ombre.", "Qualite des donnees"),
    ("03", "Lecture predictive", "Le moteur analytique compare le present a l'historique, calcule les tendances et isole les comportements epidemiologiques inhabituels.", "Modeles filtres"),
    ("04", "Graduation du risque", "Le systeme traduit la complexite en niveaux d'alerte lisibles pour faciliter la priorisation et la mobilisation.", "Priorisation rapide"),
    ("05", "Diffusion instantanee", "Les autorites concernees recoivent des signaux contextualises avec localisation, gravite et mesures recommandees.", "Notification utile"),
    ("06", "Suivi executable", "Des rapports et syntheses sont prepares pour prolonger l'analyse dans les reunions, les cellules de crise et les equipes terrain.", "Rapport activable"),
]

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Mecanique intelligente",
  "Une chaine de decision lisible, de la saisie au signal d'alerte.",
  "SAFE CONGO agit comme une chaine de traitement disciplinee: il capte, ordonne, analyse et restitue. L'objectif est simple: offrir a chaque acteur sanitaire une lecture plus nette, plus rapide et plus exploitable.",
    [
        (str(len(steps)), "etapes structurees"),
    (str(reference_metrics.get("diseases", 0)), "maladies retenues"),
    (str(reference_metrics.get("zones", 0)), "zones observees"),
    ],
    tone="flow",
)

render_public_steps(steps)

st.markdown(
    """
<div class="public-page">
  <div class="public-grid-2">
    <div class="public-panel">
      <div class="public-section-head">
        <div>
          <div class="public-section-kicker">Graduation</div>
          <div class="public-section-title">Niveaux d'alerte utilises</div>
        </div>
        <p class="public-section-copy">La graduation privilegie une lecture simple, compatible avec une prise de decision rapide.</p>
      </div>
      <div class="public-auto-grid">
        <div class="public-card"><div class="public-card-title">Critique</div><p class="public-card-copy">Croissance tres elevee ou situation exigeant une intervention immediate et une mobilisation forte.</p></div>
        <div class="public-card"><div class="public-card-title">Haute</div><p class="public-card-copy">Pression nette demandant une reaction rapide, une verification terrain et une coordination resserree.</p></div>
        <div class="public-card"><div class="public-card-title">Moderee</div><p class="public-card-copy">Signal significatif appelant une surveillance renforcee, une lecture plus fine et un suivi structure.</p></div>
        <div class="public-card"><div class="public-card-title">Faible</div><p class="public-card-copy">Signal encore limite mais conserve pour suivre la tendance et documenter une possible evolution.</p></div>
      </div>
    </div>
    <div class="public-accent-card">
      <h3>Ce que la plateforme apporte vraiment</h3>
      <p>Elle reduit la friction entre information, interpretation et action. Au lieu d'un simple tableau de chiffres, l'utilisateur accede a une lecture du risque plus intelligible, plus responsable et directement exploitable.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Socle d'execution</div>
        <div class="public-section-title">Technologies mobilisees</div>
      </div>
      <p class="public-section-copy">Le choix technologique privilegie la lisibilite, la tracabilite et la vitesse d'operation plutot qu'une complexite demonstrative.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Python 3</div><p class="public-card-copy">Orchestre l'application et supporte les traitements analytiques avec un cadre lisible et maitrisable.</p></div>
      <div class="public-card"><div class="public-card-title">Streamlit</div><p class="public-card-copy">Fournit une interface web directe, rapide a maintenir et adaptee au pilotage sanitaire.</p></div>
      <div class="public-card"><div class="public-card-title">Modeles filtres</div><p class="public-card-copy">La prediction ne retient que les modeles juges assez solides pour un usage de decision.</p></div>
      <div class="public-card"><div class="public-card-title">SQLite</div><p class="public-card-copy">Assure un stockage simple, robuste et tracable pour les flux essentiels de l'application.</p></div>
      <div class="public-card"><div class="public-card-title">Pandas</div><p class="public-card-copy">Structure et prepare les donnees pour l'analyse, la consolidation et la restitution.</p></div>
      <div class="public-card"><div class="public-card-title">ReportLab</div><p class="public-card-copy">Transforme les alertes et syntheses en rapports exploitables par les reunions et les cellules terrain.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
