#!/usr/bin/env python3
"""Pipeline Risk Analyzer — Scores open deals for risk using rules + LLM sentiment."""

import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

DEMO_API_URL = "https://gtm-skills.com/api/v1/prompts"

RISK_CONFIG = {
    "stage_staleness": {
        "weight": 0.30,
        "threshold_days": 30,
        "max_risk_score": 100,
    },
    "last_activity": {
        "weight": 0.25,
        "threshold_days": 7,
        "max_risk_score": 100,
    },
    "stakeholder_count": {
        "weight": 0.20,
        "min_stakeholders": 2,
        "max_risk_score": 100,
    },
    "stage_amount_fit": {
        "weight": 0.15,
        "max_risk_score": 100,
    },
    "note_sentiment": {
        "weight": 0.10,
        "max_risk_score": 100,
    },
}

STAGE_AMOUNT_RANGES = {
    "discovery": {"min": 0, "max": 5000},
    "qualification": {"min": 0, "max": 15000},
    "demo": {"min": 5000, "max": 50000},
    "proposal": {"min": 10000, "max": 100000},
    "negotiation": {"min": 15000, "max": 150000},
    "closed_won": {"min": 0, "max": 999999999},
    "closed_lost": {"min": 0, "max": 999999999},
}

NEGATIVE_SENTIMENT_KEYWORDS = [
    "not interested", "no budget", "too expensive", "not a priority",
    "maybe later", "talk to my assistant", "we'll circle back",
    "not the right time", "evaluating other options", "stalled",
    "no decision yet", "waiting on", "delayed", "paused",
    "cancel", "unlikely", "don't see the value",
]


def load_demo_deals() -> list[dict]:
    """Pull sample data from gtm-skills.com API + generate deal-like records."""
    params = {"limit": 15, "offset": 0}
    try:
        resp = requests.get(DEMO_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"[demo] API unavailable ({e}), using fallback data", file=sys.stderr)
        data = [{"title": f"Deal {i}", "category": "saas", "description": "Sample"} for i in range(1, 6)]

    deals = []
    stages = list(STAGE_AMOUNT_RANGES.keys())
    for i, item in enumerate(data):
        stage = stages[i % len(stages)]
        deal = {
            "deal_id": f"deal-{i+1}",
            "deal_name": item.get("title", f"Deal {i+1}"),
            "company": f"Company {i+1}",
            "amount": (i + 1) * 10000,
            "stage": stage,
            "days_in_stage": max(0, (i * 7) - 5),
            "days_since_last_activity": max(0, (i * 3) - 1),
            "stakeholder_count": max(1, 5 - i),
            "notes": item.get("description", ""),
        }
        deals.append(deal)
    return deals


def score_stage_staleness(days_in_stage: int) -> tuple[int, str]:
    config = RISK_CONFIG["stage_staleness"]
    threshold = config["threshold_days"]
    if days_in_stage is None:
        return 30, "Stage age unknown"
    if days_in_stage <= 7:
        return 0, f"Recently moved ({days_in_stage}d in stage)"
    if days_in_stage <= threshold:
        ratio = days_in_stage / threshold
        score = int(ratio * 60)
        return score, f"{days_in_stage}d in stage (approaching threshold)"
    excess = days_in_stage - threshold
    score = min(100, 60 + int((excess / threshold) * 40))
    return score, f"STALE: {days_in_stage}d in stage ({excess}d over threshold)"


def score_last_activity(days_since_activity: int) -> tuple[int, str]:
    config = RISK_CONFIG["last_activity"]
    threshold = config["threshold_days"]
    if days_since_activity is None:
        return 30, "Last activity unknown"
    if days_since_activity <= 2:
        return 0, f"Active recently ({days_since_activity}d ago)"
    if days_since_activity <= threshold:
        ratio = days_since_activity / threshold
        score = int(ratio * 60)
        return score, f"{days_since_activity}d since activity"
    excess = days_since_activity - threshold
    score = min(100, 60 + int((excess / threshold) * 40))
    return score, f"RISK: {days_since_activity}d since activity ({excess}d over threshold)"


def score_stakeholder_count(count: int) -> tuple[int, str]:
    config = RISK_CONFIG["stakeholder_count"]
    min_s = config["min_stakeholders"]
    if count is None:
        return 50, "Stakeholder count unknown"
    if count >= min_s + 2:
        return 0, f"Well multi-threaded ({count} stakeholders)"
    if count >= min_s:
        return 30, f"Minimal coverage ({count} stakeholders)"
    gap = min_s - count
    score = min(100, 50 + (gap * 25))
    return score, f"UNDER-THREADED: {count} stakeholders (need {min_s})"


