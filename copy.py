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

LANDING_TITLE = "Know Your Heart Health Score"

LANDING_PARAGRAPHS = [
    (
        "I'm Menachem Jacobs, MD, MPH, an Internal Medicine resident and "
        "<a href='https://pubmed.ncbi.nlm.nih.gov/?term=menachem+jacobs&sort=date' target='_blank' rel='noopener noreferrer'>preventive cardiology researcher</a>. "
        "I created Vital8 because one of the biggest challenges in medicine is not discovering what improves health - "
        "we often already know that. The challenge is helping people understand where they stand and what to do next."
    ),
    (
        "Vital8 is a free cardiovascular health assessment built from the American Heart Association's Life's Essential 8 "
        "framework, one of the most extensively studied measures of cardiovascular health. Decades of research involving "
        "millions of individuals have shown that better cardiovascular health is associated with longer life, fewer heart "
        "attacks and strokes, lower rates of diabetes and dementia, and more years lived free from chronic disease."
    ),
    (
        "A lot of modern health products make longevity feel expensive, proprietary, and confusing. Vital8 starts from a "
        "different belief: some of the most powerful prevention tools should be understandable, evidence-based, and freely available."
    ),
    (
        "This assessment translates prevention science into a simple, actionable score built around the habits and health factors "
        "that matter most: nutrition, physical activity, sleep, nicotine exposure, body weight, cholesterol, blood sugar, and blood pressure. "
        "The goal is not perfection. The goal is identifying the next change most likely to improve long-term health."
    ),
    "No supplements to sell. No paywall. No mystery algorithm. Just the best available science, presented in a way that helps people take action.",
]

LANDING_SUBTITLE = LANDING_PARAGRAPHS[0]

DISCLAIMER = (
    "This tool is for education only and does not diagnose, treat, or replace care from your clinician. "
    "If you have symptoms or urgent concerns, seek medical care."
)

WHAT_THIS_MEASURES = (
    "Life's Essential 8, or LE8, scores eight areas: eating pattern, physical activity, nicotine exposure, "
    "sleep, body size, cholesterol, blood sugar, and blood pressure. Each area is scored from 0 to 100, "
    "and the total score is the average of the areas you enter."
)

LE8_INTRO = (
    "Vital8 translates prevention science into a simple, actionable score built around the habits and measurements that "
    "most consistently track with long-term heart, metabolic, and brain health."
)

EVIDENCE_NOTE = (
    "Large population studies link higher LE8 scores with longer life, fewer years lived with chronic disease, "
    "and lower risk of heart disease, stroke, and dementia. This is not a diagnosis or a product pitch. It is a "
    "plain-language guide to what is worth measuring, protecting, and improving next."
)

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
