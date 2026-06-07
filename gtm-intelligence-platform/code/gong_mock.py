"""Mock Gong conversation intelligence API. Returns sample call transcripts with speaker turns."""

from __future__ import annotations
import json
import os
from typing import Any


def _load_fixtures() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "fixtures", "gong-calls.json")
    with open(path) as f:
        return json.load(f)


def get_transcript(call_id: str = "") -> dict[str, Any]:
    """Get a single call transcript by ID. Mirrors Gong API response.

    Args:
        call_id: Specific call ID to retrieve

    Returns:
        Dict with call metadata, participants, topics, key points,
        sentiment, action items, MEDDPICC analysis, and full transcript.
    """
    fixtures = _load_fixtures()
    for call in fixtures:
        if call["call_id"] == call_id:
            return _format_call(call)
    return {"error": f"Call not found: {call_id}"}


def get_transcripts(company: str = "", max_results: int = 3) -> list[dict]:
    """Get the most recent call transcripts for a company.

    Args:
        company: Company name to find calls for
        max_results: Maximum number of calls to return (default 3)

    Returns:
        List of call dicts sorted by date descending, each with metadata,
        participants, topics, key points, sentiment, MEDDPICC, and full transcript.
    """
    fixtures = _load_fixtures()
    company_lower = company.lower()

    matches = [c for c in fixtures if company_lower in c.get("company", "").lower()]
    matches.sort(key=lambda c: c.get("date", ""), reverse=True)

    if not matches:
        return []

    return [_format_call(c) for c in matches[:max_results]]


def list_available_calls() -> list[dict]:
    """Return summary of all available calls."""
    return [{"call_id": c["call_id"], "company": c["company"], "date": c["date"], "duration_minutes": round(c["duration_seconds"] / 60, 1)} for c in _load_fixtures()]


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
        "full_transcript": call.get("full_transcript", []),
    }