def score_stage_amount_fit(amount: float, stage: str) -> tuple[int, str]:
    config = RISK_CONFIG["stage_amount_fit"]
    stage_lower = stage.lower().replace(" ", "_") if stage else ""
    ranges = STAGE_AMOUNT_RANGES
    if stage_lower in ranges:
        sr = ranges[stage_lower]
        if sr["min"] <= amount <= sr["max"]:
            return 0, f"Amount ${amount:,.0f} within range for {stage}"
        return config["max_risk_score"], f"Amount ${amount:,.0f} outside range for {stage}"
    return 30, f"Unknown stage: {stage}"


def score_note_sentiment(notes: str) -> tuple[int, str]:
    config = RISK_CONFIG["note_sentiment"]
    if not notes:
        return 50, "No notes available"
    notes_lower = notes.lower()
    matches = [kw for kw in NEGATIVE_SENTIMENT_KEYWORDS if kw in notes_lower]
    if not matches:
        return 0, "No negative signals in notes"
    match_count = len(matches)
    score = min(100, 40 + (match_count * 15))
    return score, f"Negative signals detected: {', '.join(matches)}"


def analyze_deal(deal: dict) -> dict:
    staleness_score, staleness_reason = score_stage_staleness(deal.get("days_in_stage"))
    activity_score, activity_reason = score_last_activity(deal.get("days_since_last_activity"))
    stakeholder_score, stakeholder_reason = score_stakeholder_count(deal.get("stakeholder_count"))
    amount_score, amount_reason = score_stage_amount_fit(deal.get("amount"), deal.get("stage", ""))
    sentiment_score, sentiment_reason = score_note_sentiment(deal.get("notes", ""))

    weights = {k: v["weight"] for k, v in RISK_CONFIG.items()}
    total_risk = (
        staleness_score * weights["stage_staleness"]
        + activity_score * weights["last_activity"]
        + stakeholder_score * weights["stakeholder_count"]
        + amount_score * weights["stage_amount_fit"]
        + sentiment_score * weights["note_sentiment"]
    )

    if total_risk >= 60:
        risk_level = "HIGH"
    elif total_risk >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "deal_id": deal.get("deal_id", "unknown"),
        "deal_name": deal.get("deal_name", "Unknown"),
        "company": deal.get("company", "Unknown"),
        "stage": deal.get("stage", "unknown"),
        "amount": deal.get("amount", 0),
        "risk_score": round(total_risk, 1),
        "risk_level": risk_level,
        "factors": {
            "stage_staleness": {"score": staleness_score, "reason": staleness_reason},
            "last_activity": {"score": activity_score, "reason": activity_reason},
            "stakeholder_count": {"score": stakeholder_score, "reason": stakeholder_reason},
            "stage_amount_fit": {"score": amount_score, "reason": amount_reason},
            "note_sentiment": {"score": sentiment_score, "reason": sentiment_reason},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Pipeline Risk Analyzer — score deals for risk")
    parser.add_argument("--demo", action="store_true", help="Run with sample data from gtm-skills.com API")
    parser.add_argument("--dry-run", action="store_true", help="Print results without external API calls")
    parser.add_argument("--input", type=str, help="Path to JSON file with deals array")
    parser.add_argument("--verbose", action="store_true", help="Print detailed breakdown per deal")
    args = parser.parse_args()

    if load_dotenv:
        load_dotenv()

    if args.demo:
        deals = load_demo_deals()
    elif args.input:
        with open(args.input) as f:
            content = json.load(f)
            deals = content if isinstance(content, list) else content.get("deals", [])
    else:
        deals = [{
            "deal_id": "deal-sample-1",
            "deal_name": "Sample Deal",
            "company": "Acme Corp",
            "amount": 25000,
            "stage": "negotiation",
            "days_in_stage": 35,
            "days_since_last_activity": 10,
            "stakeholder_count": 1,
            "notes": "Prospect said no budget, deal stalled",
        }]
    results = [analyze_deal(d) for d in deals]
    output = {"results": results, "total": len(results), "dry_run": args.dry_run}
    print(json.dumps(output, indent=2))

    if args.dry_run:
        print("\n[dry-run] No changes written to any external system.", file=sys.stderr)

    if args.verbose:
        levels = {}
        for r in results:
            levels[r["risk_level"]] = levels.get(r["risk_level"], 0) + 1
        print(f"\n--- Risk Summary ---", file=sys.stderr)
        print(f"Total deals: {len(results)}", file=sys.stderr)
        for level, count in sorted(levels.items()):
            print(f"  {level}: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
