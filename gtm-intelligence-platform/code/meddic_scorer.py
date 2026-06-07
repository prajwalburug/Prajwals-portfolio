"""MEDDIC scoring engine. Scores 6 dimensions 0-10, detects gaps, ranks by risk, generates NBA."""

from __future__ import annotations
from typing import Any

MEDDIC_DIMENSIONS = [
    {"key": "metrics", "label": "M - Metrics", "description": "Quantified ROI established"},
    {"key": "economic_buyer", "label": "E - Economic buyer", "description": "Budget approver identified and engaged"},
    {"key": "decision_criteria", "label": "D1 - Decision criteria", "description": "Must-haves defined by prospect"},
    {"key": "decision_process", "label": "D2 - Decision process", "description": "Procurement steps mapped"},
    {"key": "identified_pain", "label": "I - Identified pain", "description": "Specific pain with business impact"},
    {"key": "champion", "label": "C - Champion", "description": "Internal advocate confirmed"},
]

GAP_RISK_WEIGHTS = {
    "economic_buyer": 1.5,
    "champion": 1.3,
    "decision_process": 1.2,
    "identified_pain": 1.3,
    "metrics": 1.0,
    "decision_criteria": 1.0,
}

GAP_THRESHOLD = 5

NBA_MAP = {
    "economic_buyer": {"action": "Arrange economic buyer intro call", "template": "Ask {champion} to arrange a 20-min {eb_name} intro call this week. Missing economic buyer is the #1 deal killer at this stage."},
    "champion": {"action": "Develop champion", "template": "Identify and develop a champion within {company}. No internal advocate means no path to close."},
    "decision_process": {"action": "Map procurement process", "template": "Ask {champion} to walk through the procurement process step by step. Write down names, stages, and approval thresholds."},
    "identified_pain": {"action": "Quantify pain in dollars", "template": "Quantify the business impact of {pain_area} in dollar terms. 'Significant time savings' is not enough — calculate hourly cost."},
    "metrics": {"action": "Build ROI model", "template": "Deliver a structured ROI document showing payback period, hours saved, and dollar impact. Use {metrics_source} data to build the case."},
    "decision_criteria": {"action": "Define must-haves", "template": "Ask {champion} to write down the top 3 evaluation criteria. Without defined criteria, you're solving for the wrong problem."},
}


def score_dimensions(scores: dict[str, int]) -> dict:
    """Score MEDDIC dimensions and detect gaps.

    Args:
        scores: Dict mapping dimension key to score 0-10
            e.g. {"metrics": 3, "economic_buyer": 2, "decision_criteria": 6,
                   "decision_process": 2, "identified_pain": 8, "champion": 7}

    Returns:
        Dict with dimension_scores[], gaps[], gap_count, top_gap, meddic_completeness (0-100)
    """
    result = {"dimension_scores": [], "gaps": [], "gap_count": 0, "top_gap": None, "meddic_completeness": 0}

    raw_total = 0.0
    gaps = []

    for dim in MEDDIC_DIMENSIONS:
        key = dim["key"]
        score = max(0, min(10, scores.get(key, 0)))
        is_gap = score < GAP_THRESHOLD
        risk_weight = GAP_RISK_WEIGHTS.get(key, 1.0)
        gap_status = "gap_detected" if is_gap else "covered"

        entry = {
            "key": key,
            "label": dim["label"],
            "description": dim["description"],
            "score": score,
            "is_gap": is_gap,
            "risk_weight": risk_weight,
            "status": gap_status,
            "risk_label": "critical" if is_gap and key == "economic_buyer" else ("high" if is_gap and risk_weight >= 1.2 else "medium") if is_gap else "none",
        }

        if is_gap:
            entry["nba"] = NBA_MAP.get(key, {}).get("template", "")
            gaps.append(entry)

        raw_total += score
        result["dimension_scores"].append(entry)

    # MEDDIC completeness: average of 6 dimensions, scaled to 0-100
    result["meddic_completeness"] = int((raw_total / 60.0) * 100)

    # Rank gaps by risk weight (highest first)
    gaps.sort(key=lambda g: g["risk_weight"], reverse=True)
    result["gaps"] = gaps
    result["gap_count"] = len(gaps)
    result["top_gap"] = gaps[0]["key"] if gaps else None

    return result


