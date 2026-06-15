"""Recommendation engine for the Vital8 prototype."""

from __future__ import annotations

from scoring import ScoreResult


def get_top_opportunities(component_scores: dict[str, ScoreResult], n: int = 3) -> list[tuple[str, ScoreResult]]:
    known = [(name, result) for name, result in component_scores.items() if result["score"] is not None]
    return sorted(known, key=lambda item: item[1]["score"])[:n]


def get_domain_recommendation(domain: str, score: int | None, raw_inputs: dict) -> str:
    if score is None:
        missing = {
            "Daily fuel": "Answer the diet questions when you are ready. A rough usual pattern is enough; it does not need to be perfect.",
            "Movement": "Enter your usual weekly activity minutes when you are ready.",
            "Nicotine": "Answer the nicotine and secondhand exposure questions when you are ready.",
            "Sleep rhythm": "Enter your usual sleep duration when you are ready.",
            "Body size": "Enter height and weight if you want BMI included as one screening signal.",
            "Cholesterol particles": "Ask for a standard lipid panel. If you want a deeper prevention view, discuss ApoB and Lp(a) with your clinician.",
            "Blood sugar": "Ask about hemoglobin A1c or fasting glucose at your next routine lab check.",
            "Blood pressure": "Check home blood pressure twice in the morning and twice in the evening for 7 days, then average the readings.",
        }
        return missing.get(domain, "This section was not entered yet. Add it when you are ready.")

    if domain == "Daily fuel":
        return "Start by adding, not subtracting: one extra serving of fruit or vegetables daily, then replace one sugary drink or heavily processed snack."
    if domain == "Movement":
        minutes = raw_inputs.get("activity_equivalent", 0)
        if minutes < 150:
            return "Your activity score would improve by reaching 150 minutes per week. A practical target is 20-30 minutes of brisk walking 5 days per week."
        return "Protect this strength by keeping a weekly rhythm you can repeat even during busy weeks."
    if domain == "Nicotine":
        if score < 75:
            return "Stopping nicotine is one of the highest-impact cardiovascular changes. Evidence-based options include nicotine replacement, varenicline, bupropion, counseling, and quitline support."
        return "Keep protecting your blood vessels by avoiding nicotine and secondhand smoke exposure."
    if domain == "Sleep rhythm":
        hours = raw_inputs.get("sleep_hours", 0)
        if hours < 7:
            return "Your sleep score is limited by short sleep duration. Start with a consistent wake time, morning light exposure, and a 30-60 minute wind-down window."
        if hours >= 9:
            return "Long sleep can reflect sleep debt, sleep quality issues, or medical concerns. If this pattern persists, consider discussing it with your clinician."
        return "Keep your sleep window steady, especially on weekends."
    if domain == "Body size":
        bmi = raw_inputs.get("bmi")
        if bmi and bmi >= 30:
            return "Weight is only one part of cardiovascular health, but even 5-10% weight loss can improve blood pressure, glucose, triglycerides, and inflammation."
        return "Use this as one context clue, not a judgment. Strength, waist size, labs, blood pressure, and trends also matter."
    if domain == "Cholesterol particles":
        return "Non-HDL cholesterol reflects cholesterol carried by plaque-forming particles. Consider discussing ApoB, LDL-C, Lp(a), lifestyle changes, and medication options with your clinician."
    if domain == "Blood sugar":
        return "The highest-yield next steps are resistance training, post-meal walking, weight reduction if appropriate, and reducing refined carbohydrates or sugary drinks."
    if domain == "Blood pressure":
        return "Home tracking is the next best step. Measure twice in the morning and twice in the evening for 7 days, then average the readings."
    return "Pick one small change you can repeat this week."


def estimate_gain(domain: str, score: int | None, raw_inputs: dict) -> str:
    if score is None:
        return "Entering this measurement could make your score more complete."
    if domain == "Movement" and score < 100:
        gain = max(0, round((100 - score) / 8))
        return f"If your activity reached 150 moderate-equivalent minutes per week, your total score could rise by about {gain} points."
    if domain == "Blood pressure" and score < 100:
        gain = max(0, round((100 - score) / 8))
        return f"If your blood pressure reached the normal range, your total score could improve by about {gain} points."
    if domain == "Sleep rhythm" and score < 100:
        gain = max(0, round((100 - score) / 8))
        return f"If your sleep averaged 7-8 hours nightly, your total score could improve by about {gain} points."
    if score < 100:
        gain = max(0, round((100 - score) / 8))
        return f"Moving this area toward the strong range could improve your total score by about {gain} points."
    return "This area is already a strength. The opportunity is consistency."


def generate_30_day_plan(component_scores: dict[str, ScoreResult], raw_inputs: dict) -> dict[str, str]:
    opportunities = get_top_opportunities(component_scores, 3)
    first_domain = opportunities[0][0] if opportunities else "Movement"

    behavior = {
        "Daily fuel": "Add one serving of fruit or vegetables daily and swap one sugary drink for water or unsweetened tea.",
        "Movement": "Walk 25 minutes after dinner 5 days per week.",
        "Nicotine": "Choose one quit-support option and set a specific start date.",
        "Sleep rhythm": "Set one consistent wake time and begin a 30-minute wind-down window.",
        "Body size": "Build meals around protein and fiber, then track weight once weekly without overreacting to daily changes.",
    }.get(first_domain, "Pick one repeatable behavior that supports your lowest-scoring area.")

    missing = [name for name, result in component_scores.items() if result["score"] is None]
    measurement = "Check home blood pressure for 7 days." if "Blood pressure" in missing or first_domain == "Blood pressure" else "Track the behavior goal for 4 weeks and note how often you complete it."
    lab = "Ask about fasting lipids, hemoglobin A1c, ApoB, and Lp(a)." if any(name in missing for name in ["Cholesterol particles", "Blood sugar"]) else "Review your latest labs and ask which marker is most worth improving next."

    return {"behavior": behavior, "measurement": measurement, "clinician_or_lab": lab}
