from typing import Optional

import streamlit as st
from utils.navigation import switch_to_home_page


PUBLIC_SIDEBAR_BRAND = """
<style>
.sidebar-logo-wrap{display:flex;flex-direction:column;align-items:center;padding:16px 0 8px;position:relative}
.sidebar-logo-glow{position:absolute;width:95px;height:95px;top:6px;border-radius:50%;background:radial-gradient(circle,rgba(10,85,184,.28) 0%,transparent 70%);animation:floatUp 4s ease-in-out infinite;z-index:0}
.sidebar-logo-svg{position:relative;z-index:2;animation:floatUp 4s ease-in-out infinite;filter:drop-shadow(0 6px 14px rgba(10,60,120,.24))}
.sidebar-brand{font-family:'Sora',sans-serif;font-size:.86rem;font-weight:800;letter-spacing:1.6px;color:#0a2c5a!important;text-align:center;margin-top:10px;text-transform:uppercase}
.sidebar-tagline{font-size:.64rem;letter-spacing:.8px;text-align:center;color:#7a9ab8!important;text-transform:none;margin-top:2px;font-weight:600}
@keyframes floatUp{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
</style>
<div class="sidebar-logo-wrap">
  <div class="sidebar-logo-glow"></div>
  <svg class="sidebar-logo-svg" width="76" height="88" viewBox="0 0 110 128" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="sig1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="rgba(255,255,255,.92)"/>
        <stop offset="58%" stop-color="rgba(180,230,255,.74)"/>
        <stop offset="100%" stop-color="rgba(100,180,240,.52)"/>
      </linearGradient>
      <filter id="sigf" x="-28%" y="-28%" width="156%" height="156%">
        <feGaussianBlur stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <circle cx="55" cy="64" r="50" fill="none" stroke="rgba(10,85,184,.14)" stroke-width="1" stroke-dasharray="6 5">
      <animateTransform attributeName="transform" type="rotate" from="0 55 64" to="360 55 64" dur="22s" repeatCount="indefinite"/>
    </circle>
    <circle cx="55" cy="64" r="40" fill="none" stroke="rgba(10,85,184,.24)" stroke-width="1">
      <animate attributeName="r" values="40;58" dur="2.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;0" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#sig1)" filter="url(#sigf)"/>
    <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="1.6"/>
    <rect x="46" y="64" width="18" height="5" rx="2.2" fill="white"/>
    <rect x="52" y="57" width="6" height="19" rx="2.2" fill="white"/>
    <!-- Sinusoid waves - RDC colors -->
    <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
    </polyline>
    <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
    </polyline>
    <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".6s" repeatCount="indefinite"/>
    </polyline>
  </svg>
  <div class="sidebar-brand">SAFE CONGO</div>
  <div class="sidebar-tagline">Veille sanitaire nationale</div>
</div>
"""


PUBLIC_SIDEBAR_THEME = """
<style>
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"],
[data-testid="stSidebarNavViewButton"],
[data-testid="stSidebarNavLinkContainer"],
[data-testid="stSidebarNavLink"]{
  display:none!important;
  visibility:hidden!important;
  opacity:0!important;
  height:0!important;
  min-height:0!important;
  max-height:0!important;
  margin:0!important;
  padding:0!important;
  overflow:hidden!important;
  pointer-events:none!important;
}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#eef6ff 0%,#e6f2fd 52%,#f0f8ff 100%)!important;
  border-right:1px solid rgba(117,171,215,.32)!important;
  box-shadow:2px 0 18px rgba(10,60,140,.07)!important;
}
[data-testid="stSidebar"] *{color:#0a2c5a!important}
[data-testid="stSidebar"] .stButton > button{
  background:rgba(255,255,255,.72)!important;
  border:1px solid rgba(151,195,228,.75)!important;
  border-radius:16px!important;
  min-height:48px!important;
  box-shadow:0 8px 22px rgba(26,91,160,.08)!important;
  color:#0a4a8a!important;
  font-size:.86rem!important;
  font-weight:700!important;
  letter-spacing:.2px!important;
  text-align:left!important;
  justify-content:flex-start!important;
  padding:0 16px!important;
  transition:all .22s ease!important;
}
[data-testid="stSidebar"] .stButton > button:hover{
  transform:translateX(4px)!important;
  border-color:#0a84d0!important;
  background:linear-gradient(135deg,#ffffff,#e8f4ff)!important;
  box-shadow:0 12px 28px rgba(10,132,208,.14)!important;
}
[data-testid="stSidebar"] .stButton > button:focus-visible,
[data-testid="stSidebar"] .stButton > button:active{
  background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
  color:#ffffff!important;
  border-color:#0a5fab!important;
  box-shadow:0 0 0 3px rgba(26,162,226,.22),0 12px 28px rgba(10,95,171,.24)!important;
  transform:translateX(2px)!important;
}
[data-testid="stSidebar"] .public-sidebar-label{
  margin:4px 0 10px 2px;
  font-size:.7rem;
  font-weight:800;
  letter-spacing:1.9px;
  text-transform:uppercase;
  color:#5d86a8!important;
}
[data-testid="stSidebar"] .public-sidebar-active-card{
  margin-top:6px;
  padding:16px 16px 15px;
  border-radius:18px;
  background:linear-gradient(135deg,#083f73 0%,#0a5fab 52%,#1aa2e2 100%);
  border:1px solid rgba(12,86,149,.45);
  box-shadow:0 16px 36px rgba(10,95,171,.24);
}
[data-testid="stSidebar"] .public-sidebar-active-card,
[data-testid="stSidebar"] .public-sidebar-active-card *{color:#ffffff!important}
[data-testid="stSidebar"] .public-sidebar-active-kicker{
  display:inline-flex;
  align-items:center;
  padding:5px 10px;
  border-radius:999px;
  background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.18);
  color:rgba(255,255,255,.82)!important;
  font-size:.64rem;
  font-weight:800;
  letter-spacing:1.4px;
  text-transform:uppercase;
}
[data-testid="stSidebar"] .public-sidebar-active-title{
  margin-top:11px;
  color:#ffffff!important;
  font-family:'Sora',sans-serif;
  font-size:1rem;
  font-weight:800;
  line-height:1.3;
}
[data-testid="stSidebar"] .public-sidebar-active-copy{
  margin-top:7px;
  color:rgba(235,246,255,.9)!important;
  font-size:.79rem;
  line-height:1.55;
}
[data-testid="stSidebar"] .element-container:first-child{
  margin-top:1.2rem!important;
}
</style>
"""


