#!/usr/bin/env python3
"""Multi-channel content repurposer.

Takes one piece of content (core narrative) and generates variants across
LinkedIn, email, and blog channels — each formatted according to channel rules.

Usage:
    python code/repurpose.py --brand awesome-hires --channels linkedin,email --demo
    python code/repurpose.py --brand awesome-hires --demo --dry-run
    python code/repurpose.py --brand awesome-hires --channels linkedin,email,blog --demo
    python code/repurpose.py --brand awesome-hires --input /path/to/source.txt
"""

import argparse
import json
import os
import re
import sys
from datetime import date


VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_PATH", "./brands")


# ── Demo narrative ──────────────────────────────────────────────────────────

DEMO_NARRATIVE = {
    "core_topic": "AI voice interviews reduce hiring bias",
    "key_points": [
        "Traditional interviews are inconsistent across candidates",
        "AI interviews ask the same questions and use same scoring",
        "Results are deterministic, reproducible, and fair",
        "PII-safe by design — personal data stripped before processing",
    ],
    "data_points": [
        "12 hours scheduling per 1 hour evaluating",
        "100% consistent question delivery",
    ],
    "angle": "Fairness through consistency",
}

# ── Utilities ───────────────────────────────────────────────────────────────


def load_writing_skills(brand: str, vault_root: str) -> str:
    """Load writing-skills.md for the brand. Exits with error if missing."""
    path = os.path.join(vault_root, brand, "writing-skills.md")
    if not os.path.isfile(path):
        print(f"Error: writing-skills.md not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return f.read()


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def extract_narrative_simple(text: str) -> dict:
    """Simple keyword-based narrative extraction from raw text (demo-grade).

    Splits text into sentences, picks a topic from the first significant
    sentence, and extracts key_points / data_points by scanning for
    patterns like numbers, bullet-listed items, and short declarative sentences.
    """
    sentences = [s.strip() for s in re.split(r"[.!?\n]+", text) if s.strip()]
    if not sentences:
        return dict(DEMO_NARRATIVE)

    # Core topic: first sentence that is not too short
    core_topic = sentences[0]
    if len(core_topic) < 15 and len(sentences) > 1:
        core_topic = sentences[1]
    core_topic = core_topic[:80]

    # Key points: short declarative sentences (20-150 chars)
    key_points = []
    seen = set()
    for s in sentences:
        normalized = s.strip().lower()
        if 20 <= len(s) <= 200 and normalized not in seen:
            seen.add(normalized)
            key_points.append(s.strip())
        if len(key_points) >= 4:
            break

    # Data points: sentences containing numbers
    data_points = [s for s in sentences if re.search(r"\d+", s)][:2]

    return {
        "core_topic": core_topic,
        "key_points": key_points or DEMO_NARRATIVE["key_points"][:2],
        "data_points": data_points or DEMO_NARRATIVE["data_points"],
        "angle": "Derived from source",
    }


# ── Channel generators ──────────────────────────────────────────────────────


def generate_linkedin(narrative: dict) -> dict:
    """Generate a LinkedIn post variant from a core narrative.

    Follows LinkedIn Channel Rules:
    - Hook in first 2 lines (bold claim / statistic)
    - One idea per paragraph
    - 3-5 hashtags (2 broad + 1-2 specific + 1 brand)
    - Engagement CTA
    """
    topic = narrative["core_topic"]
    kp = narrative["key_points"]
    dp = narrative["data_points"]

    hook = (
        f"Most hiring teams don't realize how much inconsistency costs them. "
        f"Here's what the data says about {topic.lower()}."
    )

    body_parts = [
        f"The problem is straightforward: {kp[0].lower() if kp else 'interviews vary wildly from candidate to candidate'}.",
    ]

    if len(kp) > 1:
        body_parts.append(kp[1])
    if len(kp) > 2:
        body_parts.append(kp[2])
    if len(kp) > 3:
        body_parts.append(kp[3])

    if dp:
        body_parts.append(f"**The numbers are clear:** {dp[0]}.")
    if len(dp) > 1:
        body_parts.append(dp[1])

    body_parts.append(
        f"The takeaway: {narrative.get('angle', 'Fairness through consistency')} "
        f"isn't a slogan — it's a design principle. When every candidate gets the "
        f"same questions and the same scoring, bias doesn't stand a chance."
    )

    body = "\n\n".join(body_parts)

    cta = "What's your take? Drop a thought below \u2193"

    broad = ["#hiring", "#ai"]
    specific = ["#hrtech", "#futureofwork"]
    brand = ["#awesomehires"]
    hashtags = broad + specific + brand

    return {
        "channel": "linkedin",
        "hook": hook,
        "body": body,
        "cta": cta,
        "hashtags": hashtags,
    }


def generate_email(narrative: dict) -> dict:
    """Generate an email variant from a core narrative.

    Follows Email Channel Rules:
    - Subject: 35-50 characters
    - Preview: 90-100 characters
    - Greeting: Hi {{name}},
    - Body: 3-5 paragraphs, max ~200 words
    """
    topic = narrative["core_topic"]
    kp = narrative["key_points"]
    dp = narrative["data_points"]

    # Subject line — aim for 35-50 chars
    subject = f"Fairer hiring starts with consistent evaluation"
    if len(subject) > 50:
        subject = f"Consistent evaluation, fairer hiring"

    preview_text = (
        f"Why traditional interviews fail candidates — and how AI fixes "
        f"the inconsistency problem."
    )[:100]

    greeting = "Hi {{name}},"

    body_parts = [
        (
            f"Hiring teams pour countless hours into screening, yet the process "
            f"remains stubbornly inconsistent. {kp[0] if kp else 'Every candidate gets a different experience.'}"
        ),
    ]

    if len(kp) > 1:
        body_parts.append(
            f"Here's the structural shift we've seen work: {kp[1]}. "
            f"When every applicant answers the same competency-based questions, "
            f"the signal-to-noise ratio in your pipeline changes dramatically."
        )

    if dp:
        data_line = dp[0]
        body_parts.append(
            f"The operational impact is measurable. Consider this: {data_line}. "
            f"That's time your team could spend evaluating fit instead of coordinating calendars."
        )

    if len(kp) > 2:
        body_parts.append(kp[2])

    body_parts.append(
        f"This isn't theoretical. Teams that adopt structured, AI-powered screening "
        f"see faster time-to-shortlist, fairer outcomes, and higher candidate satisfaction. "
        f"The fix is architectural, and it starts with consistent evaluation."
    )

    body = "\n\n".join(body_parts)

    return {
        "channel": "email",
        "subject": subject,
        "preview_text": preview_text,
        "greeting": greeting,
        "body": body,
    }


def generate_blog(narrative: dict) -> dict:
    """Generate a blog variant from a core narrative.

    Follows Blog Channel Rules:
    - Title: 50-60 characters, includes primary keyword
    - Meta description: 150-160 characters
    - Sections with headings and content based on key points
    """
    topic = narrative["core_topic"]
    kp = narrative["key_points"]
    dp = narrative["data_points"]
    angle = narrative.get("angle", "Fairness through consistency")

    # Title — aim for 50-60 chars
    title = f"AI Voice Interviews: Fairness Through Consistent Evaluation"
    if len(title) > 60:
        title = f"Fairness Through Consistent AI Interviews"

    meta_description = (
        f"Traditional interviews are inconsistent and prone to bias. "
        f"Learn how AI voice interviews use consistent scoring, "
        f"deterministic evaluation, and PII-safe design to level the playing field."
    )[:160]

    sections = []

    # Section 1: Problem statement
    sections.append({
        "heading": "The Hidden Cost of Inconsistent Interviews",
        "content": (
            f"Every hiring team knows the pain of scheduling interviews. "
            f"But the real cost isn't the calendar chaos — it's the inconsistency. "
            f"{kp[0] if kp else 'Traditional interviews vary wildly across candidates.'} "
            f"When the format, questions, and evaluation criteria change from one "
            f"candidate to the next, you're not evaluating skills. You're evaluating luck.\n\n"
            f"{dp[0] if dp else ''} This imbalance erodes fairness at every stage."
        ),
        "word_count": 70,
    })

    # Section 2: How structured evaluation works
    if len(kp) > 1:
        sections.append({
            "heading": "How Structured AI Interviews Remove Bias",
            "content": (
                f"{kp[1]}. The mechanism is simple: the same questions, the same "
                f"scoring rubric, the same evaluation criteria — applied uniformly "
                f"to every candidate. No interviewer fatigue, no gut-feel scoring, "
                f"no unconscious drift between the morning and afternoon slots.\n\n"
                f"When scoring is deterministic, the same answer always receives "
                f"the same score. This auditability is the foundation of fair evaluation."
            ),
            "word_count": 65,
        })

    # Section 3: PII-safe design
    if len(kp) > 2:
        sections.append({
            "heading": "PII-Safe by Design: Privacy Meets Fairness",
            "content": (
                f"{kp[2]}. Candidate personal data — name, age, location — is "
                f"stripped before any AI processing touches their evaluation. "
                f"This architectural choice removes the single largest source of "
                f"unconscious bias from the screening stage.\n\n"
                f"Privacy isn't a compliance checkbox here. It's a fairness feature."
            ),
            "word_count": 60,
        })

    # Section 4: Business impact
    sections.append({
        "heading": "What Consistent Evaluation Means for Your Pipeline",
        "content": (
            f"The teams that adopt structured, AI-powered screening see measurable "
            f"results: faster time-to-shortlist, fairer outcomes across demographic "
            f"groups, and higher candidate satisfaction. "
            f"{angle} isn't just a principle — it's a competitive advantage in "
            f"building a hiring process that candidates trust."
        ),
        "word_count": 55,
    })

    total_word_count = sum(s["word_count"] for s in sections)

    return {
        "channel": "blog",
        "title": title,
        "meta_description": meta_description,
        "sections": sections,
        "total_word_count": total_word_count,
    }


# ── Obsidian output ─────────────────────────────────────────────────────────


CHANNEL_GENERATORS = {
    "linkedin": generate_linkedin,
    "email": generate_email,
    "blog": generate_blog,
}


def make_obsidian_doc(variant: dict, narrative: dict, brand: str, date_str: str) -> str:
    """Format a single variant as an Obsidian markdown document.

    Different channels have different structures — this dispatches to the
    appropriate formatter based on variant['channel'].
    """
    channel = variant["channel"]
    topic = narrative["core_topic"]

    if channel == "linkedin":
        return _obsidian_linkedin(variant, topic, brand, date_str)
    elif channel == "email":
        return _obsidian_email(variant, topic, brand, date_str)
    elif channel == "blog":
        return _obsidian_blog(variant, topic, brand, date_str)
    return ""


def _obsidian_linkedin(v: dict, topic: str, brand: str, date_str: str) -> str:
    lines = [
        f"# LinkedIn: {topic}",
        f"**Brand:** {brand}",
        f"**Source:** repurpose.py",
        f"**Date:** {date_str}",
        "",
        "---",
        "",
        v["hook"],
        "",
        v["body"],
        "",
        f"**CTA:** {v['cta']}",
        f"Hashtags: {' '.join(v['hashtags'])}",
        "",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def _obsidian_email(v: dict, topic: str, brand: str, date_str: str) -> str:
    lines = [
        f"# Email: {topic}",
        f"**Brand:** {brand}",
        f"**Source:** repurpose.py",
        f"**Date:** {date_str}",
        "",
        "---",
        "",
        f"**Subject:** {v['subject']}",
        f"**Preview:** {v['preview_text']}",
        "",
        v["greeting"],
        "",
        v["body"],
        "",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def _obsidian_blog(v: dict, topic: str, brand: str, date_str: str) -> str:
    lines = [
        f"# Blog: {topic}",
        f"**Brand:** {brand}",
        f"**Source:** repurpose.py",
        f"**Date:** {date_str}",
        f"**Total Words:** {v['total_word_count']}",
        "",
        "---",
        "",
    ]
    for section in v["sections"]:
        lines.extend([
            f"## {section['heading']}",
            "",
            section["content"],
            "",
        ])
    return "\n".join(lines).rstrip("\n") + "\n"


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Multi-channel content repurposer. Generates LinkedIn, email, "
                    "and blog variants from a single source narrative."
    )
    parser.add_argument("--brand", required=True, help="Brand name (matches vault directory)")
    parser.add_argument(
        "--input", help="Path to source content file (required in real mode)"
    )
    parser.add_argument(
        "--channels", default="linkedin,email",
        help="Comma-separated channel list (default: linkedin,email)"
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Use hardcoded demo narrative (no input file needed)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print JSON to stdout and skip file writes"
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    vault_root = VAULT_ROOT
    brand_path = os.path.join(vault_root, args.brand)
    channel_list = [c.strip() for c in args.channels.split(",") if c.strip()]

    # Validate brand directory exists
    if not os.path.isdir(brand_path):
        print(f"Error: brand directory not found at {brand_path}", file=sys.stderr)
        available = [
            d for d in os.listdir(vault_root)
            if os.path.isdir(os.path.join(vault_root, d))
        ]
        if available:
            print(f"Available brands: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    # Load writing-skills.md — required for real mode
    load_writing_skills(args.brand, vault_root)

    date_str = date.today().isoformat()

    # ── Extract narrative ───────────────────────────────────────────────
    source = None
    narrative = None

    if args.demo:
        source = "demo"
        narrative = dict(DEMO_NARRATIVE)
    elif args.input:
        source = args.input
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
        narrative = extract_narrative_simple(text)
    else:
        print("Real mode requires input file or --demo flag.", file=sys.stderr)
        sys.exit(1)

    # ── Validate channels ───────────────────────────────────────────────
    valid_channels = set(CHANNEL_GENERATORS.keys())
    unknown = [c for c in channel_list if c not in valid_channels]
    if unknown:
        print(
            f"Error: unknown channel(s): {', '.join(unknown)}. "
            f"Valid: {', '.join(sorted(valid_channels))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Generate variants ───────────────────────────────────────────────
    variants = []
    for ch in channel_list:
        generator = CHANNEL_GENERATORS[ch]
        variant = generator(narrative)
        variants.append(variant)

    # ── Build output ────────────────────────────────────────────────────
    slug = slugify(narrative["core_topic"])

    output = {
        "brand": args.brand,
        "source": source,
        "channels": channel_list,
        "narrative": narrative,
        "variants": variants,
        "dry_run": args.dry_run,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

    # ── Write Obsidian files ────────────────────────────────────────────
    if args.dry_run:
        print("[dry-run] No files written.", file=sys.stderr)
        return

    generated_dir = os.path.join(brand_path, "generated")
    os.makedirs(generated_dir, exist_ok=True)

    for v in variants:
        channel = v["channel"]
        filename = f"{date_str}-repurpose-{channel}-{slug}.md"
        filepath = os.path.join(generated_dir, filename)
        doc = make_obsidian_doc(v, narrative, args.brand, date_str)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"Written to {filepath}", file=sys.stderr)


if __name__ == "__main__":
    main()