def generate_nba(scored: dict, deal_context: dict | None = None) -> dict:
    """Generate a single next best action from the top gap."""
    ctx = deal_context or {}
    top_gap_key = scored.get("top_gap")
    if not top_gap_key:
        return {"nba_text": "No gaps detected. Continue progressing the deal.", "top_gap": None, "action": None}

    gap_entry = next((g for g in scored["gaps"] if g["key"] == top_gap_key), None)
    nba_info = NBA_MAP.get(top_gap_key, {})

    template = nba_info.get("template", "")
    nba_text = template.format(
        champion=ctx.get("champion_name", "the champion"),
        company=ctx.get("company", "the company"),
        eb_name=ctx.get("eb_name", "the economic buyer"),
        pain_area=ctx.get("pain_area", "the identified pain"),
        metrics_source=ctx.get("metrics_source", "transcript"),
    )

    return {
        "nba_text": nba_text,
        "top_gap": top_gap_key,
        "top_gap_score": gap_entry["score"] if gap_entry else None,
        "top_gap_risk": gap_entry["risk_label"] if gap_entry else None,
        "action": nba_info.get("action", ""),
        "gap_count": scored["gap_count"],
    }


def score_from_transcript(transcript_text: str) -> dict:
    """Score MEDDIC dimensions from transcript text using keyword heuristics.

    In production, this would call an LLM. In demo mode, uses rule-based
    keyword scoring to extract dimension signals from call text.
    """
    text_lower = transcript_text.lower()

    scores = {}

    # Metrics — look for numbers, ROI language, quantification
    metric_keywords = ["hours", "dollars", "percent", "%", "roi", "payback", "saving", "cost", "budget"]
    metrics_count = sum(1 for kw in metric_keywords if kw in text_lower)
    scores["metrics"] = min(10, metrics_count + 2)

    # Economic buyer — look for CFO/CEO/VP mentions as decision makers
    eb_keywords = ["cfo", "ceo", "sign", "approve", "budget holder", "economic buyer", "signs the check"]
    eb_count = sum(1 for kw in eb_keywords if kw in text_lower)
    has_eb_present = any(p in text_lower for p in ["sarah chen", "mark chen"])
    scores["economic_buyer"] = min(10, eb_count + (4 if has_eb_present else 1))

    # Decision criteria — look for requirements, must-haves
    dc_keywords = ["requirement", "must have", "need", "criteria", "integration", "api"]
    dc_count = sum(1 for kw in dc_keywords if kw in text_lower)
    scores["decision_criteria"] = min(10, dc_count + 1)

    # Decision process — look for procurement steps, timeline
    dp_keywords = ["process", "timeline", "board", "quarter", "procurement", "evaluation", "stage"]
    dp_count = sum(1 for kw in dp_keywords if kw in text_lower)
    red_flags = ["figure out the process", "we'll figure it out", "not sure yet", "tbd"]
    has_red_flag = any(rf in text_lower for rf in red_flags)
    scores["decision_process"] = max(1, min(10, dp_count - (3 if has_red_flag else 0)))

    # Identified pain — look for pain language
    pain_keywords = ["pain", "frustrat", "slow", "manual", "broken", "not scaling", "delay", "risk", "problem"]
    pain_count = sum(1 for kw in pain_keywords if kw in text_lower)
    scores["identified_pain"] = min(10, pain_count + 3)

    # Champion — look for advocacy language
    champ_keywords = ["we need this", "exactly what we need", "champion", "advocate", "org chart", "internal"]
    champ_count = sum(1 for kw in champ_keywords if kw in text_lower)
    scores["champion"] = min(10, champ_count + 3)

    return scores


