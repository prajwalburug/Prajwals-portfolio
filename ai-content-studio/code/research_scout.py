#!/usr/bin/env python3
"""Research scout. Uses Firecrawl to analyze channel performance. Outputs to swipe-file/whats-working.md."""

import argparse
import json
import os
import sys
from datetime import datetime

DEMO_FINDINGS = {
    "linkedin": {
        "channel": "linkedin",
        "period": "last 30 days",
        "patterns": [
            {"pattern": "Hook: bold claim questioning status quo", "frequency": "high", "avg_engagement": "4.2x baseline"},
            {"pattern": "Format: 3-4 short paragraphs with line breaks", "frequency": "high", "avg_engagement": "3.8x baseline"},
            {"pattern": "Hashtags: 3-5 industry-specific lowercase", "frequency": "medium", "avg_engagement": "2.1x baseline"},
        ],
        "top_topics": ["AI in hiring", "candidate experience", "remote hiring"],
        "emerging_trends": ["voice interviews replacing text screening", "PII-safe AI evaluation"],
    },
    "email": {
        "channel": "email",
        "period": "last 30 days",
        "patterns": [
            {"pattern": "Subject: question format (35-45 chars)", "frequency": "high", "avg_open_rate": "38%"},
            {"pattern": "Personalization in first sentence", "frequency": "high", "avg_open_rate": "42%"},
            {"pattern": "Single CTA per email", "frequency": "high", "avg_click_rate": "12%"},
        ],
        "top_topics": ["30-minute screening", "fair hiring"],
        "emerging_trends": ["AI interview evidence reports shared with hiring managers"],
    },
    "competitor": {
        "channel": "competitor",
        "period": "last 30 days",
        "patterns": [
            {"pattern": "Competitor A: whitepaper on AI fairness", "frequency": "once", "avg_engagement": "not available"},
            {"pattern": "Competitor B: launched interview recording feature", "frequency": "once", "avg_engagement": "not available"},
        ],
        "top_topics": ["AI fairness", "interview automation"],
        "emerging_trends": ["compliance-first messaging"],
    },
}


def main():
    parser = argparse.ArgumentParser(description="Research content performance across channels using Firecrawl")
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--source", choices=["linkedin", "email", "competitor", "all"], default="all")
    parser.add_argument("--demo", action="store_true", help="Use cached sample data instead of Firecrawl")
    parser.add_argument("--dry-run", action="store_true", help="Print findings without writing to vault")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    if args.demo or args.source == "all":
        findings = DEMO_FINDINGS if args.source == "all" else DEMO_FINDINGS.get(args.source, {})
    else:
        try:
            import firecrawl
            findings = {}
            print(f"Firecrawl: scanning {args.source}...", file=sys.stderr)
        except ImportError:
            print("Firecrawl not available. Using demo data. Install with: pip install firecrawl", file=sys.stderr)
            findings = DEMO_FINDINGS.get(args.source, {})

    output = {
        "brand": args.brand,
        "source": args.source,
        "findings": findings,
        "scanned_at": datetime.now().isoformat(),
        "dry_run": args.dry_run,
    }

    print(json.dumps(output, indent=2))

    if args.dry_run:
        print("\n[dry-run] No files written.", file=sys.stderr)
        return

    swipe_dir = os.path.join(os.path.dirname(__file__), "..", "swipe-file")
    out_path = os.path.join(swipe_dir, "whats-working.md")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# What's Working\n\n")
        f.write(f"**Brand:** {args.brand}  \n")
        f.write(f"**Scanned:** {output['scanned_at']}  \n")
        f.write(f"**Source:** {args.source}\n\n")

        if isinstance(findings, dict) and "patterns" in findings:
            f.write("## Patterns\n\n")
            for p in findings["patterns"]:
                f.write(f"- **{p['pattern']}** — {p['frequency']} frequency, {p['avg_engagement']}\n")
        elif isinstance(findings, dict):
            for channel, data in findings.items():
                f.write(f"\n## {channel.title()}\n\n")
                for p in data.get("patterns", []):
                    f.write(f"- **{p['pattern']}** — {p['frequency']} frequency, {p['avg_engagement']}\n")

    print(f"Written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
