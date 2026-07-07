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
    ("01", "Collecte cadrée", "Les données de terrain sont saisies avec les informations essentielles: territoire, maladie, volume, gravité et évolution.", "Saisie claire"),
    ("02", "Vérification", "Chaque enregistrement est contrôlé, daté et rattaché à son territoire pour garder une trace fiable.", "Qualité des données"),
    ("03", "Analyse", "Le système compare les données récentes à l'historique et repère les comportements inhabituels.", "Lecture du risque"),
    ("04", "Niveau d'alerte", "Le risque est traduit en niveaux simples pour faciliter la priorisation.", "Priorisation rapide"),
    ("05", "Notification", "Les autorités concernées reçoivent un signal contextualisé: localisation, gravité et informations utiles.", "Alerte utile"),
    ("06", "Suivi", "Les rapports et synthèses prolongent l'analyse dans les réunions, cellules de crise et équipes terrain.", "Action documentée"),
]

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Fonctionnement",
    "Un parcours simple, de la saisie terrain à l'alerte utile.",
    "SAFE CONGO capte, vérifie, analyse et restitue les signaux sanitaires. L'objectif est de donner à chaque acteur une information claire, rapide et exploitable.",
    [
        (str(len(steps)), "étapes structurées"),
    (str(reference_metrics.get("diseases", 0)), "maladies retenues"),
    (str(reference_metrics.get("zones", 0)), "zones observées"),
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
          <div class="public-section-title">Niveaux d'alerte utilisés</div>
        </div>
        <p class="public-section-copy">Une lecture simple pour aider les équipes à agir sans perdre de temps.</p>
      </div>
      <div class="public-auto-grid">
        <div class="public-card"><div class="public-card-title">Critique</div><p class="public-card-copy">Situation exigeant une intervention immédiate et une mobilisation forte.</p></div>
        <div class="public-card"><div class="public-card-title">Haute</div><p class="public-card-copy">Pression nette demandant une réaction rapide, une vérification terrain et une coordination serrée.</p></div>
        <div class="public-card"><div class="public-card-title">Modérée</div><p class="public-card-copy">Signal significatif appelant une surveillance renforcée et un suivi structuré.</p></div>
        <div class="public-card"><div class="public-card-title">Faible</div><p class="public-card-copy">Signal limité, mais conservé pour suivre la tendance et documenter l'évolution.</p></div>
      </div>
    </div>
    <div class="public-accent-card">
      <h3>Ce que la plateforme apporte vraiment</h3>
      <p>Elle réduit l'écart entre information, interprétation et action. L'utilisateur ne voit pas seulement des chiffres: il comprend mieux le niveau de risque et les priorités.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Socle technique</div>
        <div class="public-section-title">Technologies mobilisées</div>
      </div>
      <p class="public-section-copy">Des outils simples et robustes pour garder une application lisible, rapide et maintenable.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Python 3</div><p class="public-card-copy">Orchestre l'application et supporte les traitements analytiques.</p></div>
      <div class="public-card"><div class="public-card-title">Streamlit</div><p class="public-card-copy">Fournit une interface web directe, claire et adaptée au pilotage sanitaire.</p></div>
      <div class="public-card"><div class="public-card-title">Modèles filtrés</div><p class="public-card-copy">La prédiction ne retient que les modèles jugés assez solides pour appuyer la décision.</p></div>
      <div class="public-card"><div class="public-card-title">SQLite</div><p class="public-card-copy">Assure un stockage simple et traçable pour les flux essentiels.</p></div>
      <div class="public-card"><div class="public-card-title">Pandas</div><p class="public-card-copy">Structure les données pour l'analyse, la consolidation et la restitution.</p></div>
      <div class="public-card"><div class="public-card-title">ReportLab</div><p class="public-card-copy">Transforme les alertes et synthèses en rapports exploitables.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
