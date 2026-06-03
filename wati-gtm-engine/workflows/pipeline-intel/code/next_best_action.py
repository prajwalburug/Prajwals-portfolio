#!/usr/bin/env python3
"""Next-Best-Action Engine — Maps deal risk patterns to actionable recommendations."""

import argparse
import json
import sys

RECOMMENDATIONS = {

    "stale_stage": {
        "condition": "stage_staleness >= 60",
        "actions": [
            {
                "action": "Schedule executive check-in",
                "why": "Deal has been in the same stage for an extended period. Escalate to re-engage.",
            },
            {
                "action": "Review deal qualification — is this a real opportunity?",
                "why": "Stale deals often indicate the opportunity isn't real or qualification was missed.",
            },
            {
                "action": "Set a 'close or kill' deadline with the rep",
                "why": "Forced decision prevents pipeline bloat and focuses effort on winnable deals.",
            },
        ],
    },

    "low_activity": {
        "condition": "last_activity >= 60",
        "actions": [
            {
                "action": "Send value-add follow-up (case study, blog post, industry insight)",
                "why": "Prospect went dark — bring new value to restart the conversation.",
            },
            {
                "action": "Try a different channel (LinkedIn, phone, mutual connection intro)",
                "why": "Email isn't working — switch channels to re-engage.",
            },
            {
                "action": "Ask champion about internal changes or competing priorities",
                "why": "Silence often means internal changes, not disinterest.",
            },
        ],
    },

    "under_threaded": {
        "condition": "stakeholder_count >= 60",
        "actions": [
            {
                "action": "Map and engage at least 2 more stakeholders",
                "why": "Single-threaded deals have 3x higher slip risk. Need buy-in from others.",
            },
            {
                "action": "Ask champion: 'Who else should be part of this conversation?'",
                "why": "Low-friction way to discover the full buying committee.",
            },
            {
                "action": "Prepare stakeholder-specific value props for each persona",
                "why": "Different roles care about different outcomes — tailor accordingly.",
            },
        ],
    },

    "amount_mismatch": {
        "condition": "stage_amount_fit >= 60",
        "actions": [
            {
                "action": "Validate deal size expectations — is this the right stage for this amount?",
                "why": "Amount doesn't match typical stage range. May need re-staging or scoping.",
            },
            {
                "action": "Consider splitting into phased deal if amount is too large for stage",
                "why": "Large deals can stall. A pilot phase reduces risk and gets momentum.",
            },
        ],
    },

    "negative_sentiment": {
        "condition": "note_sentiment >= 40",
        "actions": [
            {
                "action": "Schedule a discovery call to address unspoken concerns",
                "why": "Negative signals in notes suggest hidden objections that need surfacing.",
            },
            {
                "action": "Send ROI calculator or business case to re-anchor on value",
                "why": "Objections often stem from unclear value. Quantify the impact.",
            },
            {
                "action": "Bring in a sales engineer or executive sponsor for credibility",
                "why": "Technical or budget concerns may need authority figures to address.",
            },
        ],
    },
}


def get_recommendations(deal_risk: dict) -> list[dict]:
    triggered = []
    factors = deal_risk.get("factors", {})

    factor_scores = {
        "stage_staleness": factors.get("stage_staleness", {}).get("score", 0),
        "last_activity": factors.get("last_activity", {}).get("score", 0),
        "stakeholder_count": factors.get("stakeholder_count", {}).get("score", 0),
        "stage_amount_fit": factors.get("stage_amount_fit", {}).get("score", 0),
        "note_sentiment": factors.get("note_sentiment", {}).get("score", 0),
    }

    for rec_key, rec in RECOMMENDATIONS.items():
        condition_expr = rec["condition"]
        var_name = condition_expr.split(" ")[0]
        threshold = int(condition_expr.split(" ")[-1])
        actual_score = factor_scores.get(var_name, 0)
        threshold_match = actual_score >= threshold

        if threshold_match:
            for action in rec["actions"]:
                triggered.append({
                    "trigger": rec_key,
                    "trigger_score": actual_score,
                    "action": action["action"],
                    "why": action["why"],
                })

    if not triggered:
        triggered.append({
            "trigger": "no_action_needed",
            "trigger_score": 0,
            "action": "No action needed — deal is healthy",
            "why": "All risk factors are within acceptable thresholds.",
        })

    return triggered


def main():
    parser = argparse.ArgumentParser(description="Next-Best-Action Engine — recommend actions from deal risk data")
    parser.add_argument("--input", type=str, help="Path to JSON file from analyze_pipeline.py")
    parser.add_argument("--demo", action="store_true", help="Run with built-in sample data")
    parser.add_argument("--dry-run", action="store_true", help="Print recommendations without side effects")
    args = parser.parse_args()

    if args.demo:
        sample_risks = [
            {
                "deal_id": "deal-risk-1",
                "deal_name": "Enterprise SaaS Corp",
                "risk_level": "HIGH",
                "risk_score": 78.4,
                "factors": {
                    "stage_staleness": {"score": 78, "reason": "44d in stage"},
                    "last_activity": {"score": 100, "reason": "20d since activity"},
                    "stakeholder_count": {"score": 75, "reason": "Only 1 stakeholder"},
                    "stage_amount_fit": {"score": 100, "reason": "Amount $80k outside range"},
                    "note_sentiment": {"score": 50, "reason": "No budget in notes"},
                },
            },
            {
                "deal_id": "deal-healthy-1",
                "deal_name": "Growth Stage Startup",
                "risk_level": "LOW",
                "risk_score": 15.0,
                "factors": {
                    "stage_staleness": {"score": 0, "reason": "3d in stage"},
                    "last_activity": {"score": 0, "reason": "1d since activity"},
                    "stakeholder_count": {"score": 0, "reason": "5 stakeholders"},
                    "stage_amount_fit": {"score": 0, "reason": "Amount within range"},
                    "note_sentiment": {"score": 0, "reason": "Positive engagement"},
                },
            },
        ]
        deals = sample_risks
    elif args.input:
        with open(args.input) as f:
            data = json.load(f)
            deals = data.get("results", data if isinstance(data, list) else [])
    else:
        deals = [{
            "deal_id": "sample-1",
            "deal_name": "Sample Deal",
            "risk_level": "HIGH",
            "risk_score": 70,
            "factors": {
                "stage_staleness": {"score": 80, "reason": "40d in stage"},
                "last_activity": {"score": 100, "reason": "14d since activity"},
                "stakeholder_count": {"score": 75, "reason": "Only 1 stakeholder"},
                "stage_amount_fit": {"score": 0, "reason": "Amount within range"},
                "note_sentiment": {"score": 0, "reason": "No notes"},
            },
        }]

    results = []
    for deal in deals:
        recommendations = get_recommendations(deal)
        results.append({
            "deal_id": deal.get("deal_id", "unknown"),
            "deal_name": deal.get("deal_name", "Unknown"),
            "current_risk_level": deal.get("risk_level", "unknown"),
            "current_risk_score": deal.get("risk_score", 0),
            "recommendations": recommendations,
        })

    output = {"results": results, "total": len(results), "dry_run": args.dry_run}
    print(json.dumps(output, indent=2))

    if args.dry_run:
        print("\n[dry-run] No recommendations sent to HubSpot or Slack.", file=sys.stderr)


if __name__ == "__main__":
    main()
