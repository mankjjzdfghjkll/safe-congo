import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND

st.set_page_config(page_title="Impact — SAFE CONGO", page_icon=None, layout="wide")

SHIELD_SIDEBAR = PUBLIC_SIDEBAR_BRAND

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@700;900&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebarNav"]{display:none}
.stApp{background:#f7f9fc}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#080c18,#0d1830,#060b16)!important}
[data-testid="stSidebar"] *{color:#e0eaff!important}

@keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
@keyframes countAnim{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:scale(1)}}
@keyframes shimmer{0%{background-position:-1200px 0}100%{background-position:1200px 0}}

.page-banner{
    background:linear-gradient(135deg,#0a5e2a 0%,#078a3c 50%,#00a84f 100%);
    border-radius:20px;padding:52px 56px;margin-bottom:40px;
    position:relative;overflow:hidden;
    box-shadow:0 8px 40px rgba(0,130,60,.25);
    animation:fadeInUp .6s ease-out;
}
.page-banner::before{content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;
background:linear-gradient(90deg,transparent,rgba(255,255,255,.1),transparent);animation:shimmer 4s infinite}
.banner-tag{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);
border-radius:100px;padding:4px 16px;font-size:.75rem;letter-spacing:3px;text-transform:uppercase;color:#fff;margin-bottom:16px}
.banner-title{font-family:'Orbitron',sans-serif;font-size:2.4rem;font-weight:900;color:#fff;margin:0 0 12px;letter-spacing:2px}
.banner-sub{font-size:1.05rem;color:rgba(255,255,255,.85);max-width:700px;line-height:1.7;margin:0}

.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:0 0 32px}
.kpi-card{
    background:#fff;border-radius:18px;padding:28px 20px;text-align:center;
    box-shadow:0 2px 16px rgba(0,0,0,.07);
    border-top:4px solid;
    animation:countAnim .8s ease-out;
    transition:transform .3s;
}
.kpi-card:hover{transform:translateY(-6px);box-shadow:0 8px 30px rgba(0,0,0,.12)}
.kpi-card:nth-child(1){border-color:#0066CC}
.kpi-card:nth-child(2){border-color:#00A86B}
.kpi-card:nth-child(3){border-color:#0088FF}
.kpi-card:nth-child(4){border-color:#E85D04}
.kpi-num{font-family:'Orbitron',sans-serif;font-size:2.2rem;font-weight:900;color:#003d99}
.kpi-label{font-size:.8rem;color:#6b7280;letter-spacing:1px;text-transform:uppercase;margin-top:6px;font-weight:600}
.kpi-desc{font-size:.75rem;color:#9ca3af;margin-top:4px}

.section-card{background:#fff;border-radius:18px;padding:36px 40px;margin-bottom:24px;
box-shadow:0 2px 16px rgba(0,0,0,.06);border-left:5px solid #00A86B;animation:fadeInUp .7s ease-out}
.section-card h3{color:#0a5e2a;font-size:1.25rem;font-weight:700;margin:0 0 16px}
.section-card p,.section-card li{color:#374151;font-size:.96rem;line-height:1.8}
.section-card ul{padding-left:20px;margin:12px 0}
.section-card li{margin-bottom:8px}

.disease-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin:16px 0}
.disease-tag{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1px solid #bbf7d0;
border-radius:10px;padding:10px 14px;font-size:.8rem;font-weight:600;color:#166534;text-align:center}

.bar-row{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.bar-label{width:140px;font-size:.82rem;color:#374151;font-weight:500;flex-shrink:0}
.bar-outer{flex:1;background:#f3f4f6;border-radius:100px;height:10px;overflow:hidden}
.bar-inner{height:100%;border-radius:100px;background:linear-gradient(90deg,#0066CC,#00D4FF)}
.bar-pct{width:40px;font-size:.8rem;font-weight:700;color:#0066CC;text-align:right}
</style>"""

SHIELD_SIDEBAR = """<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
@keyframes floatUp{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes textGlow{0%,100%{text-shadow:0 0 10px rgba(0,212,255,.4)}50%{text-shadow:0 0 20px rgba(0,212,255,.8),0 0 40px rgba(0,102,204,.6)}}
.sidebar-logo-wrap{display:flex;flex-direction:column;align-items:center;padding:28px 0 16px;position:relative}
.sidebar-logo-glow{position:absolute;width:110px;height:110px;top:20px;border-radius:50%;background:radial-gradient(circle,rgba(0,102,204,.35) 0%,transparent 70%);animation:floatUp 4s ease-in-out infinite}
.sidebar-logo-svg{position:relative;z-index:2;animation:floatUp 4s ease-in-out infinite;filter:drop-shadow(0 0 14px rgba(0,212,255,.5)) drop-shadow(0 4px 12px rgba(0,0,0,.6))}
.sidebar-brand{font-family:'Orbitron',sans-serif;font-size:1.05rem;font-weight:900;letter-spacing:3px;color:#fff!important;text-align:center;margin-top:12px;animation:textGlow 3s ease-in-out infinite;text-transform:uppercase}
.sidebar-tagline{font-size:.65rem;letter-spacing:2px;text-align:center;color:rgba(0,212,255,.7)!important;text-transform:uppercase;margin-top:3px}
</style>
<div class="sidebar-logo-wrap">
  <div class="sidebar-logo-glow"></div>
  <svg class="sidebar-logo-svg" width="80" height="95" viewBox="0 0 120 145" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="sidebarShieldGrad" x1="0%" y1="0%" x2="100%" y2="120%">
        <stop offset="0%" stop-color="#9BE9FF"/>
        <stop offset="34%" stop-color="#1795FF"/>
        <stop offset="70%" stop-color="#0058B8"/>
        <stop offset="100%" stop-color="#051A46"/>
      </linearGradient>
      <linearGradient id="sidebarShieldGloss" x1="20%" y1="0%" x2="72%" y2="62%">
        <stop offset="0%" stop-color="rgba(255,255,255,.46)"/>
        <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
      </linearGradient>
      <linearGradient id="sidebarRingGold" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#FFF1A1"/>
        <stop offset="45%" stop-color="#FFD45E"/>
        <stop offset="100%" stop-color="#A86B0B"/>
      </linearGradient>
      <linearGradient id="sidebarWaveYellow" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#FFD447"/><stop offset="40%" stop-color="#FFF59D"/><stop offset="70%" stop-color="#FFCA28"/><stop offset="100%" stop-color="#FFD447"/><animateTransform attributeName="gradientTransform" type="translate" values="-0.8 0;0.8 0;-0.8 0" dur="3.2s" repeatCount="indefinite"/></linearGradient>
      <linearGradient id="sidebarWaveBlue" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#0077C8"/><stop offset="38%" stop-color="#2DB6FF"/><stop offset="68%" stop-color="#0099E5"/><stop offset="100%" stop-color="#0077C8"/><animateTransform attributeName="gradientTransform" type="translate" values="0.8 0;-0.8 0;0.8 0" dur="3.4s" repeatCount="indefinite"/></linearGradient>
      <linearGradient id="sidebarWaveRed" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#A90D1F"/><stop offset="42%" stop-color="#FF4D5F"/><stop offset="72%" stop-color="#CE1126"/><stop offset="100%" stop-color="#A90D1F"/><animateTransform attributeName="gradientTransform" type="translate" values="-0.6 0;0.6 0;-0.6 0" dur="2.9s" repeatCount="indefinite"/></linearGradient>
      <filter id="sidebarShadow" x="-30%" y="-30%" width="170%" height="170%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="3.4" result="blur"/>
        <feOffset dx="0" dy="5" result="offset"/>
        <feFlood flood-color="rgba(5,22,58,.34)"/>
        <feComposite in2="offset" operator="in"/>
        <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="sidebarGlow" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="2.1" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <ellipse cx="60" cy="70" rx="48" ry="48" fill="none" stroke="rgba(0,102,204,.12)" stroke-width="1" stroke-dasharray="3 7">
      <animateTransform attributeName="transform" type="rotate" from="0 60 70" to="360 60 70" dur="18s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="60" cy="70" rx="55" ry="55" fill="none" stroke="rgba(0,212,255,.18)" stroke-width="1.2" stroke-dasharray="6 4">
      <animateTransform attributeName="transform" type="rotate" from="0 60 70" to="-360 60 70" dur="22s" repeatCount="indefinite"/>
    </ellipse>
    <g>
      <circle cx="60" cy="70" r="45" fill="rgba(255,255,255,.22)"/>
      <circle cx="60" cy="70" r="44" fill="url(#sidebarShieldGrad)" filter="url(#sidebarShadow)"/>
      <circle cx="60" cy="70" r="44" fill="url(#sidebarShieldGloss)" opacity=".5"/>
      <circle cx="60" cy="70" r="48" fill="none" stroke="url(#sidebarRingGold)" stroke-width="2.4" opacity=".94"/>
      <circle cx="60" cy="70" r="36" fill="none" stroke="rgba(255,255,255,.18)" stroke-width="1.1"/>
    </g>
    <g opacity=".56">
      <line x1="60" y1="15" x2="60" y2="21" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
      <line x1="60" y1="119" x2="60" y2="125" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
      <line x1="7" y1="70" x2="13" y2="70" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
      <line x1="107" y1="70" x2="113" y2="70" stroke="#6BC6FF" stroke-width="1.6" stroke-linecap="round"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0 60 70" to="360 60 70" dur="14s" repeatCount="indefinite"/>
      <circle cx="60" cy="23" r="2.5" fill="#00E1FF"/>
      <circle cx="107" cy="70" r="1.8" fill="#9FE9FF" opacity=".88"/>
      <circle cx="60" cy="117" r="2.1" fill="#64C8FF" opacity=".74"/>
      <circle cx="13" cy="70" r="1.7" fill="#5FB8FF" opacity=".74"/>
    </g>
    <g>
      <path d="M60 38 L79 49 L79 73 Q79 92 60 103 Q41 92 41 73 L41 49 Z" fill="rgba(4,21,60,.24)" transform="translate(1.5,4)"/>
      <path d="M60 38 L79 49 L79 73 Q79 92 60 103 Q41 92 41 73 L41 49 Z" fill="rgba(255,255,255,.06)"/>
      <path d="M60 38 L79 49 L79 73 Q79 92 60 103 Q41 92 41 73 L41 49 Z" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="1"/>
    </g>
    <g filter="url(#sidebarGlow)">
      <path d="M31 70 H44 L49 58 L55 83 L60 69 L68 69 L73 54 L79 80 L84 70 H89" fill="none" stroke="#00EEFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="140" stroke-dashoffset="140">
        <animate attributeName="stroke-dashoffset" values="140;0;0;140" dur="4.2s" repeatCount="indefinite"/>
      </path>
    </g>
    <g>
      <circle cx="60" cy="51" r="5.4" fill="url(#sidebarWaveYellow)"/>
      <path d="M60 58 C66 58 71 62 71 69 V79 C71 82 68.5 84 65.5 84 H54.5 C51.5 84 49 82 49 79 V69 C49 62 54 58 60 58 Z" fill="url(#sidebarWaveBlue)"/>
      <rect x="57" y="58" width="6" height="26" rx="3" fill="url(#sidebarWaveRed)"/>
    </g>
    <circle cx="60" cy="70" r="28" fill="none" stroke="rgba(0,235,255,.26)" stroke-width="1.1">
      <animate attributeName="r" values="28;44" dur="3.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".55;0" dur="3.2s" repeatCount="indefinite"/>
    </circle>
  </svg>
  <div class="sidebar-brand">SAFE CONGO</div>
  <div class="sidebar-tagline">Surveillance &#8226; RDC</div>
</div>"""

SHIELD_SIDEBAR = PUBLIC_SIDEBAR_BRAND

st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SHIELD_SIDEBAR, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("← Retour à l'accueil", use_container_width=True):
        st.switch_page("app.py")

st.markdown("""
<div class="page-banner">
  <div class="banner-tag">&#9670; Impact & Chiffres</div>
  <div class="banner-title">Un Impact Mesurable<br>sur la Santé Publique</div>
  <p class="banner-sub">Des données concrètes qui témoignent de la portée et de l'efficacité du système 
  de surveillance épidémiologique SAFE CONGO à travers toute la RDC.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-num">27 671</div>
    <div class="kpi-label">Observations Analysées</div>
    <div class="kpi-desc">Données épidémiologiques traitées par le modèle IA</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num">81.6%</div>
    <div class="kpi-label">Précision du Modèle</div>
    <div class="kpi-desc">Taux de précision XGBoost validé par cross-validation</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num">26</div>
    <div class="kpi-label">Provinces Couvertes</div>
    <div class="kpi-desc">Couverture nationale complète du territoire congolais</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num">517</div>
    <div class="kpi-label">Zones de Santé</div>
    <div class="kpi-desc">Zones surveillées en temps réel par le système</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
  <h3>&#9670; Maladies Surveillées (27 pathologies)</h3>
  <p>SAFE CONGO surveille les 27 maladies prioritaires identifiées par le Ministère de la Santé de la RDC :</p>
  <div class="disease-grid">
    <div class="disease-tag">Choléra</div>
    <div class="disease-tag">Mpox</div>
    <div class="disease-tag">Ebola</div>
    <div class="disease-tag">Rougeole</div>
    <div class="disease-tag">Méningite</div>
    <div class="disease-tag">Paludisme</div>
    <div class="disease-tag">Fièvre typhoïde</div>
    <div class="disease-tag">Tuberculose</div>
    <div class="disease-tag">COVID-19</div>
    <div class="disease-tag">Dengue</div>
    <div class="disease-tag">Fièvre jaune</div>
    <div class="disease-tag">Rage</div>
    <div class="disease-tag">Tétanos</div>
    <div class="disease-tag">Coqueluche</div>
    <div class="disease-tag">Diphtérie</div>
    <div class="disease-tag">Poliomyélite</div>
    <div class="disease-tag">Trypanosomiase</div>
    <div class="disease-tag">Leishmaniose</div>
    <div class="disease-tag">Bilharziose</div>
    <div class="disease-tag">Onchocercose</div>
    <div class="disease-tag">Filariose</div>
    <div class="disease-tag">Lèpre</div>
    <div class="disease-tag">Hépatite A</div>
    <div class="disease-tag">Hépatite B</div>
    <div class="disease-tag">Hépatite E</div>
    <div class="disease-tag">Grippe saisonnière</div>
    <div class="disease-tag">IRA sévère</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
  <h3>&#9670; Performance du Modèle par Métrique</h3>
  <div class="bar-row">
    <div class="bar-label">Précision globale</div>
    <div class="bar-outer"><div class="bar-inner" style="width:81.6%"></div></div>
    <div class="bar-pct">81.6%</div>
  </div>
  <div class="bar-row">
    <div class="bar-label">F1-Score macro</div>
    <div class="bar-outer"><div class="bar-inner" style="width:45.8%"></div></div>
    <div class="bar-pct">45.8%</div>
  </div>
  <div class="bar-row">
    <div class="bar-label">Couverture nationale</div>
    <div class="bar-outer"><div class="bar-inner" style="width:100%"></div></div>
    <div class="bar-pct">100%</div>
  </div>
  <div class="bar-row">
    <div class="bar-label">Disponibilité système</div>
    <div class="bar-outer"><div class="bar-inner" style="width:99.5%"></div></div>
    <div class="bar-pct">99.5%</div>
  </div>
  <br>
  <p><strong>Algorithme :</strong> XGBoost (eXtreme Gradient Boosting) — entraîné sur 22 157 échantillons 
  avec validation croisée 5-fold. Optimisé pour la détection des maladies à fort potentiel épidémique.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-card">
  <h3>&#9670; Provinces sous Surveillance Active</h3>
  <p>Les 26 provinces de la RDC sont intégrées au système, avec des niveaux de surveillance adaptés aux risques locaux :</p>
  <ul>
    <li><strong>Zone Est (haute priorité) :</strong> Nord-Kivu, Sud-Kivu, Ituri, Maniema, Tanganyika</li>
    <li><strong>Zone Centrale :</strong> Kinshasa, Kongo Central, Kwango, Kwilu, Mai-Ndombe, Kasaï</li>
    <li><strong>Zone Nord :</strong> Équateur, Sud-Ubangi, Nord-Ubangi, Mongala, Tshopo, Bas-Uele, Haut-Uele</li>
    <li><strong>Zone Sud :</strong> Haut-Katanga, Lualaba, Haut-Lomami, Tanganyika, Lomami, Sankuru</li>
  </ul>
</div>
""", unsafe_allow_html=True)
