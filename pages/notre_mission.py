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


st.set_page_config(page_title="Notre Mission — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "notre_mission"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Mission",
    "Renforcer la veille sanitaire en RDC, territoire par territoire.",
    "SAFE CONGO organise la lecture du risque épidémiologique pour rendre l'alerte plus rapide, plus lisible et plus utile aux décisions sanitaires.",
    [
        (str(reference_metrics.get("provinces", 0)), "provinces suivies"),
        (str(reference_metrics.get("zones", 0)), "zones structurées"),
        (str(reference_metrics.get("diseases", 0)), "maladies retenues"),
    ],
    tone="mission",
)

st.markdown(
    """
<div class="public-page">
  <div class="public-grid-2">
    <div class="public-accent-card">
      <div class="public-section-head">
        <div>
          <div class="public-section-kicker">Priorité publique</div>
          <div class="public-section-title">Pourquoi SAFE CONGO est utile</div>
        </div>
        <p class="public-section-copy">Quand les signaux sont clairs, les décisions arrivent plus vite et au bon niveau.</p>
      </div>
      <p class="public-copy">SAFE CONGO a été conçu pour raccourcir le temps entre l'apparition d'une anomalie, son interprétation et la décision qui suit. L'objectif n'est pas de multiplier les tableaux, mais de donner aux responsables une lecture stable, claire et partagée.</p>
      <p class="public-copy">La plateforme soutient une réponse sanitaire sobre, rapide et traçable, en respectant les rôles de chaque niveau de responsabilité.</p>
      <div class="public-pill-row">
        <span class="public-pill">Lecture précoce</span>
        <span class="public-pill">Alerte graduée</span>
        <span class="public-pill">Coordination nationale</span>
      </div>
    </div>
    <div class="public-panel">
      <h3>Notre engagement</h3>
      <p>Transformer les observations territoriales en informations utiles, sans rompre le lien entre terrain, autorités sanitaires et pilotage national. SAFE CONGO doit rester lisible, traçable et utile à l'action.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Engagements</div>
        <div class="public-section-title">Ce que SAFE CONGO doit garantir</div>
      </div>
      <p class="public-section-copy">Chaque module vise la même finalité: rendre la décision sanitaire plus nette, mieux partagée et plus cohérente.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">01</div><div class="public-card-title">Lecture précoce</div><p class="public-card-copy">Identifier l'inhabituel à partir de données historiques et de signaux territoriaux.</p></div>
      <div class="public-card"><div class="public-card-kicker">02</div><div class="public-card-title">Alerte compréhensible</div><p class="public-card-copy">Présenter le risque dans un langage simple, utile à l'action et sans surcharge technique.</p></div>
      <div class="public-card"><div class="public-card-kicker">03</div><div class="public-card-title">Coordination continue</div><p class="public-card-copy">Relier administration centrale, provinces et zones de santé dans une même chaîne d'information.</p></div>
      <div class="public-card"><div class="public-card-kicker">04</div><div class="public-card-title">Décision mieux appuyée</div><p class="public-card-copy">Donner aux équipes un appui factuel partageable pour arbitrer plus vite et avec confiance.</p></div>
    </div>
  </div>

  <div class="public-band">
    <p>SAFE CONGO est un outil de confiance pour mieux lire, suivre et partager le risque sanitaire en RDC.</p>
    <span>Vision SAFE CONGO</span>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Trajectoire</div>
        <div class="public-section-title">Vision 2030</div>
      </div>
      <p class="public-section-copy">La plateforme est pensée pour évoluer avec les besoins de surveillance, sans perdre en simplicité.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Surveillance enrichie</div><p class="public-card-copy">Intégrer progressivement de nouveaux facteurs utiles: climat, mobilité, historique et pression territoriale.</p></div>
      <div class="public-card"><div class="public-card-title">Interopérabilité</div><p class="public-card-copy">Dialoguer avec les cadres nationaux et internationaux sans compliquer l'usage quotidien.</p></div>
      <div class="public-card"><div class="public-card-title">Qualité d'exécution</div><p class="public-card-copy">Garder une interface lisible, rapide et orientée vers les tâches réelles des équipes.</p></div>
      <div class="public-card"><div class="public-card-title">Portée nationale</div><p class="public-card-copy">Renforcer progressivement une surveillance moderne, responsable et adaptée au contexte de la RDC.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