PUBLIC_SIDEBAR_NAV_CLEANUP = """
<script>
const selectors = [
  '[data-testid="stSidebarNav"]',
  '[data-testid="stSidebarNavItems"]',
  '[data-testid="stSidebarNavSeparator"]',
  '[data-testid="stSidebarNavViewButton"]',
  '[data-testid="stSidebarNavLinkContainer"]',
  '[data-testid="stSidebarNavLink"]'
];

function hideNativeSidebarNav() {
  const doc = window.parent?.document || document;
  selectors.forEach((selector) => {
    doc.querySelectorAll(selector).forEach((node) => {
      node.style.display = 'none';
      node.style.visibility = 'hidden';
      node.style.opacity = '0';
      node.style.height = '0';
      node.style.minHeight = '0';
      node.style.maxHeight = '0';
      node.style.margin = '0';
      node.style.padding = '0';
      node.style.overflow = 'hidden';
      node.setAttribute('aria-hidden', 'true');
    });
  });
}

hideNativeSidebarNav();
new MutationObserver(hideNativeSidebarNav).observe(window.parent?.document?.body || document.body, {
  childList: true,
  subtree: true,
});
</script>
"""


PUBLIC_NAV_ITEMS = [
  ("apropos", "pages/apropos.py", "A Propos", "Objectif, role et vision de SAFE CONGO"),
    ("notre_mission", "pages/notre_mission.py", "Perspective Strategique", "Notre mission souveraine"),
    ("impact", "pages/impact.py", "Preuves & Resultats", "Impact national mesurable"),
    ("fonctionnement", "pages/fonctionnement.py", "Mecanique Intelligente", "Comment SAFE CONGO orchestre l'alerte"),
    ("contact", "pages/contact.py", "Alliance & Coordination", "Contacts et partenaires de confiance"),
]


def render_sidebar_active_button(button_index: int) -> None:
    st.markdown(
        f"""
<style>
[data-testid="stSidebar"] .stButton:nth-of-type({button_index}) > button{{
  background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
  color:#ffffff!important;
  border-color:#0a5fab!important;
  box-shadow:0 0 0 3px rgba(26,162,226,.18),0 10px 24px rgba(10,95,171,.28)!important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_public_sidebar(active_page: Optional[str] = None, show_home_button: bool = True) -> None:
    with st.sidebar:
        apropos_button_index = 2 if show_home_button else 1
        st.markdown(PUBLIC_SIDEBAR_THEME, unsafe_allow_html=True)
        st.html(PUBLIC_SIDEBAR_NAV_CLEANUP)
        st.markdown(PUBLIC_SIDEBAR_BRAND, unsafe_allow_html=True)
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"] .stButton:nth-of-type({apropos_button_index}) > button{{
              text-align:center!important;
              justify-content:center!important;
              padding:0 12px!important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        if show_home_button and st.button(
            "Retour vers l'accueil central",
            use_container_width=True,
            key="sidebar_back_home",
        ):
            switch_to_home_page()

        st.markdown("---")
        st.markdown('<div class="public-sidebar-label">Parcours public</div>', unsafe_allow_html=True)
        button_index = 1 if show_home_button else 0
        for item_key, page_path, title, _description in PUBLIC_NAV_ITEMS:
            button_index += 1
            if st.button(title, use_container_width=True, key=f"public_nav_{item_key}"):
                st.switch_page(page_path)
            if active_page == item_key:
                render_sidebar_active_button(button_index)
