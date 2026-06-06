"""Mock Gong conversation intelligence API. Returns sample call transcripts."""

from __future__ import annotations
import json
import os
from typing import Any


def _load_fixtures() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "fixtures", "gong-calls.json")
    with open(path) as f:
        return json.load(f)


def get_transcript(company: str = "", call_id: str = "") -> dict[str, Any]:
    """Get call transcript data for a company. Mirrors Gong API response.

    Args:
        company: Company name to find calls for
        call_id: Specific call ID

    Returns:
        Dict with call metadata, participants, topics, key points,
        sentiment, action items, and MEDDPICC analysis.
    """
    fixtures = _load_fixtures()

    if call_id:
        for call in fixtures:
            if call["call_id"] == call_id:
                return _format_call(call)
        return {"error": f"Call not found: {call_id}"}

    if company:
        company_lower = company.lower()
        for call in fixtures:
            if company_lower in call.get("company", "").lower():
                return _format_call(call)
        return {"error": f"No calls found for: {company}"}

    return {"error": "Provide company name or call_id"}


def _format_call(call: dict) -> dict:
    return {
        "call_id": call["call_id"],
        "company": call["company"],
        "date": call["date"],
        "duration_minutes": round(call["duration_seconds"] / 60, 1),
        "participants": call["participants"],
        "topics_discussed": call["topics"],
        "key_points": call["key_points"],
        "sentiment": call["sentiment"],
        "action_items": call["action_items"],
        "meddpicc_analysis": call["meddpicc"],
    }


def list_available_calls() -> list[dict]:
    """Return summary of all available calls."""
    return [{"call_id": c["call_id"], "company": c["company"], "date": c["date"], "duration_minutes": round(c["duration_seconds"] / 60, 1)} for c in _load_fixtures()]
