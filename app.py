from __future__ import annotations

import base64
import html
import importlib.util
import urllib.parse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from biomarkers import advanced_category, biomarker_next_steps, calculate_biomarker_adjustment, required_raw_le8
from chatbot import render_chatbot
from fitness import CRF_CATEGORIES, calculate_fitness_adjustment, estimate_percentile_category
from le8_scoring import build_score_summary
from recommendations import estimate_gain, generate_30_day_plan, get_domain_recommendation, get_top_opportunities
from scoring import (
    calculate_bmi,
    calculate_total_score,
    category_for_total,
    score_activity,
    score_bmi,
    score_bp,
    score_diet,
    score_glucose,
    score_lipids,
    score_nicotine,
    score_sleep,
    status_for_score,
)


_copy_spec = importlib.util.spec_from_file_location("vital8_copy", Path(__file__).with_name("copy.py"))
_copy_module = importlib.util.module_from_spec(_copy_spec)
assert _copy_spec and _copy_spec.loader
_copy_spec.loader.exec_module(_copy_module)
DISCLAIMER = _copy_module.DISCLAIMER
BIOMARKER_EXPLAINERS = _copy_module.BIOMARKER_EXPLAINERS
DOMAIN_COPY = _copy_module.DOMAIN_COPY
DOMAIN_MEANINGS = _copy_module.DOMAIN_MEANINGS
EVIDENCE_NOTE = _copy_module.EVIDENCE_NOTE
LANDING_PARAGRAPHS = _copy_module.LANDING_PARAGRAPHS
LANDING_TITLE = _copy_module.LANDING_TITLE
WHAT_THIS_MEASURES = _copy_module.WHAT_THIS_MEASURES


DOMAIN_ORDER = [
    "Daily fuel",
    "Movement",
    "Nicotine",
    "Sleep rhythm",
    "Body size",
    "Cholesterol particles",
    "Blood sugar",
    "Blood pressure",
]

AUTHOR_PHOTO = Path("assets/menachem-jacobs-photo.jpg")
LOGO_PATH = Path("assets/vital8-logo.png")
ICON_PATH = Path("assets/vital8-icon.png")
FAVICON_PATH = Path("assets/vital8-favicon.png")
AUTHOR_EMAIL = "menachem.m.jacobs@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/menachem-jacobs-b35222122/"


st.set_page_config(
    page_title="Vital8 Heart Health Score",
    page_icon=Image.open(FAVICON_PATH) if FAVICON_PATH.exists() else "V8",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DEFAULTS = {
    "age": None,
    "sex": None,
    "fruit_veg": None,
    "whole_grains": None,
    "sugary_drinks": None,
    "processed_food": None,
    "healthy_proteins": None,
    "fish_seafood": None,
    "nuts_legumes": None,
    "sodium_foods": None,
    "fruit_veg_scale": 0,
    "whole_grains_scale": 0,
    "sugary_drinks_scale": 0,
    "processed_food_scale": 0,
    "healthy_proteins_scale": 0,
    "fish_seafood_scale": 0,
    "nuts_legumes_scale": 0,
    "sodium_foods_scale": 0,
    "moderate_minutes": None,
    "vigorous_minutes": None,
    "nicotine_current_use": None,
    "nicotine_former_status": None,
    "nicotine_quit_timing": None,
    "secondhand_exposure_status": None,
    "sleep_hours": None,
    "body_units": "us",
    "height_ft": None,
    "height_in": None,
    "weight_lbs": None,
    "height_cm": None,
    "weight_kg": None,
    "knows_lipids": False,
    "total_chol": None,
    "hdl": None,
    "has_diabetes": None,
    "glucose_method": None,
    "glucose_value": None,
    "knows_bp": False,
    "sbp": None,
    "dbp": None,
    "bp_treated": False,
    "advanced_enabled": False,
    "knows_hs_crp": False,
    "hs_crp": None,
    "knows_lpa": False,
    "lpa": None,
    "fitness_enabled": False,
    "fitness_method": None,
    "vo2max": None,
    "crf_percentile_category": None,
}

for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)

if st.session_state.whole_grains in {"0", "1", "2+"}:
    st.session_state.whole_grains = DEFAULTS["whole_grains"]
