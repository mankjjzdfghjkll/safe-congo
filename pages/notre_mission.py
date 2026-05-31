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
    "Une mission de souverainete sanitaire, pensee pour proteger chaque territoire.",
    "SAFE CONGO transforme la surveillance epidemiologique en capacite d'anticipation. L'ambition n'est pas seulement de voir l'epidemie arriver, mais d'offrir aux decideurs congolais une longueur d'avance plus claire, plus lisible et plus actionnable.",
    [
        (str(reference_metrics.get("provinces", 0)), "provinces structurees"),
        (str(reference_metrics.get("zones", 0)), "zones observees"),
      (str(reference_metrics.get("diseases", 0)), "maladies suivies"),
    ],
    tone="mission",
)

st.markdown(
    """
<div class="public-page">
  <div class="public-grid-2">
    <div class="public-panel">
      <h3>Pourquoi SAFE CONGO existe</h3>
      <p class="public-copy">Dans un pays-continent, la vitesse de lecture des signaux faibles devient une force de protection collective. SAFE CONGO a ete concu pour reduire le delai entre l'apparition d'une anomalie, sa comprehension et la decision publique qui suit.</p>
      <p class="public-copy">La plateforme fait converger intelligence analytique, expertise epidemiologique et ergonomie de decision afin que les responsables sanitaires disposent d'un systeme qui rassure, eclaire et accelere l'action.</p>
    </div>
    <div class="public-panel">
      <h3>Notre promesse institutionnelle</h3>
      <ul>
        <li>Transformer les donnees locales en vision nationale nette.</li>
        <li>Rehausser la confiance des autorites dans la lecture des risques.</li>
        <li>Fournir des alertes dignes d'une gouvernance moderne et reactive.</li>
      </ul>
      <div class="public-note" style="margin-top:16px">Le socle public et les espaces admin/autorite parlent desormais le meme langage visuel, pour renforcer la perception d'un systeme unique et non d'une juxtaposition d'ecrans.</div>
    </div>
  </div>

  <div class="public-panel">
    <h3>Les quatre fondations qui portent SAFE CONGO</h3>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Lecture precoce</div><p class="public-card-copy">Identifier l'inhabituel avant qu'il ne devienne une crise visible, grace a un moteur analytique entraine sur des donnees reelles.</p></div>
      <div class="public-card"><div class="public-card-title">Alerte de precision</div><p class="public-card-copy">Envoyer le bon signal, au bon niveau, au bon moment, avec un langage comprehensible pour l'action publique.</p></div>
      <div class="public-card"><div class="public-card-title">Coordination continue</div><p class="public-card-copy">Relier provinces, zones de sante et gouvernance centrale au sein d'une meme colonne vertebrale operationnelle.</p></div>
      <div class="public-card"><div class="public-card-title">Decision augmentee</div><p class="public-card-copy">Permettre aux equipes de terrain et aux autorites de choisir vite, avec une base factuelle solide et partageable.</p></div>
    </div>
  </div>

  <div class="public-band">
    <p>SAFE CONGO n'est pas seulement une interface. C'est une architecture de confiance pour la sante publique congolaise.</p>
    <span>Vision SAFE CONGO</span>
  </div>

  <div class="public-panel">
    <h3>Vision 2030</h3>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Surveillance enrichie</div><p class="public-card-copy">Integrer climat, mobilite, pression demographique et historiques locaux pour des alertes encore plus fines.</p></div>
      <div class="public-card"><div class="public-card-title">Interoperabilite regionale</div><p class="public-card-copy">Connecter SAFE CONGO aux cadres OMS, Africa CDC et aux initiatives transfrontalieres des Grands Lacs.</p></div>
      <div class="public-card"><div class="public-card-title">Excellence d'execution</div><p class="public-card-copy">Faire de la plateforme une reference de sobriete, de lisibilite et de rapidite pour les equipes sanitaires.</p></div>
      <div class="public-card"><div class="public-card-title">Rayonnement continental</div><p class="public-card-copy">Faire emerger depuis la RDC un standard africain de surveillance epidemiologique moderne et souverain.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
