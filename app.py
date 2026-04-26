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
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
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
.stApp { background: linear-gradient(180deg, #eef6ff 0%, #e6f2fd 52%, #f0f8ff 100%) !important; }

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
  background: #ffffff;
  border-right: 1px solid #d0e8f8;
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

.expander-info {
    font-size: .82rem; line-height: 1.7;
    color: #4a6a8a !important;
}
.info-link {
    display: block; color: #1a6db5 !important;
    text-decoration: none; padding: 4px 0; font-size: .82rem;
    transition: color .2s;
}
.info-link:hover { color: #0a84d0 !important; }

/* ─── HERO SECTION ──────────────────────────────────────────────────────── */
.hero-wrapper {
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #040812 0%, #0a1a3e 40%, #071230 100%);
    border-radius: 28px; padding: 50px 40px 40px;
    margin-bottom: 36px;
    border: 1px solid rgba(0,212,255,.12);
    box-shadow: 0 0 60px rgba(0,102,204,.2), inset 0 0 60px rgba(0,0,0,.3);
    animation: fadeIn .8s ease-out;
}
.hero-bg-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
}
.hero-bg-radial {
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,102,204,.25) 0%, transparent 65%);
    pointer-events: none;
}
.hero-content { position: relative; z-index: 2; text-align: center; }

