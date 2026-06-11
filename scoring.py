"""Scoring helpers for the Vital8 Life's Essential 8 prototype."""

from __future__ import annotations

from typing import Any


ScoreResult = dict[str, Any]


def _result(score: int | None, label: str, explanation: str, **extra: Any) -> ScoreResult:
    return {"score": score, "label": label, "explanation": explanation, **extra}


def status_for_score(score: int | None) -> str:
    if score is None:
        return "Not entered"
    if score >= 80:
        return "Strong"
    if score >= 50:
        return "Opportunity"
    return "Priority"


def category_for_total(score: float | None) -> tuple[str, str]:
    if score is None:
        return "More information needed", "Enter at least 5 of 8 areas to create a useful snapshot."
    if score >= 80:
        return (
            "High LE8 cardiovascular health",
            "You're starting from a strong foundation. The next step is to protect what is working and look for any hidden risk markers in your blood pressure, cholesterol, blood sugar, or family history.",
        )
    if score >= 50:
        return (
            "Moderate LE8 cardiovascular health",
            "You have a meaningful starting point, with clear areas where small, steady changes could move your score higher. In LE8 research, the biggest gains often come from getting out of the low range.",
        )
    return (
        "Low LE8 cardiovascular health",
        "Several areas are pulling your score down, but that also means there is real room to improve. Start with one high-impact change, not all eight at once.",
    )


def calculate_bmi(height_inches: float, weight_lbs: float) -> float | None:
    if height_inches <= 0 or weight_lbs <= 0:
        return None
    return round((weight_lbs / (height_inches**2)) * 703, 1)


def score_diet(
    fruit_veg: str,
    whole_grains: str,
    sugary_drinks: str,
    processed_food: str,
    healthy_proteins: str,
) -> ScoreResult:
    fruit_points = {"0": 0, "1-2": 15, "3-4": 25, "5+": 35}[fruit_veg]
    grain_points = {"0": 0, "1": 10, "2+": 20}[whole_grains]
    drink_points = {"0": 15, "1-3": 10, "4-7": 5, "7+": 0}[sugary_drinks]
    processed_points = {"0-1": 15, "2-3": 10, "4-6": 5, "7+": 0}[processed_food]
    protein_points = {"0-1": 0, "2-3": 5, "4-6": 12, "daily": 15, "4+": 15}[healthy_proteins]
    score = min(100, fruit_points + grain_points + drink_points + processed_points + protein_points)
    return _result(
        score,
        "Estimated diet score",
        "Your eating pattern has room to become more heart-protective." if score < 75 else "Your daily fuel pattern is supporting your cardiovascular health.",
    )


def score_activity(moderate_minutes: float, vigorous_minutes: float) -> ScoreResult:
    equivalent = max(0, moderate_minutes) + 2 * max(0, vigorous_minutes)
    if equivalent == 0:
        score = 0
    elif equivalent < 30:
        score = 20
    elif equivalent < 60:
        score = 40
    elif equivalent < 90:
        score = 60
    elif equivalent < 150:
        score = 80
    else:
        score = 100
    return _result(score, f"{equivalent:.0f} moderate-equivalent min/week", "Regular movement improves blood pressure, insulin sensitivity, sleep, mood, and long-term heart health.", equivalent_minutes=equivalent)


def score_nicotine(status: str) -> ScoreResult:
    scores = {
        "none": 100,
        "quit_5_plus": 90,
        "quit_1_5": 75,
        "quit_under_1": 50,
        "current_nicotine": 25,
        "current_tobacco": 0,
    }
    labels = {
        "none": "No current nicotine or tobacco",
        "quit_5_plus": "Quit more than 5 years ago",
        "quit_1_5": "Quit 1-5 years ago",
        "quit_under_1": "Quit within the past year",
        "current_nicotine": "Current vaping or nicotine product",
        "current_tobacco": "Current combustible tobacco",
    }
    score = scores[status]
    return _result(score, labels[status], "Avoiding nicotine exposure is one of the highest-impact cardiovascular choices.")


