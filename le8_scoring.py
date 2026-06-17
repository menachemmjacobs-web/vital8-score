"""Compact score-summary helpers for Vital8 AI context."""

from __future__ import annotations

from recommendations import get_domain_recommendation


def score_category(score: int | None, known_count: int) -> str:
    if score is None or known_count < 5:
        return "insufficient data"
    if score >= 80:
        return "high"
    if score >= 50:
        return "moderate"
    return "low"


def build_score_summary(total: dict, components: dict, raw_inputs: dict, next_steps: dict | None = None) -> dict:
    """Build a compact, non-identifying summary for the chatbot."""
    composite_score = total.get("score") if total.get("known_count", 0) >= 5 else None
    domain_scores = {
        name: result.get("score")
        for name, result in components.items()
        if result.get("score") is not None
    }
    missing_domains = [
        name
        for name, result in components.items()
        if result.get("score") is None
    ]
    completed_domains = list(domain_scores.keys())
    strengths = [
        name
        for name, score in domain_scores.items()
        if score >= 80
    ]
    biggest_levers = [
        name
        for name, _score in sorted(domain_scores.items(), key=lambda item: item[1])[:3]
    ]
    recommendation_domains = biggest_levers if biggest_levers else missing_domains[:3]
    recommendations = [
        {"domain": name, "next_step": get_domain_recommendation(name, components[name].get("score"), raw_inputs)}
        for name in recommendation_domains
    ]

    return {
        "composite_score": composite_score,
        "score_category": score_category(composite_score, total.get("known_count", 0)),
        "completed_domains": completed_domains,
        "missing_domains": missing_domains,
        "domain_scores": domain_scores,
        "strengths": strengths,
        "biggest_levers": biggest_levers,
        "next_steps": next_steps or {},
        "recommendations": recommendations,
    }