.hero-logo-container {
    display: inline-block; position: relative;
    margin-bottom: 24px;
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem; font-weight: 900;
    letter-spacing: 6px; text-transform: uppercase;
    background: linear-gradient(135deg, #ffffff 0%, #a8d4ff 40%, #00D4FF 70%, #0066CC 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: textGlow 3s ease-in-out infinite, slideInUp .8s ease-out .2s both;
    margin-bottom: 8px;
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
.global-footer {
  max-width: 1120px;
  margin: 18px auto 8px;
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fcff 0%, #eef6ff 100%);
  border: 1px solid rgba(71, 136, 194, .18);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.global-footer-left {
  color: #3b5677 !important;
  font-size: .82rem;
  font-weight: 700;
}
.global-footer-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.global-footer-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid #dbeafe;
  color: #0b4d95 !important;
  font-size: .68rem;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
}
@media (max-width: 900px) {
  .auth-feature-grid, .bridge-grid, .signal-strip, .entry-grid { grid-template-columns: 1fr; }
  .bridge-head { flex-direction: column; align-items: center; }
  .auth-shell-head, .auth-shell-statbox { grid-template-columns: 1fr; }
  .auth-topline { flex-direction: column; }
  .global-footer { justify-content: center; text-align: center; }
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
.section-head{margin:0 0 14px}
.section-label{font-size:.7rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#3a7ebf;padding-left:2px}
.cards-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:20px}
.card{background:#ffffff;border:1px solid #d0e8f8;border-radius:22px;padding:24px 22px;box-shadow:0 6px 26px rgba(10,60,120,.07);position:relative;overflow:hidden;transition:transform .28s,box-shadow .28s;animation:fadeUp .65s ease-out both}
.card:nth-child(1){animation-delay:.08s}.card:nth-child(2){animation-delay:.16s}.card:nth-child(3){animation-delay:.24s}
.card::after{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:22px 22px 0 0}
.c1::after{background:linear-gradient(90deg,#0a84d0,#38b6e8)}.c2::after{background:linear-gradient(90deg,#0b9e6e,#3ec99a)}.c3::after{background:linear-gradient(90deg,#f57c00,#ffb74d)}
.card:hover{transform:translateY(-6px);box-shadow:0 14px 38px rgba(10,60,120,.13)}
.c-ico{width:50px;height:50px;border-radius:15px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.ci-b{background:#e6f4fd}.ci-g{background:#e6f8f0}.ci-o{background:#fff3e0}
.c-title{font-family:'Sora',sans-serif;font-size:.98rem;font-weight:800;color:#0a2040;margin-bottom:8px}
.c-copy{font-size:.84rem;line-height:1.66;color:#5a7a99}
.c-tag{display:inline-block;margin-top:11px;padding:5px 10px;border-radius:999px;font-size:.67rem;font-weight:800;letter-spacing:.9px;text-transform:uppercase}
.ct-b{background:#e6f4fd;color:#1268b0}.ct-g{background:#e6f8f0;color:#0b7a52}.ct-o{background:#fff3e0;color:#c05800}

/* ── STEPS ──────────────────────────────────────── */
.steps-wrap{background:#ffffff;border:1px solid #d0e8f8;border-radius:22px;padding:28px 30px 30px;margin-bottom:20px;box-shadow:0 6px 26px rgba(10,60,120,.06);animation:fadeUp .7s ease-out .3s both}
.steps-title{font-family:'Sora',sans-serif;font-size:1.25rem;font-weight:800;color:#0a2c5a;text-align:center;margin-bottom:6px}
.steps-sub{font-size:.86rem;color:#7a9ab8;text-align:center;margin-bottom:26px}
.steps-row{display:flex;align-items:flex-start;gap:0}
.step{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center}
.step-line{flex:.42;height:2px;margin-top:23px;background:linear-gradient(90deg,#b8d8f0,#8ebfde)}
.step-num{width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2);color:#fff;font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:11px;box-shadow:0 6px 18px rgba(10,95,171,.26)}
.step-t{font-size:.9rem;font-weight:800;color:#0a2040;margin-bottom:5px}
.step-c{font-size:.78rem;color:#7a9ab8;line-height:1.56;max-width:150px}

/* ── FOOTER ─────────────────────────────────────── */
.footer{background:#ffffff;border:1px solid #d0e8f8;border-radius:20px;padding:20px 26px;margin-bottom:16px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;align-items:center;box-shadow:0 4px 18px rgba(10,60,120,.05);animation:fadeUp .8s ease-out .42s both}
.foot-brand{display:flex;align-items:center;gap:10px}
.foot-shield{width:26px;height:30px}
.foot-name{font-family:'Sora',sans-serif;font-size:.86rem;font-weight:800;letter-spacing:1.5px;color:#0a2c5a;text-transform:uppercase}
.foot-copy{font-size:.7rem;color:#8ab0cc;margin-top:2px}
.foot-links{display:flex;justify-content:center;gap:6px;flex-wrap:wrap}
.foot-link{padding:6px 10px;border-radius:999px;background:#eef7ff;border:1px solid #c8e2f5;font-size:.7rem;font-weight:700;color:#1a6db5;white-space:nowrap}
.foot-right{text-align:right}
.foot-partners{display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;margin-bottom:6px}
.foot-p{font-size:.67rem;font-weight:800;letter-spacing:.8px;text-transform:uppercase;color:#5a91c0}
.foot-year{font-size:.68rem;color:#b0c8da}

@media(max-width:900px){
  .hero-inner{grid-template-columns:1fr}.hero-visual{display:none}
  .cards-grid{grid-template-columns:1fr}
  .steps-row{flex-direction:column;align-items:center;gap:16px}.step-line{display:none}
  .footer{grid-template-columns:1fr;text-align:center}.foot-partners,.foot-right{justify-content:center;text-align:center}
  .nav-pills{display:none}.hero-title{font-size:2.4rem}.hero-title em{font-size:2rem}
}
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
  <div class="section-head"><div class="section-label">Capacites cles de la plateforme</div></div>
  <div class="cards-grid">
    <div class="card c1">
      <div class="c-ico ci-b">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0a84d0" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>
        </svg>
      </div>
      <div class="c-title">Detection rapide</div>
      <div class="c-copy">Identification precoce des signaux d'alerte epidemiologique sur l'ensemble du territoire national.</div>
      <span class="c-tag ct-b">Surveillance</span>
    </div>
    <div class="card c2">
      <div class="c-ico ci-g">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0b9e6e" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
        </svg>
      </div>
      <div class="c-title">Analyse intelligente</div>
      <div class="c-copy">Traitement et visualisation des donnees sanitaires pour une lecture claire des tendances et risques.</div>
      <span class="c-tag ct-g">Analyse</span>
    </div>
    <div class="card c3">
      <div class="c-ico ci-o">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f57c00" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2 4 6v6c0 5.5 3.5 10.7 8 13 4.5-2.3 8-7.5 8-13V6l-8-4Z"/><path d="m9 12 2 2 4-4"/>
        </svg>
      </div>
      <div class="c-title">Reponse coordonnee</div>
      <div class="c-copy">Alertes prioritaires et outils de pilotage pour mobiliser rapidement les ressources de sante publique.</div>
      <span class="c-tag ct-o">Pilotage</span>
    </div>
  </div>

  <!-- STEPS -->
  <div class="steps-wrap">
    <div class="steps-title">Du signal a la reponse</div>
    <div class="steps-sub">Un processus structure pour agir efficacement sur le terrain</div>
    <div class="steps-row">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-t">Signalement</div>
        <div class="step-c">Les autorites locales remontent les donnees de leur zone de sante.</div>
      </div>
      <div class="step-line"></div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-t">Analyse</div>
        <div class="step-c">La plateforme detecte les anomalies et produit des visualisations.</div>
      </div>
      <div class="step-line"></div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-t">Alerte</div>
        <div class="step-c">Les responsables sont notifies avec les informations necessaires.</div>
      </div>
      <div class="step-line"></div>
      <div class="step">
        <div class="step-num">4</div>
        <div class="step-t">Reponse</div>
        <div class="step-c">Coordination et mobilisation des ressources pour une intervention.</div>
      </div>
    </div>
  </div>

  <!-- DRAPEAU RDC -->
  <!-- IMPACT SECTION -->
  <div style="padding:100px 40px;background:linear-gradient(135deg,#eef6ff 0%,#f0f8ff 100%);border-top:2px solid rgba(26,162,226,.2);border-bottom:2px solid rgba(26,162,226,.2)">
    <div style="max-width:1200px;margin:0 auto">
      <div style="text-align:center;margin-bottom:80px">
        <div style="font-size:32px;font-weight:700;color:#0a5fab;margin-bottom:12px;font-family:'Sora',sans-serif;letter-spacing:1px">Notre Impact pour la Sante Publique</div>
        <div style="font-size:16px;color:#1aa2e2;font-family:'Manrope',sans-serif">Engagement continu vers une couverture sanitaire universelle en RDC</div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:40px;margin-bottom:60px">
        <div style="text-align:center;padding:30px;background:rgba(255,255,255,.8);border-radius:12px;border:1.5px solid rgba(10,85,184,.15);position:relative">
          <div style="font-size:48px;font-weight:700;background:linear-gradient(135deg,#0055B8,#1aa2e2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif">2,400+</div>
          <div style="font-size:14px;color:#666;font-family:'Manrope',sans-serif;font-weight:600;letter-spacing:0.5px">STRUCTURES DE SANTE</div>
        </div>
        <div style="text-align:center;padding:30px;background:rgba(255,255,255,.8);border-radius:12px;border:1.5px solid rgba(206,17,38,.15);position:relative">
          <div style="font-size:48px;font-weight:700;background:linear-gradient(135deg,#CE1126,#FF5555);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif">85M+</div>
          <div style="font-size:14px;color:#666;font-family:'Manrope',sans-serif;font-weight:600;letter-spacing:0.5px">PERSONNES SURVEILLEES</div>
        </div>
        <div style="text-align:center;padding:30px;background:rgba(255,255,255,.8);border-radius:12px;border:1.5px solid rgba(252,209,22,.15);position:relative">
          <div style="font-size:48px;font-weight:700;background:linear-gradient(135deg,#FCD116,#FFE55C);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;font-family:'Sora',sans-serif">98%</div>
          <div style="font-size:14px;color:#666;font-family:'Manrope',sans-serif;font-weight:600;letter-spacing:0.5px">DONNEES TRACEES</div>
        </div>
      </div>
      <div style="text-align:center;padding:40px;background:rgba(26,162,226,.08);border-radius:16px;border-left:4px solid #0055B8">
        <div style="font-size:18px;color:#0a5fab;font-family:'Sora',sans-serif;font-weight:600;margin-bottom:8px">Mission Sanitaire</div>
        <div style="font-size:14px;color:#666;font-family:'Manrope',sans-serif;line-height:1.6">Assurer une surveillance epidemiologique en temps reel, detecter rapidement les foyers de maladie et coordonner les interventions pour proteger la sante de tous les Congolais.</div>
      </div>
    </div>
  </div>

  <!-- CTA STRATEGIQUE AVANT FOOTER -->
  <div style="padding:80px 40px;position:relative;overflow:hidden;background:linear-gradient(135deg,rgba(10,85,184,.06) 0%,rgba(26,162,226,.04) 50%,rgba(10,85,184,.04) 100%)">
    <div style="position:absolute;top:0;left:0;right:0;bottom:0;background-image:radial-gradient(circle at 20% 30%,rgba(10,85,184,.08) 0%,transparent 40%),radial-gradient(circle at 80% 70%,rgba(26,162,226,.08) 0%,transparent 40%);pointer-events:none"></div>
    
    <div style="max-width:900px;margin:0 auto;position:relative;z-index:1;text-align:center">
      <!-- Indicateur top -->
      <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:24px;padding:9px 18px;border-radius:999px;background:#fff;border:1px solid #d4e8f5;box-shadow:0 3px 12px rgba(10,60,120,.08)">
        <div style="width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2);animation:pulse 2s ease-in-out infinite"></div>
        <span style="font-size:.75rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;color:#0a5fab;font-family:'Sora',sans-serif">Plateforme Active 24/7</span>
      </div>

      <!-- Titre principal -->
      <h2 style="font-size:2.8rem;font-weight:800;color:#0a2040;font-family:'Sora',sans-serif;margin:0 0 16px;line-height:1.15;letter-spacing:-0.5px">
        Rejoignez la <span style="background:linear-gradient(135deg,#0055B8,#1aa2e2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">surveillance nationale</span>
      </h2>

      <!-- Sous-titre -->
      <p style="font-size:1.05rem;color:#4a6d8a;line-height:1.8;max-width:650px;margin:0 auto 40px;font-family:'Manrope',sans-serif">
        Accédez à la plateforme pour surveiller, analyser et coordonner les réponses aux menaces sanitaires.
      </p>

      <!-- Confiance indicators -->
      <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:50px">
        <div style="display:flex;align-items:center;gap:7px;padding:10px 16px;border-radius:999px;background:#fff;border:1px solid #d4e8f5;font-size:.78rem;font-weight:700;color:#3a6080;box-shadow:0 2px 8px rgba(10,60,120,.06)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0a84d0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          2,400+ structures
        </div>
        <div style="display:flex;align-items:center;gap:7px;padding:10px 16px;border-radius:999px;background:#fff;border:1px solid #d4e8f5;font-size:.78rem;font-weight:700;color:#3a6080;box-shadow:0 2px 8px rgba(10,60,120,.06)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0a84d0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          85M+ personnes
        </div>
        <div style="display:flex;align-items:center;gap:7px;padding:10px 16px;border-radius:999px;background:#fff;border:1px solid #d4e8f5;font-size:.78rem;font-weight:700;color:#3a6080;box-shadow:0 2px 8px rgba(10,60,120,.06)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0a84d0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          98% données tracées
        </div>
      </div>

      <!-- Placeholder pour les boutons Streamlit (mis en Python) -->
      <div id="cta-buttons-python-zone" style="min-height:50px"></div>

      <!-- Trust line -->
      <div style="margin-top:48px;padding-top:32px;border-top:1px solid rgba(10,85,184,.12)">
        <p style="font-size:.82rem;color:#5a7a99;font-family:'Manrope',sans-serif;letter-spacing:.3px">
          ✓ Sécurité de grade gouvernemental &nbsp;•&nbsp; ✓ Support 24/7 &nbsp;•&nbsp; ✓ Zéro coût initial
        </p>
      </div>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <div class="foot-brand">
      <svg class="foot-shield" viewBox="0 0 110 128" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="ff1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38b6e8"/><stop offset="100%" stop-color="#0a5fab"/>
          </linearGradient>
        </defs>
        <path d="M55 8 L92 24 L92 58 Q92 92 55 116 Q18 92 18 58 L18 24 Z" fill="url(#ff1)"/>
        <rect x="46" y="64" width="18" height="5" rx="2" fill="white" opacity=".9"/>
        <rect x="52" y="57" width="6" height="19" rx="2" fill="white" opacity=".9"/>
      </svg>
      <div>
        <div class="foot-name">SAFE CONGO</div>
        <div class="foot-copy">Surveillance Epidemiologique Nationale</div>
      </div>
    </div>
    <div class="foot-links">
      <span class="foot-link">Notre Mission</span>
      <span class="foot-link">Impact</span>
      <span class="foot-link">Fonctionnement</span>
      <span class="foot-link">Contact</span>
    </div>
    <div class="foot-right">
      <div class="foot-partners">
        <span class="foot-p">RDC</span>
        <span class="foot-p">OMS</span>
        <span class="foot-p">UNICEF</span>
        <span class="foot-p">Africa CDC</span>
      </div>
      <div class="foot-year">&copy; 2026 SAFE CONGO &mdash; Tous droits reserves</div>
    </div>
  </div>

</div>
</body></html>"""

def sidebar_info():
    with st.sidebar:
        st.markdown(SHIELD_SIDEBAR, unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<p style="font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:#5a9ac0;font-weight:800;padding:0 8px;margin-bottom:8px">Navigation</p>', unsafe_allow_html=True)

        if st.button("&#9670; Notre Mission",    use_container_width=True, key="nav_mission"):
            st.switch_page("pages/notre_mission.py")
        if st.button("&#9650; Impact & Chiffres", use_container_width=True, key="nav_impact"):
            st.switch_page("pages/impact.py")
        if st.button("&#9654; Comment ca fonctionne", use_container_width=True, key="nav_fonc"):
            st.switch_page("pages/fonctionnement.py")
        if st.button("&#9993; Contact & Partenaires", use_container_width=True, key="nav_contact"):
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

    components.html(HERO_HTML, height=1720, scrolling=False)

    # ── CTA BUTTONS (strategic placement, styled to match hero CTA section) ─────
    st.markdown("""
<style>

.cta-section{
  background:linear-gradient(135deg,#f0f8ff 0%,#e6f2fd 45%,#eef6ff 100%);
  border:1px solid #c8dff0;border-radius:32px;
  padding:60px 48px 52px;text-align:center;position:relative;overflow:hidden;
  margin:0 auto 32px;max-width:860px;
}
.cta-section::before{
  content:'';position:absolute;inset:0;border-radius:32px;
  background:radial-gradient(ellipse at 50% -10%,rgba(10,95,171,.08),transparent 60%);
  pointer-events:none;
}
.cta-dots{
  position:absolute;inset:0;border-radius:32px;
  background-image:radial-gradient(circle,rgba(10,95,171,.07) 1px,transparent 1px);
  background-size:22px 22px;pointer-events:none;
}

.cta-badge{
  display:inline-flex;align-items:center;gap:7px;
  padding:7px 16px;border-radius:999px;
  background:rgba(10,95,171,.08);border:1px solid rgba(10,95,171,.18);
  font-size:.7rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;
  color:#0a5fab;margin-bottom:20px;
}
.cta-badge-dot{
  width:7px;height:7px;border-radius:50%;
  background:linear-gradient(135deg,#0a5fab,#1aa2e2);
  animation:ctaFloat 2s ease-in-out infinite;
}
.cta-headline{
  font-family:'Sora',sans-serif;font-size:2.4rem;font-weight:800;
  letter-spacing:-1px;line-height:1.1;
  color:#0a2040;margin-bottom:12px;
}
.cta-headline em{
  font-style:normal;
  background:linear-gradient(135deg,#0a5fab,#1aa2e2);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.cta-sub{
  font-size:.96rem;color:#4a6d8a;line-height:1.7;
  max-width:500px;margin:0 auto 36px;
}

.cta-trust{
  display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:36px;
}
.cta-trust-item{
  display:flex;align-items:center;gap:7px;
  padding:8px 14px;border-radius:999px;
  background:#fff;border:1px solid #d4e8f5;
  font-size:.76rem;font-weight:700;color:#3a6080;
  box-shadow:0 2px 8px rgba(10,60,120,.06);
}
.cta-trust-item svg{width:14px;height:14px;stroke:#0a84d0;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

.cta-buttons{
  display:flex;justify-content:center;align-items:center;gap:16px;flex-wrap:wrap;
}
.cta-btn-primary{
  display:inline-flex;align-items:center;gap:10px;
  padding:16px 36px;border-radius:16px;
  background:linear-gradient(135deg,#0a5fab,#1aa2e2);
  color:#fff;font-family:'Sora',sans-serif;font-weight:800;font-size:1rem;
  letter-spacing:.3px;text-decoration:none;cursor:pointer;
  border:none;outline:none;
  box-shadow:0 8px 28px rgba(10,95,171,.32);
  transition:all .25s cubic-bezier(.34,1.56,.64,1);
  animation:ctaGlow 3s ease-in-out infinite;
  position:relative;overflow:hidden;
}
.cta-btn-primary::after{
  content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.22),transparent);
  animation:ctaShimmer 3s 1s infinite;
}
.cta-btn-primary:hover{
  transform:translateY(-3px) scale(1.03);
  box-shadow:0 14px 36px rgba(10,95,171,.4);
}
.cta-btn-primary svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}

.cta-btn-outline{
  display:inline-flex;align-items:center;gap:10px;
  padding:15px 34px;border-radius:16px;
  background:#fff;
  color:#0a5fab;font-family:'Sora',sans-serif;font-weight:800;font-size:1rem;
  letter-spacing:.3px;text-decoration:none;cursor:pointer;
  border:2px solid #b8d8f0;outline:none;
  box-shadow:0 4px 18px rgba(10,60,120,.08);
  transition:all .25s cubic-bezier(.34,1.56,.64,1);
}
.cta-btn-outline:hover{
  border-color:#0a84d0;
  background:linear-gradient(135deg,#eef7ff,#e2f0fb);
  transform:translateY(-3px);
  box-shadow:0 10px 28px rgba(10,95,171,.16);
}
.cta-btn-outline svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}

.cta-or{
  font-size:.78rem;font-weight:700;color:#94afc8;letter-spacing:1.2px;
}

.cta-note{
  margin-top:28px;font-size:.76rem;color:#8aa8c0;
  display:flex;align-items:center;justify-content:center;gap:6px;
}
.cta-note svg{width:13px;height:13px;stroke:#8aa8c0;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
</style>

<div class="cta-section">
  <div class="cta-dots"></div>

  <div class="cta-badge">
    <div class="cta-badge-dot"></div>
    Plateforme nationale active
  </div>

  <div class="cta-headline">
    Prêt à rejoindre<br>la veille <em>sanitaire nationale</em> ?
  </div>
  <div class="cta-sub">
    Connectez-vous à votre espace ou créez un accès pour surveiller, analyser et agir sur les alertes épidémiologiques de votre province.
  </div>

  <div class="cta-trust">
    <div class="cta-trust-item">
      <svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3Z"/><path d="m9.5 12 1.8 1.8 3.2-3.6"/></svg>
      Accès sécurisé &amp; chiffré
    </div>
    <div class="cta-trust-item">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
      26 provinces couvertes
    </div>
    <div class="cta-trust-item">
      <svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
      Données en temps réel
    </div>
    <div class="cta-trust-item">
      <svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      Rôles et droits personnalisés
    </div>
  </div>

  <div class="cta-buttons" id="cta-btns-html">
    <!-- buttons injected by Streamlit below -->
  </div>

  <div class="cta-note">
    <svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.7-7 10-4-2.3-7-5.5-7-10V6l7-3Z"/></svg>
    Plateforme réservée aux agents de santé autorisés · République Démocratique du Congo
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CTA buttons (Streamlit handles routing) ────────────────────────
    st.markdown("""
<style>
/* Styles pour les nouveaux boutons CTA centrés */
[data-testid="column"] .stButton > button {
  border-radius: 14px !important;
  padding: 18px 40px !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 800 !important;
  font-size: 1.02rem !important;
  letter-spacing: .3px !important;
  width: 100% !important;
  transition: all .3s cubic-bezier(.34,1.56,.64,1) !important;
  min-height: 50px !important;
}

/* Bouton gauche - Connexion (bleu gradient) */
[data-testid="column"]:nth-of-type(2) .stButton > button {
  background: linear-gradient(135deg,#0a5fab 0%,#1aa2e2 100%) !important;
  color: #fff !important;
  border: 2px solid transparent !important;
  box-shadow: 0 10px 32px rgba(10,95,171,.3) !important;
}

[data-testid="column"]:nth-of-type(2) .stButton > button:hover {
  transform: translateY(-4px) !important;
  box-shadow: 0 16px 48px rgba(10,95,171,.42) !important;
  background: linear-gradient(135deg,#0a4fa0 0%,#1a94d0 100%) !important;
}

/* Bouton droite - S'inscrire (blanc avec bordure) */
[data-testid="column"]:nth-of-type(3) .stButton > button {
  background: #ffffff !important;
  color: #0a5fab !important;
  border: 2px solid #0a5fab !important;
  box-shadow: 0 8px 24px rgba(10,60,120,.12) !important;
}

[data-testid="column"]:nth-of-type(3) .stButton > button:hover {
  transform: translateY(-4px) !important;
  background: linear-gradient(135deg,#f0f8ff,#e8f3ff) !important;
  box-shadow: 0 14px 36px rgba(10,95,171,.22) !important;
  border-color: #1aa2e2 !important;
}

/* Override default stButton for CTA zone */
.cta-streamlit-btns .stButton > button {
  border-radius: 16px !important;
  padding: 15px 32px !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 800 !important;
  font-size: .97rem !important;
  letter-spacing: .3px !important;
  width: auto !important;
  min-width: 200px !important;
  transition: all .25s cubic-bezier(.34,1.56,.64,1) !important;
}
.cta-streamlit-btns [data-testid="column"]:first-child .stButton > button {
  background: linear-gradient(135deg,#0a5fab,#1aa2e2) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 8px 28px rgba(10,95,171,.32) !important;
}
.cta-streamlit-btns [data-testid="column"]:first-child .stButton > button:hover {
  transform: translateY(-3px) scale(1.03) !important;
  box-shadow: 0 14px 36px rgba(10,95,171,.42) !important;
}
.cta-streamlit-btns [data-testid="column"]:last-child .stButton > button {
  background: #ffffff !important;
  color: #0a5fab !important;
  border: 2px solid #b8d8f0 !important;
  box-shadow: 0 4px 18px rgba(10,60,120,.08) !important;
}
.cta-streamlit-btns [data-testid="column"]:last-child .stButton > button:hover {
  border-color: #0a84d0 !important;
  background: linear-gradient(135deg,#eef7ff,#e2f0fb) !important;
  transform: translateY(-3px) !important;
  box-shadow: 0 10px 28px rgba(10,95,171,.18) !important;
}
</style>
""", unsafe_allow_html=True)

    _, col_cta, _ = st.columns([0.8, 2.4, 0.8])
    with col_cta:
        st.markdown("""
<style>
.cta-hero-section {
  background: linear-gradient(135deg, rgba(10,85,184,.08) 0%, rgba(26,162,226,.04) 50%, rgba(10,85,184,.05) 100%);
  border: 2px solid rgba(10,85,184,.15);
  border-radius: 28px;
  padding: 50px 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  margin: 30px 0;
}
.cta-hero-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, rgba(10,85,184,.08), transparent 70%);
  pointer-events: none;
}
.cta-hero-title {
  font-size: 26px;
  font-weight: 800;
  color: #0a5fab;
  font-family: 'Sora', sans-serif;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
  position: relative;
  z-index: 1;
}
.cta-hero-title em {
  font-style: normal;
  color: #1aa2e2;
}
.cta-hero-desc {
  font-size: 14px;
  color: #4a6d8a;
  font-family: 'Manrope', sans-serif;
  line-height: 1.8;
  margin-bottom: 32px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  position: relative;
  z-index: 1;
}
.cta-hero-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
}
</style>

<div class="cta-hero-section">
  <div class="cta-hero-title">Rejoignez la <em>surveillance nationale</em></div>
  <div class="cta-hero-desc">Accédez à la plateforme pour surveiller, analyser et coordonner les réponses aux menaces sanitaires.</div>
  <div class="cta-hero-buttons" id="cta-buttons-container">
    <!-- Boutons injectés ci-dessous -->
  </div>
</div>
""", unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        
        b_left, b_right = st.columns(2, gap="small")
        with b_left:
            if st.button("🔐 Se connecter", use_container_width=True, key="open_login_new", help="Accès aux agents autorisés"):
                st.session_state.auth_view = "login"
                st.switch_page("pages/auth.py")
        with b_right:
            if st.button("✦ Créer un accès", use_container_width=True, key="open_register_new", help="Inscription pour autorités"):
                st.session_state.auth_view = "register"
                st.switch_page("pages/auth.py")

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


if __name__ == "__main__":
    main()
