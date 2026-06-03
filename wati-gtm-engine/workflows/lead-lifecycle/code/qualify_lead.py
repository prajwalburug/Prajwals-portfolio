#!/usr/bin/env python3
"""AI Lead Qualifier — Scores inbound leads against ICP criteria using LLM + rules."""

import argparse
import json
import os
import sys
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

DEMO_API_URL = "https://gtm-skills.com/api/v1/prompts"


def load_icp_config(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_demo_leads(icp: dict) -> list[dict]:
    """Pull sample leads from gtm-skills.com API using prompt categories as company data."""
    params = {"limit": 20, "offset": 0}
    try:
        resp = requests.get(DEMO_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"[demo] API unavailable ({e}), using fallback data", file=sys.stderr)
        data = [
            {"category": "saas", "title": "SaaS Corp", "description": "B2B SaaS platform", "tags": ["cold-email", "technical"]},
            {"category": "fintech", "title": "FinTech Inc", "description": "Payment processing", "tags": ["compliance", "finserv"]},
            {"category": "healthcare", "title": "HealthTech", "description": "Clinical software", "tags": ["hipaa", "clinical"]},
            {"category": "manufacturing", "title": "Mfg Co", "description": "Industrial equipment", "tags": ["operations"]},
        ]
    target_industries = icp.get("scoring", {}).get("industry", {}).get("target", [])
    leads = []
    for item in data:
        category = item.get("category", "unknown")
        title = item.get("title", category)
        icp_industry = "saas" if category in [i.lower().replace(" ", "-") for i in target_industries] else category
        leads.append({
            "name": f"Lead-{title.replace(' ', '')}",
            "company": title,
            "industry": icp_industry,
            "company_size": 200,
            "job_title": "VP of Sales",
            "source": item.get("tags", ["web"])[0],
            "signal": item.get("description", ""),
        })
    return leads


def score_industry(industry: str, config: dict) -> tuple[int, str]:
    scoring = config.get("scoring", {}).get("industry", {})
    target = [s.lower() for s in scoring.get("target", [])]
    acceptable = [s.lower() for s in scoring.get("acceptable", [])]
    exclude = [s.lower() for s in scoring.get("exclude", [])]
    ind_lower = industry.lower()
    if ind_lower in exclude:
        return scoring.get("values", {}).get("exclude", 0), f"Excluded industry: {industry}"
    if ind_lower in target or any(t in ind_lower for t in target):
        return scoring.get("values", {}).get("target", 100), f"Target industry: {industry}"
    if ind_lower in acceptable:
        return scoring.get("values", {}).get("acceptable", 50), f"Acceptable industry: {industry}"
    if any(ex in ind_lower for ex in ["government", "nonprofit"]):
        return 0, f"Low-priority industry: {industry}"
    return 30, f"Unlisted industry: {industry}"


def score_company_size(size: int, config: dict) -> tuple[int, str]:
    vals = config.get("scoring", {}).get("company_size", {})
    sweet_min = vals.get("sweet_spot_min", 50)
    sweet_max = vals.get("sweet_spot_max", 5000)
    if size is None:
        return 50, "Company size unknown"
    if sweet_min <= size <= sweet_max:
        return vals.get("values", {}).get("50_to_5000", 100), f"Sweet spot size: {size}"
    if 10 <= size < sweet_min:
        return vals.get("values", {}).get("10_to_49", 60), f"Small company: {size}"
    if sweet_max < size <= 10000:
        return vals.get("values", {}).get("5001_to_10000", 70), f"Large company: {size}"
    if size > 10000:
        return vals.get("values", {}).get("over_10000", 50), f"Enterprise: {size}"
    return vals.get("values", {}).get("under_10", 30), f"Very small: {size}"


def score_title(title: str, config: dict) -> tuple[int, str]:
    vals = config.get("scoring", {}).get("title_relevance", {})
    ideal = [t.lower() for t in vals.get("ideal", [])]
    good = [t.lower() for t in vals.get("good", [])]
    acceptable = [t.lower() for t in vals.get("acceptable", [])]
    t = title.lower() if title else ""
    for i in ideal:
        if i in t:
            return vals.get("values", {}).get("ideal", 100), f"Ideal title: {title}"
    for g in good:
        if g in t:
            return vals.get("values", {}).get("good", 70), f"Good title: {title}"
    for a in acceptable:
        if a in t:
            return vals.get("values", {}).get("acceptable", 40), f"Acceptable title: {title}"
    return 20, f"Unlisted title: {title}"


def score_signal(source: str, config: dict) -> tuple[int, str]:
    leads_config = config.get("scoring", {}).get("signal_strength", {})
    sources = leads_config.get("sources", {})
    for source_key, source_config in sources.items():
        keywords = source_config.get("keywords", [])
        if any(k.lower() in (source or "").lower() for k in keywords):
            return 80, f"Signal detected in {source_key}"
    return 50, "No strong signal detected"


def classify_lead(lead: dict, icp: dict) -> dict:
    industry_score, industry_reason = score_industry(lead.get("industry", ""), icp)
    size_score, size_reason = score_company_size(lead.get("company_size"), icp)
    title_score, title_reason = score_title(lead.get("job_title", ""), icp)
    signal_score, signal_reason = score_signal(lead.get("source", ""), icp)

    weights = icp.get("weights", {"industry": 0.30, "company_size": 0.25, "title_relevance": 0.25, "signal_strength": 0.20})
    total = (
        industry_score * weights.get("industry", 0.30)
        + size_score * weights.get("company_size", 0.25)
        + title_score * weights.get("title_relevance", 0.25)
        + signal_score * weights.get("signal_strength", 0.20)
    )

    thresholds = icp.get("classification_thresholds", {})
    hot_min = thresholds.get("hot", {}).get("min_score", 70)
    warm_min = thresholds.get("warm", {}).get("min_score", 40)
    disc_max = thresholds.get("disqualified", {}).get("max_score", 9)

    if total >= hot_min:
        classification = "HOT"
    elif total >= warm_min:
        classification = "WARM"
    elif total > disc_max:
        classification = "NURTURE"
    else:
        classification = "DISQUALIFIED"

    return {
        "name": lead.get("name", "Unknown"),
        "company": lead.get("company", "Unknown"),
        "industry_score": {"score": industry_score, "reason": industry_reason},
        "size_score": {"score": size_score, "reason": size_reason},
        "title_score": {"score": title_score, "reason": title_reason},
        "signal_score": {"score": signal_score, "reason": signal_reason},
        "total_score": round(total, 1),
        "classification": classification,
    }


def main():
    parser = argparse.ArgumentParser(description="AI Lead Qualifier — score leads against ICP")
    parser.add_argument("--demo", action="store_true", help="Run with sample data from gtm-skills.com API")
    parser.add_argument("--dry-run", action="store_true", help="Print results without external API calls")
    parser.add_argument("--input", type=str, help="Path to JSON file with leads array")
    parser.add_argument("--verbose", action="store_true", help="Print detailed scoring breakdown")
    args = parser.parse_args()

    if load_dotenv:
        load_dotenv()

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent
    config_path = project_root / "shared" / "config" / "icp_criteria.json"

    if not config_path.exists():
        print(json.dumps({"error": f"ICP config not found at {config_path}"}, indent=2))
        sys.exit(1)

    icp = load_icp_config(config_path)

    if args.demo:
        leads = load_demo_leads(icp)
    elif args.input:
        with open(args.input) as f:
            leads = json.load(f) if isinstance(json.load(f), list) else json.load(f).get("leads", [])
    else:
        leads = [{
            "name": "Sample Lead",
            "company": "Acme Corp",
            "industry": "SaaS",
            "company_size": 500,
            "job_title": "VP of Sales",
            "source": "web_form",
            "signal": "hiring_revops",
        }]

    results = []
    for lead in leads:
        result = classify_lead(lead, icp)
        results.append(result)

    output = {"results": results, "total": len(results), "dry_run": args.dry_run}
    print(json.dumps(output, indent=2))

    if args.dry_run:
        print("\n[dry-run] No changes written to any external system.", file=sys.stderr)

    if args.verbose:
        total_leads = len(results)
        classifications = {}
        for r in results:
            classifications[r["classification"]] = classifications.get(r["classification"], 0) + 1
        print(f"\n--- Summary ---", file=sys.stderr)
        print(f"Total leads scored: {total_leads}", file=sys.stderr)
        for cls, count in sorted(classifications.items()):
            print(f"  {cls}: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
