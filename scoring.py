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


def calculate_bmi(height_inches: float | None, weight_lbs: float | None) -> float | None:
    if height_inches is None or weight_lbs is None or height_inches <= 0 or weight_lbs <= 0:
        return None
    return round((weight_lbs / (height_inches**2)) * 703, 1)


def score_diet(
    fruit_veg: str | None,
    whole_grains: str | None,
    sugary_drinks: str | None,
    processed_food: str | None,
    healthy_proteins: str | None,
    fish_seafood: str | None,
    nuts_legumes: str | None,
    sodium_foods: str | None,
) -> ScoreResult:
    if None in {fruit_veg, whole_grains, sugary_drinks, processed_food, healthy_proteins, fish_seafood, nuts_legumes, sodium_foods}:
        return _result(
            None,
            "Not complete",
            "Answer each diet question to estimate this LE8-style eating-pattern score.",
        )
    fruit_points = {"0": 0, "1-2": 5, "3-4": 15, "5+": 25}[fruit_veg]
    grain_points = {"rarely": 0, "sometimes": 5, "most": 10, "always": 15}[whole_grains]
    drink_points = {"0": 10, "1-3": 7, "4-7": 3, "7+": 0}[sugary_drinks]
    processed_points = {"0-1": 10, "2-3": 7, "4-6": 3, "7+": 0}[processed_food]
    protein_points = {"plant_fish": 15, "mixed": 10, "lean_meat": 5, "red_processed": 0}[healthy_proteins]
    fish_points = {"2+": 10, "1": 7, "monthly": 3, "rarely": 0}[fish_seafood]
    nuts_legumes_points = {"most_days": 10, "few_weekly": 7, "weekly": 3, "rarely": 0}[nuts_legumes]
    sodium_points = {"rarely": 5, "sometimes": 3, "often": 0}[sodium_foods]
    score = fruit_points + grain_points + drink_points + processed_points + protein_points + fish_points + nuts_legumes_points + sodium_points
    return _result(
        score,
        "Estimated diet score",
        "Your eating pattern has room to become more heart-protective." if score < 75 else "Your daily fuel pattern is supporting your cardiovascular health.",
    )


def score_activity(moderate_minutes: float | None, vigorous_minutes: float | None) -> ScoreResult:
    if moderate_minutes is None or vigorous_minutes is None:
        return _result(None, "Not complete", "Enter your usual weekly activity minutes to score this domain.", equivalent_minutes=0)
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


def score_nicotine(current_use: str, former_use: bool, quit_timing: str | None, secondhand_exposure: bool) -> ScoreResult:
    if current_use == "combustible":
        base_score = 0
        label = "Current combustible tobacco"
    elif current_use == "ecig_smokeless":
        base_score = 20
        label = "Current non-combustible nicotine or tobacco"
    elif current_use == "dual":
        base_score = 0
        label = "Current combustible plus other nicotine use"
    elif former_use:
        former_scores = {"under_1": 50, "1_2": 60, "3_4": 70, "5_9": 80, "10_plus": 90}
        former_labels = {
            "under_1": "Quit less than 1 year ago",
            "1_2": "Quit 1-2 years ago",
            "3_4": "Quit 3-4 years ago",
            "5_9": "Quit 5-9 years ago",
            "10_plus": "Quit 10 or more years ago",
        }
        timing = quit_timing or "under_1"
        base_score = former_scores[timing]
        label = former_labels[timing]
    else:
        base_score = 100
        label = "Never or no regular nicotine/tobacco use"

    score = max(0, base_score - 5) if secondhand_exposure else base_score
    if secondhand_exposure:
        label = f"{label}; regular secondhand exposure"
    return _result(score, label, "Avoiding nicotine and secondhand exposure is one of the highest-impact cardiovascular choices.")


def score_sleep(hours: float | None) -> ScoreResult:
    if hours is None:
        return _result(None, "Not entered", "Enter your usual sleep duration to score this domain.")
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


def score_glucose(method: str | None, value: float | None, has_diabetes: bool | None) -> ScoreResult:
    if method is None or method == "unknown" or value is None:
        return _result(None, "Not entered", "A1c or fasting glucose can help show how your body handles energy over time.")
    if has_diabetes is None:
        return _result(None, "Not complete", "Select whether you have been told you have diabetes.")
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
    mean_arterial_pressure = round((sbp + 2 * dbp) / 3, 1)
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
    score = max(0, untreated - 20) if treated and untreated < 100 else untreated
    return _result(
        score,
        f"{sbp:.0f}/{dbp:.0f} mmHg",
        "This score focuses on elevated blood pressure. Very low blood pressure depends on symptoms and clinical context.",
        map=mean_arterial_pressure,
        low_map_flag=mean_arterial_pressure < 65,
    )


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
