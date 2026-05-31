import inspect
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.public_ui import apply_public_theme, get_public_reference_metrics, render_public_hero
from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Impact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "impact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Preuves & resultats",
    "Un impact lisible, national et directement utile a la decision sanitaire.",
    "Ici, la promesse devient mesure. SAFE CONGO consolide l'information epidemiologique, en extrait des signaux exploitables et la transforme en indices de pilotage que les autorites peuvent mobiliser avec confiance.",
    [
        (f"{reference_metrics.get('observations', 0):,}".replace(",", " "), "observations traitees"),
        (str(reference_metrics.get("diseases", 0)), "maladies structurees"),
        (str(reference_metrics.get("provinces", 0)), "provinces couvertes"),
      (str(reference_metrics.get("zones", 0)), "zones observees"),
    ],
    tone="impact",
)

st.markdown(
    f"""
<div class="public-page">
  <div class="public-auto-grid">
    <div class="public-card"><div class="public-card-kicker">Base analytique</div><div class="public-card-title">{reference_metrics.get('observations', 0):,} observations consolidees</div><p class="public-card-copy">Une base dense qui nourrit la robustesse des signaux epidemiologiques et donne de l'epaisseur aux comparaisons temporelles.</p></div>
    <div class="public-card"><div class="public-card-kicker">Referentiel</div><div class="public-card-title">{reference_metrics.get('diseases', 0)} maladies sous lecture</div><p class="public-card-copy">Le systeme structure les pathologies suivies autour d'un referentiel unique pour eviter la derive entre pages et usages.</p></div>
    <div class="public-card"><div class="public-card-kicker">Maillage</div><div class="public-card-title">{reference_metrics.get('zones', 0)} zones de sante</div><p class="public-card-copy">Le pilotage national conserve une finesse territoriale suffisante pour rendre les alertes plus utiles au terrain.</p></div>
    <div class="public-card"><div class="public-card-kicker">Lecture nationale</div><div class="public-card-title">{reference_metrics.get('provinces', 0)} provinces sous lecture</div><p class="public-card-copy">La page publique reste informative sans afficher les volumes internes de comptes, d'alertes ou de saisies de l'application.</p></div>
  </div>

  <div class="public-grid-2">
    <div class="public-panel">
      <h3>Ce que ces chiffres changent</h3>
      <p class="public-copy">Ils montrent qu'une plateforme bien pensee peut faire gagner en lucidite institutionnelle, en vitesse de lecture et en credibilite technique. L'impact n'est pas decoratif: il change la qualite de la reponse.</p>
      <p class="public-copy">L'enjeu n'est pas seulement de compter, mais de transformer ces volumes en hierarchisation du risque, priorites d'action et coordination plus rapide.</p>
    </div>
    <div class="public-panel">
      <h3>Ce qui est deja visible</h3>
      <ul>
        <li>Un referentiel harmonise entre accueil public, authentification et pages de pilotage.</li>
        <li>Une lecture consolidee du territoire, des maladies et des zones sanitaires couvertes.</li>
        <li>Une experience publique recentree sur l'information utile, sans exposition des volumes internes de l'application.</li>
      </ul>
    </div>
  </div>

  <div class="public-panel">
    <h3>Lecture operationnelle</h3>
    <div class="public-bar-row"><div class="public-bar-label">Couverture provinciale</div><div class="public-bar-track"><div class="public-bar-fill" style="width:100%"></div></div><div class="public-bar-value">{reference_metrics.get('provinces', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Profondeur territoriale</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('zones', 0)} / 6 * 1%))"></div></div><div class="public-bar-value">{reference_metrics.get('zones', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Diversite sanitaire</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('diseases', 0)} * 4%))"></div></div><div class="public-bar-value">{reference_metrics.get('diseases', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Volume observe</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('observations', 0)} / 250 * 1%))"></div></div><div class="public-bar-value">{reference_metrics.get('observations', 0):,}</div></div>
    <p class="public-copy">Ces repères restent publics et descriptifs: ils montrent la couverture du referentiel traite sans publier les volumes internes de comptes, d'alertes ou de saisies.</p>
  </div>

  <div class="public-panel">
    <h3>Impact territorial attendu</h3>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Lecture plus rapide</div><p class="public-card-copy">Les equipes voient plus vite les foyers de tension et disposent d'un socle commun pour les arbitrages.</p></div>
      <div class="public-card"><div class="public-card-title">Dialogue plus propre</div><p class="public-card-copy">Les signaux remontent avec un langage moins ambigu entre terrain, administration et autorites sanitaires.</p></div>
      <div class="public-card"><div class="public-card-title">Decision plus sobre</div><p class="public-card-copy">La plateforme aide a agir avec une base factuelle simple, au lieu d'empiler des tableaux opaques et disperses.</p></div>
      <div class="public-card"><div class="public-card-title">Trajectoire evolutive</div><p class="public-card-copy">Chaque nouveau jeu de donnees renforce une lecture territoriale plus stable, sans surcharger la page publique de details internes.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
