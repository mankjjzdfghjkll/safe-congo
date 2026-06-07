import re
import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.navigation import switch_to_home_page
from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND, render_sidebar_active_button


ADMIN_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
html { zoom: 1 !important; }
#MainMenu,footer{visibility:hidden}
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(11,77,149,.16)!important;border-radius:14px!important;box-shadow:0 10px 28px rgba(15,23,42,.12)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important}
[data-testid="stSidebarNav"]{display:none}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-1200px 0}100%{background-position:1200px 0}}
@keyframes floatLift{0%{transform:translateY(0)}100%{transform:translateY(-4px)}}
@keyframes pulseGlow{0%,100%{box-shadow:0 12px 28px rgba(15,23,42,.06)}50%{box-shadow:0 18px 34px rgba(10,95,171,.12)}}
.stApp{background:linear-gradient(180deg,#eef6ff 0%,#e7f2fc 48%,#f4f9ff 100%)!important}
[data-testid="stAppViewContainer"] .main .block-container{max-width:1280px!important;padding-top:1.5rem!important;padding-bottom:1.5rem!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#f4f9ff 100%)!important;border-right:1px solid rgba(176,208,233,.55)!important;box-shadow:2px 0 12px rgba(10,60,120,.04)!important}
[data-testid="stSidebar"] *{color:#0f2542!important}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{
background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;
color:#ffffff!important;
border:0!important;
border-radius:12px!important;
padding:10px 14px!important;
font-weight:800!important;
font-size:.82rem!important;
letter-spacing:.2px!important;
box-shadow:0 8px 20px rgba(10,95,171,.22)!important;
transition:transform .2s ease,box-shadow .2s ease,filter .2s ease!important;
}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{
transform:translateY(-2px)!important;
box-shadow:0 12px 24px rgba(10,95,171,.28)!important;
filter:saturate(1.03)!important;
}
.stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible,.stDownloadButton>button:focus-visible{
box-shadow:0 0 0 3px rgba(26,162,226,.16),0 12px 24px rgba(10,95,171,.28)!important;
}
.stButton>button:disabled,.stFormSubmitButton>button:disabled,.stDownloadButton>button:disabled{
background:linear-gradient(135deg,#90b5d7,#b7d3ea)!important;
color:#eef6ff!important;
box-shadow:none!important;
}
.admin-sidebar-user-card{margin:10px 6px 12px;padding:13px 13px 11px;border-radius:16px;background:linear-gradient(180deg,#ffffff 0%,#eef7ff 100%);border:1px solid #d8e9f6;box-shadow:0 10px 22px rgba(10,60,120,.08)}
.admin-sidebar-role{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:rgba(10,95,171,.08);color:#0a5fab!important;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase}
.admin-sidebar-role::before{content:'';width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#0a5fab,#1aa2e2)}
.admin-sidebar-name{margin-top:10px;font-family:'Sora',sans-serif;font-size:.95rem;line-height:1.35;color:#0f2542!important}
.admin-sidebar-meta{margin-top:6px;font-size:.76rem;line-height:1.55;color:#67839c!important}
.admin-sidebar-separator{height:1px;background:linear-gradient(90deg,rgba(200,223,240,0),rgba(200,223,240,1),rgba(200,223,240,0));margin:8px 0 8px}
.admin-shell{max-width:1280px;margin:0 auto;padding-bottom:0}
.admin-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#0b4d95 0%,#0f75cc 58%,#48acef 100%);border-radius:24px;padding:24px 24px 20px;box-shadow:0 18px 40px rgba(11,77,149,.18);margin:0 0 16px;animation:fadeIn .45s ease-out}
.admin-hero .admin-eyebrow,.admin-hero .admin-title,.admin-hero .admin-subtitle,.admin-hero .admin-chip,.admin-hero .admin-chip *{color:#ffffff!important}
.admin-hero::before{content:'';position:absolute;inset:auto -10% -58% auto;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%)}
.admin-hero-top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.admin-eyebrow{display:inline-flex;align-items:center;gap:8px;padding:6px 11px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.26);font-size:.64rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#fff}
.admin-eyebrow-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#fff,#cce8ff)}
.admin-hero-actions{display:flex;justify-content:flex-end;align-items:flex-start;height:100%}
.admin-bell-wrap{display:grid;gap:8px;width:100%;max-width:320px;padding-top:4px;margin-left:auto}
.admin-bell-panel{position:relative;overflow:hidden;border-radius:20px;padding:12px 12px 10px;background:linear-gradient(145deg,#0b4d95 0%,#1376c8 55%,#25a8e0 100%);border:1px solid rgba(255,255,255,.18);box-shadow:0 18px 36px rgba(15,87,129,.22),inset 0 1px 0 rgba(255,255,255,.14)}
.admin-bell-panel::before{content:'';position:absolute;inset:-12% -10% auto auto;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.38),transparent 66%)}
.admin-bell-panel::after{content:'';position:absolute;inset:auto auto -30% -18%;width:90px;height:90px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.1),transparent 70%)}
.admin-bell-head{position:relative;display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
.admin-bell-icon-wrap{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:11px;background:linear-gradient(135deg,#0b4d95,#1677c8);border:1px solid rgba(11,77,149,.25);box-shadow:0 8px 16px rgba(11,77,149,.22);flex:none}
.admin-bell-kicker{display:inline-flex;align-items:center;gap:8px;font-size:.62rem;font-weight:900;letter-spacing:1.35px;text-transform:uppercase;color:#ffffff}
.admin-bell-count{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;padding:0 9px;border-radius:999px;font:900 .76rem 'Sora',sans-serif;transition:all .3s ease}
.admin-bell-count.has-unread{background:linear-gradient(135deg,#ff4d4d 0%,#f97316 100%);color:#fff;box-shadow:0 0 0 0 rgba(255,77,77,.55);animation:pulseRed 2.2s ease-in-out infinite}
.admin-bell-count.no-unread{background:rgba(255,255,255,.96);color:#0f172a;box-shadow:0 4px 12px rgba(15,87,129,.12)}
.admin-bell-divider{height:1px;background:linear-gradient(90deg,rgba(255,255,255,.34),rgba(255,255,255,.1));margin:0 0 7px}
.admin-bell-note{position:relative;font-size:.72rem;line-height:1.45;color:rgba(255,255,255,.92);margin-bottom:5px}
.admin-bell-note strong{color:#ffffff;font-weight:900}
.admin-bell-status-row{display:flex;align-items:center;gap:6px;font-size:.61rem;font-weight:700;letter-spacing:.35px;color:rgba(255,255,255,.84);margin-bottom:8px}
.admin-bell-status-dot{width:6px;height:6px;border-radius:50%;flex:none;background:#4ade80;box-shadow:0 0 0 3px rgba(74,222,128,.22)}
[data-testid="stPopover"],[data-testid="stPopover"]>div{width:100%}
[data-testid="stPopover"] button[kind="secondary"],.admin-bell-wrap .stButton>button{position:relative;width:100%!important;background:linear-gradient(135deg,#0b4d95 0%,#1376c8 55%,#25a8e0 100%)!important;color:#ffffff!important;border:1px solid rgba(10,95,171,.28)!important;border-radius:16px!important;min-height:56px!important;padding:10px 14px!important;font-weight:900!important;font-size:.86rem!important;line-height:1.06!important;text-align:left!important;justify-content:flex-start!important;box-shadow:0 14px 26px rgba(15,87,129,.22),inset 0 1px 0 rgba(255,255,255,.18)!important;transition:all .22s cubic-bezier(.4,0,.2,1)!important;letter-spacing:.05px!important}
[data-testid="stPopover"] button[kind="secondary"]::after,.admin-bell-wrap .stButton>button::after{content:'Centre de notifications';display:block;font-size:.6rem;font-weight:700;letter-spacing:.28px;color:rgba(255,255,255,.82);margin-top:4px}
[data-testid="stPopover"] button[kind="secondary"]:hover,.admin-bell-wrap .stButton>button:hover{transform:translateY(-1px)!important;background:linear-gradient(135deg,#0d5aa7 0%,#1684d6 55%,#2fc0f3 100%)!important;box-shadow:0 18px 30px rgba(15,87,129,.24),inset 0 1px 0 rgba(255,255,255,.2)!important;color:#ffffff!important}
[data-testid="stPopover"] button[kind="secondary"]:active,.admin-bell-wrap .stButton>button:active{transform:translateY(-1px)!important}
.admin-bell-chip{display:inline-flex;align-items:center;justify-content:center;min-width:24px;height:24px;padding:0 7px;border-radius:999px;background:#ffffff;color:#0b4d95;font:800 .74rem Sora,sans-serif}
.admin-inbox-shell{padding:2px 0 0}
.admin-inbox-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:0 0 10px;border-bottom:1px solid #e4edf7;margin-bottom:12px}
.admin-inbox-title{font-family:'Sora',sans-serif;font-size:.98rem;font-weight:800;color:#0f3f73;margin:0 0 4px}
.admin-inbox-subtitle{font-size:.74rem;color:#718ea4;line-height:1.52;margin:0;max-width:280px}
.admin-inbox-stats{display:flex;flex-wrap:wrap;justify-content:flex-end;align-items:flex-start;gap:6px;flex-shrink:0}
.admin-inbox-stat{display:inline-flex;align-items:center;gap:5px;padding:5px 9px;border-radius:999px;font-size:.65rem;font-weight:800;letter-spacing:.35px;border:1px solid transparent}
.admin-inbox-stat.total{background:#eef6ff;border-color:#d0e4f7;color:#0a5fab}
.admin-inbox-stat.unread{background:#eefcf5;border-color:#c8f0e0;color:#047857}
.admin-inbox-item{padding:12px 14px;border-radius:16px;border:1px solid rgba(180,208,232,.5);border-left-width:4px;border-left-color:#22c55e;background:linear-gradient(165deg,#ffffff 0%,#f9fbff 100%);box-shadow:0 6px 16px rgba(15,23,42,.05);transition:transform .18s ease,box-shadow .18s ease}
.admin-inbox-item:hover{transform:translateX(3px);box-shadow:0 10px 22px rgba(15,23,42,.09)}
.admin-inbox-item.niveau-critique{border-left-color:#ef4444}
.admin-inbox-item.niveau-haute{border-left-color:#f97316}
.admin-inbox-item.niveau-moderee{border-left-color:#f59e0b}
.admin-inbox-item.niveau-faible{border-left-color:#22c55e}
.admin-inbox-item.unread.niveau-critique{background:linear-gradient(165deg,#fff8f7 0%,#fffdfd 100%);border-color:rgba(239,68,68,.22);border-left-color:#ef4444}
.admin-inbox-item.unread.niveau-haute{background:linear-gradient(165deg,#fff9f5 0%,#fffefb 100%);border-color:rgba(249,115,22,.2);border-left-color:#f97316}
.admin-inbox-item.unread.niveau-moderee{background:linear-gradient(165deg,#fffef3 0%,#fffffe 100%);border-color:rgba(245,158,11,.2);border-left-color:#f59e0b}
.admin-inbox-item.unread.niveau-faible{background:linear-gradient(165deg,#f0fdf4 0%,#fafdfb 100%);border-color:rgba(34,197,94,.2);border-left-color:#22c55e}
.admin-inbox-item-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px}
.admin-inbox-item-left{display:flex;align-items:flex-start;gap:8px;flex:1;min-width:0}
.admin-inbox-dot{width:8px;height:8px;border-radius:50%;flex:none;margin-top:6px;animation:dotBlink 2.4s ease-in-out infinite}
.admin-inbox-dot.critique{background:#ef4444;box-shadow:0 0 0 3px rgba(239,68,68,.18)}
.admin-inbox-dot.haute{background:#f97316;box-shadow:0 0 0 3px rgba(249,115,22,.18)}
.admin-inbox-dot.moderee{background:#f59e0b;box-shadow:0 0 0 3px rgba(245,158,11,.18)}
.admin-inbox-dot.faible{background:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.15)}
.admin-inbox-dot{background:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.15)}
.admin-inbox-item-title-col{flex:1;min-width:0}
.admin-inbox-level-badge{display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:999px;font-size:.57rem;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin-bottom:5px;border:1px solid transparent}
.admin-inbox-level-badge.critique{background:rgba(239,68,68,.1);color:#b91c1c;border-color:rgba(239,68,68,.2)}
.admin-inbox-level-badge.haute{background:rgba(249,115,22,.1);color:#c2410c;border-color:rgba(249,115,22,.2)}
.admin-inbox-level-badge.moderee{background:rgba(245,158,11,.1);color:#92400e;border-color:rgba(245,158,11,.2)}
.admin-inbox-level-badge.faible{background:rgba(34,197,94,.1);color:#15803d;border-color:rgba(34,197,94,.2)}
.admin-inbox-item-title{font-size:.82rem;font-weight:900;color:#0f3f73;line-height:1.42;overflow-wrap:anywhere;word-break:break-word}
.admin-inbox-item.unread .admin-inbox-item-title{color:#0a4d8a}
.admin-inbox-date{font-size:.65rem;color:#96afc4;white-space:nowrap;flex-shrink:0;margin-top:2px}
.admin-inbox-text{font-size:.76rem;color:#587391;line-height:1.62;overflow-wrap:anywhere;word-break:break-word;padding-left:16px;margin-top:5px}
.admin-inbox-action-sep{height:1px;background:#edf2f8;margin:8px 0 7px}
.admin-inbox-actions .stButton>button{min-height:32px!important;padding:6px 10px!important;font-size:.7rem!important;font-weight:700!important;border-radius:9px!important}
.admin-inbox-more{margin-top:8px;font-size:.7rem;color:#7c94ab;text-align:center;padding:6px 8px;border-radius:10px;background:rgba(230,240,250,.5)}
.admin-title{font-family:'Sora',sans-serif;font-size:2.2rem;line-height:1.02;color:#fff;margin:16px 0 10px;max-width:760px}
.admin-subtitle{max-width:760px;color:rgba(255,255,255,.86);font-size:.97rem;line-height:1.74;margin:0}
.admin-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.admin-chip{padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);font-size:.7rem;font-weight:700;color:#fff;animation:fadeIn .7s ease-out both;transition:transform .2s ease,background .2s ease}
.admin-chip:hover{transform:translateY(-2px);background:rgba(255,255,255,.18)}
.admin-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px;margin:0 0 24px}
.admin-kpi-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e2edf8;border-radius:24px;padding:20px 18px;box-shadow:0 12px 28px rgba(15,23,42,.06);position:relative;overflow:hidden;animation:fadeIn .55s ease-out;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.admin-kpi-card:hover{transform:translateY(-4px);box-shadow:0 20px 34px rgba(10,95,171,.10);border-color:#cfe3f4}
.admin-kpi-card::before{content:'';position:absolute;left:20px;right:20px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent-soft))}
.admin-kpi-label{font-size:.72rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#6b7f99;margin-bottom:10px}
.admin-kpi-value{font-family:'Sora',sans-serif;font-size:2rem;line-height:1;color:#0f172a;margin-bottom:8px}
.admin-kpi-delta{display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:999px;background:var(--pill);font-size:.74rem;font-weight:700;color:var(--accent)}
.admin-kpi-copy{margin-top:10px;font-size:.84rem;line-height:1.6;color:#6b7f99}
.admin-section-label{display:flex;align-items:center;gap:10px;margin:22px 0 12px;font-size:.68rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#8aa0b8}
.admin-section-label::after{content:'';flex:1;height:1px;background:#dbe8f5}
.admin-panel{background:linear-gradient(180deg,rgba(255,255,255,.96) 0%,rgba(247,251,255,.96) 100%);border:1px solid rgba(180,208,232,.55);border-radius:18px;padding:16px;box-shadow:0 10px 24px rgba(15,23,42,.05);margin-bottom:14px;animation:fadeIn .6s ease-out;backdrop-filter:blur(8px);transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.admin-panel:hover{transform:translateY(-3px);box-shadow:0 18px 30px rgba(10,95,171,.08);border-color:rgba(135,186,226,.75)}
.admin-panel-title{font-family:'Sora',sans-serif;font-size:.98rem;color:#0f3f73;margin:0 0 12px}
.admin-note{font-size:.79rem;line-height:1.56;color:#62758b;margin:0}
.admin-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.admin-grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.admin-mini-card{padding:12px;border-radius:12px;background:linear-gradient(180deg,#ffffff,#f4f9ff);border:1px solid #e1edf9;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.admin-mini-card:hover{transform:translateY(-3px);box-shadow:0 12px 22px rgba(10,95,171,.08);border-color:#cfe3f4}
.admin-mini-card h4{margin:0 0 6px;font-size:.84rem;color:#103d6f}
.admin-mini-card p{margin:0;color:#6b7f99;font-size:.79rem;line-height:1.56}
.admin-highlight{padding:12px 14px;border-radius:14px;background:linear-gradient(135deg,#eff7ff,#e7f2ff);border:1px solid rgba(160,200,232,.6);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.admin-highlight:hover{transform:translateY(-3px);box-shadow:0 12px 22px rgba(10,95,171,.08);border-color:rgba(120,182,226,.65)}
.admin-highlight strong{display:block;color:#0a4a8a;font-size:.9rem;margin-bottom:3px}
.admin-highlight span{font-size:.79rem;line-height:1.56;color:#62758b}
.admin-support-copy{margin:-2px 0 12px;font-size:.8rem;line-height:1.62;color:#68819a}
.admin-empty-state{padding:14px;border-radius:14px;background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border:1px dashed #c8dff0;color:#5f7992;font-size:.79rem;line-height:1.58}
.admin-form-hero{display:grid;grid-template-columns:1.15fr .85fr;gap:12px;margin-bottom:12px}
.admin-form-banner{padding:12px 14px;border-radius:12px;background:linear-gradient(135deg,#f8fbff 0%,#edf6ff 48%,#e5f3ff 100%);border:1px solid rgba(173,207,236,.40);box-shadow:inset 0 1px 0 rgba(255,255,255,.4);transition:transform .2s ease,box-shadow .2s ease}
.admin-form-banner:hover{transform:translateY(-2px);box-shadow:0 10px 18px rgba(10,95,171,.08),inset 0 1px 0 rgba(255,255,255,.4)}
.admin-form-banner strong{display:block;font-family:'Sora',sans-serif;font-size:.9rem;color:#0d447d;margin-bottom:4px}
.admin-form-banner span{display:block;font-size:.79rem;line-height:1.56;color:#617991}
.admin-form-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.admin-form-stat{padding:10px;border-radius:12px;background:linear-gradient(180deg,#ffffff 0%,#f6fbff 100%);border:1px solid #dcebf8;box-shadow:0 4px 10px rgba(15,23,42,.02)}
.admin-form-stat strong{display:block;font-family:'Sora',sans-serif;font-size:.9rem;color:#0b4d95;margin-bottom:3px}
.admin-form-stat span{display:block;font-size:.68rem;letter-spacing:1px;text-transform:uppercase;color:#6e86a0;font-weight:800}
.admin-form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.admin-form-section{padding:12px;border-radius:12px;background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%);border:1px solid #e0edf8}
.admin-form-section h4{margin:0 0 4px;font-family:'Sora',sans-serif;font-size:.84rem;color:#103d6f}
.admin-form-section p{margin:0 0 8px;font-size:.79rem;line-height:1.56;color:#6b7f99}
.admin-form-note{margin-top:8px;padding:10px 12px;border-radius:10px;background:rgba(10,95,171,.06);border:1px solid rgba(10,95,171,.08);font-size:.74rem;line-height:1.56;color:#5f7690}
.admin-form-actions{margin-top:8px;padding-top:8px;border-top:1px solid #e2edf8}
.admin-form-actions [data-testid="stButton"]{margin-top:0}
[data-testid="stExpander"]{border:1px solid rgba(180,208,232,.65)!important;border-radius:18px!important;background:linear-gradient(180deg,rgba(255,255,255,.96) 0%,rgba(247,251,255,.96) 100%)!important;box-shadow:0 10px 24px rgba(15,23,42,.05)!important;overflow:hidden!important}
[data-testid="stExpander"] details{border-radius:18px!important}
[data-testid="stExpander"] summary{padding-top:.15rem!important;padding-bottom:.15rem!important}
.admin-action-card{padding:14px;border-radius:16px;background:linear-gradient(180deg,#ffffff 0%,#f5faff 100%);border:1px solid #ddebf8;box-shadow:0 10px 22px rgba(15,23,42,.04)}
.admin-action-kicker{font-size:.68rem;font-weight:800;letter-spacing:1.2px;text-transform:uppercase;color:#6b87a1;margin-bottom:6px}
.admin-action-card h4{margin:0 0 8px;font-family:'Sora',sans-serif;font-size:.92rem;color:#0f3f73}
.admin-action-card p{margin:0 0 12px;color:#667f98;font-size:.79rem;line-height:1.56}
.admin-info-list{display:grid;gap:10px}
.admin-info-item{padding:10px 12px;border-radius:12px;background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%);border:1px solid #e0edf8}
.admin-info-item strong{display:block;font-size:.68rem;letter-spacing:1px;text-transform:uppercase;color:#0a5fab;margin-bottom:4px}
.admin-info-item span{display:block;font-size:.79rem;line-height:1.56;color:#647c95}
[data-testid="stDataFrame"]{border-radius:10px!important;overflow:hidden!important;border:1px solid #e2edf8!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#f2f8ff;border:1px solid #d7e7f6;border-radius:999px;padding:9px 14px;font-weight:700;color:#0f4d8c;font-size:.8rem}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important}
.stTextInput>div>div>input,.stSelectbox>div>div,.stNumberInput>div>div>input,.stTextArea textarea{border-radius:10px!important;border:1px solid #d6e6f5!important;font-size:.82rem!important}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{border-color:#0a5fab!important;box-shadow:0 0 0 2px rgba(26,162,226,.08)!important}
@media (max-width: 1100px){.admin-grid-3{grid-template-columns:repeat(2,minmax(0,1fr))}.admin-grid-2{grid-template-columns:1fr}.admin-hero-top{flex-direction:column}.admin-hero-actions{width:100%}.admin-bell-wrap{max-width:none;margin-left:0}.admin-shell{padding:0 .35rem}}
@media (max-width: 720px){.admin-kpi-grid,.admin-grid-3,.admin-form-grid,.admin-form-stats{grid-template-columns:1fr}.admin-hero{padding:18px 16px}.admin-title{font-size:1.6rem}.admin-panel{padding:12px}.admin-form-hero{grid-template-columns:1fr}.admin-chip-row{gap:6px}.admin-bell-panel{padding:10px}.admin-bell-note{font-size:.68rem;line-height:1.4}}
@media (max-width: 900px){div[data-testid="stHorizontalBlock"]{gap:.8rem!important}div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}}
@media (max-width: 560px){[data-testid="stAppViewContainer"] .main .block-container{padding-top:1rem!important;padding-bottom:1rem!important;padding-left:.55rem!important;padding-right:.55rem!important}.admin-hero{border-radius:18px;padding:16px 12px}.admin-title{font-size:1.35rem;line-height:1.14}.admin-subtitle{font-size:.84rem;line-height:1.58}.admin-kpi-value{font-size:1.55rem}.admin-panel-title{font-size:.9rem}.admin-sidebar-user-card{margin:8px 4px 10px;padding:11px}.admin-bell-wrap [data-testid="stPopover"] button[kind="secondary"],.admin-bell-wrap .stButton>button{min-height:50px!important;font-size:.8rem!important;padding:8px 12px!important}}
</style>
"""


def apply_admin_theme() -> None:
    st.markdown(ADMIN_THEME, unsafe_allow_html=True)


def render_admin_sidebar(user: dict, active_item: int, show_logo: bool = True) -> None:
    with st.sidebar:
        # Affiche toujours le logo et le bloc utilisateur
        st.markdown(PUBLIC_SIDEBAR_BRAND, unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="admin-sidebar-user-card">
  <div class="admin-sidebar-role">Administrateur</div>
  <div class="admin-sidebar-name">{user['full_name']}</div>
  <div class="admin-sidebar-meta">Console de supervision SAFE CONGO<br/>Acces central aux operations et a la gouvernance.</div>
</div>
<div class="admin-sidebar-separator"></div>
""",
            unsafe_allow_html=True,
        )
        render_sidebar_active_button(active_item)
        page_suffix = f"_{active_item}" if active_item is not None else ""
        if st.button("  Tableau de bord executif", use_container_width=True, key=f"sidebar_dashboard_btn{page_suffix}"):
            st.switch_page("pages/admin_dashboard.py")
        if st.button("  Saisie & intelligence", use_container_width=True, key=f"sidebar_data_entry_btn{page_suffix}"):
            st.switch_page("pages/admin_data_entry.py")
        if st.button("  Gouvernance utilisateurs", use_container_width=True, key=f"sidebar_users_btn{page_suffix}"):
            st.switch_page("pages/admin_users.py")
        if st.button("  Centre de pilotage", use_container_width=True, key=f"sidebar_panel_btn{page_suffix}"):
            st.switch_page("pages/admin_panel.py")
        st.markdown("---")
        if st.button("  Retour accueil", use_container_width=True, key=f"sidebar_home_btn{page_suffix}"):
            switch_to_home_page()
        if st.button("  Deconnexion", use_container_width=True, key=f"sidebar_logout_btn{page_suffix}"):
            st.session_state.user = None
            st.switch_page("pages/auth.py")


def render_admin_hero(
    title: str,
    subtitle: str,
    chips: Iterable[str],
    eyebrow: str = "Administration",
    notification_count: Optional[int] = None,
    auth=None,
    user_id: Optional[int] = None,
    inbox_key_prefix: str = "admin_inbox",
    inbox_limit: int = 8,
) -> None:
    chip_markup = "".join(f'<span class="admin-chip">{chip}</span>' for chip in chips)
    shell = st.container()
    hero_col, bell_col = shell.columns([0.8, 0.2], gap="small")
    with hero_col:
        st.markdown(
            f"""
<div class="admin-hero">
  <div class="admin-hero-top">
    <div class="admin-eyebrow"><span class="admin-eyebrow-dot"></span>{eyebrow}</div>
  </div>
  <div class="admin-title">{title}</div>
  <p class="admin-subtitle">{subtitle}</p>
  <div class="admin-chip-row">{chip_markup}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    should_show_fallback = False
    if notification_count is not None and auth is not None and user_id is not None:
        state_key = f"{inbox_key_prefix}_open"
        unread_total = int(notification_count)
        unread_label = "Aucune notification en attente." if unread_total == 0 else f"<strong>{unread_total}</strong> message(s) prioritaire(s) a consulter."
        count_class = "has-unread" if unread_total > 0 else "no-unread"
        bell_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6V11c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/></svg>'
        with bell_col:
            st.markdown(
                f'<div class="admin-hero-actions"><div class="admin-bell-wrap"><div class="admin-bell-panel"><div class="admin-bell-head"><span class="admin-bell-kicker"><span class="admin-bell-icon-wrap">{bell_svg}</span>Messagerie SAFE</span><span class="admin-bell-count {count_class}">{unread_total}</span></div><div class="admin-bell-divider"></div><div class="admin-bell-note">{unread_label}</div><div class="admin-bell-status-row"><span class="admin-bell-status-dot"></span>Canal administratif securise</div></div></div></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            bell_label = "Ouvrir la messagerie SAFE"
            if hasattr(st, "popover"):
                with st.popover(bell_label, use_container_width=True):
                    render_admin_notifications_panel(
                        auth,
                        user_id,
                        key_prefix=inbox_key_prefix,
                        title="Boite de reception",
                        intro="",
                        limit=inbox_limit,
                    )
            else:
                if st.button(bell_label, key=f"{inbox_key_prefix}_toggle", use_container_width=True):
                    st.session_state[state_key] = not st.session_state.get(state_key, False)
                should_show_fallback = st.session_state.get(state_key, False)
    if should_show_fallback and auth is not None and user_id is not None:
        render_admin_notifications_panel(
            auth,
            user_id,
            key_prefix=inbox_key_prefix,
            title="Boite de reception",
            intro="",
            limit=inbox_limit,
        )


def render_kpi_cards(cards: List[dict]) -> None:
    markup = []
    for card in cards:
        accent = card.get('accent', '#0a5fab')
        accent_soft = card.get('accent_soft', accent + '33') # Semi-transparent
        pill_bg = card.get('pill', accent + '1A') # Very transparent
        
        markup.append(
            f"""
<div class="admin-kpi-card" style="--accent:{accent};--accent-soft:{accent_soft};--pill:{pill_bg}">
  <div class="admin-kpi-label">{card['label']}</div>
  <div class="admin-kpi-value">{card['value']}</div>
  <div class="admin-kpi-delta">{card['delta']}</div>
  <div class="admin-kpi-copy">{card['copy']}</div>
</div>
"""
        )
    st.markdown(f'<div class="admin-kpi-grid">{"".join(markup)}</div>', unsafe_allow_html=True)


def section_label(text: str) -> None:
    st.markdown(f'<div class="admin-section-label">{text}</div>', unsafe_allow_html=True)


def panel_title(title: str) -> None:
    st.markdown(f'<div class="admin-panel-title">{title}</div>', unsafe_allow_html=True)


def admin_notifications_snapshot(auth, user_id: int) -> tuple[list[dict], int]:
    notifications = auth.get_notifications(user_id, unread_only=False)
    unread_count = auth.get_unread_count(user_id)
    return notifications, unread_count


def _admin_notification_level(title: str, message: str = "") -> tuple[str, str, str]:
    haystack = f"{title} {message}".upper()
    if "CRITIQUE" in haystack:
        return "critique", "CRITIQUE", "🔴"
    if "HAUTE" in haystack or "HIGH" in haystack:
        return "haute", "HAUTE", "🟠"
    if "MODER" in haystack:
        return "moderee", "MODEREE", "🟡"
    if "FAIBLE" in haystack or "LOW" in haystack:
        return "faible", "FAIBLE", "🟢"
    return "faible", "FAIBLE", "🟢"


def _clean_admin_notification_text(text: str, preserve_newlines: bool = False) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    if "<" in cleaned and ">" in cleaned:
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("&nbsp;", " ")
    if preserve_newlines:
        lines = [" ".join(line.split()) for line in cleaned.split("\n")]
        return "\n".join(line for line in lines if line).strip()
    return " ".join(cleaned.split()).strip()


def _admin_display_title(title: str) -> str:
    cleaned = _clean_admin_notification_text(title)
    upper = cleaned.upper()
    legacy_tokens = ("ALERTE INFO", "INFORMATION TERRAIN", "NOUVELLE_DONNEE", "NOUVELLE DONNEE")
    if any(token in upper for token in legacy_tokens):
        if " - " in cleaned:
            suffix = cleaned.split(" - ", 1)[1].strip()
        elif "-" in cleaned:
            suffix = cleaned.split("-", 1)[1].strip()
        else:
            suffix = ""
        return f"ALERTE FAIBLE - {suffix}" if suffix else "ALERTE FAIBLE"
    return cleaned or "ALERTE FAIBLE"


def render_admin_notifications_panel(
    auth,
    user_id: int,
    key_prefix: str,
    title: str = "Boite de reception",
    intro: str = "",
    limit: int = 6,
) -> tuple[list[dict], int]:
    notifications = auth.get_notifications(user_id, unread_only=False)
    unread_count = auth.get_unread_count(user_id)
    visible_count = min(len(notifications), limit)
    intro_text = intro or "Alertes admin, confirmations d'emission et messages internes de pilotage."
    head_left, head_right = st.columns([0.72, 0.28])
    with head_left:
        st.markdown(f"**📬 {title}**")
        st.caption(intro_text)
    with head_right:
        st.markdown(f"**📨 {len(notifications)} message(s)**")
        st.markdown(f"**🔴 {unread_count} non lu(s)**")
    st.divider()

    if not notifications:
        st.info("📭 Boite vide\n\nAucun message pour le moment. Les confirmations admin et alertes internes s'afficheront ici.")
        return notifications, unread_count

    for index, notif in enumerate(notifications[:limit]):
        is_unread = int(notif["is_read"]) == 0
        date_str = str(notif.get("created_at") or "")[:16]
        clean_title = _admin_display_title(str(notif.get("title") or ""))
        raw_message = str(notif.get("message") or "")
        clean_message = _clean_admin_notification_text(raw_message, preserve_newlines=True)
        _, lvl_text, lvl_dot = _admin_notification_level(clean_title, clean_message)

        item_box = st.container()
        top_left, top_right = item_box.columns([0.76, 0.24])
        status_prefix = "• " if is_unread else ""
        with top_left:
            st.markdown(f"**{lvl_dot} {lvl_text}**")
            st.markdown(f"**{status_prefix}{clean_title}**")
        with top_right:
            st.caption(date_str or "-")
        # Afficher le message nettoyé, ou un message clair si vide
        display_message = clean_message if clean_message else ("(Message vide après nettoyage)" if raw_message else "(Pas de contenu disponible)")
        item_box.write(display_message)
        btn_c1, btn_c2 = item_box.columns([1, 1])
        with btn_c1:
            if is_unread and st.button("✓ Lu", key=f"{key_prefix}_rd_{notif['id']}", use_container_width=True):
                auth.mark_notification_read(int(notif["id"]))
                st.rerun()
        with btn_c2:
            if st.button("🗑 Supp.", key=f"{key_prefix}_rm_{notif['id']}", use_container_width=True):
                auth.delete_notification(int(notif["id"]))
                st.rerun()
        if index < visible_count - 1:
            st.divider()
    if len(notifications) > visible_count:
        st.caption(f"{len(notifications) - visible_count} autre(s) message(s) sont conserves dans la boite de reception.")

    st.divider()
    foot1, foot2 = st.columns(2)
    with foot1:
        if unread_count > 0 and st.button("✓✓ Tout marquer lu", use_container_width=True, key=f"{key_prefix}_all_read"):
            auth.mark_all_notifications_read(user_id)
            st.rerun()
    with foot2:
        if notifications and st.button("🗑 Tout supprimer", use_container_width=True, key=f"{key_prefix}_all_del"):
            auth.delete_all_notifications(user_id)
            st.rerun()

    return notifications, unread_count


def render_admin_inbox_expander(
    auth,
    user_id: int,
    key_prefix: str,
    unread_count: Optional[int] = None,
    title: str = "Boite de reception",
    intro: str = "",
    limit: int = 6,
) -> tuple[list[dict], int]:
    effective_unread = auth.get_unread_count(user_id) if unread_count is None else unread_count
    icon = "📬" if effective_unread > 0 else "📭"
    label = f"{icon}  Messagerie — {effective_unread} non lue(s)" if effective_unread > 0 else f"{icon}  Messagerie — aucun message non lu"
    with st.expander(label, expanded=effective_unread > 0):
        return render_admin_notifications_panel(
            auth,
            user_id,
            key_prefix=key_prefix,
            title=title,
            intro=intro,
            limit=limit,
        )


def make_plotly_layout(fig: go.Figure, title: Optional[str] = None) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left", y=0.98, yanchor="top", pad=dict(t=6, b=20)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=18, r=18, t=78 if title else 20, b=18),
        font=dict(family="Manrope", color="#17314f"),
        title_font=dict(family="Sora", size=15, color="#0f3f73"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(255,255,255,.68)", bordercolor="rgba(185,212,234,.65)", borderwidth=1),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="rgba(10,95,171,.18)", font=dict(color="#15304d")),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True, title_standoff=16)
    fig.update_yaxes(gridcolor="rgba(151,195,228,.22)", zeroline=False, automargin=True, title_standoff=16)
    return fig


def safe_read_sqlite(db_path: Path, query: str) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(db_path)
        frame = pd.read_sql_query(query, conn)
        conn.close()
        return frame
    except Exception:
        return pd.DataFrame()


def recent_entries_frame(db_path: Path) -> pd.DataFrame:
    return safe_read_sqlite(
        db_path,
        """
        SELECT disease, province, zone_sante, week, year, total_cases, total_deaths, entry_date
        FROM epidemiological_data
        ORDER BY entry_date DESC
        LIMIT 200
        """,
    )


def alerts_frame(db_path: Path) -> pd.DataFrame:
    return safe_read_sqlite(
        db_path,
        """
        SELECT disease, province, zone_sante, week, year, alert_level, growth_rate, current_cases, predicted_cases, message, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 200
        """,
    )


def users_frame(auth) -> pd.DataFrame:
    users = auth.get_all_users()
    return pd.DataFrame(users) if users else pd.DataFrame()


def _sorted_unique(values) -> List[str]:
    cleaned = {
        str(value).strip()
        for value in values
        if pd.notna(value) and str(value).strip() and str(value).strip().lower() != "nan"
    }
    return sorted(cleaned, key=lambda item: item.casefold())


def aggregated_csv_frame() -> pd.DataFrame:
    root = Path(__file__).parent.parent
    for candidate in [
        root / "data" / "processed" / "aggregated_data_clean.csv",
        root / "data" / "processed" / "donnees_agregees_nettoyees.csv",
        root / "data" / "processed" / "aggregated_data.csv",
    ]:
        if candidate.exists():
            try:
                return pd.read_csv(candidate)
            except Exception:
                return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def reference_catalog_frame() -> pd.DataFrame:
    root = Path(__file__).parent.parent
    for candidate in [
        root / "data" / "processed" / "donnees_agregees_nettoyees.csv",
        root / "data" / "processed" / "aggregated_data_clean.csv",
        root / "data" / "processed" / "aggregated_data.csv",
    ]:
        if not candidate.exists():
            continue
        try:
            reference_df = pd.read_csv(candidate)
        except Exception:
            continue

        rename_map = {}
        for column in reference_df.columns:
            normalized = column.strip().upper()
            if normalized in {"MALADIE", "PROVINCE", "ZONE_SANTE"}:
                rename_map[column] = normalized
        reference_df = reference_df.rename(columns=rename_map)
        for required in ["MALADIE", "PROVINCE", "ZONE_SANTE"]:
            if required not in reference_df.columns:
                reference_df[required] = None

        return reference_df[["MALADIE", "PROVINCE", "ZONE_SANTE"]].drop_duplicates()

    return pd.DataFrame(columns=["MALADIE", "PROVINCE", "ZONE_SANTE"])


def reference_disease_options() -> List[str]:
    return _sorted_unique(reference_catalog_frame().get("MALADIE", []))


def reference_province_options() -> List[str]:
    return _sorted_unique(reference_catalog_frame().get("PROVINCE", []))


def reference_zone_options(province: Optional[str] = None) -> List[str]:
    reference_df = reference_catalog_frame()
    if reference_df.empty:
        return []
    if province:
        filtered = reference_df.loc[
            reference_df["PROVINCE"].astype(str).str.casefold() == province.casefold(),
            "ZONE_SANTE",
        ]
        return _sorted_unique(filtered)
    return _sorted_unique(reference_df.get("ZONE_SANTE", []))
