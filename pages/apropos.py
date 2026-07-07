import inspect
import importlib
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

import utils.public_ui as public_ui
import utils.sidebar_brand as sidebar_brand

importlib.reload(public_ui)
importlib.reload(sidebar_brand)

from utils.public_ui import apply_public_theme, get_public_reference_metrics, render_public_hero
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="À propos - SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "apropos"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "À propos de la plateforme",
    "SAFE CONGO, un portail de veille sanitaire clair et sécurisé.",
    "SAFE CONGO aide les équipes sanitaires à suivre les signaux épidémiologiques, comprendre les niveaux de risque et coordonner les réponses avec une information plus lisible.",
    [
        (str(reference_metrics.get("provinces", 0)), "provinces suivies"),
        (str(reference_metrics.get("zones", 0)), "zones observées"),
        (str(reference_metrics.get("diseases", 0)), "maladies retenues"),
    ],
    tone="mission",
)

st.markdown(
    """
<div class="public-page">
  <div class="public-grid-2">
    <div class="public-panel">
      <div class="public-section-head">
        <div>
          <div class="public-section-kicker">Définition</div>
          <div class="public-section-title">Ce qu'est SAFE CONGO</div>
        </div>
        <p class="public-section-copy">Un outil pensé pour comprendre plus vite et mieux organiser la réponse sanitaire.</p>
      </div>
      <p class="public-copy">SAFE CONGO consolide les observations de santé publique, les transforme en repères faciles à lire et aide les responsables à prioriser leurs décisions. La plateforme ne remplace pas l'expertise humaine: elle la rend plus rapide, plus structurée et plus partageable.</p>
      <div class="public-pill-row">
        <span class="public-pill">Lecture du risque</span>
        <span class="public-pill">Alerte graduée</span>
        <span class="public-pill">Coordination territoriale</span>
      </div>
    </div>
    <div class="public-accent-card">
      <h3>Rôle de l'application</h3>
      <p>SAFE CONGO relie les données, l'analyse et l'action. Son rôle est d'aider les acteurs sanitaires à détecter les tensions, qualifier l'urgence et diffuser l'information au bon niveau territorial.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Objectifs</div>
        <div class="public-section-title">Les objectifs de SAFE CONGO</div>
      </div>
      <p class="public-section-copy">Des objectifs concrets: mieux lire les signaux, réduire les délais et soutenir la coordination.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">Objectif 01</div><div class="public-card-title">Détecter plus tôt</div><p class="public-card-copy">Repérer les signaux inhabituels avant qu'ils ne deviennent des situations critiques.</p></div>
      <div class="public-card"><div class="public-card-kicker">Objectif 02</div><div class="public-card-title">Qualifier le risque</div><p class="public-card-copy">Traduire la complexité épidémiologique en niveaux d'alerte simples et exploitables.</p></div>
      <div class="public-card"><div class="public-card-kicker">Objectif 03</div><div class="public-card-title">Mieux coordonner</div><p class="public-card-copy">Relier les provinces, zones de santé et équipes de pilotage autour d'une même information.</p></div>
      <div class="public-card"><div class="public-card-kicker">Objectif 04</div><div class="public-card-title">Soutenir l'action</div><p class="public-card-copy">Donner aux responsables des repères utiles pour prioriser, notifier et agir plus vite.</p></div>
    </div>
  </div>

  <div class="public-band">
    <p>SAFE CONGO aide à passer d'une surveillance descriptive à une surveillance utile à la décision.</p>
    <span>Rôle stratégique de la plateforme</span>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Périmètre</div>
        <div class="public-section-title">Ce que la plateforme apporte</div>
      </div>
      <p class="public-section-copy">Un parcours complet, du signal local jusqu'à la lecture nationale.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Collecte structurée</div><p class="public-card-copy">Les informations terrain sont saisies dans un cadre commun qui facilite la consolidation.</p></div>
      <div class="public-card"><div class="public-card-title">Analyse interprétable</div><p class="public-card-copy">Les données deviennent des tendances, alertes et repères visuels faciles à lire.</p></div>
      <div class="public-card"><div class="public-card-title">Diffusion ciblée</div><p class="public-card-copy">Les signaux utiles sont adressés aux bons acteurs selon le territoire et le niveau de responsabilité.</p></div>
      <div class="public-card"><div class="public-card-title">Suivi documenté</div><p class="public-card-copy">La plateforme soutient les rapports, traces et restitutions utiles aux réunions de coordination.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
