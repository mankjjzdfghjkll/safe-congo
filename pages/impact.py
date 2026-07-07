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


st.set_page_config(page_title="Impact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "impact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

apply_public_theme()
render_public_sidebar(**SIDEBAR_KWARGS)

reference_metrics = get_public_reference_metrics()

render_public_hero(
    "Impact",
    "Des indicateurs lisibles pour mieux orienter la décision sanitaire.",
    "SAFE CONGO transforme des données dispersées en repères simples: couverture territoriale, maladies suivies, observations consolidées et lecture du risque.",
    [
        (f"{reference_metrics.get('observations', 0):,}".replace(",", " "), "observations traitées"),
    (str(reference_metrics.get("diseases", 0)), "maladies retenues"),
        (str(reference_metrics.get("provinces", 0)), "provinces couvertes"),
    (str(reference_metrics.get("zones", 0)), "zones observées"),
    ],
    tone="impact",
)

st.markdown(
    f"""
<div class="public-page">
  <div class="public-auto-grid">
    <div class="public-card"><div class="public-card-kicker">Base analytique</div><div class="public-card-title">{reference_metrics.get('observations', 0):,} observations consolidées</div><p class="public-card-copy">Un socle de données qui aide à comparer les périodes, suivre les tendances et repérer les écarts.</p></div>
    <div class="public-card"><div class="public-card-kicker">Référentiel</div><div class="public-card-title">{reference_metrics.get('diseases', 0)} maladies retenues</div><p class="public-card-copy">Un périmètre clair pour garder une lecture cohérente entre l'espace public et les tableaux de bord internes.</p></div>
    <div class="public-card"><div class="public-card-kicker">Maillage</div><div class="public-card-title">{reference_metrics.get('zones', 0)} zones de santé</div><p class="public-card-copy">Une lecture territoriale assez fine pour soutenir les coordinations provinciales et locales.</p></div>
    <div class="public-card"><div class="public-card-kicker">Lecture nationale</div><div class="public-card-title">{reference_metrics.get('provinces', 0)} provinces suivies</div><p class="public-card-copy">Une vue nationale utile, sans exposer les informations sensibles d'exploitation.</p></div>
  </div>

  <div class="public-grid-2">
    <div class="public-panel">
      <div class="public-section-head">
        <div>
          <div class="public-section-kicker">Lecture sanitaire</div>
          <div class="public-section-title">Ce que ces indicateurs montrent</div>
        </div>
        <p class="public-section-copy">Ces repères sont utiles lorsqu'ils rendent la décision plus fiable et plus rapide.</p>
      </div>
      <p class="public-copy">Ils montrent qu'une plateforme bien structurée peut améliorer la vitesse de lecture, la qualité du suivi et la coordination. L'impact ne vient pas seulement du volume de données, mais de la façon dont elles deviennent exploitables.</p>
      <p class="public-copy">L'enjeu est de convertir les chiffres en priorités claires: où regarder, quoi vérifier, qui informer et quand agir.</p>
    </div>
    <div class="public-panel">
      <h3>Ce qui est déjà visible</h3>
      <p>Un référentiel harmonisé, une lecture consolidée du territoire sanitaire et un espace public recentré sur l'information utile.</p>
    </div>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Capacite publique</div>
        <div class="public-section-title">Lecture operationnelle</div>
      </div>
      <p class="public-section-copy">Ces repères restent descriptifs: ils montrent la couverture suivie sans publier les volumes internes du dispositif.</p>
    </div>
    <div class="public-bar-row"><div class="public-bar-label">Couverture provinciale</div><div class="public-bar-track"><div class="public-bar-fill" style="width:100%"></div></div><div class="public-bar-value">{reference_metrics.get('provinces', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Zones de santé</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('zones', 0)} / 6 * 1%))"></div></div><div class="public-bar-value">{reference_metrics.get('zones', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Maladies retenues</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('diseases', 0)} * 4%))"></div></div><div class="public-bar-value">{reference_metrics.get('diseases', 0)}</div></div>
    <div class="public-bar-row"><div class="public-bar-label">Volume observé</div><div class="public-bar-track"><div class="public-bar-fill" style="width:min(100%, calc({reference_metrics.get('observations', 0)} / 250 * 1%))"></div></div><div class="public-bar-value">{reference_metrics.get('observations', 0):,}</div></div>
    <p class="public-copy">Ces indicateurs publics montrent l'étendue de la couverture traitée sans exposer les comptes, alertes ou saisies internes.</p>
  </div>

  <div class="public-panel">
    <div class="public-section-head">
      <div>
        <div class="public-section-kicker">Effets attendus</div>
        <div class="public-section-title">Impact territorial</div>
      </div>
      <p class="public-section-copy">Le gain attendu est à la fois analytique, opérationnel et organisationnel.</p>
    </div>
    <div class="public-auto-grid">
      <div class="public-card"><div class="public-card-title">Lecture plus rapide</div><p class="public-card-copy">Les équipes localisent plus vite les foyers de tension et partagent un même socle d'analyse.</p></div>
      <div class="public-card"><div class="public-card-title">Dialogue plus net</div><p class="public-card-copy">Les signaux remontent avec un langage plus clair entre terrain, administration et autorités sanitaires.</p></div>
      <div class="public-card"><div class="public-card-title">Décision plus sobre</div><p class="public-card-copy">La plateforme privilégie des repères factuels simples au lieu d'accumuler des tableaux dispersés.</p></div>
      <div class="public-card"><div class="public-card-title">Évolution progressive</div><p class="public-card-copy">Chaque nouveau jeu de données renforce une lecture territoriale plus stable, sans surcharger l'espace public.</p></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
