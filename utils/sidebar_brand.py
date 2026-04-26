import streamlit as st


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


def render_public_sidebar() -> None:
    with st.sidebar:
        st.markdown(PUBLIC_SIDEBAR_BRAND, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("← Retour à l'accueil", use_container_width=True):
            st.switch_page("app.py")
