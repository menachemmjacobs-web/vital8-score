"""Vital8 Advanced biomarker adjustment helpers.

This module intentionally keeps the proposed biomarker layer separate from the
standard AHA Life's Essential 8 score. The model is a conceptual translation of
published risk gradients into an exploratory score modifier; it is not a
validated clinical calculator.
"""

from __future__ import annotations

from typing import Any


def hs_crp_multiplier(value: float | None) -> dict[str, Any]:
    if value is None:
        return {"multiplier": None, "category": "Not entered", "note": "hsCRP was not entered."}
    if value < 1:
        return {"multiplier": 1.0, "category": "Low inflammation", "note": "hsCRP is quiet here. That does not prove zero inflammation, but it is a favorable signal."}
    if value < 2:
        return {"multiplier": 1.12, "category": "Mild inflammation", "note": "This suggests a mild inflammatory signal. It is often modifiable, especially when driven by sleep, activity, weight, nicotine exposure, oral health, or diet quality."}
    if value < 3:
        return {"multiplier": 1.18, "category": "Moderate inflammation", "note": "This is a meaningful inflammatory signal. Because hsCRP is cross-sectional, repeat testing and context matter: recent illness, injury, sleep, weight, activity, nicotine, and inflammatory conditions can all move it."}
    if value < 5:
        return {"multiplier": 1.30, "category": "High inflammation", "note": "This suggests higher biological drag from inflammation if persistent. The encouraging part is that hsCRP can often improve when the drivers are identified and addressed."}
    if value <= 10:
        return {"multiplier": 1.45, "category": "Very high inflammation", "note": "Repeat testing may help distinguish chronic inflammation from a recent illness or injury."}
    return {"multiplier": 1.75, "category": "Extreme if persistent", "note": "Values above 10 mg/L can reflect infection, injury, or inflammatory disease and should be interpreted clinically."}


def lpa_multiplier(value: float | None) -> dict[str, Any]:
    if value is None:
        return {"multiplier": None, "category": "Not entered", "note": "Lp(a) was not entered."}
    if value < 75:
        return {"multiplier": 1.0, "category": "Lower Lp(a)", "note": "This is generally a favorable inherited lipid signal."}
    if value < 125:
        return {"multiplier": 1.2, "category": "Mildly elevated Lp(a)", "note": "This is a mild inherited risk signal. Lp(a) is largely genetic and not very responsive to lifestyle, so the practical move is to keep the modifiable risks around it especially well controlled."}
    if value < 250:
        return {"multiplier": 1.4, "category": "Elevated Lp(a)", "note": "This is a risk-enhancing inherited lipid signal. Since Lp(a) itself is not easily changed right now, LDL/non-HDL/ApoB, blood pressure, glucose, and nicotine exposure become more important."}
    if value < 350:
        return {"multiplier": 2.0, "category": "High Lp(a)", "note": "This can meaningfully raise risk even when standard cholesterol looks reasonable."}
    if value < 430:
        return {"multiplier": 3.0, "category": "Very high Lp(a)", "note": "This is a strong inherited risk signal and usually deserves aggressive management of modifiable risk factors."}
    return {"multiplier": 4.0, "category": "Extreme Lp(a)", "note": "This can represent a very high inherited risk burden."}


def calculate_biomarker_adjustment(raw_le8: int | None, hs_crp: float | None, lpa: float | None) -> dict[str, Any]:
    crp = hs_crp_multiplier(hs_crp)
    lpa_result = lpa_multiplier(lpa)
    entered = [item for item in [crp["multiplier"], lpa_result["multiplier"]] if item is not None]
    combined = None
    penalty = None
    adjusted = None
    if raw_le8 is not None and entered:
        combined = 1.0
        for value in entered:
            combined *= value
        penalty = round((1 - (1 / combined)) * 100)
        adjusted = round(raw_le8 / combined)
    return {
        "hs_crp": crp,
        "lpa": lpa_result,
        "combined_multiplier": combined,
        "penalty_percent": penalty,
        "adjusted_score": adjusted,
        "known_count": len(entered),
    }


def advanced_category(adjusted_score: int | None) -> tuple[str, str]:
    if adjusted_score is None:
        return "Advanced layer not calculated", "Enter hsCRP and/or Lp(a) to estimate the proposed Vital8 Advanced adjustment."
    if adjusted_score >= 80:
        return "Low biological drag", "Based on the advanced labs entered, inflammation and inherited Lp(a) burden do not substantially change the LE8 story. The goal is to maintain the foundation."
    if adjusted_score >= 50:
        return "Moderate biological drag", "Your LE8 foundation still matters, but these biomarkers suggest less room for drift. In plain English: the same LE8 score may require tighter control of LDL/non-HDL/ApoB, blood pressure, glucose, sleep, activity, and nicotine exposure."
    return "High biological drag", "The biomarker layer suggests that the standard LE8 score may understate risk. The practical message is not panic; it is precision. Keep every modifiable risk factor as favorable as possible and discuss risk-enhancing labs with a clinician."


def required_raw_le8(target_adjusted: int, combined_multiplier: float | None) -> int | None:
    if combined_multiplier is None:
        return None
    return round(target_adjusted * combined_multiplier)


def biomarker_next_steps(adjustment: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    crp_multiplier = adjustment["hs_crp"]["multiplier"]
    lpa_multiplier_value = adjustment["lpa"]["multiplier"]

    if crp_multiplier is None:
        steps.append("Consider hsCRP if you want to understand inflammatory burden beyond standard LE8.")
    elif crp_multiplier >= 1.18:
        steps.append("Treat hsCRP as a modifiable signal, not a verdict. If it stays elevated, the next step is to look for drivers: recent illness, sleep debt, body weight, activity, nicotine exposure, gum disease, autoimmune or inflammatory conditions, and medication context.")
    else:
        steps.append("Keep using LE8 habits to maintain a low inflammatory burden: regular movement, sleep consistency, no nicotine, and a fiber-rich eating pattern.")

    if lpa_multiplier_value is None:
        steps.append("Consider a one-time Lp(a) measurement, especially with family history of early heart disease, stroke, or high cholesterol.")
    elif lpa_multiplier_value >= 1.2:
        steps.append("Because Lp(a) is mostly genetic and not very modifiable yet, the response is to lower the risks you can control: keep LDL/non-HDL/ApoB lower, blood pressure and glucose in range, avoid nicotine, and maintain a high LE8 foundation.")
    else:
        steps.append("Lp(a) is not adding much inherited lipid drag in this model, so the standard LE8 priorities remain the main focus.")

    steps.append("Use this as a conversation guide: it is cross-sectional, conceptual, and meant to clarify prevention priorities rather than diagnose disease.")
    return steps
