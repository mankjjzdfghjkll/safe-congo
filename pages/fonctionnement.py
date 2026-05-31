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
    "Une chaine de decision fluide, du terrain jusqu'au signal d'alerte.",
    "SAFE CONGO fonctionne comme une salle de pilotage silencieuse: il capte, ordonne, analyse et restitue. L'objectif est simple: donner a chaque acteur sanitaire une lecture plus nette, plus rapide et plus exploitable.",
    [
        (str(len(steps)), "etapes structurees"),
    (str(reference_metrics.get("diseases", 0)), "maladies suivies"),
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
      <h3>Niveaux d'alerte actuellement utilises</h3>
      <div class="public-auto-grid">
        <div class="public-card"><div class="public-card-title">Critique</div><p class="public-card-copy">Croissance superieure a 50% et intervention immediate.</p></div>
        <div class="public-card"><div class="public-card-title">Haute</div><p class="public-card-copy">Croissance superieure a 25% et mobilisation rapide.</p></div>
        <div class="public-card"><div class="public-card-title">Moderee</div><p class="public-card-copy">Croissance a partir de 10% et surveillance renforcee.</p></div>
        <div class="public-card"><div class="public-card-title">Info</div><p class="public-card-copy">Signal faible conserve pour le suivi et la lecture de tendance.</p></div>
      </div>
    </div>
    <div class="public-panel">
      <h3>Ce que la plateforme apporte vraiment</h3>
      <p class="public-copy">Elle reduit la friction entre information, interpretation et action. Au lieu d'un simple tableau de chiffres, l'utilisateur accede a une narration du risque, lisible et directement exploitable.</p>
      <p class="public-copy">La page publique n'exagere plus les seuils: elle decrit la graduation effectivement utilisee dans les alertes du systeme.</p>
    </div>
  </div>

  <div class="public-panel">
    <h3>Socle technologique</h3>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Python 3</div><p class="public-card-copy">Pilote l'orchestration applicative et les traitements analytiques.</p></div>
      <div class="public-card"><div class="public-card-title">Streamlit</div><p class="public-card-copy">Offre une experience web rapide, lisible et operationnelle.</p></div>
      <div class="public-card"><div class="public-card-title">Modeles filtres</div><p class="public-card-copy">La prediction conserve les modeles qui restent assez solides pour un usage de pilotage.</p></div>
      <div class="public-card"><div class="public-card-title">SQLite</div><p class="public-card-copy">Garantit un stockage simple, solide et tracable.</p></div>
      <div class="public-card"><div class="public-card-title">Pandas</div><p class="public-card-copy">Met les donnees en forme pour l'analyse et la restitution.</p></div>
      <div class="public-card"><div class="public-card-title">ReportLab</div><p class="public-card-copy">Transforme les alertes en rapports distribuables.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
