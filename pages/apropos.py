import inspect
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.public_ui import apply_public_theme, get_public_reference_metrics, render_public_hero
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="A propos - SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "apropos"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "A propos de la plateforme",
    "SAFE CONGO, une application de veille sanitaire orientee decision.",
    "SAFE CONGO est une plateforme de surveillance epidemiologique qui aide a structurer les signaux, a accelerer la lecture du risque et a soutenir une coordination plus fiable entre les acteurs sanitaires.",
    [
        (str(reference_metrics.get("provinces", 0)), "provinces suivies"),
        (str(reference_metrics.get("zones", 0)), "zones observees"),
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
          <div class="public-section-kicker">Definition</div>
          <div class="public-section-title">Ce qu'est SAFE CONGO</div>
        </div>
        <p class="public-section-copy">Une plateforme utile lorsque l'enjeu principal est de comprendre plus vite et de mieux coordonner la reponse.</p>
      </div>
      <p class="public-copy">SAFE CONGO est une application de veille sanitaire qui consolide des observations epidemiologiques, les transforme en repères lisibles et aide les responsables a prioriser leurs decisions. Elle ne remplace pas l'expertise humaine: elle la rend plus rapide, plus structuree et plus partageable.</p>
      <div class="public-pill-row">
        <span class="public-pill">Lecture du risque</span>
        <span class="public-pill">Alerte graduee</span>
        <span class="public-pill">Coordination territoriale</span>
      </div>
    </div>
    <div class="public-accent-card">
      <h3>Role de l'application</h3>
      <p>SAFE CONGO sert a faire le lien entre la donnee, l'analyse et l'action. Son role est d'aider les acteurs sanitaires a detecter les tensions, qualifier le niveau d'urgence et diffuser une information utile au bon niveau territorial.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Objectifs</div>
        <div class="public-section-title">Les objectifs de SAFE CONGO</div>
      </div>
      <p class="public-section-copy">L'application poursuit des objectifs concrets, orientes vers la lisibilite de la decision et la rapidite de la reponse.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">Objectif 01</div><div class="public-card-title">Detecter plus tot</div><p class="public-card-copy">Reperer les signaux inhabituels avant qu'ils ne deviennent des crises visibles dans les territoires.</p></div>
      <div class="public-card"><div class="public-card-kicker">Objectif 02</div><div class="public-card-title">Qualifier le risque</div><p class="public-card-copy">Traduire la complexite epidemiologique en niveaux d'alerte simples et exploitables.</p></div>
      <div class="public-card"><div class="public-card-kicker">Objectif 03</div><div class="public-card-title">Mieux coordonner</div><p class="public-card-copy">Relier les provinces, zones de sante et equipes de pilotage autour d'un meme niveau d'information.</p></div>
      <div class="public-card"><div class="public-card-kicker">Objectif 04</div><div class="public-card-title">Soutenir l'action</div><p class="public-card-copy">Donner aux responsables des reperes utiles pour prioriser, notifier et agir plus vite.</p></div>
    </div>
  </div>

  <div class="public-band">
    <p>SAFE CONGO aide a passer d'une surveillance descriptive a une surveillance utile a la decision.</p>
    <span>Role strategique de la plateforme</span>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Perimetre</div>
        <div class="public-section-title">Ce que la plateforme apporte</div>
      </div>
      <p class="public-section-copy">L'application structure un parcours complet, du signal local jusqu'a la lecture nationale.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Collecte structuree</div><p class="public-card-copy">Les informations terrain sont saisies dans un cadre commun qui facilite la consolidation.</p></div>
      <div class="public-card"><div class="public-card-title">Analyse interpretable</div><p class="public-card-copy">Les donnees sont converties en tendances, alertes et reperes visuels plus faciles a lire.</p></div>
      <div class="public-card"><div class="public-card-title">Diffusion ciblee</div><p class="public-card-copy">Les signaux utiles sont adresses aux bons acteurs selon le territoire et le niveau de responsabilite.</p></div>
      <div class="public-card"><div class="public-card-title">Suivi documente</div><p class="public-card-copy">La plateforme soutient aussi les rapports, traces et restitutions utiles aux reunions et cellules de coordination.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
