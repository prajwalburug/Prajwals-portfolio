"""Mock Clay enrichment API. Mirrors the real Clay API shape for demo/dry-run."""

from __future__ import annotations
import json
import os
from typing import Any


def _load_fixtures() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "fixtures", "clay-accounts.json")
    with open(path) as f:
        return json.load(f)


def enrich_account(company: str, domain: str = "") -> dict[str, Any]:
    """Enrich an account with firmographic data. Mirrors Clay API response shape.

    Args:
        company: Company name to enrich
        domain: Optional company domain

    Returns:
        Dict with company_name, domain, industry, headcount, revenue_range,
        funding, tech_stack, and metadata fields matching Clay API shape.

    In demo mode, returns data from fixtures. In production, calls Clay API.
    """
    fixtures = _load_fixtures()
    company_lower = company.lower()
    match = None
    for acct in fixtures:
        if company_lower in acct.get("company", "").lower():
            match = acct
            break
        if domain and domain == acct.get("domain", ""):
            match = acct
            break

    if match:
        return {
            "company_name": match["company"],
            "domain": match["domain"],
            "industry": match["industry"],
            "employee_count": match["headcount"],
            "revenue_range": match["revenue_range"],
            "funding": {
                "total": match.get("funding_total"),
                "round": match.get("funding_round"),
                "date": match.get("funding_date"),
            },
            "technologies": match["tech_stack"],
            "location": match.get("headquarters", ""),
            "linkedin_url": match.get("linkedin_url", ""),
            "description": match.get("description", ""),
            "source": "clay_mock",
            "enriched_at": "2026-06-03T12:00:00Z",
        }

    return {
        "company_name": company,
        "domain": domain or f"{company.lower().replace(' ', '')}.com",
        "industry": "Unknown",
        "employee_count": None,
        "revenue_range": None,
        "funding": {"total": None, "round": None, "date": None},
        "technologies": [],
        "location": None,
        "linkedin_url": None,
        "description": None,
        "source": "clay_mock",
        "enriched_at": "2026-06-03T12:00:00Z",
        "error": "Company not found in mock database",
    }


def list_available_companies() -> list[str]:
    """Return list of companies available in the mock database."""
    return [a["company"] for a in _load_fixtures()]
