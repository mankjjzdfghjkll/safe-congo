import streamlit as st
import streamlit.components.v1 as components
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="SAFE CONGO - Surveillance Epidemiologique",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
* { font-family: 'Manrope', sans-serif; box-sizing: border-box; }
/* #MainMenu { visibility: hidden; } */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  color: #0b4d95 !important;
  background: rgba(255,255,255,.96) !important;
  border: 1px solid rgba(11,77,149,.16) !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 28px rgba(15,23,42,.12) !important;
}
[data-testid="collapsedControl"] svg {
  fill: #0b4d95 !important;
}
[data-testid="stSidebarNav"] { display: none; }


/* ─── MAIN BG LIGHT BLUE ────────────────────────────────────────────── */
html, body, .stApp, .main, .block-container {
  background: linear-gradient(180deg, #eef6ff 0%, #e6f2fd 52%, #f0f8ff 100%) !important;
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
  height: auto !important;
  box-sizing: border-box;
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
  overflow-y: auto !important;
}
.stApp:after, .main:after, .block-container:after, body:after, html:after {
  display: none !important;
  content: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Supprime l’espace vide au-dessus et en dessous */
.block-container, .main, .stApp > div:first-child, .stApp > div:last-child {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* ─── GLOW BUTTON ANIMATION ─────────────────────────────────────────── */
.stButton > button {
  position: relative;
  z-index: 1;
  overflow: hidden;
}
.stButton > button::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 12px;
  box-shadow: 0 0 0 0 rgba(26,162,226,0.0);
  transition: box-shadow .28s cubic-bezier(.22,1,.36,1);
  z-index: -1;
}
.stButton > button:hover::after {
  box-shadow: 0 0 16px 4px rgba(26,162,226,0.18), 0 0 32px 8px rgba(11,77,149,0.12);
}

:root {
    --primary: #0066CC;
    --primary-dark: #004D99;
    --primary-glow: rgba(0,102,204,.7);
    --cyan: #00D4FF;
    --danger: #DC3545;
    --warning: #FFC107;
    --success: #00A86B;
    --dark: #0a0e1a;
    --dark2: #111827;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes shimmer {
    0%   { background-position: -1200px 0; }
    100% { background-position:  1200px 0; }
}
@keyframes floatUp {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-8px); }
}
@keyframes orbitRing {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes orbitRingRev {
    from { transform: rotate(0deg); }
    to   { transform: rotate(-360deg); }
}
@keyframes glow {
    0%,100% { opacity:.4; r:44; }
    50%     { opacity:1;  r:48; }
}
@keyframes scanLine {
    0%   { transform: translateY(-60px); opacity:0; }
    10%  { opacity:.8; }
    90%  { opacity:.8; }
    100% { transform: translateY(60px); opacity:0; }
}
@keyframes heartbeat {
    0%   { stroke-dashoffset: 200; }
    100% { stroke-dashoffset: 0; }
}
@keyframes particleFloat {
    0%   { transform: translate(0,0);   opacity:1; }
    100% { transform: translate(var(--tx),var(--ty)); opacity:0; }
}
@keyframes ripple {
    0%   { transform: scale(.6); opacity:.7; }
    100% { transform: scale(2.2); opacity:0; }
}
@keyframes textGlow {
    0%,100% { text-shadow: 0 0 10px rgba(0,212,255,.4), 0 0 20px rgba(0,102,204,.3); }
    50%     { text-shadow: 0 0 20px rgba(0,212,255,.8), 0 0 40px rgba(0,102,204,.6), 0 0 60px rgba(0,102,204,.3); }
}
@keyframes countUp {
    from { opacity:0; transform:scale(.8); }
    to   { opacity:1; transform:scale(1); }
}
@keyframes borderSpin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes slideInUp {
    from { opacity:0; transform:translateY(40px); }
    to   { opacity:1; transform:translateY(0); }
}

/* stApp already set above */

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #eef6ff 0%, #e6f2fd 52%, #f0f8ff 100%) !important;
  border-right: 1px solid rgba(117,171,215,.32);
  box-shadow: 2px 0 18px rgba(10,60,140,.07);
}
[data-testid="stSidebar"] * { color: #0a2c5a !important; }
[data-testid="stSidebar"] .stMarkdown { color: #0a2c5a; }
[data-testid="stSidebar"] .stButton > button {
  background: #eef7ff !important;
  border: 1px solid #c8e2f5 !important;
  border-radius: 12px !important;
  min-height: 42px !important;
  box-shadow: none !important;
  color: #0a4a8a !important;
  font-size: .86rem !important;
  font-weight: 700 !important;
  letter-spacing: .2px !important;
  text-align: left !important;
  justify-content: flex-start !important;
  padding: 0 16px !important;
  transition: all .22s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  transform: translateX(4px) !important;
  border-color: #0a84d0 !important;
  background: linear-gradient(135deg, #dff0ff, #eaf6ff) !important;
  box-shadow: 0 4px 16px rgba(10,132,208,.14) !important;
}

/* ─── SIDEBAR LOGO ─────────────────────────────────────────────────────── */
.sidebar-logo-wrap {
    display: flex; flex-direction: column; align-items: center;
    padding: 16px 14px 8px; position: relative;
    margin: 4px 8px 0;
    border-radius: 18px;
    background: transparent;
}
.sidebar-logo-glow {
    position: absolute; width: 95px; height: 95px; top: 6px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(10,85,184,.28) 0%, transparent 70%);
    animation: floatUp 4s ease-in-out infinite;
    z-index: 0;
}
.sidebar-logo-svg {
    position: relative; z-index: 2;
    animation: floatUp 4s ease-in-out infinite;
    filter: drop-shadow(0 6px 14px rgba(10,60,120,.24));
}
.sidebar-brand {
    font-family: 'Sora', sans-serif;
    font-size: .86rem; font-weight: 800; letter-spacing: 1.6px;
    color: #0a2c5a !important; text-align: center;
    margin-top: 10px;
    text-transform: uppercase;
}
.sidebar-tagline {
    font-size: .64rem; letter-spacing: .8px; text-align: center;
    color: #7a9ab8 !important;
    text-transform: none; margin-top: 2px; font-weight: 600;
}
.hero-subtitle {
    font-size: 1rem; letter-spacing: 4px; text-transform: uppercase;
    color: rgba(0,212,255,.8); font-weight: 500;
    animation: slideInUp .8s ease-out .4s both;
    margin-bottom: 28px;
}
.hero-divider {
    width: 80px; height: 2px; margin: 0 auto 28px;
    background: linear-gradient(90deg, transparent, #00D4FF, transparent);
    animation: slideInUp .8s ease-out .5s both;
}

.hero-stats {
    display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
    animation: slideInUp .8s ease-out .6s both;
}
.hero-stat {
    text-align: center;
}
.hero-stat-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem; font-weight: 900;
    color: #00D4FF;
    animation: textGlow 3s ease-in-out infinite;
}
.hero-stat-label {
    font-size: .7rem; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,.5); margin-top: 2px;
}

/* ─── FEATURE CARDS ─────────────────────────────────────────────────────── */
.feat-card {
    background: rgba(255,255,255,.04); border-radius: 18px; padding: 24px 20px;
    text-align: center; transition: all .35s;
    border: 1px solid rgba(0,212,255,.12);
    backdrop-filter: blur(8px);
    animation: fadeIn .9s ease-out;
    position: relative; overflow: hidden;
}
.feat-card::before {
    content:''; position:absolute; inset:0;
    background: linear-gradient(135deg, rgba(0,212,255,.05), transparent);
    opacity:0; transition: opacity .35s;
}
.feat-card:hover { transform: translateY(-8px); border-color: rgba(0,212,255,.4);
    box-shadow: 0 12px 40px rgba(0,102,204,.25); }
.feat-card:hover::before { opacity:1; }
.feat-icon { font-size: 2.6rem; margin-bottom: 10px; }
.feat-label { font-weight: 700; color: #e0eaff; font-size: .95rem; }
.feat-desc  { font-size: .78rem; color: rgba(160,180,220,.7); margin-top: 5px; }

/* ─── FORM / CARD ───────────────────────────────────────────────────────── */
.form-wrapper {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(0,212,255,.15);
    border-radius: 24px; padding: 36px;
    backdrop-filter: blur(12px);
    box-shadow: 0 20px 60px rgba(0,0,0,.4);
    animation: fadeIn .7s ease-out;
}

.stButton > button {
    background: linear-gradient(135deg, #0066CC, #004D99) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    padding: 12px 24px !important; font-weight: 700 !important;
    transition: all .3s !important; width: 100% !important;
    letter-spacing: 1px !important;
    box-shadow: 0 4px 20px rgba(0,102,204,.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,102,204,.5) !important;
}
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid rgba(0,212,255,.2) !important;
    padding: 12px 16px !important;
    background: rgba(255,255,255,.06) !important;
    color: #e0eaff !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,.15) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(160,180,220,.5) !important; }
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1px solid rgba(0,212,255,.2) !important;
    background: rgba(255,255,255,.06) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px; padding: 8px 20px; font-weight: 600;
    color: rgba(160,200,255,.7) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#0066CC,#004D99) !important;
    color:#fff !important;
}
.stMarkdown p, .stMarkdown label, .stMarkdown { color: #374151 !important; }

/* ─── LOGIN FORM OVERRIDES (white bg) ──────────────────────────────── */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #d1d5db !important;
    padding: 12px 16px !important;
    background: #fff !important;
    color: #111827 !important;
    font-size: .95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0066CC !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,.12) !important;
}
.stTextInput label { color: #374151 !important; font-weight: 600 !important; font-size: .88rem !important; }
.stSelectbox label { color: #374151 !important; font-weight: 600 !important; font-size: .88rem !important; }
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #d1d5db !important;
    background: #fff !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 10px;
  background: #f3f8ff;
  border: 1px solid #dde9f8;
  border-radius: 16px;
  padding: 6px;
}
.stTabs [data-baseweb="tab"] { border-radius: 12px; padding: 10px 24px; font-weight: 700; color: #6b7280 !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,#0066CC,#004D99) !important; color:#fff !important; box-shadow: 0 10px 22px rgba(0,102,204,.18) !important; }

.auth-shell {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255,255,255,.97) 0%, rgba(241,249,255,.98) 100%);
  border: 1px solid rgba(77, 142, 198, .18);
  border-radius: 34px;
  padding: 20px;
  box-shadow: 0 26px 60px rgba(52, 106, 163, .10), 0 0 0 1px rgba(255,255,255,.84) inset;
}
.auth-shell::before {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: 30px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(11,77,149,.34), rgba(111,206,244,.36), rgba(255,255,255,.18));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
.auth-shell::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top right, rgba(74,177,228,.14), transparent 30%),
    radial-gradient(circle at bottom left, rgba(8,82,144,.08), transparent 24%),
    linear-gradient(180deg, rgba(255,255,255,.24), transparent 46%);
  pointer-events: none;
}
.auth-shell-head {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1.15fr .85fr;
  gap: 18px;
  margin-bottom: 16px;
  padding: 22px 20px 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f2f9ff 70%, #eef7ff 100%);
  border: 1px solid #d5e8f7;
  border-radius: 28px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.88);
  text-align: center;
  align-items: center;
}
.auth-shell-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.22rem;
  font-weight: 800;
  letter-spacing: -.2px;
  color: #10345f !important;
  margin-bottom: 10px;
}
.auth-shell-copy {
  color: #5f7492 !important;
  font-size: .92rem;
  line-height: 1.76;
  max-width: 560px;
  margin: 0 auto;
}
.auth-shell-statbox {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.auth-shell-stat {
  background: linear-gradient(180deg, #ffffff 0%, #edf8ff 100%);
  border: 1px solid #d7eaf9;
  border-radius: 20px;
  padding: 15px 14px;
  box-shadow: 0 12px 26px rgba(72, 128, 184, .07);
}
.auth-shell-stat-k {
  font-size: .66rem;
  font-weight: 800;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: #6d87a7 !important;
  margin-bottom: 6px;
}
.auth-shell-stat-v {
  font-family: 'Sora', sans-serif;
  font-size: .98rem;
  font-weight: 800;
  color: #0b4d95 !important;
}
.auth-panel {
  background: linear-gradient(180deg, #ffffff 0%, #f8fcff 100%);
  border: 1px solid rgba(71, 136, 194, .14);
  border-radius: 28px;
  padding: 30px 28px 24px;
  box-shadow: 0 18px 34px rgba(72, 127, 184, .08);
}
.auth-kicker {
  display: inline-block;
  font-size: .68rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #0b4d95 !important;
  background: linear-gradient(135deg, #ebf7ff 0%, #f6fbff 100%);
  border: 1px solid #cfe8fa;
  border-radius: 999px;
  padding: 6px 12px;
  margin-bottom: 10px;
  margin-left: auto;
  margin-right: auto;
}
.auth-panel-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.22rem;
  font-weight: 800;
  color: #11355e !important;
  margin: 0 0 6px;
  letter-spacing: .5px;
  text-align: center;
}
.auth-panel-sub {
  color: #5f7490 !important;
  font-size: .9rem;
  line-height: 1.6;
  margin-bottom: 16px;
  text-align: center;
}
.auth-inline-note {
  color: #4f6886 !important;
  background: linear-gradient(135deg, #f7fcff 0%, #edf8ff 100%);
  border: 1px solid #d8ebf9;
  border-radius: 16px;
  padding: 12px 14px;
  font-size: .82rem;
  line-height: 1.6;
  margin: 10px 0 6px;
  text-align: center;
}
.trust-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 14px 0 8px;
  justify-content: center;
}
.trust-pill {
  font-size: .74rem;
  font-weight: 700;
  color: #17477d !important;
  background: linear-gradient(135deg, #eff8ff 0%, #f8fcff 100%);
  border: 1px solid #d7ebfb;
  border-radius: 999px;
  padding: 7px 12px;
}
.auth-mini-note {
  color: #94a3b8 !important;
  font-size: .75rem;
  margin-top: 8px;
  line-height: 1.5;
  text-align: center;
}
.auth-feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 22px;
}
.auth-feature-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  border: 1px solid rgba(0, 102, 204, .12);
  border-radius: 22px;
  padding: 20px;
  min-height: 184px;
  box-shadow: 0 16px 36px rgba(15, 23, 42, .07);
}
.auth-feature-card::before {
  content: "";
  position: absolute;
  left: 16px;
  right: 16px;
  top: 0;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #0066CC, #00D4FF, #FFD447);
}
.auth-feature-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff8dd 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  margin-bottom: 14px;
}
.auth-feature-icon svg {
  width: 24px;
  height: 24px;
  stroke: #0b4d95;
  fill: none;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.auth-feature-title {
  color: #0f172a !important;
  font-size: .95rem;
  font-weight: 800;
  letter-spacing: .4px;
  margin-bottom: 8px;
  text-align: center;
}
.auth-feature-copy {
  color: #64748b !important;
  font-size: .84rem;
  line-height: 1.62;
  text-align: center;
}
.bridge-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  max-width: 1160px;
  margin: 10px auto 22px;
}
.bridge-shell {
  max-width: 1160px;
  margin: 6px auto 20px;
}
.bridge-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  margin-bottom: 16px;
  text-align: center;
}
.bridge-titleline {
  color: #0f172a !important;
  font-family: 'Sora', sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -.4px;
  text-align: center;
}
.bridge-subline {
  color: #64748b !important;
  font-size: .92rem;
  line-height: 1.7;
  max-width: 640px;
  text-align: center;
  margin: 0 auto;
}
.bridge-tag {
  padding: 10px 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff8dd 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .74rem;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  white-space: nowrap;
  margin: 0 auto;
}
.bridge-card {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  border: 1px solid rgba(0, 102, 204, .12);
  border-radius: 22px;
  padding: 22px;
  min-height: 190px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, .07);
  text-align: center;
}
.bridge-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top right, rgba(0,212,255,.10), transparent 36%);
  pointer-events: none;
}
.bridge-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff4cc 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  margin: 0 auto 14px;
}
.bridge-icon svg {
  width: 26px;
  height: 26px;
  stroke: #0b4d95;
  fill: none;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.bridge-title {
  color: #0f172a !important;
  font-size: .98rem;
  font-weight: 800;
  letter-spacing: .5px;
  margin-bottom: 8px;
}
.bridge-copy {
  color: #64748b !important;
  font-size: .86rem;
  line-height: 1.64;
}
.entry-shell {
  max-width: 1120px;
  margin: 10px auto 0;
}
.entry-head {
  text-align: center;
  margin: 0 auto 20px;
  max-width: 760px;
}
.entry-kicker {
  display: inline-block;
  padding: 7px 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #eef6ff 0%, #fff8dd 100%);
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .72rem;
  font-weight: 800;
  letter-spacing: 1.7px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.entry-title {
  color: #0f172a !important;
  font-family: 'Sora', sans-serif;
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: -.5px;
  margin-bottom: 10px;
}
.entry-copy {
  color: #64748b !important;
  font-size: .95rem;
  line-height: 1.7;
}
.entry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 16px auto 22px;
}
.entry-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid rgba(71, 136, 194, .14);
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 18px 34px rgba(72, 127, 184, .08);
  text-align: center;
}
.entry-card-title {
  color: #0f172a !important;
  font-size: .98rem;
  font-weight: 800;
  margin-bottom: 8px;
}
.entry-card-copy {
  color: #64748b !important;
  font-size: .84rem;
  line-height: 1.62;
}
.auth-stage {
  max-width: 920px;
  margin: 6px auto 0;
}
.auth-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.auth-mode-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .74rem;
  font-weight: 800;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar compact logo SVG ───────────────────────────────────────────────
