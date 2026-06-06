"""Weighted intent signal scoring engine. Normalizes signals to 0-100 ICP fit score."""

from datetime import datetime, timezone
from typing import Any

SIGNAL_WEIGHTS = {
    "funding": 3.0,
    "executive_change": 2.5,
    "hiring": 2.0,
    "tech_adoption": 1.5,
    "review_activity": 1.0,
}

MAX_RAW_SCORE = 30.0  # 5 signals × 3.0 (max weight) × 2 (recency boost max)


def score_signals(signals: list[dict], days_back: int = 90) -> dict:
    """Score a list of signals and return a normalized ICP fit score (0-100).

    Args:
        signals: List of signal dicts with keys: signal_type, weight, detected_at
        days_back: How far back to consider for recency boost

    Returns:
        Dict with total_score, breakdown per signal, and reason summary
    """
    if not signals:
        return {"total_score": 0, "breakdown": [], "summary": "No signals detected"}

    now = datetime.now(timezone.utc)
    scored = []
    raw_total = 0.0

    for s in signals:
        s_type = s.get("signal_type", "")
        base_weight = SIGNAL_WEIGHTS.get(s_type, 1.0)
        weight = float(s.get("weight", base_weight))

        detected_str = s.get("detected_at", "")
        try:
            detected = datetime.fromisoformat(detected_str.replace("Z", "+00:00"))
            days_ago = (now - detected).days
        except (ValueError, TypeError):
            days_ago = 999

        if days_ago <= 7:
            recency_boost = 2.0
        elif days_ago <= 30:
            recency_boost = 1.5
        elif days_ago <= 60:
            recency_boost = 1.2
        elif days_ago <= 90:
            recency_boost = 1.0
        else:
            recency_boost = 0.5

        signal_score = weight * recency_boost
        raw_total += signal_score

        scored.append({
            "signal_type": s_type,
            "title": s.get("title", ""),
            "weight": weight,
            "recency_boost": recency_boost,
            "days_ago": days_ago,
            "score": round(signal_score, 1),
        })

    normalized = min(100, int((raw_total / MAX_RAW_SCORE) * 100))
    scored.sort(key=lambda x: x["score"], reverse=True)

    top_signals = [s["title"] for s in scored[:3] if s["title"]]
    summary = f"{len(scored)} signals processed. Top: {'; '.join(top_signals)}." if top_signals else f"{len(scored)} signals processed."

    return {
        "total_score": normalized,
        "breakdown": scored,
        "raw_total": round(raw_total, 1),
        "summary": summary,
    }


def recommend_engagement_priority(score: int, signals: list[dict]) -> str:
    """Map ICP score to engagement recommendation."""
    if score >= 80:
        return "HIGH — Contact immediately. Multiple strong signals indicate active buying window."
    elif score >= 50:
        return "MEDIUM — Worth pursuing. Nurture with relevant content and monitor for new signals."
    else:
        return "LOW — Monitor only. Insufficient signal strength to warrant outbound effort."
