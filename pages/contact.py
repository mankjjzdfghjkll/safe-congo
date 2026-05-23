import inspect
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.public_ui import apply_public_theme, get_public_database_metrics, render_public_hero
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Contact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "contact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

database_metrics = get_public_database_metrics()

render_public_hero(
    "Alliance & coordination",
    "Un point de contact plus clair pour une plateforme qui travaille en coalition.",
    "SAFE CONGO s'inscrit dans une logique d'ecosysteme. La valeur de la plateforme grandit lorsqu'elle relie institutions, partenaires et equipes techniques autour d'un meme langage de vigilance et d'action.",
    [
        ("4", "partenaires de reference"),
        (str(database_metrics.get("users_total", 0)), "comptes en base"),
        (str(database_metrics.get("alerts_total", 0)), "alertes historisees"),
    ],
    tone="contact",
)

st.markdown(
    """
<div class="public-page">
  <div class="public-auto-grid">
    <div class="public-card"><div class="public-card-kicker">Coordination</div><div class="public-card-title">Canal institutionnel central</div><p class="public-card-copy">Les demandes relatives a la plateforme passent par la coordination et les circuits administratifs du dispositif de deploiement.</p></div>
    <div class="public-card"><div class="public-card-kicker">Acces</div><div class="public-card-title">Activation des profils</div><p class="public-card-copy">Les comptes d'autorites sanitaires sont ouverts, verifies puis actives selon le territoire et le niveau de responsabilite.</p></div>
    <div class="public-card"><div class="public-card-kicker">Partenariats</div><div class="public-card-title">Dialogue d'ecosysteme</div><p class="public-card-copy">La plateforme est pensee pour travailler avec les institutions publiques, les partenaires multilateraux et les equipes de terrain.</p></div>
    <div class="public-card"><div class="public-card-kicker">Support</div><div class="public-card-title">Accompagnement d'exploitation</div><p class="public-card-copy">Les usages critiques, les parcours d'acces et la prise en main peuvent etre encadres par l'administration du systeme.</p></div>
  </div>

  <div class="public-panel">
    <h3>Partenaires d'ancrage</h3>
    <p class="public-copy">La credibilite de SAFE CONGO repose aussi sur la qualite de ses alliances. La plateforme est pensee pour dialoguer avec les institutions de sante publique, les partenaires multilateraux et les acteurs de terrain qui renforcent l'execution.</p>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Ministere de la Sante</div><p class="public-card-copy">Ancrage institutionnel et priorisation nationale.</p><a class="public-partner-link" href="https://www.minisanterdc.cd" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">OMS RDC</div><p class="public-card-copy">Cadre de reference international et expertise de sante publique.</p><a class="public-partner-link" href="https://www.who.int/fr" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">UNICEF RDC</div><p class="public-card-copy">Coordination sur les enjeux populationnels et communautaires.</p><a class="public-partner-link" href="https://www.unicef.org/drcongo" target="_blank">Visiter le site</a></div>
      <div class="public-card"><div class="public-card-title">Africa CDC</div><p class="public-card-copy">Perspective regionale et harmonisation des pratiques.</p><a class="public-partner-link" href="https://africacdc.org" target="_blank">Visiter le site</a></div>
    </div>
  </div>

  <div class="public-panel">
    <h3>Demande d'acces</h3>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-kicker">Etape 1</div><div class="public-card-title">Formuler la demande</div><p class="public-card-copy">Lancez la pre-inscription ou signalez le besoin d'acces avec votre fonction, votre territoire et votre usage attendu.</p></div>
      <div class="public-card"><div class="public-card-kicker">Etape 2</div><div class="public-card-title">Verifier le profil</div><p class="public-card-copy">Les informations sont rapprochees du bon niveau de responsabilite, de la province et de la zone de sante concernes.</p></div>
      <div class="public-card"><div class="public-card-kicker">Etape 3</div><div class="public-card-title">Activer et accompagner</div><p class="public-card-copy">Apres validation, l'equipe admin ouvre l'acces et accompagne la prise en main initiale du compte.</p></div>
    </div>
    <div class="public-note" style="margin-top:18px">Les utilisateurs peuvent egalement lancer une pre-inscription depuis la page d'accueil, en attendant validation administrative. Cette page reste volontairement institutionnelle et ne publie pas de contacts fictifs.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
