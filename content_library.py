"""Approved short educational snippets for Vital8 AI grounding."""

from __future__ import annotations


LE8_DOMAIN_EXPLANATIONS = {
    "Daily fuel": "Eating pattern affects cholesterol, blood pressure, blood sugar, weight, and inflammation.",
    "Movement": "Regular activity supports blood pressure, insulin sensitivity, sleep, mood, and long-term heart health.",
    "Nicotine": "Avoiding nicotine and secondhand smoke exposure protects blood vessels and lowers cardiovascular risk.",
    "Sleep rhythm": "Usual sleep duration is connected with blood pressure, glucose control, appetite, and recovery.",
    "Body size": "BMI is one screening signal. It does not measure muscle, body composition, or overall health by itself.",
    "Cholesterol particles": "Non-HDL cholesterol estimates cholesterol carried by plaque-forming particles.",
    "Blood sugar": "A1c or fasting glucose helps show how the body handles energy over time.",
    "Blood pressure": "Blood pressure is common, often silent, measurable at home, and treatable.",
}


APPROVED_SCOPE = (
    "Vital8 is educational only. It can explain Life's Essential 8, prevention priorities, "
    "general lifestyle concepts, home measurement, and clinician discussion topics. It is not a diagnosis, "
    "treatment plan, emergency triage tool, or validated clinical risk calculator."
)


SCORING_METHODOLOGY = (
    "The core Vital8 score is an educational LE8-style score from 0 to 100. It averages the available domain "
    "scores across Daily fuel, Movement, Nicotine, Sleep rhythm, Body size, Cholesterol particles, Blood sugar, "
    "and Blood pressure when enough domains are entered. Missing labs can produce a partial score. Diet and "
    "nicotine are consumer-facing approximations designed to align with the spirit of AHA Life's Essential 8, "
    "not exact clinical recalls. Optional VO2max/cardiorespiratory fitness and hsCRP/Lp(a) sections are "
    "exploratory interpretive lenses that do not replace the raw LE8 score and are not validated risk calculators."
)