if st.session_state.healthy_proteins in {"0-1", "2-3", "4-6", "daily", "4+"}:
    st.session_state.healthy_proteins = DEFAULTS["healthy_proteins"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        :root {
          --navy: #0d1520;
          --teal: #1f5fd6;
          --green: #1f5fd6;
          --amber: #c0851b;
          --red: #e0414a;
          --bg: #eef1f6;
          --surface: #ffffff;
          --surface-soft: #e7efff;
          --border: #e2e7ef;
          --border-soft: #eef1f6;
          --ink-soft: #56627a;
          --ink-faint: #8a96aa;
          --red-soft: #fdeced;
          --amber-soft: #fbf2e0;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
          background: var(--bg);
          color: var(--navy);
          font-family: 'IBM Plex Sans', sans-serif;
        }
        [data-testid="stHeader"] { background: rgba(238, 241, 246, .82); }
        .block-container { padding-top: 1.25rem; max-width: 1200px; }
        h1, h2, h3, h4, h5, h6 {
          font-family: 'Archivo', sans-serif;
          letter-spacing: -.015em;
          color: var(--navy);
        }
        h1 { font-size: clamp(2.55rem, 5vw, 4.45rem); line-height: 1.02; margin-bottom: 1.1rem; }
        h2 { font-size: clamp(1.85rem, 3vw, 2.65rem); line-height: 1.07; }
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        .stCheckbox label,
        .stRadio label {
          color: var(--navy) !important;
        }
        div[data-testid="stTabs"] button { font-size: 1rem; font-weight: 700; }
        .brand-bar {
          position: sticky;
          top: 0;
          z-index: 30;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          padding: 14px 0 18px;
          margin-bottom: 12px;
          background: rgba(238, 241, 246, .86);
          backdrop-filter: blur(12px);
          border-bottom: 1px solid var(--border);
        }
        .brand-lockup {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          font-family: 'IBM Plex Mono', monospace;
          font-weight: 600;
          letter-spacing: .06em;
          font-size: .94rem;
        }
        .brand-logo-img {
          display: block;
          height: 34px;
          width: auto;
          object-fit: contain;
        }
        .diamond {
          width: 11px;
          height: 11px;
          background: var(--red);
          border-radius: 2px;
          transform: rotate(45deg);
          display: inline-block;
          flex: none;
        }
        .brand-nav {
          display: flex;
          align-items: center;
          gap: 20px;
          flex-wrap: wrap;
        }
        .brand-nav a {
          font-family: 'IBM Plex Mono', monospace;
          font-size: .78rem;
          font-weight: 600;
          letter-spacing: .03em;
          color: var(--ink-soft);
          text-decoration: none !important;
        }
        .brand-nav .nav-cta {
          color: #fff;
          background: var(--navy);
          border-radius: 8px;
          padding: 10px 16px;
        }
        .hero {
          display: grid;
          grid-template-columns: 1.05fr .95fr;
          gap: clamp(28px, 5vw, 60px);
          align-items: center;
          padding: clamp(34px, 6vw, 74px) 0 34px;
        }
        .hero p {
          max-width: 31em;
          font-size: 1.14rem;
          line-height: 1.58;
          margin: 0 0 1.25rem;
          text-wrap: pretty;
        }
        .hero-actions {
          display: flex;
          align-items: center;
          gap: 14px;
          flex-wrap: wrap;
          margin: 1.55rem 0 1.15rem;
        }
        .hero-button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border-radius: 9px;
          padding: 14px 22px;
          font-family: 'IBM Plex Mono', monospace;
          font-weight: 600;
          font-size: .86rem;
          letter-spacing: .02em;
          text-decoration: none !important;
          border: 1px solid var(--border);
        }
        .hero-button:hover,
        .hero-button:visited,
        .brand-nav a:hover,
        .brand-nav a:visited {
          text-decoration: none !important;
        }
        .hero-button.primary { background: var(--navy); color: #fff !important; border-color: var(--navy); }
        .hero-button.secondary { color: var(--navy) !important; background: transparent; }
        .proof-line {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          color: var(--ink-faint);
          font-family: 'IBM Plex Mono', monospace;
          font-size: .75rem;
          letter-spacing: .02em;
        }
        .hero-score-card {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: 18px;
          padding: 28px;
          box-shadow: 0 22px 50px -28px rgba(13, 21, 32, .32);
        }
        .score-card-top,
        .score-card-main {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 18px;
        }
        .score-card-top {
          margin-bottom: 18px;
          color: var(--ink-faint);
          font-family: 'IBM Plex Mono', monospace;
          font-size: .68rem;
          font-weight: 600;
          letter-spacing: .14em;
          text-transform: uppercase;
        }
        .sample-badge {
          border: 1px solid var(--border);
          border-radius: 999px;
          padding: 4px 9px;
        }
        .sample-ring {
          width: 128px;
          height: 128px;
          border-radius: 999px;
          background: conic-gradient(var(--teal) 0 82%, var(--border-soft) 82% 100%);
          display: grid;
          place-items: center;
          flex: none;
        }
        .sample-ring-inner {
          width: 94px;
          height: 94px;
          border-radius: 999px;
          background: var(--surface);
          display: grid;
          place-items: center;
          text-align: center;
          font-family: 'IBM Plex Mono', monospace;
        }
        .sample-ring-score {
          display: block;
          color: var(--navy);
          font-size: 2.45rem;
          font-weight: 600;
          line-height: 1;
        }
        .sample-ring-denom {
          color: var(--ink-faint);
          font-size: .65rem;
          letter-spacing: .12em;
        }
        .sample-status {
          display: inline-flex;
          background: var(--surface-soft);
          color: var(--teal);
          font-family: 'IBM Plex Mono', monospace;
          font-size: .75rem;
          font-weight: 600;
          letter-spacing: .03em;
          border-radius: 999px;
          padding: 6px 11px;
          margin-bottom: 10px;
        }
        .sample-copy {
          color: var(--ink-soft);
          font-size: .88rem !important;
          line-height: 1.5 !important;
          margin: 0 !important;
        }
        .sample-bars {
          display: flex;
          flex-direction: column;
          gap: 9px;
          margin-top: 22px;
        }
        .sample-bar {
          display: grid;
          grid-template-columns: 96px 1fr 30px;
          gap: 12px;
          align-items: center;
          font-family: 'IBM Plex Mono', monospace;
          font-size: .69rem;
          color: var(--ink-soft);
        }
        .sample-track {
          height: 7px;
          background: var(--border-soft);
          border-radius: 999px;
          overflow: hidden;
        }
        .sample-fill {
          height: 100%;
          border-radius: 999px;
          background: var(--teal);
        }
        .result-score-card {
          margin: 8px 0 22px;
        }
        .result-score-card .score-card-main {
          justify-content: flex-start;
          gap: 26px;
          align-items: flex-start;
        }
        .result-summary {
          max-width: 620px;
        }
        .result-summary h2 {
          margin: 8px 0 10px;
          font-size: clamp(1.7rem, 3vw, 2.4rem);
        }
        .partial-note {
          display: inline-flex;
          margin-top: 12px;
          color: var(--ink-soft);
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 999px;
          padding: 7px 12px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: .72rem;
          letter-spacing: .02em;
        }
        .result-bars {
          margin-top: 24px;
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px 22px;
        }
        .card {
          border-radius: 14px;
          padding: 22px;
          background: var(--surface);
          border: 1px solid var(--border);
          box-shadow: none;
          height: 100%;
        }
        .card h3 {
          margin: 0 0 10px;
          font-size: 1.25rem;
          line-height: 1.18;
        }
        .card p {
          margin-bottom: 0;
          font-size: 1rem;
          line-height: 1.55;
        }
        .equal-card { min-height: 118px; }
        .plan-card { min-height: 175px; }
        .metric-card { min-height: 158px; }
        .intro-strip {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 1px;
          overflow: hidden;
          border: 1px solid var(--border);
          border-radius: 14px;
          background: var(--border);
        }
        .intro-item {
          background: var(--surface);
          padding: 18px;
          min-height: 132px;
        }
        .intro-item h3 {
          margin: 0 0 8px;
          font-size: 1.08rem;
          line-height: 1.2;
        }
        .intro-item p {
          margin: 0;
          color: var(--ink-soft);
          font-size: .96rem;
          line-height: 1.45;
        }
        .evidence-band {
          display: grid;
          grid-template-columns: 1.25fr repeat(3, minmax(0, .55fr));
          gap: 18px;
          align-items: stretch;
          padding: 24px;
          border-radius: 18px;
          background: #11243a;
          color: #ffffff;
          box-shadow: 0 14px 34px rgba(17, 36, 58, .12);
        }
        .evidence-band h2,
        .evidence-band h3,
        .evidence-band p {
          color: #ffffff !important;
        }
        .evidence-band h2 {
          margin: 0 0 8px;
          font-size: clamp(1.55rem, 3vw, 2.25rem);
        }
        .evidence-band p {
          margin: 0;
          line-height: 1.52;
          opacity: .88;
        }
        .evidence-stat {
          border-left: 1px solid rgba(255,255,255,.18);
          padding-left: 18px;
        }
        .evidence-stat h3 {
          margin: 0 0 6px;
          font-size: 1.55rem;
        }
        .evidence-stat p {
          font-size: .9rem;
        }
        .compact-explainer {
          border-radius: 14px;
          padding: 16px 18px;
          background: var(--surface);
          border: 1px solid var(--border);
          box-shadow: 0 8px 20px rgba(17, 36, 58, .045);
        }
        .compact-explainer-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 14px;
        }
        .compact-explainer-item {
          border-left: 2px solid rgba(31, 95, 214, .35);
          padding-left: 12px;
        }
        .compact-explainer-item h3 {
          margin: 0 0 4px;
          font-size: 1rem;
          line-height: 1.2;
        }
        .compact-explainer-item p {
          margin: 0;
          color: var(--ink-soft);
          font-size: .92rem;
          line-height: 1.35;
        }
        .author-note {
          border-radius: 8px;
          padding: 22px;
          background: var(--surface);
          border: 1px solid var(--border);
          box-shadow: 0 12px 30px rgba(17, 36, 58, .06);
        }
        .small-label {
          margin: 0 0 8px;
          color: var(--red);
          font-family: 'IBM Plex Mono', monospace;
          font-size: .78rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: .14em;
        }
        .muted { color: var(--ink-soft); }
        .score-number { font-size: 4.5rem; line-height: 1; font-weight: 850; color: var(--navy); }
        .status-Strong { color: var(--green); font-weight: 800; }
        .status-Opportunity { color: var(--amber); font-weight: 800; }
        .status-Priority { color: var(--red); font-weight: 800; }
        .status-Not-entered { color: #697586; font-weight: 800; }
        .disclaimer {
          border-left: 4px solid var(--red);
          background: var(--surface);
          border-radius: 8px;
          padding: 14px 16px;
          color: var(--ink-soft);
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        input,
        textarea {
          background-color: var(--surface) !important;
          color: var(--navy) !important;
          border-color: var(--border) !important;
        }
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] svg,
        input::placeholder,
        textarea::placeholder {
          color: var(--ink-soft) !important;
          fill: var(--ink-soft) !important;
        }
        div[data-baseweb="popover"],
        ul[role="listbox"] {
          background: var(--surface) !important;
          color: var(--navy) !important;
        }
        ul[role="listbox"] li,
        div[role="option"] {
          color: var(--navy) !important;
        }
        .stButton > button {
          border-radius: 9px;
          border: 0;
          color: white;
          background: var(--navy);
          font-family: 'IBM Plex Mono', monospace;
          font-weight: 600;
          padding: .75rem 1.2rem;
        }
        .st-key-vital8_ai_floating {
          position: fixed;
          right: 22px;
          bottom: 22px;
          z-index: 9999;
          width: min(220px, calc(100vw - 32px));
          pointer-events: none;
        }
        .st-key-vital8_ai_floating > div {
          pointer-events: auto;
        }
        .st-key-vital8_ai_floating button {
          box-shadow: 0 14px 40px rgba(17, 36, 58, .22);
        }
        .st-key-vital8_ai_floating button::before {
          content: "";
          width: 22px;
          height: 22px;
          background-image: var(--vital8-ai-icon);
          background-size: contain;
          background-repeat: no-repeat;
          background-position: center;
          display: inline-block;
          margin-right: 4px;
          vertical-align: middle;
        }
        div[data-testid="stPopoverBody"] {
          width: min(420px, calc(100vw - 32px));
          max-height: min(720px, calc(100vh - 120px));
          overflow-y: auto;
        }
        div[data-testid="stPopoverBody"] .stButton > button {
          background: #ffffff !important;
          color: var(--navy) !important;
          border: 1px solid #c7d0dc !important;
          box-shadow: none !important;
        }
        div[data-testid="stPopoverBody"] .stButton > button:hover {
          background: #eef2f7 !important;
          border-color: #aeb9c7 !important;
        }
        div[data-testid="stPopoverBody"] .stButton > button::before {
          content: none !important;
          display: none !important;
        }
        @media (max-width: 900px) {
          .brand-bar {
            position: static;
            align-items: flex-start;
          }
          .brand-nav {
            display: none;
          }
          .hero {
            grid-template-columns: 1fr;
            padding-top: 28px;
          }
          .hero-score-card {
            padding: 22px;
          }
          .score-card-main {
            align-items: flex-start;
          }
          .result-score-card .score-card-main {
            flex-direction: column;
          }
          .result-bars {
            grid-template-columns: 1fr;
          }
          .sample-ring {
            width: 108px;
            height: 108px;
          }
          .sample-ring-inner {
            width: 80px;
            height: 80px;
          }
          .sample-ring-score {
            font-size: 2rem;
          }
          .intro-strip,
          .evidence-band,
          .compact-explainer-grid {
            grid-template-columns: 1fr;
          }
          .evidence-stat {
            border-left: 0;
            border-top: 1px solid rgba(255,255,255,.18);
            padding-left: 0;
            padding-top: 14px;
          }
          .st-key-vital8_ai_floating {
            right: 12px;
            bottom: 12px;
            width: calc(100vw - 24px);
          }
          .st-key-vital8_ai_floating > div > div > button {
            width: 100%;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, label: str | None = None, class_name: str = "") -> None:
    label_html = f"<p class='small-label'>{label}</p>" if label else ""
    st.markdown(f"<div class='card {class_name}'>{label_html}<h3>{title}</h3><p class='muted'>{body}</p></div>", unsafe_allow_html=True)


def integrated_advanced_score(raw_score: int | None, fitness_adjustment: dict, biomarker_adjustment: dict) -> dict:
    if raw_score is None:
        return {"score": None, "delta": None, "fitness_multiplier": None, "biomarker_multiplier": None, "active_lenses": []}

    active_lenses: list[str] = []
    fitness_multiplier = fitness_adjustment.get("vmq")
    biomarker_multiplier = biomarker_adjustment.get("combined_multiplier")

    combined = float(raw_score)
    if fitness_multiplier is not None:
        combined *= fitness_multiplier
        active_lenses.append("fitness")
    if biomarker_multiplier is not None:
        combined /= biomarker_multiplier
        active_lenses.append("biomarkers")

    if not active_lenses:
        return {"score": None, "delta": None, "fitness_multiplier": None, "biomarker_multiplier": None, "active_lenses": []}

    score = round(max(0, min(100, combined)))
    return {
        "score": score,
        "delta": score - raw_score,
        "fitness_multiplier": fitness_multiplier,
        "biomarker_multiplier": biomarker_multiplier,
        "active_lenses": active_lenses,
    }


def optional_number(label: str, known: bool, min_value: float, max_value: float, value: float | None, step: float, help_text: str = "") -> float | None:
    if not known:
        return None
    return st.number_input(label, min_value=min_value, max_value=max_value, value=value, step=step, placeholder="Enter value", help=help_text)


def legacy_diet_args() -> tuple[str | None, str, str | None, str | None, str, str, str, str]:
    grain_map = {"0": "rarely", "1": "sometimes", "2+": "most", "rarely": "rarely", "sometimes": "sometimes", "most": "most", "always": "always"}
    protein_map = {
        "daily": "plant_fish",
        "4+": "plant_fish",
        "4-6": "mixed",
        "2-3": "lean_meat",
        "0-1": "red_processed",
        "plant_fish": "plant_fish",
        "mixed": "mixed",
        "lean_meat": "lean_meat",
        "red_processed": "red_processed",
    }
    return (
        st.session_state.fruit_veg,
        grain_map.get(st.session_state.whole_grains, "sometimes"),
        st.session_state.sugary_drinks,
        st.session_state.processed_food,
        protein_map.get(st.session_state.healthy_proteins, "mixed"),
        st.session_state.fish_seafood or "monthly",
        st.session_state.nuts_legumes or "weekly",
        st.session_state.sodium_foods or "sometimes",
    )


DIET_BLANK = "Not answered"
DIET_SCALE_OPTIONS = list(range(0, 11))


def diet_scale(label: str, key: str, low_label: str, high_label: str, help_text: str | None = None) -> int:
    if st.session_state.get(key) == DIET_BLANK:
        st.session_state[key] = 0
    value = st.select_slider(
        label,
        options=DIET_SCALE_OPTIONS,
        key=key,
        help=help_text,
    )
    st.caption(f"0 = {low_label} | 10 = {high_label}")
    if value == 0:
        st.markdown(
            "<span style='color:#e0414a; font-size:.86rem; font-weight:600;'>Defaulted to 0. Move this if 0 does not reflect your usual pattern.</span>",
            unsafe_allow_html=True,
        )
    return int(value)


def sync_diet_scale_answers() -> None:
    fruit = st.session_state.fruit_veg_scale
    st.session_state.fruit_veg = "0" if fruit == 0 else "1-2" if fruit <= 2 else "3-4" if fruit <= 4 else "5+"

    grains = st.session_state.whole_grains_scale
    st.session_state.whole_grains = "rarely" if grains <= 2 else "sometimes" if grains <= 5 else "most" if grains <= 8 else "always"

    drinks = st.session_state.sugary_drinks_scale
    st.session_state.sugary_drinks = "0" if drinks == 0 else "1-3" if drinks <= 3 else "4-7" if drinks <= 7 else "7+"

    processed = st.session_state.processed_food_scale
    st.session_state.processed_food = "0-1" if processed <= 1 else "2-3" if processed <= 3 else "4-6" if processed <= 6 else "7+"

    proteins = st.session_state.healthy_proteins_scale
    st.session_state.healthy_proteins = (
        "red_processed"
        if proteins <= 2
        else "lean_meat"
        if proteins <= 4
        else "mixed"
        if proteins <= 7
        else "plant_fish"
    )

    fish = st.session_state.fish_seafood_scale
    st.session_state.fish_seafood = "rarely" if fish <= 2 else "monthly" if fish <= 4 else "1" if fish <= 7 else "2+"

    nuts = st.session_state.nuts_legumes_scale
    st.session_state.nuts_legumes = "rarely" if nuts <= 2 else "weekly" if nuts <= 4 else "few_weekly" if nuts <= 7 else "most_days"

    sodium = st.session_state.sodium_foods_scale
    st.session_state.sodium_foods = "rarely" if sodium <= 2 else "sometimes" if sodium <= 6 else "often"


def score_diet_with_blank_check() -> dict:
    sync_diet_scale_answers()
    diet_values = [
        st.session_state.fruit_veg,
        st.session_state.whole_grains,
        st.session_state.sugary_drinks,
        st.session_state.processed_food,
        st.session_state.healthy_proteins,
        st.session_state.fish_seafood,
        st.session_state.nuts_legumes,
        st.session_state.sodium_foods,
    ]
    if any(value is None for value in diet_values):
        return {
            "score": None,
            "label": "Not complete",
            "explanation": "Answer each diet question to estimate this LE8-style eating-pattern score.",
        }
    try:
        return score_diet(*diet_values)
    except (TypeError, KeyError):
        return score_diet(*legacy_diet_args())


def legacy_nicotine_status() -> str:
    if st.session_state.nicotine_current_use is None:
        return "none"
    if st.session_state.nicotine_current_use in {"combustible", "dual"}:
        return "current_tobacco"
    if st.session_state.nicotine_current_use == "ecig_smokeless":
        return "current_nicotine"
    if st.session_state.nicotine_former_status != "former":
        return "none"
    if st.session_state.nicotine_quit_timing in {"10_plus", "5_9"}:
        return "quit_5_plus"
    if st.session_state.nicotine_quit_timing in {"3_4", "1_2"}:
        return "quit_1_5"
    return "quit_under_1"


def score_nicotine_with_fallback() -> dict:
    if st.session_state.nicotine_current_use is None:
        return {
            "score": None,
            "label": "Not entered",
            "explanation": "Answer the nicotine and secondhand exposure questions to score this domain.",
        }
    if st.session_state.nicotine_current_use == "none" and st.session_state.nicotine_former_status is None:
        return {
            "score": None,
            "label": "Not complete",
            "explanation": "Select whether you are a never-user or former user.",
        }
    if st.session_state.nicotine_former_status == "former" and st.session_state.nicotine_quit_timing is None:
        return {
            "score": None,
            "label": "Not complete",
            "explanation": "Select how long ago you quit nicotine or tobacco.",
        }
    if st.session_state.secondhand_exposure_status is None:
        return {
            "score": None,
            "label": "Not complete",
            "explanation": "Select whether you have regular secondhand smoke or vapor exposure.",
        }
    try:
        return score_nicotine(
            st.session_state.nicotine_current_use,
            st.session_state.nicotine_former_status == "former",
            st.session_state.nicotine_quit_timing,
            st.session_state.secondhand_exposure_status == "yes",
        )
    except TypeError:
        return score_nicotine(legacy_nicotine_status())


def collect_scores() -> tuple[dict, dict]:
    height_inches = None
    weight_lbs = None
    if st.session_state.body_units == "metric":
        if st.session_state.height_cm is not None:
            height_inches = st.session_state.height_cm / 2.54
        if st.session_state.weight_kg is not None:
            weight_lbs = st.session_state.weight_kg * 2.2046226218
    elif st.session_state.height_ft is not None and st.session_state.height_in is not None:
        height_inches = st.session_state.height_ft * 12 + st.session_state.height_in
        weight_lbs = st.session_state.weight_lbs
    bmi = calculate_bmi(height_inches, weight_lbs)
    diet = score_diet_with_blank_check()
    activity = score_activity(st.session_state.moderate_minutes, st.session_state.vigorous_minutes)
    lipids = score_lipids(
        st.session_state.total_chol if st.session_state.knows_lipids else None,
        st.session_state.hdl if st.session_state.knows_lipids else None,
    )
    glucose_value = None if st.session_state.glucose_method in {None, "unknown"} else st.session_state.glucose_value
    bp = score_bp(
        st.session_state.sbp if st.session_state.knows_bp else None,
        st.session_state.dbp if st.session_state.knows_bp else None,
        st.session_state.bp_treated,
    )
    components = {
        "Daily fuel": diet,
        "Movement": activity,
        "Nicotine": score_nicotine_with_fallback(),
        "Sleep rhythm": score_sleep(st.session_state.sleep_hours),
        "Body size": score_bmi(bmi),
        "Cholesterol particles": lipids,
        "Blood sugar": score_glucose(st.session_state.glucose_method, glucose_value, st.session_state.has_diabetes),
        "Blood pressure": bp,
    }
    raw = {
        "age": st.session_state.age,
        "sex": st.session_state.sex,
        "bmi": bmi,
        "diet": {
            "fruit_veg": st.session_state.fruit_veg,
            "whole_grains": st.session_state.whole_grains,
            "sugary_drinks": st.session_state.sugary_drinks,
            "processed_food": st.session_state.processed_food,
            "healthy_proteins": st.session_state.healthy_proteins,
            "fish_seafood": st.session_state.fish_seafood,
            "nuts_legumes": st.session_state.nuts_legumes,
            "sodium_foods": st.session_state.sodium_foods,
        },
        "nicotine": {
            "current_use": st.session_state.nicotine_current_use,
            "former_status": st.session_state.nicotine_former_status,
            "quit_timing": st.session_state.nicotine_quit_timing,
            "secondhand_exposure": st.session_state.secondhand_exposure_status,
        },
        "body_units": st.session_state.body_units,
        "height_inches": height_inches,
        "height_cm": st.session_state.height_cm if st.session_state.body_units == "metric" else None,
        "weight_lbs": weight_lbs,
        "weight_kg": st.session_state.weight_kg if st.session_state.body_units == "metric" else None,
        "sleep_hours": st.session_state.sleep_hours,
        "moderate_minutes": st.session_state.moderate_minutes,
        "vigorous_minutes": st.session_state.vigorous_minutes,
        "activity_equivalent": activity.get("equivalent_minutes", 0),
        "known_lipids": st.session_state.knows_lipids,
        "total_cholesterol": st.session_state.total_chol if st.session_state.knows_lipids else None,
        "hdl_cholesterol": st.session_state.hdl if st.session_state.knows_lipids else None,
        "non_hdl_cholesterol": lipids.get("non_hdl"),
        "known_bp": st.session_state.knows_bp,
        "systolic_bp": st.session_state.sbp if st.session_state.knows_bp else None,
        "diastolic_bp": st.session_state.dbp if st.session_state.knows_bp else None,
        "bp_treated": st.session_state.bp_treated,
        "glucose_method": st.session_state.glucose_method,
        "glucose_value": glucose_value,
        "has_diabetes": st.session_state.has_diabetes,
    }
    return components, raw


def gauge(score: int | None) -> go.Figure:
    value = score or 0
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number" if score is not None else "gauge",
            value=value,
            number={"suffix": "/100", "font": {"size": 54}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0},
                "bar": {"color": "#11a7a4"},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "#f8ddda"},
                    {"range": [50, 80], "color": "#faecd1"},
                    {"range": [80, 100], "color": "#dff4eb"},
                ],
            },
        )
    )
    if score is None:
        fig.add_annotation(
            text="--/100",
            x=0.5,
            y=0.28,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 54, "color": "#6f7785"},
        )
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def radar_chart(components: dict) -> go.Figure:
    labels = DOMAIN_ORDER
    values = [components[name]["score"] if components[name]["score"] is not None else 0 for name in labels]
    fig = go.Figure(go.Scatterpolar(r=values + values[:1], theta=labels + labels[:1], fill="toself", line_color="#11a7a4"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=390,
        margin=dict(l=40, r=40, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def bar_chart(components: dict) -> go.Figure:
    rows = sorted(
        [{"Domain": name, "Score": result["score"] if result["score"] is not None else 0} for name, result in components.items()],
        key=lambda row: row["Score"],
    )
    colors = ["#c9473d" if row["Score"] < 50 else "#d88a1d" if row["Score"] < 75 else "#1d9a6c" for row in rows]
    fig = go.Figure(go.Bar(x=[row["Score"] for row in rows], y=[row["Domain"] for row in rows], orientation="h", marker_color=colors))
    fig.update_layout(
        xaxis=dict(range=[0, 100]),
        height=390,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def component_dataframe(components: dict, raw: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Domain": name,
                "Score": "Not entered" if result["score"] is None else f"{result['score']}/100",
                "Status": status_for_score(result["score"]),
                "Meaning": DOMAIN_MEANINGS.get(name, result["explanation"]),
                "Suggested next step": get_domain_recommendation(name, result["score"], raw),
            }
            for name, result in components.items()
        ]
    )


def newsletter_url() -> str:
    try:
        return st.secrets.get("SUBSTACK_URL", "https://vital8.substack.com/")
    except Exception:
        return "https://vital8.substack.com/"


def asset_data_url(path: Path, mime: str | None = None) -> str:
    if mime is None:
        suffix = path.suffix.lower()
        if suffix == ".svg":
            mime = "image/svg+xml"
        elif suffix in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        else:
            mime = "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def linked_author_photo() -> str:
    return f"""
    <a href="{AUTHOR_LINKEDIN}" target="_blank" rel="noopener noreferrer" aria-label="Menachem Jacobs LinkedIn profile">
      <img src="{asset_data_url(AUTHOR_PHOTO, 'image/jpeg')}" alt="Menachem Jacobs" style="width:110px; border-radius:8px; display:block;" />
    </a>
    """


def score_color(score: int | float | None) -> str:
    if score is None:
        return "var(--border)"
    if score >= 80:
        return "var(--teal)"
    if score >= 50:
        return "var(--amber)"
    return "var(--red)"


def score_soft_color(score: int | float | None) -> str:
    if score is None:
        return "var(--bg)"
    if score >= 80:
        return "var(--surface-soft)"
    if score >= 50:
        return "var(--amber-soft)"
    return "var(--red-soft)"


def score_display_label(score: int | float | None) -> str:
    if score is None:
        return "Add more data"
    if score >= 80:
        return "High cardiovascular health"
    if score >= 50:
        return "Moderate cardiovascular health"
    return "Low cardiovascular health"


def result_score_card(components: dict, score: int | None, category: str, category_copy: str, total: dict) -> str:
    score_text = "--" if score is None else str(score)
    ring_value = 0 if score is None else max(0, min(100, score))
    ring_color = score_color(score)
    status_color = score_color(score)
    status_soft = score_soft_color(score)
    partial = f"Snapshot based on {total['known_count']} of 8 levers." if total["is_partial"] else "Complete score based on all 8 levers."
    rows = []
    for domain in DOMAIN_ORDER:
        result = components[domain]
        domain_score = result["score"]
        width = 0 if domain_score is None else max(0, min(100, domain_score))
        label = html.escape(domain)
        display = "--" if domain_score is None else str(domain_score)
        fill = score_color(domain_score)
        rows.append(
            f"<div class='sample-bar'><span>{label}</span><div class='sample-track'><div class='sample-fill' style='width:{width}%; background:{fill}'></div></div><span>{display}</span></div>"
        )
    return (
        "<section class='hero-score-card result-score-card'>"
        "<div class='score-card-top'><span>Your LE8 score</span><span class='sample-badge'>Live result</span></div>"
        "<div class='score-card-main'>"
        f"<div class='sample-ring' style='background:conic-gradient({ring_color} 0 {ring_value}%, var(--border-soft) {ring_value}% 100%)'>"
        "<div class='sample-ring-inner'>"
        f"<span class='sample-ring-score'>{score_text}</span><span class='sample-ring-denom'>/ 100</span>"
        "</div></div>"
        "<div class='result-summary'>"
        f"<div class='sample-status' style='background:{status_soft}; color:{status_color}'>{html.escape(score_display_label(score))}</div>"
        f"<h2>{html.escape(category)}</h2>"
        f"<p class='sample-copy'>{html.escape(category_copy)}</p>"
        f"<span class='partial-note'>{html.escape(partial)}</span>"
        "</div></div>"
        f"<div class='result-bars'>{''.join(rows)}</div>"
        "</section>"
    )


def share_summary_text(
    score: int | None,
    category: str,
    total: dict,
    top_opportunities: list[tuple[str, dict]],
    strengths: list[tuple[str, dict]],
    plan: dict[str, str],
) -> str:
    score_line = (
        f"My Vital8 LE8 score is {score}/100 ({category})."
        if score is not None
        else f"My Vital8 snapshot is not complete yet. I entered {total['known_count']} of 8 areas."
    )
    strength_line = (
        "Strongest areas: " + ", ".join(f"{name} ({result['score']}/100)" for name, result in strengths[:3]) + "."
        if strengths
        else "Strongest areas will become clearer once more domains are complete."
    )
    lever_line = (
        "Highest-ROI levers: " + ", ".join(f"{name} ({result['score']}/100)" for name, result in top_opportunities[:3]) + "."
        if top_opportunities
        else "Highest-ROI levers will appear once enough domains are entered."
    )
    return "\n".join(
        [
            "Vital8 Heart Health Score",
            score_line,
            strength_line,
            lever_line,
            "",
            "My next 30 days:",
            f"1. Behavior: {plan['behavior']}",
            f"2. Measurement: {plan['measurement']}",
            f"3. Follow-up: {plan['clinician_or_lab']}",
            "",
            "Vital8 is educational only and does not replace clinician-guided care.",
            "Try it: https://vital8-score.streamlit.app/",
        ]
    )


inject_css()
logo_data_url = asset_data_url(LOGO_PATH) if LOGO_PATH.exists() else ""
icon_data_url = asset_data_url(ICON_PATH) if ICON_PATH.exists() else ""
st.markdown(
    f"""
    <style>
      :root {{ --vital8-ai-icon: url("{icon_data_url}"); }}
    </style>
    """,
    unsafe_allow_html=True,
)

landing_body = "\n".join(
    f"<p class='muted'>{paragraph}</p>"
    for paragraph in LANDING_PARAGRAPHS
)

st.markdown(
    f"""
    <header class='brand-bar'>
      <div class='brand-lockup'><img class='brand-logo-img' src='{logo_data_url}' alt='Vital8' /></div>
      <nav class='brand-nav'>
        <a href='#how-it-works'>How it works</a>
        <a href='#eight-levers'>The 8 levers</a>
        <a class='nav-cta' href='#assessment'>Start assessment</a>
      </nav>
    </header>
    <section class='hero'>
      <div>
        <p class='small-label'><span class='diamond'></span> Life's Essential 8 assessment</p>
        <h1>{LANDING_TITLE}</h1>
        {landing_body}
        <div class='hero-actions'>
          <a class='hero-button primary' href='#assessment'>Start free assessment</a>
          <a class='hero-button secondary' href='#how-it-works'>See how scoring works</a>
        </div>
        <div class='proof-line'>
          <span>No signup</span><span>·</span><span>No paywall</span><span>·</span><span>Labs optional</span><span>·</span><span>No black-box longevity score</span>
        </div>
      </div>
      <aside class='hero-score-card'>
        <div class='score-card-top'>
          <span>Your LE8 score</span>
          <span class='sample-badge'>Sample</span>
        </div>
        <div class='score-card-main'>
          <div class='sample-ring'>
            <div class='sample-ring-inner'>
              <span class='sample-ring-score'>82</span>
              <span class='sample-ring-denom'>/ 100</span>
            </div>
          </div>
          <div>
            <div class='sample-status'>High cardiovascular health</div>
            <p class='sample-copy'>Top-tier foundation. Biggest opportunity: <strong>sleep consistency</strong>.</p>
          </div>
        </div>
        <div class='sample-bars'>
          <div class='sample-bar'><span>Nutrition</span><div class='sample-track'><div class='sample-fill' style='width:85%'></div></div><span>85</span></div>
          <div class='sample-bar'><span>Activity</span><div class='sample-track'><div class='sample-fill' style='width:90%'></div></div><span>90</span></div>
          <div class='sample-bar'><span>Nicotine</span><div class='sample-track'><div class='sample-fill' style='width:100%'></div></div><span>100</span></div>
          <div class='sample-bar'><span>Sleep</span><div class='sample-track'><div class='sample-fill' style='width:55%; background:var(--amber)'></div></div><span>55</span></div>
          <div class='sample-bar'><span>Body size</span><div class='sample-track'><div class='sample-fill' style='width:80%'></div></div><span>80</span></div>
          <div class='sample-bar'><span>Cholesterol</span><div class='sample-track'><div class='sample-fill' style='width:90%'></div></div><span>90</span></div>
          <div class='sample-bar'><span>Blood sugar</span><div class='sample-track'><div class='sample-fill' style='width:100%'></div></div><span>100</span></div>
          <div class='sample-bar'><span>Blood pressure</span><div class='sample-track'><div class='sample-fill' style='width:75%; background:var(--amber)'></div></div><span>75</span></div>
        </div>
      </aside>
    </section>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.markdown(
    """
    <section id='how-it-works' class='intro-strip'>
      <div class='intro-item'>
        <p class='small-label'>Step 1</p>
        <h3>Answer eight levers</h3>
        <p>Plain questions about everyday health. No lab results required to begin.</p>
      </div>
      <div class='intro-item'>
        <p class='small-label'>Step 2</p>
        <h3>Get your composite score</h3>
        <p>See your 0-100 LE8 score and which lever is dragging it down.</p>
      </div>
      <div class='intro-item'>
        <p class='small-label'>Step 3</p>
        <h3>Make one clear move</h3>
        <p>Leave with a practical 30-day focus, not a vague to-do list.</p>
      </div>
      <div class='intro-item'>
        <p class='small-label'>Optional</p>
        <h3>Add deeper context</h3>
        <p>Layer in VO2max, hsCRP, and Lp(a) when you want a sharper picture.</p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.markdown(
    f"""
    <section class='evidence-band'>
      <div>
        <h2>Why this matters</h2>
        <p>Cardiovascular disease is the leading cause of death. LE8 measures the prevention levers most tied to longevity, mortality, and years lived well.</p>
      </div>
      <div class='evidence-stat'>
        <h3>0-100</h3>
        <p>Each domain gets a plain-language score.</p>
      </div>
      <div class='evidence-stat'>
        <h3>Higher is better</h3>
        <p>Better LE8 scores are linked with lower mortality and more healthy years.</p>
      </div>
      <div class='evidence-stat'>
        <h3>No gimmick</h3>
        <p>No supplement stack. No mystery score.</p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.write("")

st.markdown(f"<div class='disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)
st.info(WHAT_THIS_MEASURES)
st.caption(EVIDENCE_NOTE)

with st.expander("Learn more about Vital8 and why it was built"):
    st.write(
        "I'm Menachem Jacobs, MD, MPH, an Internal Medicine resident and "
        "[preventive cardiology researcher](https://pubmed.ncbi.nlm.nih.gov/?term=menachem+jacobs&sort=date). "
        "I built Vital8 because prevention often fails at the translation step: people hear that lifestyle and risk factors matter, "
        "but they do not always know where they stand or which change would help most."
    )
    st.write(
        "Vital8 is meant to be a free, evidence-based starting point. The standard LE8 score comes first. "
        "The VO2max and biomarker sections are optional exploratory layers for people who want a more refined prevention conversation."
    )

st.divider()
st.markdown("<span id='assessment'></span>", unsafe_allow_html=True)
st.header("Your LE8 assessment")
st.caption("Complete the sections in one scroll. If you do not know a lab or blood pressure value, leave it blank and Vital8 will calculate a partial score.")
st.progress(1.0, text="8 Life's Essential 8 sections")

with st.container(border=True):
    st.markdown("<p class='small-label'>About you</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Age", min_value=18, max_value=100, value=None, placeholder="Enter age", key="age")
    with c2:
        st.selectbox("Sex", ["Female", "Male", "Other", "Prefer not to say"], index=None, placeholder="Choose one", key="sex")

with st.container(border=True):
    st.markdown("<p class='small-label'>1 of 8 - LE8 diet domain</p>", unsafe_allow_html=True)
    st.subheader("Your daily fuel")
    st.caption(DOMAIN_COPY["Daily fuel"])
    st.caption("Use the 0-10 scales below. They will be translated into an LE8-style diet estimate.")
    diet_scale(
        "On a typical day, how many servings of fruits and vegetables do you eat?",
        "fruit_veg_scale",
        "none",
        "10+ servings",
        help_text="One serving is about a handful, a cup of salad, or one piece of fruit. Estimate your usual day, not your best day.",
    )
    diet_scale(
        "How often do you choose whole-grain foods over white or refined grains?",
        "whole_grains_scale",
        "rarely or never",
        "almost always",
        help_text="Examples include oatmeal, whole wheat bread, brown rice, quinoa, barley, or high-fiber cereal.",
    )
    diet_scale(
        "In a typical week, how many sugary drinks do you have?",
        "sugary_drinks_scale",
        "none",
        "10+ drinks",
        help_text="Include soda, sweet tea, juice drinks, energy drinks, and sweetened coffee drinks.",
    )
    diet_scale(
        "In a typical week, how many meals come from fast food, fried food, or heavily processed foods?",
        "processed_food_scale",
        "none",
        "10+ meals",
        help_text="Estimate meals or snack occasions per week.",
    )
    diet_scale(
        "How heart-healthy are your usual protein sources?",
        "healthy_proteins_scale",
        "mostly red or processed meat",
        "mostly plants, beans, nuts, fish",
        help_text="Examples of heart-healthy proteins include fish, beans, lentils, tofu, nuts, and seeds.",
    )
    diet_scale(
        "How often do you eat fish or seafood?",
        "fish_seafood_scale",
        "rarely or never",
        "2+ times per week",
    )
    diet_scale(
        "How often do you eat nuts, seeds, beans, or lentils?",
        "nuts_legumes_scale",
        "rarely or never",
        "most days",
    )
    diet_scale(
        "How often do you add salt at the table or eat high-sodium foods?",
        "sodium_foods_scale",
        "rarely",
        "often",
        help_text="Examples include canned soups, chips, soy sauce, pickled foods, deli meats, and frequent restaurant meals.",
    )

with st.container(border=True):
    st.markdown("<p class='small-label'>2 of 8 - LE8 activity domain</p>", unsafe_allow_html=True)
    st.subheader("How much do you move?")
    st.caption(DOMAIN_COPY["Movement"])
    c1, c2 = st.columns(2)
    with c1:
        st.number_input(
            "In an average week over the past month, how many minutes did you spend doing moderate activity?",
            min_value=0,
            max_value=2000,
            value=None,
            step=10,
            placeholder="Enter minutes",
            key="moderate_minutes",
            help="Moderate means your breathing picks up, but you can still talk. Examples: brisk walking, cycling, dancing, swimming, or yard work.",
        )
    with c2:
        st.number_input(
            "In an average week over the past month, how many minutes did you spend doing vigorous activity?",
            min_value=0,
            max_value=1000,
            value=None,
            step=10,
            placeholder="Enter minutes",
            key="vigorous_minutes",
            help="Vigorous means you are breathing hard and can only say a few words at a time.",
        )

c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("<p class='small-label'>3 of 8 - LE8 nicotine domain</p>", unsafe_allow_html=True)
        st.subheader("Nicotine and smoke exposure")
        st.caption(DOMAIN_COPY["Nicotine and smoke exposure"])
        st.selectbox(
            "Do you currently use tobacco or nicotine?",
            [
                "none",
                "combustible",
                "ecig_smokeless",
                "dual",
            ],
            format_func=lambda value: {
                "none": "No current tobacco or nicotine",
                "combustible": "Yes - cigarettes, cigars, or pipe tobacco",
                "ecig_smokeless": "Yes - e-cigarettes, vapes, nicotine pouches, or smokeless tobacco",
                "dual": "Yes - combustible tobacco plus another nicotine product",
            }[value],
            index=None,
            placeholder="Choose one",
            key="nicotine_current_use",
        )
        if st.session_state.nicotine_current_use == "none":
            st.radio(
                "Have you ever been a regular user of cigarettes, vaping, or other tobacco/nicotine products?",
                ["never", "former"],
                format_func=lambda value: {
                    "never": "No, never a regular user",
                    "former": "Yes, I used to, but I quit",
                }[value],
                index=None,
                key="nicotine_former_status",
            )
            if st.session_state.nicotine_former_status == "former":
                st.selectbox(
                    "How long ago did you quit?",
                    ["under_1", "1_2", "3_4", "5_9", "10_plus"],
                    format_func=lambda value: {
                        "under_1": "Less than 1 year ago",
                        "1_2": "1-2 years ago",
                        "3_4": "3-4 years ago",
                        "5_9": "5-9 years ago",
                        "10_plus": "10 or more years ago",
                    }[value],
                    index=None,
                    placeholder="Choose one",
                    key="nicotine_quit_timing",
                )
        st.radio(
            "In a typical week, am I regularly exposed to tobacco smoke or e-cigarette vapor at home, work, or in vehicles?",
            ["no", "yes"],
            format_func=lambda value: {"no": "No", "yes": "Yes"}[value],
            index=None,
            key="secondhand_exposure_status",
            horizontal=True,
        )
with c2:
    with st.container(border=True):
        st.markdown("<p class='small-label'>4 of 8 - LE8 sleep domain</p>", unsafe_allow_html=True)
        st.subheader("Your sleep rhythm")
        st.caption(DOMAIN_COPY["Sleep rhythm"])
        st.number_input(
            "Over the past month, how many hours did you usually sleep per night?",
            min_value=0.0,
            max_value=16.0,
            value=None,
            step=0.25,
            placeholder="Enter hours",
            key="sleep_hours",
            help="Use your usual sleep duration, including weekends if they are part of your normal pattern.",
        )

with st.container(border=True):
    st.markdown("<p class='small-label'>5 of 8 - LE8 body size domain</p>", unsafe_allow_html=True)
    st.subheader("Body size")
    st.caption(DOMAIN_COPY["Body size"])
    st.radio(
        "Units",
        ["us", "metric"],
        format_func=lambda value: {"us": "Feet / inches / pounds", "metric": "Centimeters / kilograms"}[value],
        horizontal=True,
        key="body_units",
    )
    preview_height = None
    preview_weight = None
    if st.session_state.body_units == "metric":
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Height in centimeters", min_value=90.0, max_value=250.0, value=None, step=1.0, placeholder="Centimeters", key="height_cm")
        with c2:
            st.number_input("Weight in kilograms", min_value=25.0, max_value=320.0, value=None, step=0.5, placeholder="Kilograms", key="weight_kg")
        if st.session_state.height_cm is not None:
            preview_height = st.session_state.height_cm / 2.54
        if st.session_state.weight_kg is not None:
            preview_weight = st.session_state.weight_kg * 2.2046226218
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Height: feet", min_value=3, max_value=8, value=None, placeholder="Feet", key="height_ft")
        with c2:
            st.number_input("Height: inches", min_value=0, max_value=11, value=None, placeholder="Inches", key="height_in")
        with c3:
            st.number_input("Weight in pounds", min_value=60.0, max_value=700.0, value=None, step=1.0, placeholder="Pounds", key="weight_lbs")
        if st.session_state.height_ft is not None and st.session_state.height_in is not None:
            preview_height = st.session_state.height_ft * 12 + st.session_state.height_in
        preview_weight = st.session_state.weight_lbs
    bmi_preview = calculate_bmi(preview_height, preview_weight)
    if bmi_preview is None:
        st.caption("Enter height and weight to estimate BMI. BMI is an imperfect screening tool and does not measure muscle, body composition, or overall health by itself.")
    else:
        st.caption(f"Your estimated BMI is {bmi_preview}. BMI is an imperfect screening tool and does not measure muscle, body composition, or overall health by itself.")

c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("<p class='small-label'>6 of 8 - LE8 cholesterol domain</p>", unsafe_allow_html=True)
        st.subheader("Cholesterol particles")
        st.caption(DOMAIN_COPY["Cholesterol particles"])
        st.checkbox("I know my recent total cholesterol and HDL cholesterol", key="knows_lipids")
        if not st.session_state.knows_lipids:
            st.info("No problem. This section will be marked as missing, and your results will suggest what to check next.")
        st.session_state.total_chol = optional_number("Total cholesterol", st.session_state.knows_lipids, 80.0, 500.0, 190.0, 1.0, "This is usually listed on a standard lipid panel.")
        st.session_state.hdl = optional_number("HDL cholesterol", st.session_state.knows_lipids, 10.0, 150.0, 55.0, 1.0, "HDL is sometimes called good cholesterol. LE8 uses total minus HDL to estimate non-HDL cholesterol.")

with c2:
    with st.container(border=True):
        st.markdown("<p class='small-label'>7 of 8 - LE8 blood sugar domain</p>", unsafe_allow_html=True)
        st.subheader("Blood sugar")
        st.caption(DOMAIN_COPY["Blood sugar"])
        st.radio("Have you ever been told you have diabetes?", [False, True], format_func=lambda value: "Yes" if value else "No", index=None, horizontal=True, key="has_diabetes")
        st.selectbox(
            "Which recent blood sugar number do you have available?",
            ["a1c", "fasting_glucose", "unknown"],
            format_func=lambda value: {"a1c": "Hemoglobin A1c", "fasting_glucose": "Fasting glucose", "unknown": "I don't know"}[value],
            index=None,
            placeholder="Choose one",
            key="glucose_method",
        )
        if st.session_state.glucose_method is None:
            st.session_state.glucose_value = None
            st.info("Leave this blank if you do not know it. This section will be marked as missing.")
        elif st.session_state.glucose_method == "unknown":
            st.session_state.glucose_value = None
            st.info("No problem. This section will be marked as missing, and your results will suggest what to check next.")
        else:
            helper = "A1c estimates your average blood sugar over about 3 months." if st.session_state.glucose_method == "a1c" else "Fasting glucose is usually measured after not eating overnight."
            step = 0.1 if st.session_state.glucose_method == "a1c" else 1.0
            max_value = 15.0 if st.session_state.glucose_method == "a1c" else 400.0
            st.session_state.glucose_value = st.number_input("Enter your value", min_value=0.0, max_value=max_value, value=None, step=step, placeholder="Enter value", help=helper)

with st.container(border=True):
    st.markdown("<p class='small-label'>8 of 8 - LE8 blood pressure domain</p>", unsafe_allow_html=True)
    st.subheader("Blood pressure")
    st.caption(DOMAIN_COPY["Blood pressure"])
    st.checkbox("I know my usual blood pressure", key="knows_bp")
    if not st.session_state.knows_bp:
        st.info("No problem. A validated home blood pressure cuff is one of the most useful prevention tools you can own.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.sbp = optional_number("Top number / systolic", st.session_state.knows_bp, 70.0, 260.0, None, 1.0, "The pressure when your heart squeezes.")
    with c2:
        st.session_state.dbp = optional_number("Bottom number / diastolic", st.session_state.knows_bp, 40.0, 160.0, None, 1.0, "The pressure when your heart relaxes.")
    with c3:
        if st.session_state.knows_bp:
            st.checkbox("I take blood pressure medication", key="bp_treated")
        else:
            st.session_state.bp_treated = False
    if st.session_state.knows_bp and st.session_state.sbp is not None and st.session_state.dbp is not None:
        bp_map = round((st.session_state.sbp + 2 * st.session_state.dbp) / 3, 1)
        if bp_map < 65:
            st.warning(
                f"Your estimated mean arterial pressure is {bp_map} mmHg. Vital8 does not penalize low blood pressure as a prevention target, "
                "but very low pressure can matter if you feel dizzy, faint, weak, confused, short of breath, or have chest pain. "
                "If this reading is unusual or you have symptoms, contact a clinician or seek urgent care."
            )
        elif st.session_state.sbp < 90 or st.session_state.dbp < 60:
            st.caption(
                "Vital8 does not penalize low blood pressure as a prevention target. If low readings are new or come with symptoms, discuss them with a clinician."
            )

st.divider()
components, raw_inputs = collect_scores()
total = calculate_total_score(components)
result_score = total["score"] if total["known_count"] >= 5 else None
category, category_copy = category_for_total(result_score)
top = get_top_opportunities(components, 3)
strengths = [(name, result) for name, result in components.items() if result["score"] is not None and result["score"] >= 80][:3]

if total["known_count"] < 5:
    st.warning(f"Enter at least 5 of 8 areas to see a useful LE8 snapshot. You have entered {total['known_count']}.")

st.markdown(result_score_card(components, result_score, category, category_copy, total), unsafe_allow_html=True)

st.markdown(f"<div class='disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)
st.write("")

c1, c2 = st.columns(2)
with c1:
    st.subheader("What is already working")
    if strengths:
        for name, result in strengths:
            st.success(f"{name}: {result['score']}/100")
    else:
        st.caption("Your strengths will appear here as more LE8 areas reach 80 or higher.")
with c2:
    st.subheader("Your biggest levers")
    st.caption("These are the areas most likely to improve your foundation if you focus on them first.")
    for name, result in top:
        st.warning(f"{name}: {result['score']}/100 - {estimate_gain(name, result['score'], raw_inputs)}")

st.subheader("Your next 30 days")
st.caption("Do not try to overhaul your life this week. Pick one behavior, one measurement, and one follow-up step.")
plan = generate_30_day_plan(components, raw_inputs)
p1, p2, p3 = st.columns(3)
with p1:
    card("Behavior goal", plan["behavior"], class_name="plan-card")
with p2:
    card("Measurement goal", plan["measurement"], class_name="plan-card")
with p3:
    card("Clinician or lab goal", plan["clinician_or_lab"], class_name="plan-card")

share_text = share_summary_text(result_score, category, total, top, strengths, plan)
encoded_share_text = urllib.parse.quote(share_text)

with st.expander("Save or share your result", expanded=False):
    st.caption("Copy or send this concise summary of your score and next steps.")
    st.text_area(
        "Shareable summary",
        value=share_text,
        height=220,
        help="Select and copy this text, or use one of the quick-share buttons below.",
    )
    share_col1, share_col2, share_col3 = st.columns(3)
    with share_col1:
        st.link_button("Share on WhatsApp", f"https://wa.me/?text={encoded_share_text}", width="stretch")
    with share_col2:
        st.link_button("Share by SMS", f"sms:?&body={encoded_share_text}", width="stretch")
    with share_col3:
        st.download_button(
            "Download summary",
            data=share_text,
            file_name="vital8-summary.txt",
            mime="text/plain",
            width="stretch",
        )
    st.caption("Only share health information where you are comfortable with the privacy of that app or conversation.")

st.subheader("Score details")
st.caption("A visual breakdown is here if you want to see which domains are carrying the score.")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(radar_chart(components), width="stretch", config={"displayModeBar": False})
with c2:
    st.plotly_chart(bar_chart(components), width="stretch", config={"displayModeBar": False})

with st.expander("Technical component details"):
    st.dataframe(component_dataframe(components, raw_inputs), width="stretch", hide_index=True)

st.divider()
st.header("Optional deeper lens: fitness")
st.caption(
    "Your LE8 score is still the foundation. This optional section adds cardiorespiratory fitness, often estimated by VO2max, "
    "because fitness is independently associated with longevity and can reveal information that activity minutes alone may miss."
)
st.warning(
    "Prototype note: this is a conceptual Vital8 lens, not a validated clinical calculator. It is meant to support education and better questions, "
    "not replace formal exercise testing or clinician-guided interpretation."
)

with st.container(border=True):
    st.markdown("<p class='small-label'>Optional fitness input</p>", unsafe_allow_html=True)
    st.checkbox("Add VO2max / cardiorespiratory fitness modifier", key="fitness_enabled")
    fitness_category_key = None
    fitness_estimate = {"category_key": None, "median": None, "ratio": None}
    if st.session_state.fitness_enabled:
        st.radio(
            "How do you want to enter cardiorespiratory fitness?",
            ["vo2max", "percentile"],
            format_func=lambda value: {
                "vo2max": "Enter VO2max and estimate a broad age/sex category",
                "percentile": "I already know the age/sex-adjusted percentile category",
            }[value],
            index=None,
            key="fitness_method",
        )

        if st.session_state.fitness_method == "vo2max":
            st.session_state.vo2max = st.number_input(
                "VO2max in mL/kg/min",
                min_value=5.0,
                max_value=90.0,
                value=None,
                step=0.5,
                placeholder="Enter VO2max",
                help="Use measured VO2max from CPET, a validated wearable estimate, or a treadmill-test estimate if available.",
            )
            fitness_estimate = estimate_percentile_category(
                st.session_state.vo2max,
                st.session_state.age,
                st.session_state.sex,
            )
            fitness_category_key = fitness_estimate["category_key"]
            if fitness_category_key is None:
                st.info("Enter age, sex, and VO2max to estimate a broad percentile category, or choose the percentile option instead.")
            else:
                ratio_text = f"{fitness_estimate['ratio']:.2f}x" if fitness_estimate["ratio"] is not None else "not calculated"
                st.caption(
                    f"Broad estimate: your VO2max is about {ratio_text} the approximate median for the selected age/sex band. "
                    "This is a simplified estimate, not a formal FRIEND percentile calculation."
                )
        elif st.session_state.fitness_method == "percentile":
            st.selectbox(
                "VO2max percentile category",
                list(CRF_CATEGORIES.keys()),
                format_func=lambda key: f"{CRF_CATEGORIES[key]['label']} - {CRF_CATEGORIES[key]['interpretation']}",
                index=None,
                placeholder="Choose one",
                key="crf_percentile_category",
            )
            fitness_category_key = st.session_state.crf_percentile_category

    fitness_adjustment = calculate_fitness_adjustment(result_score, fitness_category_key)

if st.session_state.fitness_enabled:
    c1, c2 = st.columns(2)
    with c1:
        category_text = "Enter VO2max or percentile." if fitness_adjustment["category"] is None else fitness_adjustment["category"]["interpretation"]
        card("Fitness category", category_text, "Cardiorespiratory fitness", "metric-card")
    with c2:
        vmq_text = "Not calculated yet." if fitness_adjustment["vmq"] is None else f"{fitness_adjustment['vmq']:.2f}x applied to the advanced score"
        card("Fitness lens", vmq_text, "Advanced score input", "metric-card")

    if fitness_adjustment["vmq"] is not None:
        vmq = fitness_adjustment["vmq"]
        if vmq > 1:
            direction = "adds some credit to"
            meaning = "your fitness level appears to give you extra margin on top of your LE8 foundation"
        elif vmq < 1:
            direction = "pulls down"
            meaning = "your fitness level may be a sign that your LE8 foundation has less margin than it looks like on paper"
        else:
            direction = "does not change"
            meaning = "your fitness level is not changing the LE8 interpretation much in this model"
        st.info(
            f"Think of this as a fitness lens on top of your regular LE8 score. "
            f"Your estimated fitness score is {fitness_adjustment['crf_score']}/100, which {direction} the LE8 result by about {abs(vmq - 1) * 100:.0f}%. "
            f"In plain English: {meaning}. Your original LE8 score is still the main score."
        )

st.divider()
st.header("Optional labs: inflammation and inherited cholesterol risk")
st.caption(
    "Two optional blood tests can add context to your LE8 score: hsCRP for inflammation and Lp(a) for inherited cholesterol risk."
)
biomarker_items = "".join(
    f"""
    <div class='compact-explainer-item'>
      <h3>{item['title']}</h3>
      <p>{item['body']}</p>
    </div>
    """
    for item in BIOMARKER_EXPLAINERS
)
st.markdown(
    f"""
    <div class='compact-explainer'>
      <div class='compact-explainer-grid'>
        {biomarker_items}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")
st.caption("Conceptual prototype only. Use this to guide better questions, not to diagnose risk or replace clinician-guided care.")

with st.container(border=True):
    st.markdown("<p class='small-label'>Optional advanced labs</p>", unsafe_allow_html=True)
    st.checkbox("Add hsCRP and Lp(a) to estimate biological drag", key="advanced_enabled")
    if st.session_state.advanced_enabled:
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("I know my hsCRP", key="knows_hs_crp")
            if st.session_state.knows_hs_crp:
                st.session_state.hs_crp = st.number_input(
                    "hsCRP in mg/L",
                    min_value=0.0,
                    max_value=50.0,
                    value=None,
                    step=0.1,
                    placeholder="Enter hsCRP",
                    help="High-sensitivity C-reactive protein is a blood marker of inflammation. Values above 10 mg/L may reflect acute illness and often need repeat testing.",
                )
            else:
                st.session_state.hs_crp = None
                st.info("hsCRP is optional. Leave it blank if you do not have a recent value.")
        with c2:
            st.checkbox("I know my Lp(a)", key="knows_lpa")
            if st.session_state.knows_lpa:
                st.session_state.lpa = st.number_input(
                    "Lp(a) in nmol/L",
                    min_value=0.0,
                    max_value=800.0,
                    value=None,
                    step=5.0,
                    placeholder="Enter Lp(a)",
                    help="Lp(a) is largely inherited. Many guidelines use 125 nmol/L as a risk-enhancing threshold.",
                )
            else:
                st.session_state.lpa = None
                st.info("Lp(a) is often measured once because it is mostly genetically determined.")

adjustment = calculate_biomarker_adjustment(result_score, st.session_state.hs_crp, st.session_state.lpa)

if st.session_state.advanced_enabled:
    advanced_title, advanced_copy = advanced_category(adjustment["adjusted_score"])
    moderate_target = required_raw_le8(65, adjustment["combined_multiplier"])
    high_target = required_raw_le8(80, adjustment["combined_multiplier"])

    c1, c2 = st.columns(2)
    with c1:
        card(
            "Raw LE8 score",
            "Not enough LE8 data yet." if result_score is None else f"{result_score}/100 before optional advanced lenses.",
            "Foundation",
            "metric-card",
        )
    with c2:
        multiplier_text = "Enter hsCRP or Lp(a)." if adjustment["combined_multiplier"] is None else f"{adjustment['combined_multiplier']:.2f}x biological drag applied to the advanced score."
        card("Biomarker lens", multiplier_text, "Advanced score input", "metric-card")

    st.subheader(advanced_title)
    st.write(advanced_copy)

    if adjustment["combined_multiplier"] is not None:
        st.info(
            f"Think of this as a biomarker lens on top of your regular LE8 score. "
            f"In this prototype, the biomarkers entered suggest about {adjustment['penalty_percent']}% less prevention margin. "
            "That does not erase your LE8 work. It means keeping LDL/non-HDL/ApoB, blood pressure, glucose, nicotine exposure, sleep, and activity in a favorable range may matter even more."
        )
        if moderate_target is not None and high_target is not None:
            moderate_copy = f"{moderate_target}/100" if moderate_target <= 100 else "above 100, not achievable by LE8 alone"
            high_copy = f"{high_target}/100" if high_target <= 100 else "above 100, not achievable by LE8 alone"
            st.caption(
                f"To reach an adjusted estimate near 65, this model would require a raw LE8 of {moderate_copy}. "
                f"To reach an adjusted estimate near 80, it would require a raw LE8 of {high_copy}. "
                "When the target is not achievable by LE8 alone, the message is to pair excellent LE8 habits with clinician-guided lipid and risk-factor management."
            )

    b1, b2 = st.columns(2)
    with b1:
        st.markdown(
            f"""
            <div class='card metric-card'>
              <p class='small-label'>hsCRP</p>
              <h3>{adjustment['hs_crp']['category']}</h3>
              <p class='muted'>{adjustment['hs_crp']['note']}</p>
              <p><strong>What it means:</strong> hsCRP is a snapshot of inflammatory signaling. It can move over time, so persistent elevation matters more than a single isolated value.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b2:
        st.markdown(
            f"""
            <div class='card metric-card'>
              <p class='small-label'>Lp(a)</p>
              <h3>{adjustment['lpa']['category']}</h3>
              <p class='muted'>{adjustment['lpa']['note']}</p>
              <p><strong>What it means:</strong> Lp(a) is mostly inherited. Since it is not very modifiable right now, the priority is tighter control of the risk factors around it.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Advanced next steps")
    for step in biomarker_next_steps(adjustment):
        st.write(f"- {step}")

advanced_score = integrated_advanced_score(result_score, fitness_adjustment, adjustment)
if advanced_score["active_lenses"]:
    st.divider()
    st.header("Base vs advanced Vital8 score")
    st.caption(
        "The standard LE8 score remains the foundation. The advanced estimate applies any optional fitness and biomarker lenses you entered, in sequence."
    )
    a1, a2, a3 = st.columns(3)
    with a1:
        card(
            "Base LE8",
            "Not enough LE8 data yet." if result_score is None else f"{result_score}/100 from the standard Life's Essential 8 domains.",
            "Foundation",
            "metric-card",
        )
    with a2:
        active_text = ", ".join(advanced_score["active_lenses"])
        card(
            "Advanced lenses",
            f"Applied: {active_text}." if active_text else "No optional advanced lens calculated yet.",
            "What changed",
            "metric-card",
        )
    with a3:
        if advanced_score["score"] is None:
            advanced_text = "Enter enough LE8 data and optional lens values to calculate."
        else:
            delta = advanced_score["delta"]
            direction = "higher" if delta > 0 else "lower" if delta < 0 else "unchanged"
            advanced_text = f"{advanced_score['score']}/100, {abs(delta)} points {direction} than the base LE8 score."
        card("Advanced Vital8", advanced_text, "Integrated estimate", "metric-card")

    lens_notes: list[str] = []
    if advanced_score["fitness_multiplier"] is not None:
        lens_notes.append(f"fitness multiplier {advanced_score['fitness_multiplier']:.2f}x")
    if advanced_score["biomarker_multiplier"] is not None:
        lens_notes.append(f"biomarker drag {advanced_score['biomarker_multiplier']:.2f}x")
    if lens_notes:
        st.info(
            "Calculation note: this prototype starts with the base LE8 score, applies "
            + ", then ".join(lens_notes)
            + ". This is conceptual and should guide questions, not diagnose risk."
        )

st.subheader("Learn more about the Vital8 project")
st.write(
    "For more detail on the methodology, scientific references, white paper development, and future updates, "
    "visit the Vital8 Substack. It is where we will share the thinking behind the score, what we are learning, "
    "and how this project is evolving."
)
st.caption("Substack handles any newsletter signup. Vital8 does not collect your email in this app.")
st.link_button("Learn more on Substack", newsletter_url())

st.write("")
with st.container(border=True):
    image_col, text_col = st.columns([1, 5])
    with image_col:
        if AUTHOR_PHOTO.exists():
            st.markdown(linked_author_photo(), unsafe_allow_html=True)
    with text_col:
        st.markdown("**Created by Menachem Jacobs, MD, MPH**")
        st.markdown(
            "Internal Medicine resident and "
            "<a href='https://pubmed.ncbi.nlm.nih.gov/?term=menachem+jacobs&sort=date' target='_blank' rel='noopener noreferrer'>preventive cardiology researcher</a>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"Have feedback, questions, or ideas for improving Vital8? "
            f"[Reach out by email](mailto:{AUTHOR_EMAIL})."
        )

score_summary = build_score_summary(total, components, raw_inputs, plan)
score_summary["optional_lenses"] = {
    "integrated_advanced_score": advanced_score,
    "fitness": {
        "enabled": st.session_state.fitness_enabled,
        "method": st.session_state.fitness_method,
        "vo2max": st.session_state.vo2max if st.session_state.fitness_enabled else None,
        "crf_percentile_category": fitness_category_key,
        "estimated_category": fitness_estimate,
        "adjustment": fitness_adjustment,
    },
    "biomarkers": {
        "enabled": st.session_state.advanced_enabled,
        "hs_crp": st.session_state.hs_crp if st.session_state.advanced_enabled else None,
        "lpa": st.session_state.lpa if st.session_state.advanced_enabled else None,
        "adjustment": adjustment,
    },
}
render_chatbot(score_summary)
