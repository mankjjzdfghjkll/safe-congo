import inspect
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.public_ui import apply_public_theme, get_public_reference_metrics, render_public_hero
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Notre Mission — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "notre_mission"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Cap strategique",
    "Une mission de souverainete sanitaire au service de chaque territoire.",
    "SAFE CONGO organise la lecture du risque epidemiologique pour que l'alerte publique soit plus rapide, plus lisible et plus responsable. La plateforme aide l'Etat, les provinces et les equipes sanitaires a partager un meme niveau d'information utile au moment de decider.",
    [
        (str(reference_metrics.get("provinces", 0)), "provinces suivies"),
        (str(reference_metrics.get("zones", 0)), "zones structurees"),
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
          <div class="public-section-kicker">Mandat public</div>
          <div class="public-section-title">Pourquoi SAFE CONGO compte</div>
        </div>
        <p class="public-section-copy">Dans un pays-continent, la qualite de lecture des signaux faibles devient un avantage de protection collective.</p>
      </div>
      <p class="public-copy">SAFE CONGO a ete concu pour raccourcir le temps entre l'apparition d'une anomalie, son interpretation et la decision publique qui en decoule. L'objectif n'est pas de multiplier les tableaux, mais de donner aux responsables sanitaires une lecture plus stable, plus claire et mieux partagee.</p>
      <p class="public-copy">La plateforme fait converger rigueur analytique, logique institutionnelle et ergonomie de pilotage pour soutenir une reponse sanitaire sobre, rapide et defensable.</p>
      <div class="public-pill-row">
        <span class="public-pill">Lecture precoce</span>
        <span class="public-pill">Alerte graduelle</span>
        <span class="public-pill">Coordination nationale</span>
      </div>
    </div>
    <div class="public-panel">
      <h3>Notre promesse institutionnelle</h3>
      <p>Transformer des observations territoriales en intelligence de decision, sans rompre la chaine entre terrain, autorites sanitaires et pilotage national. SAFE CONGO doit rester un outil de confiance: lisible, traceable et utile a l'action.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Fondations</div>
        <div class="public-section-title">Les quatre engagements qui structurent SAFE CONGO</div>
      </div>
      <p class="public-section-copy">Chaque brique du systeme vise la meme finalite: rendre la decision sanitaire plus nette, mieux distribuee et plus coherente.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">01</div><div class="public-card-title">Lecture precoce</div><p class="public-card-copy">Identifier l'inhabituel avant qu'il ne devienne une crise visible, a partir d'un historique consolide et de signaux recontextualises.</p></div>
      <div class="public-card"><div class="public-card-kicker">02</div><div class="public-card-title">Alerte intelligible</div><p class="public-card-copy">Formuler le risque dans un langage exploitable par la decision publique, sans surcharge technique ni ambiguite operationnelle.</p></div>
      <div class="public-card"><div class="public-card-kicker">03</div><div class="public-card-title">Coordination continue</div><p class="public-card-copy">Relier administration centrale, provinces et zones de sante dans une meme chaine d'information et de responsabilite.</p></div>
      <div class="public-card"><div class="public-card-kicker">04</div><div class="public-card-title">Decision augmentee</div><p class="public-card-copy">Donner aux equipes un appui factuel partageable, pour arbitrer plus vite et avec un meilleur niveau de confiance.</p></div>
    </div>
  </div>

  <div class="public-band">
    <p>SAFE CONGO n'est pas seulement une interface. C'est une architecture de confiance pour la lecture du risque sanitaire en RDC.</p>
    <span>Vision institutionnelle SAFE CONGO</span>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Trajectoire</div>
        <div class="public-section-title">Vision 2030</div>
      </div>
      <p class="public-section-copy">La plateforme est pensee pour grandir avec les besoins de surveillance, sans perdre en sobriete ni en lisibilite.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Surveillance enrichie</div><p class="public-card-copy">Integrer climat, mobilite, pression demographique et historiques territoriaux pour affiner encore la lecture du risque.</p></div>
      <div class="public-card"><div class="public-card-title">Interoperabilite regionale</div><p class="public-card-copy">Dialoguer avec les cadres OMS, Africa CDC et les initiatives transfrontalieres sans fragmenter les usages nationaux.</p></div>
      <div class="public-card"><div class="public-card-title">Excellence d'execution</div><p class="public-card-copy">Faire de SAFE CONGO une reference de discipline visuelle, de rapidite de lecture et de sobriete operationnelle.</p></div>
      <div class="public-card"><div class="public-card-title">Rayonnement africain</div><p class="public-card-copy">Faire emerger depuis la RDC un standard continental de surveillance epidemiologique moderne, responsable et souverain.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
