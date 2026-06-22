from __future__ import annotations

import base64
import importlib.util
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
WHY_SCORE_MATTERS = _copy_module.WHY_SCORE_MATTERS


st.set_page_config(page_title="Vital8 Heart Health Score", page_icon="V8", layout="wide", initial_sidebar_state="collapsed")


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
AUTHOR_EMAIL = "menachem.m.jacobs@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/menachem-jacobs-b35222122/"


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
    "moderate_minutes": None,
    "vigorous_minutes": None,
    "nicotine_current_use": None,
    "nicotine_former_status": None,
    "nicotine_quit_timing": None,
    "secondhand_exposure_status": None,
    "sleep_hours": None,
    "height_ft": None,
    "height_in": None,
    "weight_lbs": None,
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
        :root {
          --navy: #11243a;
          --teal: #11a7a4;
          --green: #1d9a6c;
          --amber: #d88a1d;
          --red: #c9473d;
          --bg: #f7f8fa;
          --surface: #ffffff;
          --surface-soft: #edf8f7;
          --border: rgba(17, 36, 58, .12);
          --ink-soft: #556070;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {
          background: var(--bg);
          color: var(--navy);
        }
        .block-container { padding-top: 2rem; max-width: 1180px; }
        h1, h2, h3, h4, h5, h6 { letter-spacing: 0; color: var(--navy); }
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
        .hero {
          border-radius: 24px;
          padding: 34px;
          background: linear-gradient(135deg, var(--surface) 0%, var(--surface-soft) 100%);
          border: 1px solid var(--border);
          box-shadow: 0 18px 50px rgba(17, 36, 58, .08);
        }
        .card {
          border-radius: 20px;
          padding: 22px;
          background: rgba(255,255,255,.94);
          border: 1px solid var(--border);
          box-shadow: 0 12px 30px rgba(17, 36, 58, .06);
          height: 100%;
        }
        .card h3 {
          margin: 0 0 12px;
          font-size: 1.55rem;
          line-height: 1.16;
        }
        .card p {
          margin-bottom: 0;
          font-size: 1rem;
          line-height: 1.55;
        }
        .equal-card { min-height: 190px; }
        .plan-card { min-height: 210px; }
        .metric-card { min-height: 185px; }
        .author-note {
          border-radius: 20px;
          padding: 22px;
          background: var(--surface);
          border: 1px solid var(--border);
          box-shadow: 0 12px 30px rgba(17, 36, 58, .06);
        }
        .small-label {
          margin: 0 0 8px;
          color: var(--teal);
          font-size: .78rem;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .08em;
        }
        .muted { color: var(--ink-soft); }
        .score-number { font-size: 4.5rem; line-height: 1; font-weight: 850; color: var(--navy); }
        .status-Strong { color: var(--green); font-weight: 800; }
        .status-Opportunity { color: var(--amber); font-weight: 800; }
        .status-Priority { color: var(--red); font-weight: 800; }
        .status-Not-entered { color: #697586; font-weight: 800; }
        .disclaimer {
          border-left: 4px solid var(--teal);
          background: var(--surface);
          border-radius: 14px;
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
          border-radius: 999px;
          border: 0;
          color: white;
          background: var(--navy);
          font-weight: 800;
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
        div[data-testid="stPopoverBody"] {
          width: min(420px, calc(100vw - 32px));
          max-height: min(720px, calc(100vh - 120px));
          overflow-y: auto;
        }
        @media (max-width: 760px) {
          .st-key-vital8_ai_floating {
            right: 12px;
            bottom: 12px;
            width: calc(100vw - 24px);
          }
          .st-key-vital8_ai_floating button {
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


def optional_number(label: str, known: bool, min_value: float, max_value: float, value: float | None, step: float, help_text: str = "") -> float | None:
    if not known:
        return None
    return st.number_input(label, min_value=min_value, max_value=max_value, value=value, step=step, placeholder="Enter value", help=help_text)


def legacy_diet_args() -> tuple[str, str, str, str, str]:
    grain_map = {"rarely": "0", "sometimes": "1", "most": "2+", "always": "2+"}
    protein_map = {
        "plant_fish": "daily",
        "mixed": "4-6",
        "lean_meat": "2-3",
        "red_processed": "0-1",
    }
    return (
        st.session_state.fruit_veg,
        grain_map.get(st.session_state.whole_grains, "1"),
        st.session_state.sugary_drinks,
        st.session_state.processed_food,
        protein_map.get(st.session_state.healthy_proteins, "2-3"),
    )


def score_diet_with_blank_check() -> dict:
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
    if st.session_state.height_ft is not None and st.session_state.height_in is not None:
        height_inches = st.session_state.height_ft * 12 + st.session_state.height_in
    bmi = calculate_bmi(height_inches, st.session_state.weight_lbs)
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
        "height_inches": height_inches,
        "weight_lbs": st.session_state.weight_lbs,
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


def linked_author_photo() -> str:
    encoded = base64.b64encode(AUTHOR_PHOTO.read_bytes()).decode("ascii")
    return f"""
    <a href="{AUTHOR_LINKEDIN}" target="_blank" rel="noopener noreferrer" aria-label="Menachem Jacobs LinkedIn profile">
      <img src="data:image/jpeg;base64,{encoded}" alt="Menachem Jacobs" style="width:110px; border-radius:8px; display:block;" />
    </a>
    """


inject_css()

landing_body = "\n".join(
    f"<p class='muted' style='font-size:1.05rem; max-width:900px;'>{paragraph}</p>"
    for paragraph in LANDING_PARAGRAPHS
)

st.markdown(
    f"""
    <section class='hero'>
      <p class='small-label'>Life's Essential 8 assessment</p>
      <h1>{LANDING_TITLE}</h1>
      {landing_body}
    </section>
    """,
    unsafe_allow_html=True,
)

st.write("")
c1, c2 = st.columns(2)
with c1:
    card("Start with LE8", "Get a plain-language score across the eight habits and health measures that form your prevention foundation.", "Core calculator", "equal-card")
with c2:
    card("Why it matters", "Higher LE8 scores are linked with longer life and fewer years lived with heart, metabolic, and brain disease.", "Evidence base", "equal-card")
st.write("")
c3, c4 = st.columns(2)
with c3:
    card("Find your biggest lever", "Vital8 highlights the area most likely to move your score, so the next step feels specific instead of vague.", "What you get", "equal-card")
with c4:
    card("Go deeper when ready", "Optional research layers explore VO2max, inflammation, and inherited lipid risk after the LE8 foundation.", "Advanced lenses", "equal-card")

st.write("")
st.subheader("Why your score matters")
st.caption("The science is population-level, not a personal guarantee. But the signal is strong: better cardiovascular health tracks with better long-term outcomes.")
for start in range(0, len(WHY_SCORE_MATTERS), 2):
    why_cols = st.columns(2)
    for col, item in zip(why_cols, WHY_SCORE_MATTERS[start : start + 2]):
        with col:
            card(item["title"], item["body"], class_name="equal-card")
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
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox(
            "On a typical day, how many servings of fruits and vegetables do you eat?",
            ["0", "1-2", "3-4", "5+"],
            index=None,
            placeholder="Choose one",
            key="fruit_veg",
            help="One serving is about a handful, a cup of salad, or one piece of fruit. Estimate your usual day, not your best day.",
        )
        st.selectbox(
            "How often do you choose whole-grain foods over white or refined grains?",
            ["rarely", "sometimes", "most", "always"],
            format_func=lambda value: {
                "rarely": "Rarely or never",
                "sometimes": "Sometimes, a few times a week",
                "most": "Most of the time",
                "always": "Almost always",
            }[value],
            index=None,
            placeholder="Choose one",
            key="whole_grains",
            help="Examples include oatmeal, whole wheat bread, brown rice, quinoa, barley, or high-fiber cereal.",
        )
        st.selectbox(
            "In a typical week, how many sugary drinks do you have?",
            ["0", "1-3", "4-7", "7+"],
            index=None,
            placeholder="Choose one",
            key="sugary_drinks",
            help="Include soda, sweet tea, juice drinks, energy drinks, and sweetened coffee drinks.",
        )
    with c2:
        st.selectbox(
            "In a typical week, how many meals come from fast food, fried food, or heavily processed foods?",
            ["0-1", "2-3", "4-6", "7+"],
            index=None,
            placeholder="Choose one",
            key="processed_food",
            help="Estimate meals or snack occasions per week.",
        )
        st.selectbox(
            "Which best describes your usual protein sources?",
            ["plant_fish", "mixed", "lean_meat", "red_processed"],
            format_func=lambda value: {
                "plant_fish": "Mostly plant-based proteins and/or fish",
                "mixed": "Mix of plant-based foods, fish, poultry, and some red meat",
                "lean_meat": "Mostly poultry or lean meat, limited red or processed meat",
                "red_processed": "Mostly red or processed meat",
            }[value],
            index=None,
            placeholder="Choose one",
            key="healthy_proteins",
            help="Examples of heart-healthy proteins include fish, beans, lentils, tofu, nuts, and seeds.",
        )
        st.selectbox(
            "How often do you eat fish or seafood?",
            ["2+", "1", "monthly", "rarely"],
            format_func=lambda value: {
                "2+": "2 or more times per week",
                "1": "About once a week",
                "monthly": "A few times a month",
                "rarely": "Rarely or never",
            }[value],
            index=None,
            placeholder="Choose one",
            key="fish_seafood",
        )
        st.selectbox(
            "How often do you eat nuts, seeds, beans, or lentils?",
            ["most_days", "few_weekly", "weekly", "rarely"],
            format_func=lambda value: {
                "most_days": "Most days, 5+ times per week",
                "few_weekly": "A few times a week",
                "weekly": "About once a week",
                "rarely": "Rarely or never",
            }[value],
            index=None,
            placeholder="Choose one",
            key="nuts_legumes",
        )
        st.selectbox(
            "How often do you add salt at the table or eat high-sodium foods?",
            ["rarely", "sometimes", "often"],
            format_func=lambda value: {
                "rarely": "Rarely - I actively limit salt",
                "sometimes": "Sometimes",
                "often": "Often - most meals are salty or restaurant-prepared",
            }[value],
            index=None,
            placeholder="Choose one",
            key="sodium_foods",
            help="Examples include canned soups, chips, soy sauce, pickled foods, deli meats, and frequent restaurant meals.",
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
    c1, c2, c3 = st.columns(3)
    with c1:
        st.number_input("How tall are you? Feet", min_value=3, max_value=8, value=None, placeholder="Feet", key="height_ft")
    with c2:
        st.number_input("How tall are you? Inches", min_value=0, max_value=11, value=None, placeholder="Inches", key="height_in")
    with c3:
        st.number_input("What is your current weight in pounds?", min_value=60.0, max_value=700.0, value=None, step=1.0, placeholder="Pounds", key="weight_lbs")
    preview_height = None
    if st.session_state.height_ft is not None and st.session_state.height_in is not None:
        preview_height = st.session_state.height_ft * 12 + st.session_state.height_in
    bmi_preview = calculate_bmi(preview_height, st.session_state.weight_lbs)
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

st.divider()
components, raw_inputs = collect_scores()
total = calculate_total_score(components)
result_score = total["score"] if total["known_count"] >= 5 else None
category, category_copy = category_for_total(result_score)
top = get_top_opportunities(components, 3)
strengths = [(name, result) for name, result in components.items() if result["score"] is not None and result["score"] >= 80][:3]

st.header("Your Vital8 LE8 score")
if total["known_count"] < 5:
    st.warning(f"Enter at least 5 of 8 areas to see a useful LE8 snapshot. You have entered {total['known_count']}.")

c1, c2 = st.columns([1, 1.15])
with c1:
    st.plotly_chart(gauge(result_score), width="stretch", config={"displayModeBar": False})
with c2:
    st.markdown("<p class='small-label'>Life's Essential 8 snapshot</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-number'>{result_score if result_score is not None else '--'}</div>", unsafe_allow_html=True)
    partial = f"Snapshot based on {total['known_count']} of 8 areas." if total["is_partial"] else "Complete score based on all 8 areas."
    st.subheader(category)
    st.write(category_copy)
    st.caption("Low is below 50, moderate is 50-79, and high is 80-100. This score is educational and depends on the information you entered.")
    st.info(partial)

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

st.subheader("Your 8 LE8 building blocks")
for name in DOMAIN_ORDER:
    result = components[name]
    score = result["score"]
    status = status_for_score(score)
    css_status = status.replace(" ", "-")
    display_score = "Not entered" if score is None else f"{score}/100"
    st.markdown(
        f"""
        <div class='card'>
          <p class='small-label'>{name}</p>
          <h3>{display_score} - <span class='status-{css_status}'>{status}</span></h3>
          <p class='muted'>{DOMAIN_MEANINGS.get(name, result['explanation'])}</p>
          <p><strong>Next best step:</strong> {get_domain_recommendation(name, score, raw_inputs)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

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
    c1, c2, c3 = st.columns(3)
    with c1:
        category_text = "Enter VO2max or percentile." if fitness_adjustment["category"] is None else fitness_adjustment["category"]["interpretation"]
        card("Fitness category", category_text, "Cardiorespiratory fitness", "metric-card")
    with c2:
        vmq_text = "Not calculated yet." if fitness_adjustment["vmq"] is None else f"{fitness_adjustment['vmq']:.2f}x fitness lens"
        card("Fitness lens", vmq_text, "Conceptual modifier", "metric-card")
    with c3:
        modified_text = "Not enough LE8 data yet." if fitness_adjustment["modified_score"] is None else f"{fitness_adjustment['modified_score']}/100 after applying the fitness lens"
        card("Fitness-informed estimate", modified_text, "Exploratory", "metric-card")

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
st.header("Optional deeper lens: biomarkers")
st.caption(
    "Your LE8 score stays exactly as-is. This optional section asks whether inflammation or inherited lipid risk might change how much prevention margin you have."
)
st.warning(
    "Prototype note: this biomarker layer is conceptual and cross-sectional. Use it to guide better questions and prevention priorities, "
    "not to diagnose disease or replace clinician-guided risk assessment."
)
bio_cols = st.columns(2)
for index, item in enumerate(BIOMARKER_EXPLAINERS):
    with bio_cols[index % 2]:
        card(item["title"], item["body"], class_name="equal-card")
if bio_cols:
    st.write("")

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

    c1, c2, c3 = st.columns(3)
    with c1:
        card(
            "Raw LE8 score",
            "Not enough LE8 data yet." if result_score is None else f"{result_score}/100 before adding the advanced biomarker lens.",
            "Foundation",
            "metric-card",
        )
    with c2:
        multiplier_text = "Enter hsCRP or Lp(a)." if adjustment["combined_multiplier"] is None else f"{adjustment['combined_multiplier']:.2f}x added context from inflammation and inherited lipid risk."
        card("Biomarker context", multiplier_text, "Advanced lens", "metric-card")
    with c3:
        adjusted_text = "Not calculated yet." if adjustment["adjusted_score"] is None else f"{adjustment['adjusted_score']}/100 after applying the biomarker lens."
        card("Biomarker-informed estimate", adjusted_text, "Exploratory", "metric-card")

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
