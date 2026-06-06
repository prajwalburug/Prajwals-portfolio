#!/usr/bin/env python3
"""GTM Intelligence Agent — orchestrates the full account research pipeline.

Usage:
    python code/agent.py --company "Meridian Capital Partners" --demo
    python code/agent.py --company "Meridian Capital Partners" --demo --dry-run
    python code/agent.py --company "Meridian" --demo --output ./brief-output.json
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone

import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import search_web, get_signals, search_deals, generate_email as gen_email
from clay_mock import enrich_account
from signal_scorer import score_signals, recommend_engagement_priority


def research_account(company: str) -> dict:
    """Execute the full 7-step account research pipeline.

    Returns a structured dict with all research findings.
    """
    result = {"company": company, "researched_at": datetime.now(timezone.utc).isoformat(), "steps": {}}

    # Step 2: CRM Context
    deals = search_deals(company=company)
    result["steps"]["crm_context"] = {"deals_found": len(deals), "deals": deals}

    # Step 3: Enrichment
    enrichment = enrich_account(company)
    result["steps"]["enrichment"] = enrichment
    result["company_info"] = {
        "industry": enrichment.get("industry"),
        "headcount": enrichment.get("employee_count"),
        "revenue": enrichment.get("revenue_range"),
        "funding": enrichment.get("funding"),
        "tech_stack": enrichment.get("technologies"),
        "location": enrichment.get("location"),
    }

    # Step 4: Signal Scoring
    signals_result = get_signals(company)
    result["steps"]["signals"] = signals_result
    icp_data = signals_result.get("scored", {})
    result["icp_score"] = icp_data.get("total_score", 0)
    result["signals"] = signals_result.get("signals", [])
    result["engagement_priority"] = recommend_engagement_priority(result["icp_score"], result["signals"])

    # Step 5: Competitive Intel
    web_results = search_web(company, "competitor review G2 Capterra")
    competitor_flags = []
    for item in web_results:
        if "allvue" in item.get("title", "").lower() or "allvue" in item.get("snippet", "").lower():
            competitor_flags.append({"competitor": "Allvue", "source": item["source"], "evidence": item.get("snippet", ""), "risk": "pilot_in_progress"})
    result["steps"]["competitive_intel"] = {"results_scanned": len(web_results), "competitor_flags": competitor_flags}
    result["competitor_flags"] = competitor_flags

    # Step 5b: Web signal search
    news = search_web(company, "news funding hiring")
    result["steps"]["web_signals"] = {"articles_found": len(news), "articles": news}

    # Step 6: Brief
    brief = _build_brief(result)
    result["brief"] = brief

    # Step 6b: Email
    email = gen_email({"company": company, "signals": result["signals"], "recommended_angle": brief.get("recommended_angle", "")})
    result["email_draft"] = email

    return result


def _build_brief(data: dict) -> dict:
    ci = data.get("competitor_flags", [])
    return {
        "company_snapshot": data.get("company_info", {}),
        "top_signals": [
            {"title": s.get("title", ""), "type": s.get("signal_type", ""), "source": s.get("source", ""), "weight": s.get("weight", 1.0)}
            for s in data.get("signals", [])[:3]
        ],
        "icp_score": data.get("icp_score", 0),
        "engagement_priority": data.get("engagement_priority", ""),
        "competitor_flags": [f.get("competitor", "") for f in ci],
        "competitive_landscape": f"{len(ci)} competitor flag(s) detected. {'Prospect is actively evaluating alternatives.' if ci else 'No competitor flags detected.'}",
        "recommended_angle": "Lead with operations efficiency angle — post-funding companies invest in infrastructure. Reference the new CFO as a natural entry point." if data.get("icp_score", 0) >= 50 else "Monitor — insufficient signal strength for outbound.",
    }


def write_brief_to_file(data: dict, output_dir: str = "./briefs"):
    """Write the research output to the file store."""
    company = data.get("company", "unknown").lower().replace(" ", "-")
    date = datetime.now().strftime("%Y-%m-%d")
    manager = "jessica-ryan"
    dir_path = os.path.join(output_dir, manager, company)
    os.makedirs(dir_path, exist_ok=True)

    # Write brief
    brief_path = os.path.join(dir_path, f"{date}--brief.json")
    with open(brief_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Brief written: {brief_path}", file=sys.stderr)

    # Write email draft
    email = data.get("email_draft", {})
    email_path = os.path.join(dir_path, f"{date}--email-draft.txt")
    with open(email_path, "w") as f:
        f.write(f"Subject: {email.get('subject', '')}\n")
        f.write(f"{email.get('greeting', '')}\n\n")
        f.write(f"{email.get('body', '')}\n")
    print(f"Email draft written: {email_path}", file=sys.stderr)

    return brief_path


def format_demo_output(data: dict) -> str:
    """Format research output as a readable console summary (matches the output mock in the spec)."""
    ci = data.get("company", "")
    score = data.get("icp_score", 0)
    signals = data.get("signals", [])
    flags = data.get("competitor_flags", [])

    lines = [f"{ci}", "=" * 50]
    lines.append(f"ICP Fit Score:  {score}/100")
    lines.append(f"Active Signals: {len(signals)}")
    lines.append(f"Competitor Flags: {len(flags)}")
    lines.append(f"Researched:     {data.get('researched_at', '')[:19].replace('T', ' ')}")
    lines.append("-" * 30)
    lines.append("Top Signals")
    lines.append("")

    for i, s in enumerate(signals[:3], 1):
        lines.append(f"=> {s.get('title', 'Signal')} - {_recency_label(s.get('detected_at', ''))}")
        lines.append(f"  {s.get('description', '')}")
        lines.append(f"  Source: {s.get('source', '')} . Weight: {s.get('weight', 1.0)}x")
        lines.append("")

    lines.append("-" * 30)
    lines.append("Competitive Intel")
    lines.append("")

    if flags:
        for f in flags:
            lines.append(f"Currently using/piloting {f.get('competitor', 'unknown')}.")
            lines.append(f"Risk: {f.get('risk', 'unknown')}")
    else:
        lines.append("No competitor flags detected - greenfield opportunity.")

    lines.append("")
    lines.append("-" * 30)
    lines.append(f"Engagement: {data.get('engagement_priority', 'N/A')}")
    lines.append("[Draft Outreach] [Comp Strategy] [Add to Sequence]")

    return "\n".join(lines)


def _recency_label(detected_at: str) -> str:
    try:
        dt = datetime.fromisoformat(detected_at.replace("Z", "+00:00"))
        now = datetime.now().astimezone()
        days = (now - dt).days
        return f"{days}d ago"
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser(description="GTM Intelligence Agent - Account Research Pipeline")
    parser.add_argument("--company", required=True, help="Company name to research")
    parser.add_argument("--demo", action="store_true", help="Run with mock data")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without writing to file store")
    parser.add_argument("--output", type=str, help="Path to write JSON output")
    args = parser.parse_args()

    data = research_account(args.company)

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
        write_brief_to_file(data)

    print(format_demo_output(data))


if __name__ == "__main__":
    main()
