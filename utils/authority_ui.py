import re
import sqlite3
from html import escape
from pathlib import Path
from typing import List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.sidebar_brand import PUBLIC_SIDEBAR_BRAND, render_sidebar_active_button

__all__ = [
    "apply_authority_theme",
    "render_authority_sidebar",
    "render_authority_hero",
    "render_authority_kpis",
    "render_authority_inbox",
    "authority_section_label",
    "authority_panel_title",
    "make_plotly_layout",
    "load_historical_province",
    "alerts_for_user",
    "alert_delivery_health",
]


AUTHORITY_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.98)!important;width:40px!important;height:40px!important;min-width:40px!important;min-height:40px!important;align-items:center!important;justify-content:center!important;padding:0!important;border:2px solid rgba(10,95,171,.28)!important;border-radius:12px!important;box-shadow:0 10px 28px rgba(15,23,42,.13)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important;stroke:#0b4d95!important;width:22px!important;height:22px!important}
[data-testid="stSidebarNav"]{display:none}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.stApp{background:linear-gradient(180deg,#edf6ff 0%,#e7f2ff 48%,#f7fbff 100%)!important}
[data-testid="stAppViewContainer"] .main .block-container{max-width:1160px!important;padding-top:1.45rem!important;padding-bottom:1.4rem!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#eff7ff 100%)!important;border-right:1px solid rgba(176,208,233,.55)!important;box-shadow:3px 0 18px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] *{color:#0f2542!important}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.9)!important;color:#0a5fab!important;border:1px solid #c8dff0!important;border-radius:12px!important;min-height:42px!important;padding:9px 13px!important;font-weight:800!important;font-size:.8rem!important;transition:all .22s ease!important;width:100%!important;justify-content:flex-start!important;box-shadow:0 8px 22px rgba(10,60,120,.06)!important}
[data-testid="stSidebar"] .stButton>button:hover{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;transform:translateX(4px)!important;box-shadow:0 10px 22px rgba(10,95,171,.22)!important}
[data-testid="stSidebar"] .stButton>button:focus-visible,[data-testid="stSidebar"] .stButton>button:active{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important;transform:translateX(2px)!important;box-shadow:0 0 0 3px rgba(26,162,226,.18),0 10px 22px rgba(10,95,171,.22)!important}
.stButton>button,.stDownloadButton>button{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border:0!important;border-radius:10px!important;padding:8px 12px!important;font-weight:800!important;font-size:.78rem!important;box-shadow:0 8px 18px rgba(10,95,171,.22)!important;transition:all .22s ease!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 12px 22px rgba(10,95,171,.28)!important}
.authority-sidebar-user-card{margin:10px 6px 12px;padding:13px 13px 11px;border-radius:16px;background:linear-gradient(180deg,#ffffff 0%,#eef7ff 100%);border:1px solid #d8e9f6;box-shadow:0 10px 22px rgba(10,60,120,.08)}
.authority-sidebar-role{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:rgba(5,150,105,.08);color:#047857!important;font-size:.68rem;font-weight:800;letter-spacing:1.3px;text-transform:uppercase}
.authority-sidebar-role::before{content:'';width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#059669,#34d399)}
.authority-sidebar-name{margin-top:10px;font-family:'Sora',sans-serif;font-size:.95rem;line-height:1.35;color:#0f2542!important}
.authority-sidebar-meta{margin-top:6px;font-size:.76rem;line-height:1.55;color:#67839c!important}
.authority-shell{max-width:1160px;margin:0 auto;padding-bottom:10px}
.authority-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#0a5fab 0%,#0d80d8 52%,#1aa2e2 100%);border-radius:24px;padding:24px 24px 20px;box-shadow:0 18px 40px rgba(10,95,171,.18);margin:0 0 16px;animation:fadeIn .45s ease-out}
.authority-hero .authority-eyebrow,.authority-hero .authority-title,.authority-hero .authority-subtitle,.authority-hero .authority-chip,.authority-hero .authority-chip *{color:#ffffff!important}
.authority-hero::before{content:'';position:absolute;inset:auto -10% -58% auto;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%)}
.authority-hero-actions{display:flex;justify-content:flex-end;align-items:flex-start;height:100%}
.authority-bell-wrap{display:grid;gap:8px;width:100%;max-width:320px;padding-top:4px;margin-left:auto}
.authority-bell-panel{position:relative;overflow:hidden;border-radius:20px;padding:12px 12px 10px;background:linear-gradient(145deg,#0b4d95 0%,#1376c8 55%,#25a8e0 100%);border:1px solid rgba(255,255,255,.18);box-shadow:0 18px 36px rgba(15,87,129,.22),inset 0 1px 0 rgba(255,255,255,.14)}
.authority-bell-panel::before{content:'';position:absolute;inset:-12% -10% auto auto;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.38),transparent 66%)}
.authority-bell-panel::after{content:'';position:absolute;inset:auto auto -30% -18%;width:90px;height:90px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.1),transparent 70%)}
.authority-bell-head{position:relative;display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
.authority-bell-icon-wrap{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:11px;background:linear-gradient(135deg,#0b4d95,#1677c8);border:1px solid rgba(11,77,149,.25);box-shadow:0 8px 16px rgba(11,77,149,.22);flex:none}
.authority-bell-kicker{display:inline-flex;align-items:center;gap:8px;font-size:.62rem;font-weight:900;letter-spacing:1.35px;text-transform:uppercase;color:#ffffff}
.authority-bell-count{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;padding:0 9px;border-radius:999px;font:900 .76rem 'Sora',sans-serif;transition:all .3s ease}
.authority-bell-count.has-unread{background:linear-gradient(135deg,#ff4d4d 0%,#f97316 100%);color:#fff;box-shadow:0 0 0 0 rgba(255,77,77,.55);animation:pulseRed 2.2s ease-in-out infinite}
.authority-bell-count.no-unread{background:rgba(255,255,255,.96);color:#0f172a;box-shadow:0 4px 12px rgba(15,87,129,.12)}
@keyframes pulseRed{0%,100%{box-shadow:0 0 0 0 rgba(255,77,77,.55),0 6px 12px rgba(3,26,54,.16)}60%{box-shadow:0 0 0 9px rgba(255,77,77,0),0 6px 12px rgba(3,26,54,.16)}}
.authority-bell-divider{height:1px;background:linear-gradient(90deg,rgba(255,255,255,.34),rgba(255,255,255,.1));margin:0 0 7px}
.authority-bell-note{position:relative;font-size:.72rem;line-height:1.45;color:rgba(255,255,255,.92);margin-bottom:5px}
.authority-bell-note strong{color:#ffffff;font-weight:900}
.authority-bell-status-row{display:flex;align-items:center;gap:6px;font-size:.61rem;font-weight:700;letter-spacing:.35px;color:rgba(255,255,255,.84);margin-bottom:8px}
.authority-bell-status-dot{width:6px;height:6px;border-radius:50%;flex:none;background:#4ade80;box-shadow:0 0 0 3px rgba(74,222,128,.22)}
[data-testid="stPopover"],[data-testid="stPopover"]>div{width:100%}
[data-testid="stPopover"] button[kind="secondary"]{position:relative;width:100%!important;background:linear-gradient(135deg,#0b4d95 0%,#1376c8 55%,#25a8e0 100%)!important;color:#ffffff!important;border:1px solid rgba(10,95,171,.28)!important;border-radius:16px!important;min-height:56px!important;padding:10px 14px!important;font-weight:900!important;font-size:.86rem!important;line-height:1.06!important;text-align:left!important;justify-content:flex-start!important;box-shadow:0 14px 26px rgba(15,87,129,.22),inset 0 1px 0 rgba(255,255,255,.18)!important;transition:all .22s cubic-bezier(.4,0,.2,1)!important;letter-spacing:.05px!important}
[data-testid="stPopover"] button[kind="secondary"]::after{content:'Centre de notifications';display:block;font-size:.6rem;font-weight:700;letter-spacing:.28px;color:rgba(255,255,255,.82);margin-top:4px}
[data-testid="stPopover"] button[kind="secondary"]:hover{transform:translateY(-1px)!important;background:linear-gradient(135deg,#0d5aa7 0%,#1684d6 55%,#2fc0f3 100%)!important;box-shadow:0 18px 30px rgba(15,87,129,.24),inset 0 1px 0 rgba(255,255,255,.2)!important;color:#ffffff!important}
[data-testid="stPopover"] button[kind="secondary"]:active{transform:translateY(-1px)!important}
.authority-inbox-shell{padding:2px 0 0}
.authority-inbox-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:0 0 10px;border-bottom:1px solid #e4edf7;margin-bottom:12px}
.authority-inbox-title{font-family:'Sora',sans-serif;font-size:.98rem;font-weight:800;color:#0f3f73;margin:0 0 4px}
.authority-inbox-subtitle{font-size:.74rem;color:#718ea4;line-height:1.52;margin:0;max-width:280px}
.authority-inbox-stats{display:flex;flex-wrap:wrap;justify-content:flex-end;align-items:flex-start;gap:6px;flex-shrink:0}
.authority-inbox-stat{display:inline-flex;align-items:center;gap:5px;padding:5px 9px;border-radius:999px;font-size:.65rem;font-weight:800;letter-spacing:.35px;border:1px solid transparent}
.authority-inbox-stat.total{background:#eef6ff;border-color:#d0e4f7;color:#0a5fab}
.authority-inbox-stat.unread{background:#eefcf5;border-color:#c8f0e0;color:#047857}
.authority-inbox-item{padding:12px 14px;border-radius:16px;border:1px solid rgba(180,208,232,.5);border-left-width:4px;border-left-color:#22c55e;background:linear-gradient(165deg,#ffffff 0%,#f9fbff 100%);box-shadow:0 6px 16px rgba(15,23,42,.05);transition:transform .18s ease,box-shadow .18s ease}
.authority-inbox-item:hover{transform:translateX(3px);box-shadow:0 10px 22px rgba(15,23,42,.09)}
.authority-inbox-item.niveau-critique{border-left-color:#ef4444}
.authority-inbox-item.niveau-haute{border-left-color:#f97316}
.authority-inbox-item.niveau-moderee{border-left-color:#f59e0b}
.authority-inbox-item.niveau-faible{border-left-color:#22c55e}
.authority-inbox-item.unread.niveau-critique{background:linear-gradient(165deg,#fff8f7 0%,#fffdfd 100%);border-color:rgba(239,68,68,.22);border-left-color:#ef4444}
.authority-inbox-item.unread.niveau-haute{background:linear-gradient(165deg,#fff9f5 0%,#fffefb 100%);border-color:rgba(249,115,22,.2);border-left-color:#f97316}
.authority-inbox-item.unread.niveau-moderee{background:linear-gradient(165deg,#fffef3 0%,#fffffe 100%);border-color:rgba(245,158,11,.2);border-left-color:#f59e0b}
.authority-inbox-item.unread.niveau-faible{background:linear-gradient(165deg,#f0fdf4 0%,#fafdfb 100%);border-color:rgba(34,197,94,.2);border-left-color:#22c55e}
.authority-inbox-item-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px}
.authority-inbox-item-left{display:flex;align-items:flex-start;gap:8px;flex:1;min-width:0}
.authority-inbox-dot{width:8px;height:8px;border-radius:50%;flex:none;margin-top:6px;animation:dotBlink 2.4s ease-in-out infinite}
.authority-inbox-dot.critique{background:#ef4444;box-shadow:0 0 0 3px rgba(239,68,68,.18)}
.authority-inbox-dot.haute{background:#f97316;box-shadow:0 0 0 3px rgba(249,115,22,.18)}
.authority-inbox-dot.moderee{background:#f59e0b;box-shadow:0 0 0 3px rgba(245,158,11,.18)}
.authority-inbox-dot.faible{background:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.15)}
.authority-inbox-dot{background:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.15)}
@keyframes dotBlink{0%,100%{opacity:1}55%{opacity:.42}}
.authority-inbox-item-title-col{flex:1;min-width:0}
.authority-inbox-level-badge{display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:999px;font-size:.57rem;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin-bottom:5px;border:1px solid transparent}
.authority-inbox-level-badge.critique{background:rgba(239,68,68,.1);color:#b91c1c;border-color:rgba(239,68,68,.2)}
.authority-inbox-level-badge.haute{background:rgba(249,115,22,.1);color:#c2410c;border-color:rgba(249,115,22,.2)}
.authority-inbox-level-badge.moderee{background:rgba(245,158,11,.1);color:#92400e;border-color:rgba(245,158,11,.2)}
.authority-inbox-level-badge.faible{background:rgba(34,197,94,.1);color:#15803d;border-color:rgba(34,197,94,.2)}
.authority-inbox-item-title{font-size:.82rem;font-weight:900;color:#0f3f73;line-height:1.42;overflow-wrap:anywhere;word-break:break-word}
.authority-inbox-item.unread .authority-inbox-item-title{color:#0a4d8a}
.authority-inbox-date{font-size:.65rem;color:#96afc4;white-space:nowrap;flex-shrink:0;margin-top:2px}
.authority-inbox-text{font-size:.76rem;color:#587391;line-height:1.62;overflow-wrap:anywhere;word-break:break-word;padding-left:16px;margin-top:5px}
.authority-inbox-action-sep{height:1px;background:#edf2f8;margin:8px 0 7px}
.authority-inbox-actions .stButton>button{min-height:32px!important;padding:6px 10px!important;font-size:.7rem!important;font-weight:700!important;border-radius:9px!important}
.authority-inbox-more{margin-top:8px;font-size:.7rem;color:#7c94ab;text-align:center;padding:6px 8px;border-radius:10px;background:rgba(230,240,250,.5)}
.authority-eyebrow{display:inline-flex;align-items:center;gap:8px;padding:6px 11px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.26);font-size:.64rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#fff}
.authority-eyebrow-dot{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#fff,#dcfce7)}
.authority-title{font-family:'Sora',sans-serif;font-size:2rem;line-height:1.08;color:#fff;margin:14px 0 8px;max-width:760px}
.authority-subtitle{max-width:760px;color:rgba(255,255,255,.9);font-size:.92rem;line-height:1.65;margin:0}
.authority-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.authority-chip{padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);font-size:.7rem;font-weight:700;color:#fff;transition:transform .2s ease,background .2s ease}
.authority-chip:hover{transform:translateY(-2px);background:rgba(255,255,255,.18)}
.authority-kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:0 0 16px}
.authority-kpi-card{background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #e2edf8;border-radius:18px;padding:16px 14px;box-shadow:0 10px 24px rgba(15,23,42,.06);position:relative;overflow:hidden;animation:fadeIn .55s ease-out;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.authority-kpi-card:hover{transform:translateY(-4px);box-shadow:0 18px 32px rgba(10,95,171,.10);border-color:#cfe3f4}
.authority-kpi-card::before{content:'';position:absolute;left:18px;right:18px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent-soft))}
.authority-kpi-label{font-size:.68rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#6b7f99;margin-bottom:8px}
.authority-kpi-value{font-family:'Sora',sans-serif;font-size:1.55rem;line-height:1;color:#0f172a;margin-bottom:7px}
.authority-kpi-delta{display:inline-flex;align-items:center;gap:6px;padding:4px 9px;border-radius:999px;background:var(--pill);font-size:.68rem;font-weight:700;color:var(--accent)}
.authority-kpi-copy{margin-top:8px;font-size:.8rem;line-height:1.58;color:#6b7f99}
.authority-section-label{display:flex;align-items:center;gap:10px;margin:22px 0 12px;font-size:.68rem;font-weight:800;letter-spacing:1.7px;text-transform:uppercase;color:#8aa0b8}
.authority-section-label::after{content:'';flex:1;height:1px;background:#dbe8f5}
.authority-panel{background:rgba(255,255,255,.94);border:1px solid rgba(180,208,232,.55);border-radius:18px;padding:14px;box-shadow:0 10px 24px rgba(15,23,42,.05);margin-bottom:14px;animation:fadeIn .6s ease-out;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.authority-panel:hover{transform:translateY(-3px);box-shadow:0 18px 30px rgba(10,95,171,.08);border-color:rgba(135,186,226,.75)}
.authority-panel-title{font-family:'Sora',sans-serif;font-size:.98rem;color:#0f3f73;margin:0 0 12px}
.authority-support-copy{margin:-2px 0 12px;font-size:.8rem;line-height:1.62;color:#68819a}
.authority-grid-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.authority-grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.authority-mini-card{padding:12px;border-radius:12px;background:linear-gradient(180deg,#ffffff,#f4f9ff);border:1px solid #e1edf9;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.authority-mini-card:hover{transform:translateY(-3px);box-shadow:0 12px 22px rgba(10,95,171,.08);border-color:#cfe3f4}
.authority-mini-card h4{margin:0 0 6px;font-size:.84rem;color:#103d6f}
.authority-mini-card p{margin:0;color:#6b7f99;font-size:.79rem;line-height:1.56}
.authority-highlight{padding:12px 14px;border-radius:14px;background:linear-gradient(135deg,#f1f8ff,#eef7ff);border:1px solid rgba(160,200,232,.6);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.authority-highlight:hover{transform:translateY(-3px);box-shadow:0 12px 22px rgba(10,95,171,.08);border-color:rgba(120,182,226,.65)}
.authority-highlight strong{display:block;color:#0a4a8a;font-size:.9rem;margin-bottom:3px}
.authority-highlight span{font-size:.79rem;line-height:1.56;color:#62758b}
.authority-empty-state{padding:14px;border-radius:14px;background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border:1px dashed #c8dff0;color:#5f7992;font-size:.79rem;line-height:1.58}
.authority-alert-card{border-radius:16px;padding:14px 14px 12px;background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);border:1px solid #deebf7;box-shadow:0 8px 18px rgba(15,23,42,.06);margin-bottom:12px;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.authority-alert-card:hover{transform:translateY(-3px);box-shadow:0 16px 24px rgba(10,95,171,.08)}
.authority-alert-card.critique{border-color:rgba(239,68,68,.3);background:linear-gradient(180deg,#fff5f5 0%,#fff9f9 100%)}
.authority-alert-card.haute{border-color:rgba(249,115,22,.28);background:linear-gradient(180deg,#fff8f3 0%,#fffdfb 100%)}
.authority-alert-card.moderee{border-color:rgba(245,158,11,.28);background:linear-gradient(180deg,#fffdf0 0%,#fffef9 100%)}
.authority-alert-card.faible{border-color:rgba(34,197,94,.25);background:linear-gradient(180deg,#f3fcf5 0%,#fbfefc 100%)}
.authority-alert-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap;margin-bottom:10px}
.authority-alert-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;font-size:.64rem;font-weight:800;letter-spacing:1.2px;text-transform:uppercase}
.authority-alert-badge.critique{background:rgba(239,68,68,.12);color:#b91c1c}
.authority-alert-badge.haute{background:rgba(249,115,22,.12);color:#c2410c}
.authority-alert-badge.moderee{background:rgba(245,158,11,.14);color:#a16207}
.authority-alert-badge.faible{background:rgba(34,197,94,.12);color:#15803d}
.authority-alert-title{font-family:'Sora',sans-serif;font-size:.97rem;color:#163e68;margin:0 0 4px}
.authority-alert-meta{font-size:.77rem;line-height:1.54;color:#69829b}
.authority-alert-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0}
.authority-alert-stat{padding:10px;border-radius:12px;background:rgba(255,255,255,.75);border:1px solid #e2edf8}
.authority-alert-stat strong{display:block;font-family:'Sora',sans-serif;font-size:.95rem;color:#0f172a;margin-bottom:3px}
.authority-alert-stat span{font-size:.66rem;letter-spacing:1px;text-transform:uppercase;color:#7c92a8;font-weight:800}
.authority-status-chip{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border-radius:999px;border:1px solid #cde2f4;background:#eff8ff;font-size:.7rem;font-weight:700;color:#0a5fab;margin-bottom:14px}
.authority-status-chip.dot-ok::before,.authority-status-chip.dot-warn::before{content:'';width:8px;height:8px;border-radius:50%}
.authority-status-chip.dot-ok::before{background:#16a34a}
.authority-status-chip.dot-warn::before{background:#f59e0b}
[data-testid="stExpander"]{border:1px solid rgba(180,208,232,.7)!important;border-radius:18px!important;background:linear-gradient(180deg,rgba(255,255,255,.97) 0%,rgba(246,251,255,.97) 100%)!important;box-shadow:0 10px 24px rgba(15,23,42,.05)!important;overflow:hidden!important;margin-bottom:12px!important}
[data-testid="stExpander"] details{border-radius:18px!important}
[data-testid="stExpander"] summary{padding:.25rem 0!important;font-weight:800!important;color:#103d6f!important}
[data-testid="stExpander"] summary:hover{color:#0a5fab!important}
[data-testid="stDataFrame"]{border-radius:16px!important;overflow:hidden!important;border:1px solid #e2edf8!important}
[data-testid="stDataFrame"] *{font-size:.8rem!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#f2f8ff;border:1px solid #d7e7f6;border-radius:999px;padding:9px 14px;font-weight:800;color:#0f4d8c;white-space:normal!important;min-height:40px}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#fff!important;border-color:#0a5fab!important}
[data-baseweb="button-group"]{background:linear-gradient(180deg,#edf6ff 0%,#f7fbff 100%);padding:4px;border:1px solid #d6e6f5;border-radius:16px;box-shadow:inset 0 1px 0 rgba(255,255,255,.9)}
[data-baseweb="button-group"] button{border-radius:12px!important;border:1px solid rgba(170,205,233,.75)!important;background:linear-gradient(180deg,#f2f8ff 0%,#e8f3ff 100%)!important;color:#0f4d8c!important;font-weight:800!important;font-size:.74rem!important;min-height:40px!important;padding:0 14px!important;box-shadow:0 4px 10px rgba(10,95,171,.06)!important}
[data-baseweb="button-group"] button:hover{background:linear-gradient(180deg,#e5f2ff 0%,#dcebff 100%)!important;color:#0a5fab!important;border-color:#b7d8f1!important}
[data-baseweb="button-group"] button[aria-pressed="true"]{background:linear-gradient(135deg,#0a5fab,#1aa2e2)!important;color:#ffffff!important;box-shadow:0 10px 18px rgba(10,95,171,.2)!important}
@media (max-width: 1100px){.authority-grid-2,.authority-grid-3,.authority-alert-stats{grid-template-columns:1fr}.authority-hero-actions{width:100%}.authority-bell-wrap{max-width:none;margin-left:0}.authority-shell{padding:0 .35rem}}
@media (max-width: 720px){.authority-hero{padding:18px 16px}.authority-title{font-size:1.45rem}.authority-kpi-grid{grid-template-columns:1fr}.authority-panel{padding:12px}.authority-chip-row{gap:6px}.authority-bell-panel{padding:10px}.authority-bell-note{font-size:.68rem;line-height:1.4}}
@media (max-width: 900px){div[data-testid="stHorizontalBlock"]{gap:.8rem!important}div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}}
@media (max-width: 560px){[data-testid="stAppViewContainer"] .main .block-container{padding-top:1rem!important;padding-bottom:1rem!important;padding-left:.55rem!important;padding-right:.55rem!important}.authority-hero{border-radius:18px;padding:16px 12px}.authority-title{font-size:1.28rem;line-height:1.14}.authority-subtitle{font-size:.84rem;line-height:1.58}.authority-kpi-value{font-size:1.35rem}.authority-panel-title{font-size:.9rem}.authority-sidebar-user-card{margin:8px 4px 10px;padding:11px}[data-testid="stPopover"] button[kind="secondary"]{min-height:50px!important;font-size:.8rem!important;padding:8px 12px!important}}
</style>
"""


def apply_authority_theme() -> None:
    st.markdown(AUTHORITY_THEME, unsafe_allow_html=True)


def render_authority_sidebar(user: dict, auth, active_item: int) -> None:
    with st.sidebar:
        st.markdown(PUBLIC_SIDEBAR_BRAND, unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="authority-sidebar-user-card">
  <div class="authority-sidebar-role">Autorité sanitaire</div>
  <div class="authority-sidebar-name">{user['full_name']}</div>
    <div class="authority-sidebar-meta">Province : {user.get('province', '—')}<br/>Zone de santé : {user.get('zone_sante', '—')}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        render_sidebar_active_button(active_item)
        if st.button("Mon tableau de bord", use_container_width=True, key=f"authority_dashboard_{active_item}"):
            st.switch_page("pages/authority_dashboard.py")
        if st.button("Mes alertes", use_container_width=True, key=f"authority_alerts_{active_item}"):
            st.switch_page("pages/authority_alerts.py")
        st.markdown("---")
        if st.button("Retour à l'accueil", use_container_width=True, key=f"authority_home_{active_item}"):
            st.switch_page("pages/home.py")
        if st.button("Déconnexion", use_container_width=True, key=f"authority_logout_{active_item}"):
            st.session_state.user = None
            st.switch_page("pages/auth.py")


def render_authority_hero(
    title: str,
    subtitle: str = "",
    chips: Optional[list] = None,
    eyebrow: str = "Tableau de veille sanitaire",
    auth=None,
    user_id: Optional[int] = None,
    notification_count: Optional[int] = None,
    inbox_key_prefix: str = "authority_inbox",
    inbox_limit: int = 8,
) -> None:
    chip_markup = "".join(f'<span class="authority-chip">{chip}</span>' for chip in (chips or []))
    chip_container = f'<div class="authority-chip-row">{chip_markup}</div>' if chip_markup else ""
    shell = st.container()
    hero_col, bell_col = shell.columns([0.8, 0.2], gap="small")
    with hero_col:
        st.markdown(
            f"""
<div class="authority-hero">
  <div class="authority-eyebrow"><span class="authority-eyebrow-dot"></span>{eyebrow}</div>
  <div class="authority-title">{title}</div>
  <div class="authority-subtitle">{subtitle}</div>
  {chip_container}
</div>
""",
            unsafe_allow_html=True,
        )
    should_show_fallback = False
    if notification_count is not None and auth is not None and user_id is not None:
        state_key = f"{inbox_key_prefix}_open"
        n = int(notification_count)
        unread_label = "Aucune notification en attente." if n == 0 else f"<strong>{n}</strong> message(s) prioritaire(s) à consulter."
        count_class = "has-unread" if n > 0 else "no-unread"
        bell_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6V11c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/></svg>'
        with bell_col:
            st.markdown(
                f'<div class="authority-hero-actions"><div class="authority-bell-wrap"><div class="authority-bell-panel"><div class="authority-bell-head"><span class="authority-bell-kicker"><span class="authority-bell-icon-wrap">{bell_svg}</span>Messagerie SAFE</span><span class="authority-bell-count {count_class}">{n}</span></div><div class="authority-bell-divider"></div><div class="authority-bell-note">{unread_label}</div><div class="authority-bell-status-row"><span class="authority-bell-status-dot"></span>Canal autorité sanitaire sécurisé</div></div></div></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            bell_label = "Ouvrir la messagerie SAFE"
            if hasattr(st, "popover"):
                with st.popover(bell_label, use_container_width=True):
                    render_authority_inbox(auth, user_id, key_prefix=inbox_key_prefix, limit=inbox_limit)
            else:
                if st.button(bell_label, key=f"{inbox_key_prefix}_toggle", use_container_width=True):
                    st.session_state[state_key] = not st.session_state.get(state_key, False)
                should_show_fallback = st.session_state.get(state_key, False)
    if should_show_fallback and auth is not None and user_id is not None:
        render_authority_inbox(auth, user_id, key_prefix=inbox_key_prefix, limit=inbox_limit)


def render_authority_kpis(cards: List[dict]) -> None:
    markup = []
    for card in cards:
        accent = card.get("accent", "#0a5fab")
        accent_soft = card.get("accent_soft", accent + "33")
        pill = card.get("pill", accent + "1A")
        markup.append(
            f"""
<div class="authority-kpi-card" style="--accent:{accent};--accent-soft:{accent_soft};--pill:{pill}">
  <div class="authority-kpi-label">{card['label']}</div>
  <div class="authority-kpi-value">{card['value']}</div>
  <div class="authority-kpi-delta">{card['delta']}</div>
  <div class="authority-kpi-copy">{card['copy']}</div>
</div>
"""
        )
    st.markdown(f'<div class="authority-kpi-grid">{"".join(markup)}</div>', unsafe_allow_html=True)


def authority_section_label(text: str) -> None:
    st.markdown(f'<div class="authority-section-label">{text}</div>', unsafe_allow_html=True)


def authority_panel_title(title: str) -> None:
    st.markdown(f'<div class="authority-panel-title">{title}</div>', unsafe_allow_html=True)


def _authority_notification_level(title: str, message: str = "") -> tuple[str, str, str]:
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


def _clean_notification_text(text: str, preserve_newlines: bool = False) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    if "<" in cleaned and ">" in cleaned:
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("&nbsp;", " ")
    if preserve_newlines:
        lines = [" ".join(line.split()) for line in cleaned.split("\n")]
        return "\n".join(line for line in lines if line).strip()
    return " ".join(cleaned.split()).strip()


def _authority_display_title(title: str) -> str:
    cleaned = _clean_notification_text(title)
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


def render_authority_inbox(
    auth,
    user_id: int,
    key_prefix: str,
    limit: int = 6,
) -> tuple[list[dict], int]:
    """Boite de reception style messagerie pour les autorites."""
    notifications = auth.get_notifications(user_id, unread_only=False)
    unread_count = auth.get_unread_count(user_id)
    visible_count = min(len(notifications), limit)
    head_left, head_right = st.columns([0.72, 0.28])
    with head_left:
        st.markdown("**📬 Boite de reception**")
        st.caption("Alertes sanitaires, signaux terrain et confirmations de diffusion.")
    with head_right:
        st.markdown(f"**📨 {len(notifications)} message(s)**")
        st.markdown(f"**🔴 {unread_count} non lu(s)**")
    st.divider()

    if not notifications:
        st.info("📭 Boite vide\n\nAucun message pour le moment. Les alertes et signaux terrain s'afficheront ici.")
        return notifications, unread_count

    for index, notif in enumerate(notifications[:limit]):
        is_unread = int(notif["is_read"]) == 0
        date_str = str(notif.get("created_at") or "")[:16]
        clean_title = _authority_display_title(str(notif.get("title") or ""))
        raw_message = str(notif.get("message") or "")
        clean_message = _clean_notification_text(raw_message, preserve_newlines=True)
        _, lvl_text, lvl_dot = _authority_notification_level(clean_title, clean_message)

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
        if notifications and st.button("🗑 Vider la boite", use_container_width=True, key=f"{key_prefix}_all_del"):
            auth.delete_all_notifications(user_id)
            st.rerun()

    return notifications, unread_count


def make_plotly_layout(fig: go.Figure, title: Optional[str] = None) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left", y=0.98, yanchor="top", pad=dict(t=6, b=20)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=72 if title else 18, b=16),
        font=dict(family="Manrope", color="#17314f"),
        title_font=dict(family="Sora", size=14, color="#0f3f73"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(255,255,255,.68)", bordercolor="rgba(185,212,234,.65)", borderwidth=1),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="rgba(10,95,171,.18)", font=dict(color="#15304d")),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True, title_standoff=16)
    fig.update_yaxes(gridcolor="rgba(151,195,228,.22)", zeroline=False, automargin=True, title_standoff=16)
    return fig


def load_historical_province(province: str) -> pd.DataFrame:
    root = Path(__file__).parent.parent
    for name in ["donnees_agregees_nettoyees.csv", "aggregated_data_clean.csv", "aggregated_data.csv"]:
        candidate = root / "data" / "processed" / name
        if not candidate.exists():
            continue
        try:
            frame = pd.read_csv(candidate)
        except Exception:
            continue
        if "PROVINCE" in frame.columns and province:
            return frame.loc[frame["PROVINCE"].astype(str).str.casefold() == province.casefold()].copy()
        return frame.copy()
    return pd.DataFrame()


def alerts_for_user(db_path: Path, user_id: int) -> pd.DataFrame:
    query = """
        SELECT
            a.id,
            COALESCE(a.disease, 'Inconnue') AS disease,
            COALESCE(a.province, '—') AS province,
            COALESCE(a.zone_sante, '—') AS zone_sante,
            COALESCE(a.week, 0) AS week,
            COALESCE(a.year, 0) AS year,
            COALESCE(a.current_cases, 0) AS current_cases,
            COALESCE(a.predicted_cases, 0) AS predicted_cases,
            COALESCE(a.growth_rate, 0) AS growth_rate,
            UPPER(TRIM(COALESCE(a.alert_level, 'FAIBLE'))) AS alert_level,
            COALESCE(a.message, 'Aucun message detaille') AS message,
            COALESCE(a.created_at, n.created_at) AS created_at,
            COALESCE(n.is_read, 0) AS is_read,
            n.id AS notif_id,
            pr.model_r2 AS r2_score
        FROM notifications n
        JOIN alerts a ON a.id = n.alert_id
        LEFT JOIN (
            SELECT pr1.alert_id, pr1.model_r2
            FROM prediction_runs pr1
            WHERE pr1.alert_id IS NOT NULL
              AND pr1.created_at = (
                  SELECT MAX(pr2.created_at)
                  FROM prediction_runs pr2
                  WHERE pr2.alert_id = pr1.alert_id
              )
        ) pr ON pr.alert_id = a.id
        WHERE n.user_id = ?
        ORDER BY n.created_at DESC
    """
    expected_cols = [
        "id", "disease", "province", "zone_sante", "week", "year", "current_cases",
        "predicted_cases", "growth_rate", "alert_level", "message", "created_at", "is_read", "notif_id",
        "r2_score",
    ]
    try:
        conn = sqlite3.connect(str(db_path))
        frame = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        if frame.empty:
            return pd.DataFrame(columns=expected_cols)
        frame = frame.drop_duplicates(subset=["notif_id"], keep="first")
        frame["alert_level"] = frame["alert_level"].replace({
            "MODERATE": "MODEREE",
            "MODERE": "MODEREE",
            "HIGH": "HAUTE",
            "CRITICAL": "CRITIQUE",
            "INFO": "FAIBLE",
            "NOUVELLE_DONNEE": "FAIBLE",
        })
        frame.loc[~frame["alert_level"].isin(["CRITIQUE", "HAUTE", "MODEREE", "FAIBLE"]), "alert_level"] = "FAIBLE"
        return frame
    except Exception:
        return pd.DataFrame(columns=expected_cols)


def alert_delivery_health(db_path: Path, user_id: int) -> dict:
    status = {
        "ok": True,
        "notification_count": 0,
        "linked_alert_count": 0,
        "unread_count": 0,
        "message": "Canal d'alerte operationnel.",
    }
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id=?", (user_id,))
        notification_count = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0", (user_id,))
        unread_count = int(cur.fetchone()[0] or 0)
        cur.execute(
            """
            SELECT COUNT(*)
            FROM notifications n
            JOIN alerts a ON a.id = n.alert_id
            WHERE n.user_id=?
            """,
            (user_id,),
        )
        linked_alert_count = int(cur.fetchone()[0] or 0)
        conn.close()
        status.update(
            {
                "notification_count": notification_count,
                "linked_alert_count": linked_alert_count,
                "unread_count": unread_count,
            }
        )
        if linked_alert_count < notification_count:
            status["ok"] = False
            status["message"] = "Certaines notifications ne sont pas liees a une alerte detaillee."
        return status
    except Exception:
        status["ok"] = False
        status["message"] = "Verification du canal d'alerte indisponible pour le moment."
        return status
