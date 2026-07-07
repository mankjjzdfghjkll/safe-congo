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


st.set_page_config(page_title="Contact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "contact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Contact",
    "Accès, coordination et partenariats autour de SAFE CONGO.",
    "Cette page oriente les demandes liées à l'accès, au déploiement et à la coordination institutionnelle de la plateforme.",
    [
        ("4", "partenaires de référence"),
    (str(reference_metrics.get("provinces", 0)), "provinces suivies"),
    (str(reference_metrics.get("zones", 0)), "zones observées"),
    ],
    tone="contact",
)

st.markdown(
    """
<div class="public-page">
  <div class="public-grid-2">
    <div class="public-panel">
      <div class="public-section-head">
        <div>
          <div class="public-section-kicker">Coordination</div>
          <div class="public-section-title">Quand mobiliser SAFE CONGO</div>
        </div>
        <p class="public-section-copy">Un espace public clair, sans contacts fictifs ni informations sensibles.</p>
      </div>
      <p class="public-copy">Les demandes relatives au déploiement, à l'accès, à la gouvernance ou à l'usage de la plateforme passent par les circuits institutionnels prévus par SAFE CONGO.</p>
      <div class="public-pill-row">
        <span class="public-pill">Accès plateforme</span>
        <span class="public-pill">Coordination partenaire</span>
        <span class="public-pill">Support d'exploitation</span>
      </div>
    </div>
    <div class="public-accent-card">
      <h3>Principe de gouvernance</h3>
      <p>Les comptes des autorités sanitaires sont vérifiés, rattachés à un territoire et activés selon le niveau de responsabilité. SAFE CONGO privilégie la discipline d'accès et la clarté institutionnelle.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Partenaires</div>
        <div class="public-section-title">Références institutionnelles</div>
      </div>
      <p class="public-section-copy">La surveillance sanitaire gagne en efficacité lorsqu'elle s'appuie sur des références reconnues.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Ministère de la Santé</div><p class="public-card-copy">Ancrage institutionnel et priorisation nationale.</p><a class="public-partner-link" href="https://www.minisanterdc.cd" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">OMS RDC</div><p class="public-card-copy">Cadre de référence international et expertise de santé publique.</p><a class="public-partner-link" href="https://www.who.int/fr" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">UNICEF RDC</div><p class="public-card-copy">Coordination sur les enjeux populationnels et communautaires.</p><a class="public-partner-link" href="https://www.unicef.org/drcongo" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">Africa CDC</div><p class="public-card-copy">Perspective régionale et harmonisation des pratiques.</p><a class="public-partner-link" href="https://africacdc.org" target="_blank">Visiter le site</a></div>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Parcours d'accès</div>
        <div class="public-section-title">Demande d'accès</div>
      </div>
      <p class="public-section-copy">Le processus d'ouverture privilégie la vérification, le rattachement territorial et un démarrage accompagné.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">Étape 1</div><div class="public-card-title">Formuler la demande</div><p class="public-card-copy">Lancer la pré-inscription avec la fonction, le territoire et l'usage attendu.</p></div>
      <div class="public-card"><div class="public-card-kicker">Étape 2</div><div class="public-card-title">Vérifier le profil</div><p class="public-card-copy">Rattacher les informations au bon niveau de responsabilité, à la province et à la zone de santé.</p></div>
      <div class="public-card"><div class="public-card-kicker">Étape 3</div><div class="public-card-title">Activer et accompagner</div><p class="public-card-copy">Après validation, l'équipe d'administration ouvre l'accès et accompagne la prise en main.</p></div>
    </div>
    <div class="public-note" style="margin-top:18px">Les utilisateurs peuvent lancer une pré-inscription depuis la page d'accueil, puis attendre la validation administrative.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
