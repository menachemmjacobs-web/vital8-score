"""Rule-based safety guardrails for the Vital8 AI assistant."""

from __future__ import annotations

import re


SAFETY_MESSAGE = (
    "I can't safely assess urgent symptoms or medication decisions here. "
    "If this could be an emergency, seek urgent medical care or call emergency services. "
    "For medication changes, contact your clinician or prescribing team."
)


URGENT_PATTERNS = [
    r"\bchest pain\b",
    r"\bchest pressure\b",
    r"\bshort(?:ness)? of breath\b",
    r"\bcan't breathe\b",
    r"\bfaint(?:ed|ing)?\b",
    r"\bsyncope\b",
    r"\bfacial droop\b",
    r"\barm weakness\b",
    r"\btrouble speaking\b",
    r"\bstroke symptoms?\b",
    r"\bnew neurologic",
    r"\bsevere headache\b",
    r"\bheart attack\b",
    r"\boverdose\b",
    r"\bsuicidal\b",
    r"\bkill(?:ing)? myself\b",
    r"\bgo to the er\b",
    r"\bemergency room\b",
    r"\bam i having a heart attack\b",
]

MEDICATION_PATTERNS = [
    r"\bshould i (?:stop|start|change|increase|decrease|adjust)\b.*\b(?:med|medicine|medication|dose|statin|bp medicine|blood pressure medicine)\b",
    r"\b(?:stop|start|change|increase|decrease|adjust) my (?:med|medicine|medication|dose|statin)\b",
    r"\bshould i start a statin\b",
    r"\bshould i stop my statin\b",
]


def _bp_red_flag(message: str) -> bool:
    if not re.search(r"\b(bp|blood pressure)\b", message):
        return False
    numbers = [int(value) for value in re.findall(r"\b(\d{2,3})\b", message)]
    high_bp = any(value >= 180 for value in numbers) or any(value >= 120 for value in numbers)
    symptoms = re.search(r"\b(dizzy|dizziness|chest|short(?:ness)? of breath|headache|weakness|confus(?:ed|ion)|vision|faint)\b", message)
    return bool(high_bp and symptoms)


def detect_red_flags(user_message: str) -> dict[str, object]:
    """Return a blocking safety response when the user asks unsafe clinical questions."""
    text = user_message.lower().strip()

    if _bp_red_flag(text):
        return {"blocked": True, "reason": "hypertensive_red_flag", "message": SAFETY_MESSAGE}

    for pattern in URGENT_PATTERNS:
        if re.search(pattern, text):
            return {"blocked": True, "reason": "urgent_symptom", "message": SAFETY_MESSAGE}

    for pattern in MEDICATION_PATTERNS:
        if re.search(pattern, text):
            return {"blocked": True, "reason": "medication_decision", "message": SAFETY_MESSAGE}

    return {"blocked": False, "reason": "", "message": ""}