SHIELD_SIDEBAR = """
<div class="sidebar-logo-wrap">
  <div class="sidebar-logo-glow"></div>
  <svg class="sidebar-logo-svg" width="84" height="94" viewBox="0 0 124 140"
       xmlns="http://www.w3.org/2000/svg">
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
    <!-- Rotating orbit rings -->
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
    <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
    </polyline>
    <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
    </polyline>
    <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
      <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".6s" repeatCount="indefinite"/>
    </polyline>
    <g transform="translate(15 102)">
      <rect x="0" y="0" width="94" height="22" rx="11" fill="rgba(255,255,255,.06)" stroke="rgba(126,198,241,.18)"/>
      <text x="47" y="14.5" text-anchor="middle" fill="rgba(200,230,255,.92)" style="font-family:'Sora',sans-serif;font-size:11px;font-weight:700;letter-spacing:1.55px">SAFE CONGO</text>
    </g>
  </svg>
  <div class="sidebar-brand">SAFE CONGO</div>
  <div class="sidebar-tagline">Veille sanitaire nationale</div>
</div>
"""

# ── Hero logo (large, for login page) ─────────────────────────────────────
SHIELD_HERO = """
<div class="hero-logo-container">
  <svg width="160" height="190" viewBox="0 0 160 190"
       xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
    <defs>
      <linearGradient id="hg1" x1="0%" y1="0%" x2="100%" y2="130%">
        <stop offset="0%"   stop-color="#80E0FF"/>
        <stop offset="40%"  stop-color="#0088FF"/>
        <stop offset="100%" stop-color="#003080"/>
      </linearGradient>
      <linearGradient id="hg2" x1="0%" y1="0%" x2="60%" y2="100%">
        <stop offset="0%"  stop-color="rgba(255,255,255,.5)"/>
        <stop offset="70%" stop-color="rgba(255,255,255,0)"/>
      </linearGradient>
      <radialGradient id="hglow" cx="50%" cy="50%" r="50%">
        <stop offset="0%"  stop-color="rgba(0,136,255,.35)"/>
        <stop offset="100%" stop-color="rgba(0,136,255,0)"/>
      </radialGradient>
      <filter id="hf" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="4" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="hf2" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="2"/>
      </filter>
    </defs>

    <!-- Pulsing background glow -->
    <ellipse cx="80" cy="95" rx="70" ry="70" fill="url(#hglow)">
      <animate attributeName="rx" values="60;80;60" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="ry" values="60;80;60" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;1;.5" dur="3s" repeatCount="indefinite"/>
    </ellipse>

    <!-- Outer orbit ring 1 -->
    <g>
      <animateTransform attributeName="transform" type="rotate"
        from="0 80 95" to="360 80 95" dur="10s" repeatCount="indefinite"/>
      <ellipse cx="80" cy="95" rx="74" ry="74"
               fill="none" stroke="rgba(0,212,255,.35)" stroke-width="1.2"
               stroke-dasharray="8 6"/>
      <circle cx="154" cy="95" r="4" fill="#00D4FF" opacity=".9"/>
      <circle cx="6"   cy="95" r="3" fill="#00D4FF" opacity=".6"/>
    </g>

    <!-- Outer orbit ring 2 (reverse) -->
    <g>
      <animateTransform attributeName="transform" type="rotate"
        from="0 80 95" to="-360 80 95" dur="15s" repeatCount="indefinite"/>
      <ellipse cx="80" cy="95" rx="82" ry="82"
               fill="none" stroke="rgba(0,102,204,.25)" stroke-width=".8"
               stroke-dasharray="3 9"/>
      <circle cx="80" cy="13" r="3" fill="#0088FF" opacity=".8"/>
    </g>

    <!-- Shield drop shadow (blur layer) -->
    <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"
          fill="rgba(0,60,160,.5)" filter="url(#hf2)"
          transform="translate(4,8)"/>

    <!-- Shield main body -->
    <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"
          fill="url(#hg1)"/>

    <!-- 3D highlight overlay -->
    <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"
          fill="url(#hg2)" opacity=".5"/>

    <!-- Inner shield bevel -->
    <path d="M80 24 L130 50 L130 96 Q130 138 80 164 Q30 138 30 96 L30 50 Z"
          fill="none" stroke="rgba(255,255,255,.22)" stroke-width="2"/>

    <!-- Animated scan line -->
    <clipPath id="shieldClip">
      <path d="M80 12 L142 42 L142 98 Q142 148 80 178 Q18 148 18 98 L18 42 Z"/>
    </clipPath>
    <g clip-path="url(#shieldClip)">
      <rect x="18" y="0" width="124" height="3"
            fill="rgba(0,212,255,.6)" rx="1">
        <animateTransform attributeName="transform" type="translate"
          values="0,20; 0,160" dur="2.8s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;.9;.9;0" dur="2.8s" repeatCount="indefinite"/>
      </rect>
    </g>

    <!-- Cross shape -->
    <rect x="65" y="76" width="30" height="10" rx="3" fill="white" opacity=".95"/>
    <rect x="73" y="68" width="14" height="26" rx="3" fill="white" opacity=".95"/>

    <!-- ECG / heartbeat line -->
    <polyline
      points="32,81 42,81 47,62 53,100 58,81 65,81"
      fill="none" stroke="#00D4FF" stroke-width="2.2"
      stroke-linecap="round" stroke-linejoin="round"
      stroke-dasharray="90" stroke-dashoffset="90">
      <animate attributeName="stroke-dashoffset"
        values="90;0;0;90" dur="3.2s" repeatCount="indefinite"/>
    </polyline>
    <polyline
      points="95,81 102,81 107,62 113,100 118,81 128,81"
      fill="none" stroke="#00D4FF" stroke-width="2.2"
      stroke-linecap="round" stroke-linejoin="round"
      stroke-dasharray="90" stroke-dashoffset="90">
      <animate attributeName="stroke-dashoffset"
        values="90;0;0;90" dur="3.2s" begin="0.3s" repeatCount="indefinite"/>
    </polyline>

    <!-- Ripple circles -->
    <circle cx="80" cy="95" r="55" fill="none"
            stroke="rgba(0,212,255,.5)" stroke-width="1.5">
      <animate attributeName="r"      values="55;90" dur="2.5s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".6;0"  dur="2.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="80" cy="95" r="55" fill="none"
            stroke="rgba(0,102,204,.4)" stroke-width="1">
      <animate attributeName="r"      values="55;90" dur="2.5s" begin="1.25s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;0"  dur="2.5s" begin="1.25s" repeatCount="indefinite"/>
    </circle>

    <!-- Corner accent dots -->
    <circle cx="80"  cy="12"  r="3.5" fill="#00D4FF"/>
    <circle cx="142" cy="42"  r="2.5" fill="#60CFFF" opacity=".8"/>
    <circle cx="18"  cy="42"  r="2.5" fill="#60CFFF" opacity=".8"/>
    <circle cx="18"  cy="98"  r="2"   fill="#0088FF" opacity=".6"/>
    <circle cx="142" cy="98"  r="2"   fill="#0088FF" opacity=".6"/>

    <!-- Floating particles -->
    <g opacity=".8">
      <circle cx="20" cy="50" r="1.8" fill="#00D4FF">
        <animate attributeName="cy" values="50;20" dur="4s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="4s" repeatCount="indefinite"/>
      </circle>
      <circle cx="140" cy="70" r="1.5" fill="#60CFFF">
        <animate attributeName="cy" values="70;30" dur="5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="5s" begin="1s" repeatCount="indefinite"/>
      </circle>
      <circle cx="50" cy="160" r="1.2" fill="#00D4FF">
        <animate attributeName="cy" values="160;130" dur="3.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;.8;0" dur="3.5s" begin=".5s" repeatCount="indefinite"/>
      </circle>
      <circle cx="110" cy="155" r="1.5" fill="#4FC3F7">
        <animate attributeName="cy" values="155;125" dur="4.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;1;0" dur="4.5s" begin="2s" repeatCount="indefinite"/>
      </circle>
    </g>
  </svg>
</div>
"""


