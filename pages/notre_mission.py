import streamlit as st
from pathlib import Path
import inspect
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Notre Mission — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "notre_mission"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
.stApp{background:linear-gradient(180deg,#eef6ff 0%,#e6f2fd 52%,#f0f8ff 100%)!important}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1180px}
.hero-card{position:relative;overflow:hidden;background:linear-gradient(135deg,#0d4d96 0%,#1278c9 58%,#49a7eb 100%);border-radius:32px;padding:54px 56px;box-shadow:0 28px 60px rgba(13,77,150,.22);margin-bottom:26px}
.hero-card::before{content:'';position:absolute;inset:auto -12% -55% auto;width:380px;height:380px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.22),transparent 70%)}
.hero-kicker{display:inline-block;padding:6px 16px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#f7fbff;font-size:.72rem;font-weight:800;letter-spacing:2.4px;text-transform:uppercase}
.hero-title{font-family:'Sora',sans-serif;font-size:3rem;line-height:1.08;color:#fff;margin:18px 0 16px;max-width:760px}
.hero-sub{max-width:700px;color:rgba(247,251,255,.88);font-size:1.02rem;line-height:1.85;margin:0}
.hero-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin:22px 0 0}
.hero-metric{padding:18px;border-radius:20px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);backdrop-filter:blur(10px)}
.hero-metric-value{font-family:'Sora',sans-serif;font-size:1.55rem;color:#fff;font-weight:800}
.hero-metric-label{font-size:.78rem;letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,.7);margin-top:4px}
.section-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:22px;margin-bottom:22px}
.section-card{background:rgba(255,255,255,.88);border:1px solid rgba(166,204,233,.58);border-radius:28px;padding:30px 32px;box-shadow:0 18px 40px rgba(35,91,150,.08)}
.section-title{font-family:'Sora',sans-serif;font-size:1.28rem;color:#0f3f73;margin:0 0 14px}
.section-text,.section-card li{font-size:.97rem;line-height:1.82;color:#4e647e}
.section-card ul{margin:14px 0 0;padding-left:18px}
.promise-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin-top:18px}
.promise-card{padding:22px;border-radius:22px;background:linear-gradient(180deg,#ffffff,#edf7ff);border:1px solid rgba(166,204,233,.55)}
.promise-index{font-family:'Sora',sans-serif;font-size:1.65rem;color:#1483d6;margin-bottom:8px}
.promise-title{font-weight:800;color:#0f3f73;margin-bottom:8px}
.promise-copy{font-size:.86rem;line-height:1.68;color:#64809b}
.quote-band{background:linear-gradient(135deg,#163d72,#2086d8);border-radius:28px;padding:30px 34px;margin:22px 0;color:#fff;box-shadow:0 24px 48px rgba(21,71,130,.18)}
.quote-band p{font-family:'Sora',sans-serif;font-size:1.3rem;line-height:1.55;margin:0 0 12px}
.quote-band span{font-size:.82rem;letter-spacing:1.8px;text-transform:uppercase;color:rgba(255,255,255,.7)}
.vision-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:18px}
.vision-card{padding:22px;border-radius:22px;background:linear-gradient(135deg,#eff8ff,#e5f2ff);border:1px solid rgba(166,204,233,.58)}
.vision-card h4{margin:0 0 8px;color:#0f3f73;font-size:1rem}
.vision-card p{margin:0;color:#64809b;font-size:.86rem;line-height:1.7}
@media (max-width: 900px){.hero-card{padding:38px 24px}.hero-title{font-size:2.2rem}.section-grid{grid-template-columns:1fr}.section-card{padding:24px}}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)
render_public_sidebar(**SIDEBAR_KWARGS)

st.markdown(
    """
    <div class="hero-card">
      <div class="hero-kicker">Cap strategique</div>
      <div class="hero-title">Une mission de souverainete sanitaire, pensee pour proteger chaque territoire.</div>
      <p class="hero-sub">SAFE CONGO transforme la surveillance epidemiologique en capacite d'anticipation. Notre ambition n'est pas seulement de voir l'epidemie arriver, mais d'offrir aux decideurs congolais une longueur d'avance claire, lisible et actionnable.</p>
      <div class="hero-metrics">
        <div class="hero-metric"><div class="hero-metric-value">26</div><div class="hero-metric-label">provinces alignees</div></div>
        <div class="hero-metric"><div class="hero-metric-value">517</div><div class="hero-metric-label">zones observees</div></div>
        <div class="hero-metric"><div class="hero-metric-value">24/7</div><div class="hero-metric-label">vigilance numerique</div></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-grid">
      <div class="section-card">
        <h3 class="section-title">Pourquoi nous existons</h3>
        <p class="section-text">Dans un pays-continent, la vitesse de lecture des signaux faibles devient une force de protection collective. SAFE CONGO a ete concu pour reduire le delai entre l'apparition d'une anomalie, sa comprehension et la decision publique qui suit.</p>
        <p class="section-text">Nous faisons converger intelligence artificielle, expertise epidemiologique et ergonomie de decision afin que les responsables sanitaires disposent d'un systeme qui rassure, eclaire et accelere l'action.</p>
      </div>
      <div class="section-card">
        <h3 class="section-title">Notre promesse</h3>
        <ul>
          <li>Transformer les donnees locales en vision nationale nette.</li>
          <li>Rehausser la confiance des autorites dans la lecture des risques.</li>
          <li>Fournir des alertes dignes d'une gouvernance moderne et reactive.</li>
        </ul>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Les quatre fondations qui portent SAFE CONGO</h3>
      <div class="promise-grid">
        <div class="promise-card"><div class="promise-index">01</div><div class="promise-title">Lecture precoce</div><div class="promise-copy">Identifier l'inhabituel avant qu'il ne devienne une crise visible, grace a un moteur analytique entraine sur des donnees reelles.</div></div>
        <div class="promise-card"><div class="promise-index">02</div><div class="promise-title">Alerte de precision</div><div class="promise-copy">Envoyer le bon signal, au bon niveau, au bon moment, avec un langage compréhensible pour l'action publique.</div></div>
        <div class="promise-card"><div class="promise-index">03</div><div class="promise-title">Coordination elegante</div><div class="promise-copy">Relier provinces, zones de sante et gouvernance centrale au sein d'une meme colonne vertebrale operationnelle.</div></div>
        <div class="promise-card"><div class="promise-index">04</div><div class="promise-title">Decision augmentee</div><div class="promise-copy">Permettre aux equipes de terrain et aux autorites de choisir vite, avec une base factuelle solide et partageable.</div></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="quote-band">
      <p>SAFE CONGO n'est pas seulement une interface. C'est une architecture de confiance pour la sante publique congolaise.</p>
      <span>Vision SAFE CONGO</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Vision 2030</h3>
      <div class="vision-grid">
        <div class="vision-card"><h4>Surveillance enrichie</h4><p>Integrer climat, mobilite, pression demographique et historiques locaux pour des alertes encore plus fines.</p></div>
        <div class="vision-card"><h4>Interoperabilite regionale</h4><p>Connecter SAFE CONGO aux cadres OMS, Africa CDC et aux initiatives transfrontalieres des Grands Lacs.</p></div>
        <div class="vision-card"><h4>Excellence d'execution</h4><p>Faire de la plateforme une reference de sobriete, de lisibilite et de rapidite pour les equipes sanitaires.</p></div>
        <div class="vision-card"><h4>Rayonnement continental</h4><p>Faire emerger depuis la RDC un standard africain de surveillance epidemiologique moderne et souverain.</p></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
