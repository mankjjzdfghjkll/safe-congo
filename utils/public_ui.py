from html import escape
from pathlib import Path
from typing import Sequence

import pandas as pd
import streamlit as st

from src.config import MODEL_RESULT_FILTERS


PROCESSED_DATA_CANDIDATES = [
    Path(__file__).parent.parent / "data" / "processed" / "donnees_agregees_nettoyees.csv",
    Path(__file__).parent.parent / "data" / "processed" / "aggregated_data.csv",
]
MODEL_SUMMARY_CANDIDATES = [
    Path(__file__).parent.parent / "models" / "evaluation" / "model_performance_summary.csv",
]
MIN_ACCEPTABLE_R2 = float(MODEL_RESULT_FILTERS.get("min_acceptable_r2", 0.5))

PUBLIC_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
:root{
    --safe-blue-950:#082949;
    --safe-blue-900:#0b3f72;
    --safe-blue-800:#0e5a99;
    --safe-blue-700:#1483d6;
    --safe-blue-500:#63b8ef;
    --safe-gold-500:#f0c44e;
    --safe-gold-300:#f7dea0;
    --safe-red-500:#ce1126;
    --safe-ink:#17324d;
    --safe-copy:#54708b;
    --safe-border:rgba(121,170,212,.28);
}
*{font-family:'Manrope',sans-serif;box-sizing:border-box}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:#0b4d95!important;background:rgba(255,255,255,.98)!important;width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;align-items:center!important;justify-content:center!important;padding:0!important;border:2px solid rgba(10,95,171,.32)!important;border-radius:12px!important;box-shadow:0 10px 24px rgba(10,60,120,.16)!important}
[data-testid="collapsedControl"] svg{fill:#0b4d95!important;stroke:#0b4d95!important;width:21px!important;height:21px!important}
.stApp{background:
    radial-gradient(circle at top right,rgba(240,196,78,.16),transparent 24%),
    radial-gradient(circle at top left,rgba(20,131,214,.12),transparent 28%),
    linear-gradient(180deg,#eef6ff 0%,#e5f1fb 50%,#f6fbff 100%)!important}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1180px;width:min(100%,1180px)}
.public-page{display:grid;gap:22px}
.public-hero{position:relative;overflow:hidden;border-radius:34px;padding:54px 56px;border:1px solid rgba(255,255,255,.16);box-shadow:0 26px 60px rgba(16,79,144,.2);isolation:isolate}
.public-hero,.public-hero *{color:#ffffff}
.public-hero::before{content:'';position:absolute;inset:0;background:linear-gradient(125deg,rgba(255,255,255,.16),transparent 42%,rgba(240,196,78,.12) 100%);pointer-events:none}
.public-hero::after{content:'';position:absolute;right:-90px;bottom:-120px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.22),transparent 72%)}
.public-kicker{display:inline-block;padding:7px 16px;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.26);color:#f7fbff;font-size:.72rem;font-weight:800;letter-spacing:2.4px;text-transform:uppercase;backdrop-filter:blur(8px)}
.public-title{font-family:'Sora',sans-serif;font-size:2.85rem;line-height:1.08;color:#fff;margin:18px 0 14px;max-width:780px}
.public-sub{max-width:760px;color:rgba(247,251,255,.88);font-size:1rem;line-height:1.82;margin:0}
.public-metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin-top:22px}
.public-metric{padding:18px;border-radius:22px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);backdrop-filter:blur(10px);box-shadow:inset 0 1px 0 rgba(255,255,255,.18)}
.public-metric-value{font-family:'Sora',sans-serif;font-size:1.55rem;color:#fff;font-weight:800}
.public-metric-label{font-size:.78rem;letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,.72);margin-top:4px}
.public-grid-2{display:grid;grid-template-columns:1.15fr .85fr;gap:22px}
.public-grid-3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.public-auto-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}
.public-panel{position:relative;background:linear-gradient(180deg,rgba(255,255,255,.96),rgba(245,251,255,.94));border:1px solid var(--safe-border);border-radius:30px;padding:30px 32px;box-shadow:0 18px 40px rgba(35,91,150,.08);overflow:hidden}
.public-panel::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,var(--safe-blue-700),var(--safe-gold-500));opacity:.9}
.public-panel h3,.public-panel h4{font-family:'Sora',sans-serif;color:var(--safe-blue-900);margin:0 0 14px}
.public-panel h3{font-size:1.22rem}
.public-panel h4{font-size:.98rem;margin-bottom:8px}
.public-copy,.public-panel li{color:var(--safe-copy);font-size:.95rem;line-height:1.82}
.public-panel ul{margin:14px 0 0;padding-left:18px}
.public-card{position:relative;background:linear-gradient(180deg,#ffffff,#edf8ff);border:1px solid rgba(166,204,233,.5);border-radius:26px;padding:22px;box-shadow:0 12px 28px rgba(35,91,150,.06);overflow:hidden}
.public-card::before{content:'';position:absolute;left:18px;right:18px;top:0;height:3px;border-radius:999px;background:linear-gradient(90deg,var(--safe-blue-700),var(--safe-gold-500),rgba(206,17,38,.6))}
.public-card-title{font-weight:800;color:var(--safe-blue-900);font-size:1rem;margin-bottom:8px}
.public-card-copy{color:#64809b;font-size:.84rem;line-height:1.7;margin:0}
.public-card-kicker{font-size:.72rem;letter-spacing:1.8px;text-transform:uppercase;color:#6a8aa6;font-weight:800;margin-bottom:8px}
.public-step-list{display:grid;gap:18px}
.public-step{position:relative;padding:0 0 20px 68px}
.public-step::before{content:'';position:absolute;left:21px;top:48px;bottom:-14px;width:2px;background:linear-gradient(180deg,#6bbdf0,rgba(240,196,78,.12),rgba(107,189,240,0))}
.public-step:last-child::before{display:none}
.public-step-index{position:absolute;left:0;top:0;width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#124f8d,#47a8e7);color:#fff;font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 14px 28px rgba(18,79,141,.22)}
.public-step-body{background:rgba(255,255,255,.9);border:1px solid rgba(166,204,233,.58);border-radius:26px;padding:22px 24px;box-shadow:0 16px 38px rgba(35,91,150,.08)}
.public-step-title{font-family:'Sora',sans-serif;color:var(--safe-blue-900);font-size:1.04rem;margin:0 0 8px}
.public-step-copy{color:#4e647e;font-size:.94rem;line-height:1.78;margin:0}
.public-step-tag{display:inline-block;margin-top:12px;padding:5px 10px;border-radius:999px;background:#e7f5ff;color:#1979bf;font-size:.72rem;font-weight:800;letter-spacing:1.1px;text-transform:uppercase}
.public-band{position:relative;background:linear-gradient(135deg,#163d72,#2086d8);border:1px solid rgba(255,255,255,.14);border-radius:30px;padding:30px 34px;color:#fff;box-shadow:0 24px 48px rgba(21,71,130,.18);overflow:hidden}
.public-band::after{content:'';position:absolute;right:-48px;top:-38px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(240,196,78,.28),transparent 66%)}
.public-band,.public-band *{color:#ffffff!important}
.public-band p{font-family:'Sora',sans-serif;font-size:1.25rem;line-height:1.55;margin:0 0 12px}
.public-band span{font-size:.82rem;letter-spacing:1.8px;text-transform:uppercase;color:rgba(255,255,255,.72)}
.public-chip-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}
.public-chip{padding:12px 14px;border-radius:16px;background:linear-gradient(135deg,#ffffff,#edf8ff);border:1px solid rgba(166,204,233,.5);font-size:.82rem;font-weight:700;color:#195b8a;text-align:center}
.public-bar-row{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.public-bar-label{width:175px;flex-shrink:0;color:#4e647e;font-size:.86rem;font-weight:700}
.public-bar-track{flex:1;height:12px;border-radius:999px;background:#ddeefa;overflow:hidden;box-shadow:inset 0 1px 3px rgba(15,35,55,.08)}
.public-bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#1483d6,#63c9e7,#f0c44e)}
.public-bar-value{width:58px;text-align:right;font-family:'Sora',sans-serif;color:#1483d6;font-size:.82rem}
.public-partner-link{display:inline-block;margin-top:10px;color:#0f7bc7;text-decoration:none;font-size:.82rem;font-weight:800}
.public-partner-link:hover{text-decoration:underline}
.public-note{padding:16px 18px;border-radius:20px;background:linear-gradient(135deg,#f7fbff,#eef7ff);border:1px solid rgba(166,204,233,.44);color:#64809b;font-size:.84rem;line-height:1.72}
.public-section-head{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:20px}
.public-section-kicker{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;background:rgba(20,131,214,.08);color:var(--safe-blue-800);font-size:.72rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase}
.public-section-kicker::before{content:'';width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,var(--safe-blue-700),var(--safe-gold-500))}
.public-section-title{font-family:'Sora',sans-serif;font-size:1.46rem;line-height:1.2;color:var(--safe-blue-900);margin:10px 0 0}
.public-section-copy{max-width:640px;color:var(--safe-copy);font-size:.92rem;line-height:1.74;margin:0}
.public-pill-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.public-pill{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:999px;background:rgba(255,255,255,.82);border:1px solid rgba(166,204,233,.48);color:var(--safe-blue-900);font-size:.8rem;font-weight:700}
.public-pill::before{content:'';width:7px;height:7px;border-radius:50%;background:var(--safe-gold-500)}
.public-accent-card{background:linear-gradient(145deg,#0d4a86,#1483d6);border-radius:28px;padding:24px 24px;color:#fff;box-shadow:0 18px 42px rgba(13,74,134,.22)}
.public-accent-card,.public-accent-card *{color:#ffffff!important}
.public-accent-card h3{font-family:'Sora',sans-serif;font-size:1.18rem;margin:0 0 12px;color:#fff}
.public-accent-card p{margin:0;color:rgba(247,251,255,.88);font-size:.92rem;line-height:1.74}
.public-accent-card .public-section-kicker{background:rgba(255,255,255,.14)!important;color:#ffffff!important}
.public-accent-card .public-section-title,.public-accent-card .public-section-copy,.public-accent-card .public-copy{color:#ffffff!important}
.public-accent-card .public-pill{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);color:#ffffff!important}

/* Refonte premium des pages publiques */
.public-page{gap:24px}
.public-hero{
    border-radius:18px;
    padding:44px;
    border:1px solid rgba(255,255,255,.30);
    box-shadow:0 24px 70px rgba(8,41,73,.20);
    min-height:360px;
}
.public-hero::before{
    background:
        linear-gradient(115deg,rgba(3,20,42,.28),rgba(3,20,42,.08) 42%,rgba(255,255,255,.10) 100%),
        radial-gradient(circle at 78% 22%,rgba(255,255,255,.22),transparent 26%);
}
.public-hero::after{display:none}
.public-hero-layout{position:relative;z-index:2;display:grid;grid-template-columns:minmax(0,1.1fr) 330px;gap:34px;align-items:center}
.public-hero-copy{min-width:0}
.public-kicker{
    background:rgba(255,255,255,.16);
    border:1px solid rgba(255,255,255,.34);
    border-radius:999px;
    color:#ffffff!important;
}
.public-title{font-size:2.55rem;letter-spacing:0;max-width:820px}
.public-sub{color:rgba(255,255,255,.92)!important;font-weight:500}
.public-metric-grid{grid-template-columns:repeat(auto-fit,minmax(142px,1fr));gap:12px;margin-top:24px}
.public-metric{
    border-radius:8px;
    background:rgba(255,255,255,.16);
    border:1px solid rgba(255,255,255,.25);
    padding:15px 16px;
}
.public-metric-value{font-size:1.42rem;color:#ffffff!important}
.public-metric-label{color:rgba(255,255,255,.82)!important;font-size:.68rem}
.public-hero-visual{
    min-height:270px;
    border-radius:16px;
    background:linear-gradient(180deg,rgba(255,255,255,.18),rgba(255,255,255,.08));
    border:1px solid rgba(255,255,255,.24);
    position:relative;
    overflow:hidden;
    display:flex;
    align-items:center;
    justify-content:center;
}
.public-hero-visual::before{
    content:'';
    width:170px;
    height:170px;
    border-radius:50%;
    border:1px solid rgba(255,255,255,.30);
    box-shadow:0 0 0 26px rgba(255,255,255,.06),0 0 0 54px rgba(255,255,255,.035);
}
.public-hero-visual::after{
    content:'SAFE';
    position:absolute;
    inset:auto auto 34px auto;
    padding:8px 16px;
    border-radius:999px;
    background:#ffffff;
    color:#0a5fab;
    font-family:'Sora',sans-serif;
    font-size:.78rem;
    letter-spacing:2px;
    font-weight:800;
}
.public-signal-card{
    position:absolute;
    left:24px;
    right:24px;
    top:24px;
    display:grid;
    gap:10px;
}
.public-signal-line{
    height:10px;
    border-radius:999px;
    background:rgba(255,255,255,.20);
    overflow:hidden;
}
.public-signal-line span{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#ffffff,#f0c44e)}
.public-panel{
    border-radius:10px;
    padding:28px;
    background:rgba(255,255,255,.94);
    border:1px solid rgba(158,195,226,.50);
    box-shadow:0 18px 44px rgba(35,91,150,.08);
}
.public-panel::before{width:3px}
.public-card{
    border-radius:8px;
    background:#ffffff;
    border:1px solid rgba(166,204,233,.62);
    box-shadow:0 10px 28px rgba(35,91,150,.06);
}
.public-card::before{left:0;right:0;height:3px;border-radius:0;background:linear-gradient(90deg,#0a5fab,#1aa2e2,#f0c44e)}
.public-card-title{color:#0b3f72!important}
.public-card-copy{color:#4d6a86!important}
.public-accent-card{
    border-radius:10px;
    background:linear-gradient(145deg,#083f73 0%,#0a5fab 62%,#1483d6 100%);
    border:1px solid rgba(255,255,255,.22);
    box-shadow:0 20px 46px rgba(10,95,171,.22);
}
.public-accent-card,.public-accent-card *{color:#ffffff!important}
.public-accent-card p,.public-accent-card .public-copy,.public-accent-card .public-section-copy{color:rgba(255,255,255,.92)!important}
.public-accent-card .public-pill{background:rgba(255,255,255,.16)!important;border-color:rgba(255,255,255,.28)!important}
.public-band{
    border-radius:10px;
    background:linear-gradient(135deg,#082949 0%,#0a5fab 76%,#f0c44e 150%);
    border:1px solid rgba(255,255,255,.20);
}
.public-band,.public-band *{color:#ffffff!important}
.public-note{border-radius:8px;background:#f7fbff;color:#4d6a86!important}
.public-chip{border-radius:8px}
.public-step-body{border-radius:8px;background:#ffffff}
.public-step-index{border-radius:12px;background:linear-gradient(135deg,#0a5fab,#1aa2e2)}
.public-step-tag{background:#eef7ff;color:#0a5fab}
.public-section-title{letter-spacing:0;color:#0b3f72!important}
.public-copy,.public-panel p,.public-panel li{color:#4d6a86!important}
.public-partner-link{color:#0a5fab!important}
@media (max-width: 1100px){
    .block-container{padding-left:1rem;padding-right:1rem}
    .public-hero{padding:42px 28px}
    .public-title{font-size:2.35rem;max-width:none}
    .public-sub{max-width:none}
    .public-panel{padding:24px 22px}
    .public-band{padding:24px 22px}
}
@media (max-width: 900px){
  .public-hero-layout{grid-template-columns:1fr}
  .public-hero-visual{min-height:190px}
  .public-hero{padding:38px 24px}
  .public-title{font-size:2.15rem}
  .public-grid-2,.public-grid-3{grid-template-columns:1fr}
  .public-panel{padding:24px}
  .public-step{padding-left:58px}
  .public-bar-row{align-items:flex-start;flex-direction:column}
  .public-bar-label,.public-bar-value{width:auto}
    .public-section-head{align-items:flex-start;flex-direction:column}
}
@media (max-width: 900px){
    div[data-testid="stHorizontalBlock"]{gap:.8rem!important}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}
}
@media (max-width: 640px){
    .block-container{padding-top:1.2rem;padding-left:.7rem;padding-right:.7rem;padding-bottom:2rem}
    .public-page{gap:16px}
    .public-hero{padding:26px 16px;border-radius:24px}
    .public-title{font-size:1.78rem;line-height:1.14;margin:14px 0 10px}
    .public-sub,.public-copy,.public-panel li,.public-step-copy{font-size:.9rem;line-height:1.68}
    .public-metric-grid,.public-auto-grid,.public-chip-grid{grid-template-columns:1fr}
    .public-panel,.public-card,.public-band{padding:18px 16px;border-radius:20px}
    .public-band p{font-size:1.02rem}
    .public-step{padding-left:0;padding-bottom:0}
    .public-step::before{display:none}
    .public-step-index{position:relative;left:auto;top:auto;margin-bottom:10px}
    .public-step-body{padding:18px 16px;border-radius:20px}
    .public-section-title{font-size:1.22rem}
    .public-accent-card{padding:18px 16px;border-radius:20px}
    .public-hero-layout{gap:18px}
    .public-hero-visual{display:none}
}
</style>
"""

HERO_GRADIENTS = {
    "mission": "linear-gradient(135deg,#093766 0%,#0d5fa6 54%,#2a90d9 82%,#f0c44e 120%)",
    "impact": "linear-gradient(135deg,#0a446f 0%,#0e6db0 52%,#4aa8df 82%,#f4d16d 122%)",
    "contact": "linear-gradient(135deg,#0b3f72 0%,#1474b9 48%,#3e9adb 78%,#f0c44e 118%)",
    "flow": "linear-gradient(135deg,#0c3d6d 0%,#1165a8 50%,#4eb1e8 82%,#f0c44e 122%)",
}


@st.cache_data(show_spinner=False)
def get_public_reference_metrics() -> dict[str, int]:
    metrics = {"observations": 0, "diseases": 0, "provinces": 0, "zones": 0}
    for candidate in PROCESSED_DATA_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            frame = pd.read_csv(candidate)
        except Exception:
            continue
        normalized = {column: column.strip().upper() for column in frame.columns}
        frame = frame.rename(columns=normalized)

        disease_col = next((column for column in ["MALADIE", "DISEASE"] if column in frame.columns), None)
        province_col = next((column for column in ["PROVINCE", "PROV"] if column in frame.columns), None)
        zone_col = next((column for column in ["ZONE_SANTE", "ZS"] if column in frame.columns), None)

        metrics["observations"] = int(len(frame.index))
        if disease_col:
            metrics["diseases"] = int(frame[disease_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())
        if province_col:
            metrics["provinces"] = int(frame[province_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())
        if zone_col:
            metrics["zones"] = int(frame[zone_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())
        break

    for candidate in MODEL_SUMMARY_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            summary_df = pd.read_csv(candidate, encoding="utf-8-sig")
        except Exception:
            continue

        if "R² (Best)" in summary_df.columns:
            r2_values = pd.to_numeric(summary_df["R² (Best)"], errors="coerce")
            metrics["diseases"] = int(r2_values.ge(MIN_ACCEPTABLE_R2).fillna(False).sum())
            break

    return metrics


def apply_public_theme() -> None:
    st.markdown(PUBLIC_THEME, unsafe_allow_html=True)


def render_public_hero(
    eyebrow: str,
    title: str,
    subtitle: str,
    metrics: Sequence[tuple[str, str]],
    tone: str = "mission",
) -> None:
    metric_markup = "".join(
        f'<div class="public-metric"><div class="public-metric-value">{escape(value)}</div><div class="public-metric-label">{escape(label)}</div></div>'
        for value, label in metrics
    )
    gradient = HERO_GRADIENTS.get(tone, HERO_GRADIENTS["mission"])
    st.markdown(
        f"""
<div class="public-hero" style="background:{gradient}">
  <div class="public-hero-layout">
    <div class="public-hero-copy">
      <div class="public-kicker">{escape(eyebrow)}</div>
      <div class="public-title">{escape(title)}</div>
      <p class="public-sub">{escape(subtitle)}</p>
      <div class="public-metric-grid">{metric_markup}</div>
    </div>
    <div class="public-hero-visual" aria-hidden="true">
      <div class="public-signal-card">
        <div class="public-signal-line"><span style="width:82%"></span></div>
        <div class="public-signal-line"><span style="width:58%"></span></div>
        <div class="public-signal-line"><span style="width:70%"></span></div>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_public_steps(steps: Sequence[tuple[str, str, str, str]]) -> None:
    step_markup = "".join(
        f"""
<div class="public-step">
  <div class="public-step-index">{escape(index)}</div>
  <div class="public-step-body">
    <div class="public-step-title">{escape(title)}</div>
    <p class="public-step-copy">{escape(copy)}</p>
    <span class="public-step-tag">{escape(tag)}</span>
  </div>
</div>
"""
        for index, title, copy, tag in steps
    )
    st.markdown(f'<div class="public-step-list">{step_markup}</div>', unsafe_allow_html=True)
