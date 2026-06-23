"""Reusable copy for the Vital8 Streamlit prototype.

This file is intentionally named ``copy.py`` because the product brief asks for
that structure. To avoid surprising third-party packages that import Python's
standard-library ``copy`` module, it also exposes stdlib-compatible names.
"""

from __future__ import annotations

import importlib.util
import sysconfig
from pathlib import Path

_stdlib_copy_path = Path(sysconfig.get_path("stdlib")) / "copy.py"
_spec = importlib.util.spec_from_file_location("_stdlib_copy", _stdlib_copy_path)
_stdlib_copy = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_stdlib_copy)

copy = _stdlib_copy.copy
deepcopy = _stdlib_copy.deepcopy
Error = _stdlib_copy.Error

LANDING_TITLE = "Your heart health, made clear."

LANDING_PARAGRAPHS = [
    (
        "Eight levers. One evidence-based score. One practical next step."
    ),
    (
        "Based on the American Heart Association's Life's Essential 8, Vital8 turns prevention science into something you can actually use."
    ),
    (
        "The goal is not a perfect score. The goal is knowing where you stand, what matters most, and what to work on next."
    ),
    (
        "Always free. No supplements. No paywall. No black-box longevity score."
    ),
]

LANDING_SUBTITLE = LANDING_PARAGRAPHS[0]

DISCLAIMER = (
    "This tool is for education only and does not diagnose, treat, or replace care from your clinician. "
    "If you have symptoms or urgent concerns, seek medical care."
)

WHAT_THIS_MEASURES = (
    "Life's Essential 8, or LE8, scores the eight habits and health numbers most tied to long-term cardiovascular health. "
    "Each area is scored from 0 to 100, and your total score is the average of the areas you enter."
)

LE8_INTRO = (
    "Vital8 translates prevention science into a simple, actionable score built around the habits and measurements that "
    "most consistently track with long-term heart, metabolic, and brain health."
)

EVIDENCE_NOTE = (
    "A score that means something. A next step you can understand."
)

WHY_SCORE_MATTERS = [
    {
        "title": "One number",
        "body": "Eight everyday levers combine into one 0-100 snapshot of cardiovascular health.",
    },
    {
        "title": "Lower risk",
        "body": "Higher LE8 scores are consistently associated with fewer heart attacks, strokes, heart failure events, diabetes, dementia, and premature deaths.",
    },
    {
        "title": "More healthy years",
        "body": "In large population studies, high cardiovascular health is linked with more years lived free of major chronic disease.",
    },
    {
        "title": "Actionable",
        "body": "You do not need to be perfect. Moving from low to moderate cardiovascular health can matter, and Vital8 helps identify where to start.",
    },
]

BIOMARKER_EXPLAINERS = [
    {
        "title": "Start with LE8",
        "body": "Your main score stays the foundation.",
    },
    {
        "title": "Lp(a)",
        "body": "An inherited cholesterol risk signal.",
    },
    {
        "title": "hsCRP",
        "body": "A snapshot of inflammation.",
    },
    {
        "title": "Why it matters",
        "body": "These labs can make prevention targets more important.",
    },
]

DOMAIN_COPY = {
    "Daily fuel": "LE8 includes diet because your usual food pattern affects cholesterol, blood pressure, blood sugar, weight, and inflammation. Think about your usual eating pattern over the last few months. There are no perfect answers - we're looking for your typical routine.",
    "Movement": "LE8 gives credit for weekly movement because activity improves blood pressure, insulin sensitivity, sleep, mood, and long-term heart health.",
    "Nicotine and smoke exposure": "LE8 includes nicotine because smoking, vaping, and secondhand smoke can affect blood vessels, blood pressure, clotting risk, and long-term heart health.",
    "Sleep rhythm": "LE8 includes sleep because too little or too much sleep can track with blood pressure, glucose control, appetite, and stress.",
    "Body size": "LE8 uses body mass index as one screening signal. It is imperfect, but body size can influence blood pressure, cholesterol, blood sugar, sleep apnea risk, and inflammation.",
    "Cholesterol particles": "LE8 uses non-HDL cholesterol, calculated as total cholesterol minus HDL, because it captures cholesterol carried by artery-plaque-forming particles.",
    "Blood sugar": "LE8 includes blood sugar because higher levels over time can increase risk for diabetes, kidney disease, and cardiovascular disease.",
    "Blood pressure": "LE8 includes blood pressure because it is common, often silent, measurable at home, and very treatable.",
}

DOMAIN_MEANINGS = {
    "Daily fuel": "Your estimated LE8 diet score reflects your usual eating routine, especially plants, whole grains, sugary drinks, processed meals, and heart-healthy proteins.",
    "Movement": "More weekly movement is one of the fastest ways to improve several heart health signals at once.",
    "Nicotine": "Avoiding nicotine and smoke exposure protects blood vessels and lowers cardiovascular risk.",
    "Sleep rhythm": "Consistent sleep duration supports blood pressure, glucose control, appetite, and recovery.",
    "Body size": "Body size is only one signal, but changes can influence blood pressure, glucose, cholesterol, and sleep.",
    "Cholesterol particles": "Non-HDL cholesterol estimates cholesterol carried by particles that contribute to plaque buildup.",
    "Blood sugar": "A1c or fasting glucose shows how your body handles energy over time.",
    "Blood pressure": "Blood pressure is high-yield because it is measurable, common, and very treatable.",
}