# ── Hero section – standalone HTML (bypasses Streamlit markdown sanitizer) ──
HERO_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#eef6ff;font-family:'Manrope',sans-serif;min-height:100%;overflow-x:hidden}
/* ── ANIMATIONS ────────────────────────────────── */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes blockGlow{0%,100%{box-shadow:0 10px 38px rgba(26,162,226,.13);}50%{box-shadow:0 24px 64px rgba(26,162,226,.22);}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{transform:scale(1);opacity:.7}50%{transform:scale(1.18);opacity:1}}
@keyframes ecgDraw{0%{stroke-dashoffset:90}60%{stroke-dashoffset:0}80%{stroke-dashoffset:0}100%{stroke-dashoffset:90}}
@keyframes ripple{0%{r:40;opacity:.55}100%{r:64;opacity:0}}

/* ── BASE ───────────────────────────────────────── */
.shell{padding:14px 18px 0}

/* ── NAVBAR ─────────────────────────────────────── */
.navbar{display:flex;align-items:center;justify-content:space-between;padding:13px 22px;border-radius:18px;background:#ffffff;border:1px solid #d0e8f8;box-shadow:0 4px 22px rgba(10,70,140,.08);margin-bottom:18px;animation:fadeUp .45s ease-out}
.nav-brand{display:flex;align-items:center;gap:12px}
.nav-shield{width:38px;height:44px;animation:float 4.5s ease-in-out infinite;flex-shrink:0}
.nav-name{font-family:'Sora',sans-serif;font-size:.95rem;font-weight:800;letter-spacing:2px;color:#0a2c5a;text-transform:uppercase;line-height:1.2}
.nav-sub{font-size:.62rem;font-weight:700;letter-spacing:1.4px;color:#5a9ac0;text-transform:uppercase;margin-top:2px}
.nav-pills{display:flex;gap:7px;flex-wrap:wrap}
.nav-pill{padding:7px 14px;border-radius:999px;background:#eef7ff;border:1px solid #c8e2f5;font-size:.72rem;font-weight:700;color:#1a6db5;letter-spacing:.3px;white-space:nowrap}

/* ── HERO ───────────────────────────────────────── */
.hero{position:relative;overflow:hidden;border-radius:26px;background:linear-gradient(135deg,#0a5fab 0%,#0d80d8 52%,#1aa2e2 100%);padding:50px 48px 46px;margin-bottom:20px;box-shadow:0 22px 58px rgba(10,95,171,.24),0 2px 0 rgba(255,255,255,.14) inset;animation:fadeUp .55s ease-out .06s both}
.hero-dots{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.11) 1px,transparent 1px);background-size:26px 26px;pointer-events:none}
.hero-glow{position:absolute;inset:0;background:radial-gradient(ellipse at 78% 18%,rgba(255,255,255,.16),transparent 34%),radial-gradient(ellipse at 12% 82%,rgba(0,40,100,.22),transparent 30%);pointer-events:none}
.hero-inner{position:relative;z-index:2;display:grid;grid-template-columns:1fr auto;gap:40px;align-items:center}
.hero-kicker{display:inline-flex;align-items:center;gap:7px;padding:7px 13px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);font-size:.7rem;font-weight:800;letter-spacing:1.7px;color:rgba(255,255,255,.95);text-transform:uppercase;margin-bottom:16px}
.kicker-dot{width:7px;height:7px;border-radius:50%;background:#72f5c0;animation:pulse 2.2s ease-in-out infinite}
.hero-title{font-family:'Sora',sans-serif;font-size:3.2rem;font-weight:800;line-height:1.06;letter-spacing:-1.4px;color:#ffffff;margin-bottom:14px}
.hero-title em{font-style:normal;display:block;color:rgba(255,255,255,.72);font-size:2.7rem}
.hero-sub{font-size:.95rem;line-height:1.72;color:rgba(255,255,255,.8);max-width:460px;margin-bottom:26px}
.hero-stats{display:flex;gap:14px;flex-wrap:wrap}
.hstat{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:11px 16px;text-align:center;min-width:80px}
.hstat-v{font-family:'Sora',sans-serif;font-size:1.3rem;font-weight:800;color:#ffffff}
.hstat-k{font-size:.62rem;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;color:rgba(255,255,255,.68);margin-top:3px}
.hero-visual{animation:float 5.5s ease-in-out infinite;filter:drop-shadow(0 18px 36px rgba(0,0,0,.16))}

/* ── CARDS ──────────────────────────────────────── */
.section-head{margin:0 0 32px 0;animation:fadeUp .8s cubic-bezier(.22,1,.36,1);}
.section-label{font-size:.7rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#3a7ebf;padding-left:2px}
.cards-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin:64px 0 64px 0;animation:fadeUp .8s cubic-bezier(.22,1,.36,1);}
.card{background:#ffffff;border:1px solid #d0e8f8;border-radius:22px;padding:32px 28px;box-shadow:0 8px 32px rgba(10,60,120,.09);position:relative;overflow:hidden;transition:transform .28s,box-shadow .28s;animation:fadeUp .65s ease-out both}
.card:nth-child(1){animation-delay:.08s}.card:nth-child(2){animation-delay:.16s}.card:nth-child(3){animation-delay:.24s}
.card::after{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:22px 22px 0 0}
.c1::after{background:linear-gradient(90deg,#0a84d0,#38b6e8)}.c2::after{background:linear-gradient(90deg,#0b9e6e,#3ec99a)}.c3::after{background:linear-gradient(90deg,#f57c00,#ffb74d)}
.card:hover{transform:translateY(-8px) scale(1.03);box-shadow:0 24px 64px rgba(26,162,226,.18),0 0 0 4px #e6f2fd;animation:blockGlow 1.8s infinite alternate;}
.c-ico{width:50px;height:50px;border-radius:15px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.ci-b{background:#e6f4fd}.ci-g{background:#e6f8f0}.ci-o{background:#fff3e0}
.c-title{font-family:'Sora',sans-serif;font-size:.98rem;font-weight:800;color:#0a2040;margin-bottom:8px}
.c-copy{font-size:.84rem;line-height:1.66;color:#5a7a99}
.c-tag{display:inline-block;margin-top:11px;padding:5px 10px;border-radius:999px;font-size:.67rem;font-weight:800;letter-spacing:.9px;text-transform:uppercase}
.ct-b{background:#e6f4fd;color:#1268b0}.ct-g{background:#e6f8f0;color:#0b7a52}.ct-o{background:#fff3e0;color:#c05800}

/* ── STEPS ──────────────────────────────────────── */
.steps-wrap{background:#ffffff;border:1px solid #d0e8f8;border-radius:22px;padding:38px 38px 38px;margin:80px 0 0 0;box-shadow:0 8px 32px rgba(10,60,120,.09);animation:fadeUp 1.1s cubic-bezier(.22,1,.36,1);}
.steps-title{font-family:'Sora',sans-serif;font-size:1.35rem;font-weight:800;color:#0a2c5a;text-align:center;margin-bottom:18px;}
.steps-sub{font-size:.98rem;color:#7a9ab8;text-align:center;margin-bottom:44px;}
.steps-row{display:flex;align-items:flex-start;gap:54px;}
.step{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;box-shadow:0 8px 32px rgba(26,162,226,.11);transition:box-shadow .22s,transform .18s;}
.step:hover{box-shadow:0 16px 48px rgba(26,162,226,.18),0 0 0 4px #e6f2fd;transform:translateY(-4px) scale(1.03);animation:blockGlow 1.8s infinite alternate;}
.step-line{flex:.42;height:2px;margin-top:23px;background:linear-gradient(90deg,#b8d8f0,#8ebfde)}
.step-num{width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2);color:#fff;font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:11px;box-shadow:0 6px 18px rgba(10,95,171,.26)}
.step-t{font-size:.9rem;font-weight:800;color:#0a2040;margin-bottom:5px}
.step-c{font-size:.78rem;color:#7a9ab8;line-height:1.56;max-width:150px}

/* ── FOOTER ─────────────────────────────────────── */

</style></head><body>
<div class="shell">

  <!-- DRAPEAU RDC AVANT HEADER -->
  <!-- DRAPEAU + HEADER HARMONISÉS -->
  <div style="background:linear-gradient(135deg,#eef6ff 0%,#f0f8ff 50%,rgba(245,251,255,.8) 100%);padding:0;position:relative;overflow:hidden">
    <!-- Accent bar avec couleurs RDC -->
    <div style="height:6px;background:linear-gradient(90deg,#0055B8 0%,#FCD116 50%,#CE1126 100%)"></div>
    
    <!-- Contenu principal -->
    <div style="padding:55px 40px;max-width:1200px;margin:0 auto">
      <div style="display:grid;grid-template-columns:1fr 1.2fr;gap:60px;align-items:center">
        <!-- Colonne gauche: Drapeau + Info RDC -->
        <div style="display:flex;flex-direction:column;align-items:flex-start;gap:24px">
          <!-- Drapeau compact -->
          <svg viewBox="0 0 900 600" style="width:75px;height:auto;margin-top:-10px;filter:drop-shadow(0 3px 10px rgba(10,85,184,.12))">
            <defs>
              <linearGradient id="flagShine" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="rgba(255,255,255,.3)"/>
                <stop offset="100%" stop-color="rgba(255,255,255,.05)"/>
              </linearGradient>
            </defs>
            <rect x="0" y="0" width="900" height="600" fill="#0055B8"/>
            <polygon points="0,180 900,350 900,450 0,280" fill="#CE1126"/>
            <polygon points="0,280 900,450 900,500 0,330" fill="#FCD116"/>
            <polygon points="150,120 165,170 220,170 180,210 200,260 150,220 100,260 120,210 80,170 135,170" fill="#FCD116" opacity=".95"/>
            <rect x="0" y="0" width="900" height="600" fill="url(#flagShine)"/>
          </svg>
          
          <!-- Infos RDC -->
          <div style="border-left:3px solid #0055B8;padding-left:20px">
            <div style="font-size:14px;font-weight:700;color:#0a5fab;font-family:'Sora',sans-serif;letter-spacing:1px;margin-bottom:4px">REPUBLIQUE DEMOCRATIQUE</div>
            <div style="font-size:14px;font-weight:700;color:#0a5fab;font-family:'Sora',sans-serif;letter-spacing:1px;margin-bottom:8px">DU CONGO</div>
            <div style="font-size:11px;color:#1aa2e2;font-family:'Manrope',sans-serif;font-weight:700;letter-spacing:1.5px">Unité • Travail • Progrès</div>
          </div>
        </div>
        
        <!-- Colonne droite: Header + Logo -->
        <div style="display:flex;flex-direction:column;gap:20px;justify-content:center">
          
          <!-- Titre et description -->
          <div>
            <div style="font-size:32px;font-weight:800;color:#0a5fab;font-family:'Sora',sans-serif;margin-bottom:12px;line-height:1.2">
              <span style="background:linear-gradient(135deg,#0a5fab 0%,#1aa2e2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">SAFE CONGO</span>
            </div>
            <div style="font-size:14px;color:#666;font-family:'Manrope',sans-serif;line-height:1.7;max-width:450px;margin-bottom:16px">
              Plateforme de surveillance épidémiologique pour la protection collective. Détection, analyse et réponse coordonnée aux menaces sanitaires en temps réel.
            </div>
            <div style="display:flex;gap:30px;flex-wrap:wrap">
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:4px;height:20px;background:#0055B8;border-radius:2px"></div>
                <div style="font-size:12px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:700">Surveillance 24/7</div>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:4px;height:20px;background:#CE1126;border-radius:2px"></div>
                <div style="font-size:12px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:700">Détection Rapide</div>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:4px;height:20px;background:#FCD116;border-radius:2px"></div>
                <div style="font-size:12px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:700">Action Immédiate</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- HERO -->
  <div class="hero">
    <div class="hero-dots"></div>
    <div class="hero-glow"></div>
    <div class="hero-inner">
      <div>
        <div class="hero-kicker"><span class="kicker-dot"></span>Plateforme epidemiologique RDC</div>
        <div class="hero-title">Surveiller<em>pour proteger.</em></div>
        <div class="hero-sub">Un outil national de veille sanitaire au service des autorites de sante de la Republique Democratique du Congo.</div>
        <div class="hero-stats">
          <div class="hstat"><div class="hstat-v">26</div><div class="hstat-k">Provinces</div></div>
          <div class="hstat"><div class="hstat-v">516</div><div class="hstat-k">Zones</div></div>
          <div class="hstat"><div class="hstat-v">24/7</div><div class="hstat-k">Alerte</div></div>
          <div class="hstat"><div class="hstat-v">RDC</div><div class="hstat-k">National</div></div>
        </div>
      </div>
      <div class="hero-visual">
        <svg width="148" height="174" viewBox="0 0 110 128" xmlns="http://www.w3.org/2000/svg" overflow="visible">
          <defs>
            <linearGradient id="hv1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="rgba(255,255,255,.92)"/>
              <stop offset="58%" stop-color="rgba(180,230,255,.74)"/>
              <stop offset="100%" stop-color="rgba(100,180,240,.52)"/>
            </linearGradient>
            <filter id="hvf" x="-28%" y="-28%" width="156%" height="156%">
              <feGaussianBlur stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>
          <circle cx="55" cy="64" r="50" fill="none" stroke="rgba(255,255,255,.18)" stroke-width="1" stroke-dasharray="6 5">
            <animateTransform attributeName="transform" type="rotate" from="0 55 64" to="360 55 64" dur="22s" repeatCount="indefinite"/>
          </circle>
          <circle cx="55" cy="64" r="40" fill="none" stroke="rgba(255,255,255,.3)" stroke-width="1">
            <animate attributeName="r" values="40;58" dur="2.6s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values=".5;0" dur="2.6s" repeatCount="indefinite"/>
          </circle>
          <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#hv1)" filter="url(#hvf)"/>
          <path d="M55 20 L80 32 L80 56 Q80 80 55 98 Q30 80 30 56 L30 32 Z" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="1.6"/>
          <rect x="46" y="64" width="18" height="5" rx="2.2" fill="white"/>
          <rect x="52" y="57" width="6" height="19" rx="2.2" fill="white"/>
          <polyline points="16,50 24,50 27,40 31,62 35,50 44,50" fill="none" stroke="#FCD116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
            <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" repeatCount="indefinite"/>
          </polyline>
          <polyline points="26,50 34,50 37,40 41,62 45,50 54,50" fill="none" stroke="#0055B8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
            <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".3s" repeatCount="indefinite"/>
          </polyline>
          <polyline points="56,50 65,50 68,40 72,62 76,50 84,50" fill="none" stroke="#CE1126" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="80" stroke-dashoffset="80">
            <animate attributeName="stroke-dashoffset" values="80;0;0;80" dur="3s" begin=".6s" repeatCount="indefinite"/>
          </polyline>
        </svg>
      </div>
    </div>
  </div>

  <!-- CARDS -->
  <div class="section-head" style="margin-bottom:0;animation:fadeUp .8s cubic-bezier(.22,1,.36,1);"><div class="section-label" style="font-size:1.1rem;letter-spacing:2.5px;color:#0a5fab;">Capacités clés de la plateforme</div></div>
  <div class="cards-grid" style="margin-top:38px;gap:44px;">
    <div class="card card-premium" style="background:linear-gradient(135deg,#fafdff 60%,#e6f2fd 100%);border-radius:36px;box-shadow:0 22px 70px 0 rgba(26,162,226,.13),0 0 0 10px #e6f2fd1a inset;border:2.5px solid #e0eaff;align-items:center;gap:28px;animation:fadeUp .7s cubic-bezier(.22,1,.36,1);position:relative;overflow:hidden;transition:box-shadow .22s,transform .22s;min-width:310px;max-width:400px;padding:38px 28px 32px 28px;">
      <span class="c-tag-float" style="position:absolute;top:18px;right:18px;background:linear-gradient(90deg,#e6f2fd 60%,#fafdff 100%);color:#0a5fab;border:1.2px solid #c8e2f5;font-size:.89rem;font-weight:800;border-radius:999px;padding:6px 14px;box-shadow:0 2px 12px #e6f2fd80;z-index:2;">Surveillance</span>
      <div style="display:flex;align-items:center;gap:18px;margin-top:18px;">
        <svg width="54" height="54" viewBox="0 0 54 54" fill="none" style="background:linear-gradient(135deg,#e6f2fd,#fafdff);border-radius:16px;box-shadow:0 0 0 6px #e6f2fd;">
          <circle cx="27" cy="27" r="20" stroke="#0a5fab" stroke-width="2.5" fill="#fafdff"/>
          <path d="M37 37L27 27L20 34" stroke="#1aa2e2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <animate attributeName="stroke-dasharray" values="0,40;40,0;0,40" dur="2.2s" repeatCount="indefinite"/>
          </path>
        </svg>
        <span style="font-size:1.19rem;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#0a5fab;font-family:'Sora',sans-serif;">Détection rapide</span>
      </div>
      <div style="font-size:1.04rem;color:#4a6a8a;font-family:'Manrope',sans-serif;text-align:center;margin:12px 0 0 0;">Identification précoce des signaux d'alerte épidémiologique sur l'ensemble du territoire national.</div>
    </div>
    <div class="card card-premium" style="background:linear-gradient(135deg,#f8fcff 60%,#e6f8f0 100%);border-radius:36px;box-shadow:0 22px 70px 0 rgba(11,158,110,.13),0 0 0 10px #e6f8f01a inset;border:2.5px solid #b8e8d5;align-items:center;gap:28px;animation:fadeUp .8s .1s cubic-bezier(.22,1,.36,1);position:relative;overflow:hidden;transition:box-shadow .22s,transform .22s;min-width:310px;max-width:400px;padding:38px 28px 32px 28px;">
      <span class="c-tag-float" style="position:absolute;top:18px;right:18px;background:linear-gradient(90deg,#e6f8f0 60%,#f8fcff 100%);color:#0b9e6e;border:1.2px solid #b8e8d5;font-size:.89rem;font-weight:800;border-radius:999px;padding:6px 14px;box-shadow:0 2px 12px #e6f8f080;z-index:2;">Analyse</span>
      <div style="display:flex;align-items:center;gap:18px;margin-top:18px;">
        <svg width="54" height="54" viewBox="0 0 54 54" fill="none" style="background:linear-gradient(135deg,#e6f8f0,#f8fcff);border-radius:16px;box-shadow:0 0 0 6px #e6f8f0;">
          <rect x="12" y="12" width="30" height="30" rx="10" stroke="#0b9e6e" stroke-width="2.5" fill="#f8fcff"/>
          <path d="M19 27h16M27 19v16" stroke="#1aa2e2" stroke-width="2.5"/>
        </svg>
        <span style="font-size:1.19rem;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#0b9e6e;font-family:'Sora',sans-serif;">Analyse intelligente</span>
      </div>
      <div style="font-size:1.04rem;color:#4a6a8a;font-family:'Manrope',sans-serif;text-align:center;margin:12px 0 0 0;">Traitement et visualisation des données sanitaires pour une lecture claire des tendances et risques.</div>
    </div>
    <div class="card card-premium" style="background:linear-gradient(135deg,#fff7f8 60%,#fff3e0 100%);border-radius:36px;box-shadow:0 22px 70px 0 rgba(245,124,0,.13),0 0 0 10px #fff3e01a inset;border:2.5px solid #ffd6b8;align-items:center;gap:28px;animation:fadeUp .8s .2s cubic-bezier(.22,1,.36,1);position:relative;overflow:hidden;transition:box-shadow .22s,transform .22s;min-width:310px;max-width:400px;padding:38px 28px 32px 28px;">
      <span class="c-tag-float" style="position:absolute;top:18px;right:18px;background:linear-gradient(90deg,#fff7f8 60%,#fff3e0 100%);color:#f57c00;border:1.2px solid #ffd6b8;font-size:.89rem;font-weight:800;border-radius:999px;padding:6px 14px;box-shadow:0 2px 12px #fff3e080;z-index:2;">Pilotage</span>
      <div style="display:flex;align-items:center;gap:18px;margin-top:18px;">
        <svg width="54" height="54" viewBox="0 0 54 54" fill="none" style="background:linear-gradient(135deg,#fff7f8,#fff3e0);border-radius:16px;box-shadow:0 0 0 6px #fff3e0;">
          <polygon points="27,12 14,20 14,34 27,42 40,34 40,20" stroke="#f57c00" stroke-width="2.5" fill="#fff7f8"/>
          <path d="M23 30l4 4 8-8" stroke="#f57c00" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <animate attributeName="stroke-dasharray" values="0,24;24,0;0,24" dur="2.2s" repeatCount="indefinite"/>
          </path>
        </svg>
        <span style="font-size:1.19rem;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#f57c00;font-family:'Sora',sans-serif;">Réponse coordonnée</span>
      </div>
      <div style="font-size:1.04rem;color:#4a6a8a;font-family:'Manrope',sans-serif;text-align:center;margin:12px 0 0 0;">Alertes prioritaires et outils de pilotage pour mobiliser rapidement les ressources</div>
    </div>
  </div>
  <style>
    .cards-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 32px;
      margin: 36px 0 44px 0;
      justify-content: center;
      overflow-x: unset;
      padding-bottom: 0;
      scroll-behavior: unset;
    }
    .card {
      min-width: 220px;
      max-width: 340px;
      flex: 1 1 280px;
      background: linear-gradient(180deg,#fff 0%,#fafdff 100%);
      border-radius: 28px;
      box-shadow: 0 8px 32px rgba(10,95,171,.09);
      border: 1.5px solid #e0eaff;
      padding: 24px 14px 20px 14px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      transition: box-shadow .18s, transform .18s;
    }
    .card:hover {
      box-shadow: 0 16px 48px rgba(10,95,171,.16);
      transform: translateY(-4px) scale(1.03);
    }
    .c-title {
      font-size: 1.13rem;
      font-weight: 900;
      color: #0a2040;
      font-family: 'Sora',sans-serif;
      margin-bottom: 8px;
      letter-spacing: -.5px;
    }
    .c-copy {
      font-size: 0.97rem;
      color: #4a6a8a;
      font-family: 'Manrope',sans-serif;
      margin-bottom: 14px;
    }
    .c-tag {
      font-size: .89rem;
      font-weight: 800;
      border-radius: 999px;
      padding: 6px 14px;
      margin-top: auto;
      letter-spacing: 1.1px;
      background: #e6f2fd;
      color: #0a5fab;
      border: 1.2px solid #c8e2f5;
    }
    @media (max-width: 1100px) {
      .cards-grid { gap: 14px; }
      .card { min-width: 0; max-width: 99vw; padding: 12px 4px 12px 4px; }
    }
    @media (max-width: 900px) {
      .cards-grid { flex-direction: column; align-items: center; gap: 12px; }
      .card { width: 100%; min-width: 0; max-width: 600px; }
    }
    @media (max-width: 700px) {
      .cards-grid { flex-direction: column; gap: 10px; }
      .card { width: 100%; min-width: 0; max-width: 99vw; }
    }
  </style>
  </div>

  <!-- STEPS -->
  <div class="steps-wrap" style="margin-top:64px;">
    <div class="steps-title" style="font-size:1.5rem;letter-spacing:1.2px;">Du signal à la réponse</div>
    <div class="steps-sub" style="font-size:1.08rem;margin-bottom:38px;">Un processus structuré pour agir efficacement sur le terrain</div>
    <div class="steps-row" style="gap:38px;">
      <div class="step" style="animation:fadeUp .7s .1s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#0a5fab,#1aa2e2);box-shadow:0 6px 18px rgba(10,95,171,.26);font-size:1.2rem;">1</div>
        <div class="step-t">Signalement</div>
        <div class="step-c">Les autorités locales remontent les données de leur zone de santé.</div>
      </div>
      <div class="step-line"></div>
      <div class="step" style="animation:fadeUp .7s .2s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#0b9e6e,#3ec99a);box-shadow:0 6px 18px rgba(11,158,110,.18);font-size:1.2rem;">2</div>
        <div class="step-t">Analyse</div>
        <div class="step-c">La plateforme détecte les anomalies et produit des visualisations.</div>
      </div>
      <div class="step-line"></div>
      <div class="step" style="animation:fadeUp .7s .3s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#f57c00,#ffb74d);box-shadow:0 6px 18px rgba(245,124,0,.18);font-size:1.2rem;">3</div>
        <div class="step-t">Alerte</div>
        <div class="step-c">Les responsables sont notifiés avec les informations nécessaires.</div>
      </div>
      <div class="step-line"></div>
      <div class="step" style="animation:fadeUp .7s .4s cubic-bezier(.22,1,.36,1);">
        <div class="step-num" style="background:linear-gradient(135deg,#0a5fab,#1aa2e2);box-shadow:0 6px 18px rgba(10,95,171,.26);font-size:1.2rem;">4</div>
        <div class="step-t">Réponse</div>
        <div class="step-c">Coordination et mobilisation des ressources pour une intervention.</div>
      </div>
    </div>
  </div>

  <!-- DRAPEAU RDC -->
  <!-- IMPACT SECTION -->
  <div style="padding:110px 40px;background:linear-gradient(180deg,#eef6ff 0%,#f6fbff 46%,#edf6ff 100%);position:relative;overflow:hidden;border-top:1px solid rgba(26,162,226,.18);border-bottom:1px solid rgba(26,162,226,.14)">
    <div style="position:absolute;inset:0;background:radial-gradient(circle at 10% 18%,rgba(0,85,184,.09),transparent 20%),radial-gradient(circle at 88% 24%,rgba(252,209,22,.12),transparent 18%),radial-gradient(circle at 50% 100%,rgba(26,162,226,.08),transparent 28%);pointer-events:none"></div>
    <div style="max-width:1200px;margin:0 auto;position:relative;z-index:1">
      <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:26px;align-items:end;margin-bottom:44px">
        <div>
          <div style="display:inline-flex;align-items:center;gap:8px;padding:8px 15px;border-radius:999px;background:rgba(255,255,255,.8);border:1px solid rgba(10,95,171,.10);box-shadow:0 6px 18px rgba(10,60,120,.05);font-size:.72rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#0a5fab;font-family:'Sora',sans-serif;margin-bottom:18px">
            <span style="width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0055B8,#1aa2e2)"></span>
            Impact national
          </div>
          <div style="font-size:38px;font-weight:800;color:#0a2040;margin-bottom:14px;font-family:'Sora',sans-serif;letter-spacing:-1px;line-height:1.08">
            Notre Impact pour la <span style="background:linear-gradient(135deg,#0a5fab,#1aa2e2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">Sante Publique</span>
          </div>
          <div style="font-size:16px;color:#587691;font-family:'Manrope',sans-serif;line-height:1.8;max-width:650px">Engagement continu vers une couverture sanitaire universelle en RDC, avec des donnees fiables, des signaux precoces et une coordination rapide entre les acteurs sanitaires.</div>
        </div>
        <div style="justify-self:end;width:100%;max-width:360px;padding:22px 24px;border-radius:24px;background:linear-gradient(145deg,#0c4e91,#1176c0);box-shadow:0 20px 48px rgba(10,95,171,.22);border:1px solid rgba(255,255,255,.10)">
          <div style="font-size:.72rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:rgba(255,255,255,.7);font-family:'Sora',sans-serif;margin-bottom:10px">Vision terrain</div>
          <div style="font-size:1rem;font-weight:700;color:#ffffff;font-family:'Sora',sans-serif;line-height:1.5;margin-bottom:10px">Une veille epidemiologique utile, lisible et actionnable au niveau national.</div>
          <div style="font-size:.82rem;color:rgba(255,255,255,.76);line-height:1.65;font-family:'Manrope',sans-serif">Le systeme transforme les signaux sanitaires en decisions plus rapides pour les zones de sante, les provinces et la coordination centrale.</div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;margin-bottom:28px">
        <div style="position:relative;overflow:hidden;padding:28px 26px 24px;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#f6fbff 100%);border:1px solid rgba(10,95,171,.10);box-shadow:0 18px 40px rgba(10,60,120,.08)">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#0055B8,#1aa2e2)"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px">
            <div style="width:54px;height:54px;border-radius:18px;background:linear-gradient(135deg,rgba(0,85,184,.10),rgba(26,162,226,.16));display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0a5fab" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15h3"/><path d="M7 11h6"/><path d="M7 7h10"/></svg>
            </div>
            <div style="font-size:.68rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#84a7c5;font-family:'Sora',sans-serif">Couverture</div>
          </div>
          <div style="font-size:52px;font-weight:800;background:linear-gradient(135deg,#0055B8,#1aa2e2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif;line-height:1">2,400+</div>
          <div style="font-size:14px;color:#0a2040;font-family:'Sora',sans-serif;font-weight:800;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">Structures de sante</div>
          <div style="font-size:14px;color:#6a879f;font-family:'Manrope',sans-serif;line-height:1.7">Un reseau de structures suivies pour alimenter une surveillance nationale plus precise et continue.</div>
        </div>

        <div style="position:relative;overflow:hidden;padding:28px 26px 24px;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#fff7f8 100%);border:1px solid rgba(206,17,38,.10);box-shadow:0 18px 40px rgba(10,60,120,.08)">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#CE1126,#ff6b78)"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px">
            <div style="width:54px;height:54px;border-radius:18px;background:linear-gradient(135deg,rgba(206,17,38,.10),rgba(255,107,120,.14));display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#CE1126" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21c4.97-4.22 8-7.44 8-11a4 4 0 0 0-7-2.65A4 4 0 0 0 4 10c0 3.56 3.03 6.78 8 11Z"/></svg>
            </div>
            <div style="font-size:.68rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#d18a92;font-family:'Sora',sans-serif">Population</div>
          </div>
          <div style="font-size:52px;font-weight:800;background:linear-gradient(135deg,#CE1126,#ff6b78);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif;line-height:1">85M+</div>
          <div style="font-size:14px;color:#0a2040;font-family:'Sora',sans-serif;font-weight:800;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">Personnes surveillees</div>
          <div style="font-size:14px;color:#6a879f;font-family:'Manrope',sans-serif;line-height:1.7">Une capacite de suivi a grande echelle pour mieux anticiper les foyers et proteger les populations.</div>
        </div>

        <div style="position:relative;overflow:hidden;padding:28px 26px 24px;border-radius:26px;background:linear-gradient(180deg,#ffffff 0%,#fffdf4 100%);border:1px solid rgba(252,209,22,.18);box-shadow:0 18px 40px rgba(10,60,120,.08)">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#FCD116,#ffe47a)"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px">
            <div style="width:54px;height:54px;border-radius:18px;background:linear-gradient(135deg,rgba(252,209,22,.18),rgba(255,228,122,.18));display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.8)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c58d00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg>
            </div>
            <div style="font-size:.68rem;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:#c2a14d;font-family:'Sora',sans-serif">Qualite</div>
          </div>
          <div style="font-size:52px;font-weight:800;background:linear-gradient(135deg,#c58d00,#FCD116);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif;line-height:1">98%</div>
          <div style="font-size:14px;color:#0a2040;font-family:'Sora',sans-serif;font-weight:800;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">Donnees tracees</div>
          <div style="font-size:14px;color:#6a879f;font-family:'Manrope',sans-serif;line-height:1.7">Une circulation fiable de l'information sanitaire pour soutenir des analyses solides et des actions rapides.</div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1.08fr .92fr;gap:22px;align-items:stretch">
        <div style="padding:30px 30px 28px;border-radius:26px;background:linear-gradient(135deg,#ffffff 0%,#f7fbff 100%);border:1px solid rgba(10,95,171,.10);box-shadow:0 16px 36px rgba(10,60,120,.07)">
          <div style="font-size:.74rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#0a84d0;font-family:'Sora',sans-serif;margin-bottom:12px">Mission Sanitaire</div>
          <div style="font-size:24px;font-weight:800;color:#0a2040;font-family:'Sora',sans-serif;line-height:1.25;margin-bottom:12px">Transformer les donnees sanitaires en action concrete sur le terrain.</div>
          <div style="font-size:14px;color:#65839c;font-family:'Manrope',sans-serif;line-height:1.8;max-width:700px">Assurer une surveillance epidemiologique en temps reel, detecter rapidement les foyers de maladie et coordonner les interventions pour proteger la sante de tous les Congolais.</div>
        </div>
        <div style="padding:26px 26px 24px;border-radius:26px;background:linear-gradient(160deg,#0c4e91,#1581cb);border:1px solid rgba(255,255,255,.08);box-shadow:0 20px 42px rgba(10,95,171,.22)">
          <div style="font-size:.72rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:rgba(255,255,255,.68);font-family:'Sora',sans-serif;margin-bottom:10px">Lecture rapide</div>
          <div style="font-size:1.35rem;font-weight:800;color:#ffffff;font-family:'Sora',sans-serif;line-height:1.35;margin-bottom:16px">Une plateforme qui renforce la reactivite nationale face aux menaces sanitaires.</div>
          <div style="display:flex;gap:10px;flex-wrap:wrap">
            <span style="padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12);font-size:.72rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#ffffff">Surveillance continue</span>
            <span style="padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12);font-size:.72rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#ffffff">Coordination rapide</span>
            <span style="padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.12);font-size:.72rem;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#ffffff">Couverture nationale</span>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>
</body></html>"""

def sidebar_info():
    with st.sidebar:
        st.markdown(SHIELD_SIDEBAR, unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<p style="font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:#5a9ac0;font-weight:800;padding:0 8px;margin-bottom:8px">Parcours editorial</p>', unsafe_allow_html=True)

        if st.button("Perspective strategique", use_container_width=True, key="nav_mission"):
            st.switch_page("pages/notre_mission.py")
        if st.button("Impact national mesurable", use_container_width=True, key="nav_impact"):
            st.switch_page("pages/impact.py")
        if st.button("Mecanique intelligente", use_container_width=True, key="nav_fonc"):
            st.switch_page("pages/fonctionnement.py")
        if st.button("Alliance & coordination", use_container_width=True, key="nav_contact"):
            st.switch_page("pages/contact.py")

        st.markdown("---")
        st.markdown(
            '<p style="font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:#5a9ac0;font-weight:800;padding:0 8px;margin-bottom:8px">Liens officiels</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="expander-info">'
            '<a class="info-link" href="https://www.minisanterdc.cd" target="_blank">Minist&egrave;re de la Sant&eacute;</a>'
            '<a class="info-link" href="https://www.who.int/fr" target="_blank">OMS</a>'
            '<a class="info-link" href="https://www.unicef.org/drcongo" target="_blank">UNICEF RDC</a>'
            '<a class="info-link" href="https://africacdc.org" target="_blank">Africa CDC</a>'
            '</p>',
            unsafe_allow_html=True,
        )


def show_login(auth):
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = None



    # Bloc test AVANT le composant principal
    # Réduire la hauteur de l'iframe pour laisser de la place en bas
    components.html(HERO_HTML, height=1500, scrolling=False)

    # Bloc Accès rapide juste après le HERO
    st.markdown('''
    <div style="margin: 0 auto; max-width: 600px; padding: 0 0 28px 0;">
      <div style="background: rgba(255,255,255,0.98); border-radius: 32px; box-shadow: 0 8px 32px rgba(10,95,171,.09); border: 1.5px solid #e0eaff; padding: 36px 32px 28px 32px; position: relative; overflow: hidden; animation: fadeIn .8s; display: flex; flex-direction: column; align-items: center;">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" style="background:linear-gradient(135deg,#fafdff,#e6f2fd);border-radius:8px;"><rect x="4" y="4" width="24" height="24" rx="8" fill="#fafdff" stroke="#0a5fab" stroke-width="1.5"/><path d="M10 18v-2a6 6 0 1 1 12 0v2" stroke="#1aa2e2" stroke-width="1.5" fill="none"/><circle cx="16" cy="12" r="3" stroke="#1aa2e2" stroke-width="1.5" fill="#e6f2fd"/></svg>
          <span style="font-size: 1.45rem; font-weight: 900; color: #0a2040; font-family: Sora,sans-serif; letter-spacing: -.5px;">Accès rapide</span>
        </div>
        <div style="font-size: 1.04rem; color: #4a6a8a; font-family: Manrope,sans-serif; margin-bottom: 22px; text-align:center;">Connexion et inscription rapides pour les autorités sanitaires.</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    _, login_col, register_col, _ = st.columns([0.45, 1, 1, 0.45], gap="medium")
    with login_col:
      if st.button("Se connecter", use_container_width=True, key="open_login_middle"):
        st.session_state.auth_view = "login"
        st.switch_page("pages/auth.py")
    with register_col:
      if st.button("Créer un accès", use_container_width=True, key="open_register_middle"):
        st.session_state.auth_view = "register"
        st.switch_page("pages/auth.py")

    # Bloc IMPACT (rendu via components.html pour compatibilité totale)
    IMPACT_HTML = """
  <div class='impact-premium' style='margin-top:18px; padding: 0 0 54px 0; background: rgba(255,255,255,0.92); border-radius: 38px; box-shadow: 0 8px 40px rgba(26,162,226,.10), 0 0 0 6px #e6f2fd inset; border: 2px solid #e6f2fd; max-width: 1100px; margin-left: auto; margin-right: auto; position: relative; overflow: hidden; animation: fadeIn .8s;'>
    <div style="padding: 54px 36px 34px 36px; background: rgba(255,255,255,0.98); border-radius: 28px; box-shadow: 0 4px 18px rgba(26,162,226,.08), 0 0 0 4px #e6f2fd inset; max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 32px;">
      <div style="font-size:2.5rem; font-weight:900; color:#0a5fab; font-family:'Sora',sans-serif; letter-spacing:-1.1px; text-align:center; text-shadow:0 2px 12px #e6f2fd;">SAFE CONGO</div>
      <div style="font-size:1.18rem; color:#1a3d5c; font-family:'Manrope',sans-serif; text-align:center; max-width:700px; font-weight:600;">Le réseau digital qui anticipe, protège et connecte tous les acteurs de la santé publique en RDC.<br><span style='color:#1876c2;font-weight:800;'>Pour une veille, une action et une solidarité sans front</span></div>
      <div style="display: flex; flex-direction: row; justify-content: center; align-items: flex-start; gap: 48px; margin-top: 24px;">
        <div style="display:flex;flex-direction:column;align-items:center;gap:14px;min-width:160px;background:linear-gradient(135deg,#fafdff 60%,#e6f2fd 100%);border-radius:18px;padding:14px 8px 14px 8px;box-shadow:0 1px 8px #e6f2fd;">
          <svg width="56" height="56" viewBox="0 0 64 64" fill="none" style="background:linear-gradient(135deg,#e6f2fd,#fafdff);border-radius:14px;box-shadow:0 0 0 3px #e6f2fd;">
            <rect x="14" y="14" width="36" height="36" rx="12" fill="#fafdff"/>
            <path d="M32 20a12 12 0 1 1 0 24a12 12 0 1 1 0-24z" stroke="#0a5fab" stroke-width="2.2" fill="none"/>
            <circle cx="32" cy="32" r="4" fill="#1aa2e2"/>
          </svg>
          <div style="font-size:1.08rem;font-weight:800;color:#0a5fab;font-family:'Sora',sans-serif;letter-spacing:.4px;">Veille active</div>
          <div style="font-size:.97rem;color:#1876c2;font-family:'Manrope',sans-serif;text-align:center;max-width:160px;">Surveillance continue, détection précoce et analyse intelligente des signaux sanitaires.</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:14px;min-width:160px;background:linear-gradient(135deg,#f8fcff 60%,#e6f8f0 100%);border-radius:18px;padding:14px 8px 14px 8px;box-shadow:0 1px 8px #e6f8f0;">
          <svg width="56" height="56" viewBox="0 0 64 64" fill="none" style="background:linear-gradient(135deg,#e6f8f0,#f8fcff);border-radius:14px;box-shadow:0 0 0 3px #e6f8f0;">
            <rect x="14" y="14" width="36" height="36" rx="12" fill="#f8fcff"/>
            <path d="M32 24l8 8-8 8-8-8z" stroke="#1aa2e2" stroke-width="2.2" fill="#e6f8f0"/>
          </svg>
          <div style="font-size:1.08rem;font-weight:800;color:#1aa2e2;font-family:'Sora',sans-serif;letter-spacing:.4px;">Réponse rapide</div>
          <div style="font-size:.97rem;color:#1876c2;font-family:'Manrope',sans-serif;text-align:center;max-width:160px;">Mobilisation immédiate et coordination efficace pour chaque alerte sanitaire.</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:14px;min-width:160px;background:linear-gradient(135deg,#fafdff 60%,#e6f2fd 100%);border-radius:18px;padding:14px 8px 14px 8px;box-shadow:0 1px 8px #e6f2fd;">
          <svg width="56" height="56" viewBox="0 0 64 64" fill="none" style="background:linear-gradient(135deg,#e6f2fd,#fafdff);border-radius:14px;box-shadow:0 0 0 3px #e6f2fd;">
            <rect x="14" y="14" width="36" height="36" rx="12" fill="#fafdff"/>
            <path d="M24 40c0-8 16-8 16 0" stroke="#0a5fab" stroke-width="2.2" stroke-linecap="round" fill="none"/>
            <circle cx="32" cy="28" r="4" fill="#1aa2e2"/>
          </svg>
          <div style="font-size:1.08rem;font-weight:800;color:#0a5fab;font-family:'Sora',sans-serif;letter-spacing:.4px;">Collaboration enrichie</div>
          <div style="font-size:.97rem;color:#1876c2;font-family:'Manrope',sans-serif;text-align:center;max-width:160px;">Partage d’informations, entraide et synergie nationale pour une santé publique renforcée.</div>
        </div>
      </div>
    </div>
  </div>
  """
    components.html(IMPACT_HTML, height=1400, scrolling=False)






    current_view = st.session_state.auth_view
    if current_view is None:
        return

    st.switch_page("pages/auth.py")


def main():
    from utils.auth import AuthSystem


    if "user" not in st.session_state:
        st.session_state.user = None

    auth = AuthSystem()
    sidebar_info()

    user = st.session_state.user
    if user is None:
        show_login(auth)
        return

    # Logged-in routing
    if user["role"] == "admin":
        st.switch_page("pages/admin_dashboard.py")
    else:
        st.switch_page("pages/authority_dashboard.py")


def run_hidden_navigation() -> None:
    from utils.navigation import register_navigation_pages

    nav_pages = {
      "home": st.Page("pages/home.py", title="Accueil", url_path="", default=True),
        "auth": st.Page("pages/auth.py", title="Authentification", url_path="auth"),
        "mission": st.Page("pages/notre_mission.py", title="Notre mission", url_path="notre-mission"),
        "impact": st.Page("pages/impact.py", title="Impact", url_path="impact"),
        "fonctionnement": st.Page("pages/fonctionnement.py", title="Fonctionnement", url_path="fonctionnement"),
        "contact": st.Page("pages/contact.py", title="Contact", url_path="contact"),
        "admin_dashboard": st.Page("pages/admin_dashboard.py", title="Admin dashboard", url_path="admin-dashboard"),
        "admin_data_entry": st.Page("pages/admin_data_entry.py", title="Admin data entry", url_path="admin-data-entry"),
        "admin_users": st.Page("pages/admin_users.py", title="Admin users", url_path="admin-users"),
        "admin_panel": st.Page("pages/admin_panel.py", title="Admin panel", url_path="admin-panel"),
        "authority_dashboard": st.Page("pages/authority_dashboard.py", title="Authority dashboard", url_path="authority-dashboard"),
        "authority_alerts": st.Page("pages/authority_alerts.py", title="Authority alerts", url_path="authority-alerts"),
    }
    register_navigation_pages(nav_pages)
    st.session_state["_nav_pages"] = nav_pages
    current_page = st.navigation(list(nav_pages.values()), position="hidden")
    current_page.run()


if __name__ == "__main__":
    run_hidden_navigation()