def score_sleep(hours: float) -> ScoreResult:
    if 7 <= hours < 9:
        score = 100
    elif 6 <= hours < 7 or 9 <= hours < 10:
        score = 70
    elif 5 <= hours < 6 or hours >= 10:
        score = 40
    else:
        score = 20
    return _result(score, f"{hours:.1f} hours/night", "Sleep helps reset blood pressure, hunger signals, glucose control, and stress.")


def score_bmi(bmi: float | None) -> ScoreResult:
    if bmi is None:
        return _result(None, "Not entered", "Height and weight are needed to estimate BMI.")
    if bmi < 18.5:
        score = 70
    elif bmi < 25:
        score = 100
    elif bmi < 30:
        score = 70
    elif bmi < 35:
        score = 30
    elif bmi < 40:
        score = 15
    else:
        score = 0
    return _result(score, f"BMI {bmi:.1f}", "BMI is an imperfect screening tool and does not measure muscle, body composition, or overall health by itself.", bmi=bmi)


def score_lipids(total_chol: float | None, hdl: float | None) -> ScoreResult:
    if total_chol is None or hdl is None:
        return _result(None, "Not entered", "Non-HDL cholesterol is total cholesterol minus HDL. It captures cholesterol carried by plaque-forming particles.")
    non_hdl = max(0, total_chol - hdl)
    if non_hdl < 130:
        score = 100
    elif non_hdl < 160:
        score = 60
    elif non_hdl < 190:
        score = 40
    elif non_hdl < 220:
        score = 20
    else:
        score = 0
    return _result(score, f"Non-HDL {non_hdl:.0f} mg/dL", "Non-HDL cholesterol is total cholesterol minus HDL.", non_hdl=non_hdl)


def score_glucose(method: str, value: float | None, has_diabetes: bool) -> ScoreResult:
    if method == "unknown" or value is None:
        return _result(None, "Not entered", "A1c or fasting glucose can help show how your body handles energy over time.")
    if method == "a1c":
        if has_diabetes:
            score = 40 if value < 7 else 30 if value < 8 else 20 if value < 9 else 10
            label = f"A1c {value:.1f}%"
        else:
            score = 100 if value < 5.7 else 60 if value < 6.5 else 40
            label = f"A1c {value:.1f}%"
    else:
        if has_diabetes:
            score = 40 if value < 130 else 30 if value < 160 else 20 if value < 200 else 10
        else:
            score = 100 if value < 100 else 60 if value < 126 else 40
        label = f"Fasting glucose {value:.0f} mg/dL"
    return _result(score, label, "Blood sugar reflects how your body handles energy.")


def score_bp(sbp: float | None, dbp: float | None, treated: bool) -> ScoreResult:
    if sbp is None or dbp is None:
        return _result(None, "Not entered", "A home blood pressure cuff is one of the most useful prevention tools you can own.")
    if sbp < 120 and dbp < 80:
        untreated = 100
    elif 120 <= sbp < 130 and dbp < 80:
        untreated = 75
    elif 130 <= sbp < 140 or 80 <= dbp < 90:
        untreated = 50
    elif 140 <= sbp < 160 or 90 <= dbp < 100:
        untreated = 25
    else:
        untreated = 0
    score = max(0, untreated - 20) if treated else untreated
    return _result(score, f"{sbp:.0f}/{dbp:.0f} mmHg", "Blood pressure is common, often silent, and very treatable.")


def calculate_total_score(component_scores: dict[str, ScoreResult]) -> dict[str, Any]:
    known = [item["score"] for item in component_scores.values() if item["score"] is not None]
    if not known:
        return {"score": None, "known_count": 0, "total_count": len(component_scores), "is_partial": True}
    return {
        "score": round(sum(known) / len(known)),
        "known_count": len(known),
        "total_count": len(component_scores),
        "is_partial": len(known) < len(component_scores),
    }