DIM_KEY_MAP = {
    "metrics": "metrics", "m": "metrics",
    "economic_buyer": "economic_buyer", "eb": "economic_buyer", "e": "economic_buyer",
    "decision_criteria": "decision_criteria", "dc": "decision_criteria", "d1": "decision_criteria",
    "decision_process": "decision_process", "dp": "decision_process", "d2": "decision_process",
    "identified_pain": "identified_pain", "pain": "identified_pain", "i": "identified_pain",
    "champion": "champion", "c": "champion",
}


def _display_scored(scores: dict, scored: dict, nba: dict, ctx: dict) -> str:
    lines = ["", "  MEDDIC Scorecard", "  " + "-" * 50]
    for d in scored["dimension_scores"]:
        gap_mark = " ! GAP" if d["is_gap"] else "      "
        risk_tag = f"  ({d['risk_label'].upper()})" if d["is_gap"] else ""
        lines.append(f"  {d['label']:30s} {d['score']:2d}/10{gap_mark}{risk_tag}")
    lines.append("  " + "-" * 50)
    lines.append(f"  Completeness:  {scored['meddic_completeness']:2d}/100    Gaps: {scored['gap_count']}")
    if nba.get("nba_text"):
        lines.append(f"  Top gap:       {scored['top_gap']}")
        lines.append(f"  NBA:           {nba['nba_text']}")
    return "\n".join(lines)


def _cli_entry():
    import argparse

    parser = argparse.ArgumentParser(description="MEDDIC Deal Scorer — interactive scorecard REPL")
    parser.add_argument("--interactive", "-i", action="store_true", help="REPL loop for live score adjustment")
    parser.add_argument("--metrics", type=int, default=5, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--economic-buyer", "--eb", type=int, default=5, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--decision-criteria", "--dc", type=int, default=5, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--decision-process", "--dp", type=int, default=5, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--identified-pain", "--pain", type=int, default=5, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--champion", type=int, default=5, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--champion-name", default="the champion")
    parser.add_argument("--company", default="the company")
    parser.add_argument("--eb-name", default="the economic buyer")
    args = parser.parse_args()

    scores = {
        "metrics": args.metrics,
        "economic_buyer": args.economic_buyer,
        "decision_criteria": args.decision_criteria,
        "decision_process": args.decision_process,
        "identified_pain": args.identified_pain,
        "champion": args.champion,
    }
    ctx = {
        "champion_name": args.champion_name,
        "company": args.company,
        "eb_name": args.eb_name,
    }

    def run(scores):
        scored = score_dimensions(scores)
        nba = generate_nba(scored, ctx)
        print(_display_scored(scores, scored, nba, ctx))
        return scored, nba

    run(scores)

    if not args.interactive:
        return

    print("\n  Interactive mode. Type commands:")
    print("    metrics=7  eb=3  dc=8  dp=2  pain=9  champion=6")
    print("    help  quit")
    while True:
        try:
            cmd = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue
        if cmd in ("quit", "q", "exit"):
            break
        if cmd in ("help", "?"):
            print("  Set dimension scores: metrics=7, eb=3, dc=8, dp=2, pain=9, champion=6")
            print("  Aliases: m, e, eb, d1, dc, d2, dp, i, pain, c")
            continue
        parts = cmd.replace(",", " ").split()
        changed = False
        for p in parts:
            if "=" not in p:
                continue
            key_raw, val_raw = p.split("=", 1)
            key_raw = key_raw.strip().lower()
            real_key = DIM_KEY_MAP.get(key_raw)
            if not real_key:
                print(f"  Unknown dimension: {key_raw}. Try help.")
                continue
            try:
                val = int(val_raw.strip())
                if val < 0 or val > 10:
                    print(f"  Score must be 0-10, got {val}")
                    continue
                scores[real_key] = val
                changed = True
            except ValueError:
                print(f"  Invalid score: {val_raw}")
        if changed:
            run(scores)


if __name__ == "__main__":
    _cli_entry()
