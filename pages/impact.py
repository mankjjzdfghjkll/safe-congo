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
  "Des resultats lisibles, nationaux et utiles a la decision sanitaire.",
  "SAFE CONGO ne cherche pas a impressionner par le volume. La plateforme vise surtout a transformer des donnees heterogenes en reperes de pilotage simples, credibles et mobilisables par les autorites sanitaires.",
    [
        (f"{reference_metrics.get('observations', 0):,}".replace(",", " "), "observations traitees"),
    (str(reference_metrics.get("diseases", 0)), "maladies retenues"),
        (str(reference_metrics.get("provinces", 0)), "provinces couvertes"),
    (str(reference_metrics.get("zones", 0)), "zones observees"),
    ],
    tone="impact",
)

st.markdown(
    f"""
<div class="public-page">
  <div class="public-auto-grid">
    <div class="public-card"><div class="public-card-kicker">Base analytique</div><div class="public-card-title">{reference_metrics.get('observations', 0):,} observations consolidees</div><p class="public-card-copy">Une base suffisamment dense pour stabiliser les comparaisons temporelles et soutenir une lecture publique plus serieuse du risque.</p></div>
    <div class="public-card"><div class="public-card-kicker">Referentiel</div><div class="public-card-title">{reference_metrics.get('diseases', 0)} maladies retenues</div><p class="public-card-copy">Le systeme met en avant les maladies retenues en production pour eviter les divergences entre l'espace public et le pilotage effectif.</p></div>
    <div class="public-card"><div class="public-card-kicker">Maillage</div><div class="public-card-title">{reference_metrics.get('zones', 0)} zones de sante</div><p class="public-card-copy">La couverture territoriale conserve une finesse suffisante pour rendre les alertes plus utiles aux coordinations locales.</p></div>
    <div class="public-card"><div class="public-card-kicker">Lecture nationale</div><div class="public-card-title">{reference_metrics.get('provinces', 0)} provinces sous lecture</div><p class="public-card-copy">L'espace public reste informatif sans exposer les volumes internes de comptes, d'alertes ou de saisies d'exploitation.</p></div>
  </div>

  <div class="public-grid-2">
    <div class="public-panel">
      <div class="public-section-head">
        <div>
          <div class="public-section-kicker">Lecture institutionnelle</div>
          <div class="public-section-title">Ce que ces indicateurs etablissent</div>
        </div>
        <p class="public-section-copy">Ces reperes ne sont utiles que s'ils rendent la decision plus fiable et plus rapide.</p>
      </div>
      <p class="public-copy">Ils montrent qu'une plateforme bien cadre peut gagner en lucidite institutionnelle, en vitesse de lecture et en credibilite technique. L'impact n'est pas decoratif: il change la qualite de l'arbitrage et la facon de prioriser.</p>
      <p class="public-copy">L'enjeu n'est pas seulement de compter, mais de convertir ces volumes en hierarchisation du risque, en ordre d'action et en coordination plus disciplinee.</p>
    </div>
    <div class="public-panel">
      <h3>Ce qui est deja visible</h3>
      <p>Un referentiel harmonise, une lecture consolidee du territoire sanitaire et un espace public recentre sur l'information utile. SAFE CONGO expose moins de bruit et davantage de clarte institutionnelle.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Capacite publique</div>
        <div class="public-section-title">Lecture operationnelle</div>
      </div>
      <p class="public-section-copy">Ces repères restent descriptifs: ils rendent visible la couverture du referentiel sans publier les volumes internes du dispositif.</p>
    </div>
    <div class="public-bar-row"><div class="public-bar-label">Couverture provinciale</div><div class="public-bar-track"><div class="public-bar-fill" style="width:100%"></div></div><div class="public-bar-value">{reference_metrics.get('provinces', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Profondeur territoriale</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('zones', 0)} / 6 * 1%))"></div></div><div class="public-bar-value">{reference_metrics.get('zones', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Maladies retenues</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('diseases', 0)} * 4%))"></div></div><div class="public-bar-value">{reference_metrics.get('diseases', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Volume observe</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('observations', 0)} / 250 * 1%))"></div></div><div class="public-bar-value">{reference_metrics.get('observations', 0):,}</div></div>
    <p class="public-copy">Ces indicateurs publics montrent l'etendue de la couverture traitee sans exposer les volumes d'exploitation, de comptes ou d'alertes internes.</p>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Effets attendus</div>
        <div class="public-section-title">Impact territorial</div>
      </div>
      <p class="public-section-copy">Le gain attendu n'est pas seulement analytique. Il touche aussi la discipline collective de la reponse.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Lecture plus rapide</div><p class="public-card-copy">Les equipes localisent plus vite les foyers de tension et partagent un meme socle d'analyse pour arbitrer.</p></div>
      <div class="public-card"><div class="public-card-title">Dialogue plus net</div><p class="public-card-copy">Les signaux remontent avec un langage moins ambigu entre terrain, administration et autorites sanitaires.</p></div>
      <div class="public-card"><div class="public-card-title">Decision plus sobre</div><p class="public-card-copy">La plateforme privilegie des repères factuels simples au lieu d'accumuler des tableaux opaques et disperses.</p></div>
      <div class="public-card"><div class="public-card-title">Trajectoire evolutive</div><p class="public-card-copy">Chaque nouveau jeu de donnees consolide une lecture territoriale plus stable sans surcharger l'espace public de details internes.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
