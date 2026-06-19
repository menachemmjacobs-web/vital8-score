"""Conceptual VO2max / cardiorespiratory fitness modifier for Vital8."""

from __future__ import annotations

from typing import Any


CRF_CATEGORIES = {
    "p80": {"label": ">=80th percentile", "score": 100, "interpretation": "Elite / highly fit"},
    "p60_79": {"label": "60th-79th percentile", "score": 80, "interpretation": "Fit"},
    "p40_59": {"label": "40th-59th percentile", "score": 60, "interpretation": "Moderate fitness"},
    "p20_39": {"label": "20th-39th percentile", "score": 40, "interpretation": "Below average fitness"},
    "p_under20": {"label": "<20th percentile", "score": 20, "interpretation": "Low fitness"},
}

MEDIAN_VO2 = {
    "Male": {
        (20, 29): 45.0,
        (30, 39): 41.0,
        (40, 49): 37.0,
        (50, 59): 33.0,
        (60, 69): 28.5,
        (70, 79): 22.0,
    },
    "Female": {
        (20, 29): 34.5,
        (30, 39): 31.0,
        (40, 49): 28.0,
        (50, 59): 25.0,
        (60, 69): 21.5,
        (70, 79): 16.5,
    },
}


def median_vo2_for_age_sex(age: int | None, sex: str | None) -> float | None:
    if age is None or sex not in MEDIAN_VO2:
        return None
    for (low, high), median in MEDIAN_VO2[sex].items():
        if low <= age <= high:
            return median
    return None


def estimate_percentile_category(vo2max: float | None, age: int | None, sex: str | None) -> dict[str, Any]:
    median = median_vo2_for_age_sex(age, sex)
    if vo2max is None or median is None or median <= 0:
        return {"category_key": None, "median": median, "ratio": None}

    ratio = vo2max / median
    if ratio >= 1.20:
        category_key = "p80"
    elif ratio >= 1.08:
        category_key = "p60_79"
    elif ratio >= 0.92:
        category_key = "p40_59"
    elif ratio >= 0.75:
        category_key = "p20_39"
    else:
        category_key = "p_under20"
    return {"category_key": category_key, "median": median, "ratio": ratio}


def vmq_from_crf_score(crf_score: int) -> float:
    return 0.80 + (0.004 * crf_score)


def calculate_fitness_adjustment(raw_le8: int | None, category_key: str | None) -> dict[str, Any]:
    if category_key is None or category_key not in CRF_CATEGORIES:
        return {
            "category": None,
            "crf_score": None,
            "vmq": None,
            "modified_score": None,
        }

    category = CRF_CATEGORIES[category_key]
    crf_score = category["score"]
    vmq = vmq_from_crf_score(crf_score)
    modified = None
    if raw_le8 is not None:
        modified = round(max(0, min(100, raw_le8 * vmq)))

    return {
        "category": category,
        "crf_score": crf_score,
        "vmq": vmq,
        "modified_score": modified,
    }
