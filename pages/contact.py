import inspect
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.public_ui import apply_public_theme, get_public_reference_metrics, render_public_hero
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Contact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "contact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Alliance & coordination",
  "Une coordination claire pour les demandes, les partenariats et l'acces.",
  "SAFE CONGO s'inscrit dans une logique d'ecosysteme. La valeur de la plateforme grandit lorsqu'elle relie institutions, partenaires et equipes techniques autour d'un meme langage de vigilance, de priorisation et d'action.",
    [
        ("4", "partenaires de reference"),
    (str(reference_metrics.get("provinces", 0)), "provinces suivies"),
    (str(reference_metrics.get("zones", 0)), "zones observees"),
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
        <p class="public-section-copy">L'espace public oriente les demandes sans publier de contacts fictifs ni d'informations sensibles.</p>
      </div>
      <p class="public-copy">Les demandes relatives au deploiement, a l'acces, a la gouvernance ou a l'usage de la plateforme passent par les circuits institutionnels et administratifs prevus par le dispositif SAFE CONGO.</p>
      <div class="public-pill-row">
        <span class="public-pill">Acces plateforme</span>
        <span class="public-pill">Coordination partenaire</span>
        <span class="public-pill">Support d'exploitation</span>
      </div>
    </div>
    <div class="public-accent-card">
      <h3>Principe de gouvernance</h3>
      <p>Les comptes des autorites sanitaires sont verifies, rattaches a un territoire et actives selon le niveau de responsabilite. SAFE CONGO privilegie la discipline d'acces et la clarte institutionnelle.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Alliances</div>
        <div class="public-section-title">Partenaires d'ancrage</div>
      </div>
      <p class="public-section-copy">La credibilite d'un systeme de veille depend aussi de la qualite de ses alliances institutionnelles et techniques.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Ministere de la Sante</div><p class="public-card-copy">Ancrage institutionnel et priorisation nationale.</p><a class="public-partner-link" href="https://www.minisanterdc.cd" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">OMS RDC</div><p class="public-card-copy">Cadre de reference international et expertise de sante publique.</p><a class="public-partner-link" href="https://www.who.int/fr" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">UNICEF RDC</div><p class="public-card-copy">Coordination sur les enjeux populationnels et communautaires.</p><a class="public-partner-link" href="https://www.unicef.org/drcongo" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">Africa CDC</div><p class="public-card-copy">Perspective regionale et harmonisation des pratiques.</p><a class="public-partner-link" href="https://africacdc.org" target="_blank">Visiter le site</a></div>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Parcours d'acces</div>
        <div class="public-section-title">Demande d'acces</div>
      </div>
      <p class="public-section-copy">Le processus d'ouverture privilegie la verification, le rattachement territorial et un demarrage accompagne.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">Etape 1</div><div class="public-card-title">Formuler la demande</div><p class="public-card-copy">Lancer la pre-inscription ou signaler le besoin d'acces avec la fonction, le territoire et l'usage attendu.</p></div>
      <div class="public-card"><div class="public-card-kicker">Etape 2</div><div class="public-card-title">Verifier le profil</div><p class="public-card-copy">Rapprocher les informations du bon niveau de responsabilite, de la province et de la zone de sante concernees.</p></div>
      <div class="public-card"><div class="public-card-kicker">Etape 3</div><div class="public-card-title">Activer et accompagner</div><p class="public-card-copy">Apres validation, l'equipe d'administration ouvre l'acces et encadre la prise en main initiale.</p></div>
    </div>
    <div class="public-note" style="margin-top:18px">Les utilisateurs peuvent egalement lancer une pre-inscription depuis la page d'accueil, en attendant validation administrative. Cette page reste volontairement institutionnelle et ne publie pas de contacts fictifs.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
