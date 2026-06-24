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

LANDING_TITLE = "Your heart health, in one honest number."

LANDING_PARAGRAPHS = [
    (
        "Eight evidence-based levers. One composite score from 0-100. A few minutes of plain questions, and the single move most likely to raise it."
    )
]

LANDING_SUBTITLE = LANDING_PARAGRAPHS[0]

DISCLAIMER = (
    "Educational tool, not medical advice. Vital8 does not diagnose, treat, or replace care from your clinician. "
    "If you have symptoms or urgent concerns, seek medical care."
)

WHAT_THIS_MEASURES = (
    "Life's Essential 8 scores eight habits and health numbers that predict cardiovascular health. "
    "Each lever is scored from 0 to 100; your composite is their average."
)

LE8_INTRO = (
    "Vital8 translates prevention science into a simple, actionable score built around the habits and measurements that "
    "most consistently track with long-term heart, metabolic, and brain health."
)

EVIDENCE_NOTE = (
    "Know where you stand. Then change one thing."
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
    "Daily fuel": "Eight quick questions about your usual eating pattern. No tracking - just your honest average.",
    "Movement": "Count weekly minutes with your heart rate up. Vigorous minutes count double toward the 150-minute target.",
    "Nicotine and smoke exposure": "Cigarettes, vaping, smokeless tobacco, and regular secondhand exposure all count here.",
    "Sleep rhythm": "Your typical sleep over the past month. Consistency and duration both matter.",
    "Body size": "Used to estimate BMI - a rough screen that does not see muscle or body composition.",
    "Cholesterol particles": "From a recent lipid panel. Vital8 uses non-HDL cholesterol: total cholesterol minus HDL.",
    "Blood sugar": "From an A1c or fasting glucose test. If you do not have it, skip it and sharpen the score later.",
    "Blood pressure": "A recent home or clinic reading works. If you do not have one, skip it for now.",
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
