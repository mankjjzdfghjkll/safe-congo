import streamlit as st
from pathlib import Path
import inspect
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.sidebar_brand import render_public_sidebar


st.set_page_config(page_title="Contact — SAFE CONGO", page_icon=None, layout="wide")


SIDEBAR_KWARGS = {"active_page": "contact"} if "active_page" in inspect.signature(render_public_sidebar).parameters else {}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
.stApp{background:linear-gradient(180deg,#eef6ff 0%,#e6f2fd 52%,#f0f8ff 100%)!important}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1180px}
.contact-hero{background:linear-gradient(135deg,#104f90 0%,#207cd0 54%,#f0b94c 100%);border-radius:32px;padding:52px 56px;position:relative;overflow:hidden;box-shadow:0 26px 60px rgba(16,79,144,.2);margin-bottom:24px}
.contact-hero::after{content:'';position:absolute;right:-100px;top:-80px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.22),transparent 70%)}
.hero-kicker{display:inline-block;padding:6px 16px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#f7fbff;font-size:.72rem;font-weight:800;letter-spacing:2.4px;text-transform:uppercase}
.hero-title{font-family:'Sora',sans-serif;font-size:2.7rem;color:#fff;line-height:1.08;margin:18px 0 14px;max-width:760px}
.hero-sub{max-width:720px;color:rgba(247,251,255,.9);font-size:1rem;line-height:1.82;margin:0}
.contact-grid,.partner-grid,.access-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin:22px 0}
.card{background:rgba(255,255,255,.9);border:1px solid rgba(166,204,233,.58);border-radius:24px;padding:24px;box-shadow:0 16px 38px rgba(35,91,150,.08)}
.card-kicker{font-size:.72rem;letter-spacing:1.8px;text-transform:uppercase;color:#6a8aa6;font-weight:800;margin-bottom:8px}
.card-title{font-family:'Sora',sans-serif;color:#104f90;font-size:1.02rem;margin:0 0 8px}
.card-copy{color:#4e647e;font-size:.9rem;line-height:1.72;margin:0}
.section-card{background:rgba(255,255,255,.9);border:1px solid rgba(166,204,233,.58);border-radius:28px;padding:30px 32px;box-shadow:0 18px 40px rgba(35,91,150,.08);margin-bottom:22px}
.section-title{font-family:'Sora',sans-serif;font-size:1.2rem;color:#104f90;margin:0 0 14px}
.section-copy,.section-card li{color:#4e647e;font-size:.95rem;line-height:1.82}
.section-card ul{margin:14px 0 0;padding-left:18px}
.partner-name{font-family:'Sora',sans-serif;color:#104f90;font-size:.96rem;margin-bottom:6px}
.partner-role{font-size:.82rem;color:#6a8aa6;line-height:1.65}
.partner-link{display:inline-block;margin-top:10px;color:#0f7bc7;text-decoration:none;font-size:.82rem;font-weight:800}
.partner-link:hover{text-decoration:underline}
@media (max-width: 900px){.contact-hero{padding:38px 24px}.hero-title{font-size:2.1rem}.section-card{padding:24px}}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)
render_public_sidebar(**SIDEBAR_KWARGS)

st.markdown(
    """
    <div class="contact-hero">
      <div class="hero-kicker">Alliance & coordination</div>
      <div class="hero-title">Un point de contact clair pour une plateforme qui travaille en coalition.</div>
      <p class="hero-sub">SAFE CONGO s'inscrit dans une logique d'ecosysteme. La valeur de la plateforme grandit lorsqu'elle relie institutions, partenaires et equipes techniques autour d'un meme langage de vigilance et d'action.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="contact-grid">
      <div class="card"><div class="card-kicker">Standard</div><h3 class="card-title">Ligne coordination</h3><p class="card-copy">+243 123 456 789<br/>Disponibilite du lundi au vendredi, 8h00 a 17h00.</p></div>
      <div class="card"><div class="card-kicker">Courriel</div><h3 class="card-title">Canal institutionnel</h3><p class="card-copy">contact@safe-congo.cd<br/>Reponse ciblee sous 24 heures ouvrables.</p></div>
      <div class="card"><div class="card-kicker">Presence</div><h3 class="card-title">Base de coordination</h3><p class="card-copy">Avenue de la Justice, No. 18<br/>Gombe, Kinshasa, RDC.</p></div>
      <div class="card"><div class="card-kicker">Support</div><h3 class="card-title">Assistance technique</h3><p class="card-copy">support@safe-congo.cd<br/>Accompagnement prioritaire pour les usages critiques.</p></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Partenaires d'ancrage</h3>
      <p class="section-copy">La credibilite de SAFE CONGO repose aussi sur la qualite de ses alliances. La plateforme est pensee pour dialoguer avec les institutions de sante publique, les partenaires multilateraux et les acteurs de terrain qui renforcent l'execution.</p>
      <div class="partner-grid">
        <div class="card"><div class="partner-name">Ministere de la Sante</div><div class="partner-role">Ancrage institutionnel et priorisation nationale.</div><a class="partner-link" href="https://www.minisanterdc.cd" target="_blank">Visiter le site</a></div>
        <div class="card"><div class="partner-name">OMS RDC</div><div class="partner-role">Cadre de reference international et expertise de sante publique.</div><a class="partner-link" href="https://www.who.int/fr" target="_blank">Visiter le site</a></div>
        <div class="card"><div class="partner-name">UNICEF RDC</div><div class="partner-role">Coordination sur les enjeux populationnels et communautaires.</div><a class="partner-link" href="https://www.unicef.org/drcongo" target="_blank">Visiter le site</a></div>
        <div class="card"><div class="partner-name">Africa CDC</div><div class="partner-role">Perspective regionale et harmonisation des pratiques.</div><a class="partner-link" href="https://africacdc.org" target="_blank">Visiter le site</a></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
      <h3 class="section-title">Demande d'acces</h3>
      <div class="access-grid">
        <div class="card"><div class="card-kicker">Etape 1</div><h3 class="card-title">Formuler la demande</h3><p class="card-copy">Adressez un courriel officiel avec votre fonction, votre territoire et votre besoin d'acces.</p></div>
        <div class="card"><div class="card-kicker">Etape 2</div><h3 class="card-title">Justifier le profil</h3><p class="card-copy">Ajoutez lettre de nomination, piece d'identite et indication de la province ou zone concernee.</p></div>
        <div class="card"><div class="card-kicker">Etape 3</div><h3 class="card-title">Activation guidee</h3><p class="card-copy">Apres validation, l'equipe admin ouvre l'acces et accompagne la prise en main initiale.</p></div>
      </div>
      <p class="section-copy">Les utilisateurs peuvent egalement lancer une pre-inscription depuis la page d'accueil, en attendant validation administrative.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
