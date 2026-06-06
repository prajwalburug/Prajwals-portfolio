"""Seed data generator. Populates database with demo accounts, deals, signals, and briefs."""

import json
import os
import sys
from datetime import datetime, timezone


DEMO_ACCOUNTS = [
    {
        "name": "Meridian Capital Partners",
        "domain": "meridiancap.com",
        "industry": "Financial Services",
        "headcount": 245,
        "revenue_range": "$50M-$100M",
        "funding_total": 42000000,
        "funding_round": "Series B",
        "funding_date": "2026-05-15",
        "tech_stack": ["Salesforce", "Excel", "Slack", "Notion"],
        "icp_score": 87,
    },
    {
        "name": "Apex Analytics",
        "domain": "apexanalytics.io",
        "industry": "SaaS - Analytics",
        "headcount": 89,
        "revenue_range": "$10M-$25M",
        "funding_total": 12000000,
        "funding_round": "Series A",
        "funding_date": "2026-04-01",
        "tech_stack": ["HubSpot", "Tableau", "Snowflake", "Slack", "Notion", "Jira"],
        "icp_score": 62,
    },
    {
        "name": "NorthStar Equity Group",
        "domain": "northstarequity.com",
        "industry": "Financial Services - Asset Management",
        "headcount": 512,
        "revenue_range": "$100M-$250M",
        "funding_total": None,
        "funding_round": None,
        "funding_date": None,
        "tech_stack": ["Salesforce", "Excel", "Bloomberg Terminal", "Allvue"],
        "icp_score": 45,
    },
]


def generate_seed_json(output_dir: str = "."):
    """Write seed data as JSON files."""
    os.makedirs(output_dir, exist_ok=True)

    accounts_path = os.path.join(output_dir, "accounts.json")
    with open(accounts_path, "w") as f:
        json.dump(DEMO_ACCOUNTS, f, indent=2)
    print(f"Written: {accounts_path}")

    signals_path = os.path.join(output_dir, "signals.json")
    signals = _generate_signals()
    with open(signals_path, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"Written: {signals_path}")

    print(f"\nSeed data generated: {len(DEMO_ACCOUNTS)} accounts, {len(signals)} signals")


def _generate_signals() -> list[dict]:
    now = datetime.now(timezone.utc)
    return [
        {"account": "Meridian Capital Partners", "signal_type": "funding", "source": "TechCrunch", "title": "Series B $42M", "weight": 3.0, "detected_at": "2026-05-15T09:00:00Z"},
        {"account": "Meridian Capital Partners", "signal_type": "executive_change", "source": "LinkedIn", "title": "New CFO Sarah Chen", "weight": 2.5, "detected_at": "2026-04-20T14:00:00Z"},
        {"account": "Meridian Capital Partners", "signal_type": "hiring", "source": "LinkedIn Jobs", "title": "3 open senior roles", "weight": 2.0, "detected_at": "2026-05-25T10:00:00Z"},
        {"account": "Meridian Capital Partners", "signal_type": "tech_adoption", "source": "Clay + BuiltWith", "title": "No fund admin platform", "weight": 1.5, "detected_at": "2026-06-01T08:00:00Z"},
        {"account": "Apex Analytics", "signal_type": "funding", "source": "Crunchbase", "title": "Series A $12M", "weight": 3.0, "detected_at": "2026-04-01T10:00:00Z"},
        {"account": "Apex Analytics", "signal_type": "hiring", "source": "LinkedIn Jobs", "title": "Hiring Head of Sales", "weight": 2.0, "detected_at": "2026-05-10T14:00:00Z"},
        {"account": "NorthStar Equity Group", "signal_type": "tech_adoption", "source": "Clay + BuiltWith", "title": "Using Allvue (competitor)", "weight": 1.5, "detected_at": "2026-04-15T12:00:00Z"},
    ]


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "./data"
    generate_seed_json(out)
