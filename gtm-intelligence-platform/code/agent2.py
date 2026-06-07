#!/usr/bin/env python3
"""GTM Intelligence Agent 2 — Deal Intelligence & Opportunity Scoring pipeline.

Usage:
    python code/agent2.py --company "Meridian Capital Partners" --deal-id deal-001 --demo
    python code/agent2.py --company "Meridian Capital Partners" --deal-id deal-001 --demo --dry-run
    python code/agent2.py --company "Meridian" --deal-id deal-001 --output ./score-output.json
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import search_deals, get_transcript
from meddic_scorer import score_dimensions, generate_nba, score_from_transcript
from deal_scorer import score_deal_health
from mcp_server import search_similar_deals as mcp_similar


DEAL_STAGES = ["discovery", "qualification", "demo", "evaluation", "proposal", "negotiation", "closed_won"]

SAMPLE_DEALS = {
    "deal-001": {
        "company": "Meridian Capital Partners",
        "stage": "qualification",
        "acv": 2400000,
        "owner": "Jessica Ryan",
        "stage_days": 25,
        "days_since_last_call": 4,
        "has_competitor": True,
        "icp_score": 87,
        "champion_name": "Marcus Webb",
        "eb_name": "Sarah Chen",
    },
    "deal-002": {
        "company": "Apex Analytics",
        "stage": "discovery",
        "acv": 600000,
        "owner": "Tom Rivera",
        "stage_days": 12,
        "days_since_last_call": 2,
        "has_competitor": False,
        "icp_score": 62,
        "champion_name": "Aisha Patel",
        "eb_name": "",
    },
}


def score_deal(company: str, deal_id: str) -> dict:
    """Execute the full 8-step deal scoring pipeline.

    Returns a structured dict with deal scorecard and handoff context.
    """
    result = {
        "company": company,
        "deal_id": deal_id,
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "steps": {},
        "handoff_to_agent3": None,
    }

    # Step 1: Context Assembly
    deal_context = SAMPLE_DEALS.get(deal_id, {})
    if not deal_context:
        crm = search_deals(company=company)
        if crm:
            deal_context = {"company": company, "crm_data": crm}
    result["steps"]["context_assembly"] = {
        "deal_context": deal_context,
        "context_fields": list(deal_context.keys()),
    }

    # Step 2: Fetch Transcripts
    calls = get_transcript(company=company, max_results=3)
    result["steps"]["transcripts"] = {
        "calls_found": len(calls) if isinstance(calls, list) else 1,
        "call_ids": [c["call_id"] for c in calls] if isinstance(calls, list) else [calls.get("call_id", "")],
    }
    transcript_calls = calls if isinstance(calls, list) else [calls]

    # Step 3: MEDDIC Analysis
    all_transcript_text = ""
    for c in transcript_calls:
        turns = c.get("full_transcript", [])
        for t in turns:
            all_transcript_text += f"{t.get('speaker', 'Agent')}: {t.get('text', '')}\n"

    meddic_scores = score_from_transcript(all_transcript_text)
    meddic_analysis = score_dimensions(meddic_scores)
    result["steps"]["meddic_analysis"] = {
        "transcript_length_chars": len(all_transcript_text),
        "calls_analyzed": len(transcript_calls),
        "extracted_scores": meddic_scores,
        "dimension_scores": meddic_analysis["dimension_scores"],
    }

    # Step 4: Gap Detection
    gaps = meddic_analysis["gaps"]
    result["steps"]["gap_detection"] = {
        "gap_count": meddic_analysis["gap_count"],
        "top_gap": meddic_analysis["top_gap"],
        "gaps": [{"dimension": g["key"], "score": g["score"], "risk": g["risk_label"]} for g in gaps],
    }

    # Step 5: Similar Deal Lookup
    similar = mcp_similar(company=company, meddic_profile=meddic_scores)
    result["steps"]["similar_deals"] = {
        "matches_found": len(similar),
        "matches": similar,
    }

    # Step 6: Deal Health Score
    ctx = deal_context
    health = score_deal_health(
        meddic_completeness=meddic_analysis["meddic_completeness"],
        account_icp_score=ctx.get("icp_score", 50),
        stage=ctx.get("stage", "discovery"),
        stage_created_days_ago=ctx.get("stage_days", 30),
        last_call_days_ago=ctx.get("days_since_last_call", 14),
        acv=ctx.get("acv", 100000),
        has_competitor=ctx.get("has_competitor", False),
    )
    result["steps"]["deal_health"] = health

    # Step 7: NBA Generation
    nba = generate_nba(meddic_analysis, ctx)
    result["steps"]["next_best_action"] = nba

    # Step 8: Build Scorecard & Handoff
    scorecard = {
        "deal_id": deal_id,
        "company": company,
        "deal_health_score": health["total_score"],
        "deal_health_label": health["health_label"],
        "meddic_completeness": meddic_analysis["meddic_completeness"],
        "meddic_scores": {d["key"]: d["score"] for d in meddic_analysis["dimension_scores"]},
        "meddic_gap_count": meddic_analysis["gap_count"],
        "meddic_top_gap": meddic_analysis["top_gap"],
        "meddic_gaps": [{"dimension": g["key"], "score": g["score"], "risk": g["risk_label"]} for g in gaps],
        "nba_text": nba["nba_text"],
        "nba_action": nba["action"],
        "warnings": health["warnings"],
        "scored_at": result["scored_at"],
    }
    result["scorecard"] = scorecard

    # Chain handoff to Agent 3 — structured JSON, no prose re-parsing
    result["handoff_to_agent3"] = {
        "source_agent": "agent2",
        "handoff_type": "deal_scored",
        "target_agent": "agent3",
        "deal_id": deal_id,
        "company": company,
        "deal_health_score": health["total_score"],
        "deal_health_label": health["health_label"],
        "meddic_completeness": meddic_analysis["meddic_completeness"],
        "meddic_gaps": [
            {"dimension": g["key"], "score": g["score"], "risk": g["risk_label"]}
            for g in gaps
        ],
        "meddic_top_gap": meddic_analysis["top_gap"],
        "nba_text": nba["nba_text"],
        "warnings": health["warnings"],
        "transcript_call_ids": result["steps"]["transcripts"]["call_ids"],
        "scored_at": result["scored_at"],
    }

    return result


def format_demo_output(data: dict) -> str:
    """Format scoring output as a readable console summary."""
    sc = data.get("scorecard", {})
    steps = data.get("steps", {})
    ctx = steps.get("context_assembly", {}).get("deal_context", {})

    lines = [
        f"{data['company']}  |  {data['deal_id']}",
        "=" * 60,
        f"Deal Health:  {sc.get('deal_health_score', 'N/A')}/100  ({sc.get('deal_health_label', 'N/A').upper()})",
        f"MEDDIC:       {sc.get('meddic_completeness', 'N/A')}/100 completeness  ({sc.get('meddic_gap_count', 0)} gaps)",
        f"Owner:        {ctx.get('owner', 'N/A')}  |  Stage: {ctx.get('stage', 'N/A')} ({ctx.get('stage_days', '?')}d)  |  ${ctx.get('acv', 0):,} ACV",
        f"Transcribed:  {steps.get('transcripts', {}).get('calls_found', 0)} calls  |  {steps.get('transcripts', {}).get('call_ids', [])}",
        f"Similar:      {steps.get('similar_deals', {}).get('matches_found', 0)} closed-won matches",
        "-" * 60,
        "MEDDIC Scores",
    ]

    dims = steps.get("meddic_analysis", {}).get("dimension_scores", [])
    for d in dims:
        gap = " GAP" if d.get("is_gap") else ""
        risk = f" ({d['risk_label']})" if d.get("is_gap") else ""
        lines.append(f"  {d['label']:30s}  {d['score']}/10{gap}{risk}")

    gaps = steps.get("gap_detection", {}).get("gaps", [])
    if gaps:
        lines.extend(["-" * 60, "Gaps by Risk", ""])
        for g in gaps:
            lines.append(f"  {g['dimension']:25s}  score={g['score']}  risk={g['risk']}")

    nba = steps.get("next_best_action", {})
    if nba.get("nba_text"):
        lines.extend(["-" * 60, "Next Best Action", f"  {nba['nba_text']}"])

    warnings = steps.get("deal_health", {}).get("warnings", [])
    if warnings:
        lines.extend(["-" * 60, "Warnings"])
        for w in warnings:
            lines.append(f"  ! {w}")

    if data.get("handoff_to_agent3"):
        h = data["handoff_to_agent3"]
        lines.extend([
            "-" * 60,
            f"Agent 3 Handoff  ({h['handoff_type']})",
            f"  health={h['deal_health_score']}/100 label={h['deal_health_label']} gaps={len(h['meddic_gaps'])} top_gap={h['meddic_top_gap']}",
            f"  NBA: {h['nba_text'][:80]}...",
        ])

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GTM Intelligence Agent 2 - Deal Scoring Pipeline")
    parser.add_argument("--company", required=True, help="Company name to analyze")
    parser.add_argument("--deal-id", required=True, help="Deal/opportunity ID to score")
    parser.add_argument("--demo", action="store_true", help="Run with mock data")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without writing")
    parser.add_argument("--output", type=str, help="Path to write JSON output")
    args = parser.parse_args()

    data = score_deal(args.company, args.deal_id)

    if args.dry_run:
        print("[dry-run] Dry run mode - no files written.", file=sys.stderr)
        print(format_demo_output(data))
        print("\nFull JSON output:")
        print(json.dumps(data, indent=2, default=str))
        return

    if args.output:
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        score_dir = "./scores"
        os.makedirs(score_dir, exist_ok=True)
        fname = f"{args.company.lower().replace(' ', '-')}--{args.deal_id}--{datetime.now().strftime('%Y-%m-%d')}.json"
        fpath = os.path.join(score_dir, fname)
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Scorecard written: {fpath}", file=sys.stderr)

    print(format_demo_output(data))


if __name__ == "__main__":
    main()
