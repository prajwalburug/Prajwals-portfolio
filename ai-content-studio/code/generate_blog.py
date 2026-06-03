#!/usr/bin/env python3
"""Generates blog outlines and full drafts grounded in a brand's voice.

Reads writing-skills.md (compiled brand voice + swipe file + channel rules),
accepts a topic and optional SEO keyword, and produces structured blog content.

Usage:
    python code/generate_blog.py --brand awesome-hires --topic "Why AI interviews are fairer" --outline-only --demo
    python code/generate_blog.py --brand awesome-hires --topic "Why AI interviews are fairer" --demo
    python code/generate_blog.py --brand awesome-hires --topic "test" --dry-run
"""

import argparse
import json
import os
import re
import sys
from datetime import date


VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_PATH", "./brands")

LENGTH_OPTIONS = ["short", "medium", "long"]
LENGTH_RANGES = {
    "short": (800, 1200),
    "medium": (1500, 2500),
    "long": (3000, 4500),
}
LENGTH_SECTIONS = {
    "short": 3,
    "medium": 5,
    "long": 8,
}

# Blog Channel Rules compliance markers
BLOG_HOOK_STATISTICS = [
    ("73% of hiring teams using AI screening tools cannot explain how their models make decisions.",
     "That's not just a compliance risk. It's a quality risk — and candidates are starting to ask."),
    ("Hiring managers spend 12 hours scheduling interviews for every 1 hour evaluating candidates.",
     "When the bottleneck is admin, not judgment, your pipeline leaks top talent."),
    ("Teams that screen candidates within 24 hours convert at 3x the rate of teams that take a week.",
     "Speed is a fairness feature: slow pipelines disproportionately lose underrepresented candidates."),
]


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


def generate_demo_outline(topic: str, seo_keyword: str, length: str) -> list[dict]:
    """Generate a realistic blog outline with H2 headings and purpose fields.

    Follows Blog Channel Rules:
    - Data point or statistic in first 150 words
    - H2 every ~300 words
    - One idea per H2 section
    - Support claims with data, sources, or named examples
    """
    num_sections = LENGTH_SECTIONS.get(length, 5)
    sections = [
        {
            "heading": "The Real Cost of an Inconsistent Interview Process",
            "purpose": (
                f"Open with a data point about hiring inconsistency. "
                f"State the problem: traditional interviews are unreliable. "
                f"Thesis: {topic} is solvable with structured evaluation."
            ),
        },
        {
            "heading": "What Most Teams Get Wrong About Interview Fairness",
            "purpose": (
                "Explain how unstructured interviews introduce bias. "
                "Contrast gut-feel evaluation with evidence-based scoring. "
                "Set up the structural solution."
            ),
        },
        {
            "heading": "How Structured Evaluation Removes Bias from the Equation",
            "purpose": (
                f"Lay out the mechanism of structured AI interviews: "
                f"same questions, same scoring criteria, same evaluation for every candidate. "
                f"Explain why consistency is the foundation of fairness."
            ),
        },
        {
            "heading": "The Data Behind Fair Screening: What the Numbers Show",
            "purpose": (
                "Present evidence that structured, consistent evaluation "
                "produces better hiring outcomes. Include demographic parity metrics "
                "and pipeline quality improvements."
            ),
        },
        {
            "heading": "Building a PII-Safe Evaluation Pipeline",
            "purpose": (
                "Explain why candidate personal data should be stripped before AI assessment. "
                f"Show how PII-safe design connects directly to {topic.lower()}. "
                "Address privacy concerns proactively."
            ),
        },
        {
            "heading": "From Application to Shortlist in 30 Minutes: The Workflow",
            "purpose": (
                "Walk through the end-to-end process: candidate applies, "
                "AI voice interview runs in real time, team receives ranked shortlist. "
                "Show how speed and fairness reinforce each other."
            ),
        },
        {
            "heading": "Why Deterministic Scoring Beats Black-Box Models",
            "purpose": (
                "Argue for transparent, auditable scoring rules over opaque AI. "
                "Explain that code-based scoring means the same inputs always "
                "produce the same outputs. No drift, no bias creep."
            ),
        },
        {
            "heading": "The Business Case for Fairer Interviews",
            "purpose": (
                f"Tie {topic.lower()} to tangible outcomes: better hires, "
                f"faster time-to-shortlist, reduced administrative overhead, "
                f"stronger employer brand. Close with a call to action."
            ),
        },
    ]

    return sections[:num_sections]


def generate_demo_sections(
    topic: str, seo_keyword: str, outline: list[dict], length: str
) -> list[dict]:
    """Expand outline headings into full paragraph content for demo mode.

    Uses the Awesome Hires brand voice: direct, analytical, evidence-forward.
    Follows Blog Channel Rules for formatting (bold emphasis, bullet lists).
    """
    # Pick a statistic to use in the first section
    stat_idx = hash(topic) % len(BLOG_HOOK_STATISTICS)
    stat, stat_elab = BLOG_HOOK_STATISTICS[stat_idx]

    target_min, target_max = LENGTH_RANGES.get(length, (1500, 2500))

    section_contents = {
        "The Real Cost of an Inconsistent Interview Process": (
            f"{stat}\n\n{stat_elab}\n\n"
            f"When every candidate walks into a different interview experience, "
            f"you're not evaluating skills — you're evaluating luck. One candidate "
            f"gets a structured conversation with competency-based questions. Another "
            f"gets an unstructured chat that drifts into personal background.\n\n"
            f"**The result is the same every time:** the data shows that unstructured "
            f"interviews predict job performance only marginally better than chance. "
            f"And the candidates who suffer most are the ones whose backgrounds don't "
            f"match the interviewer's mental model of a 'good hire.'\n\n"
            f"This isn't about bad intentions. It's about bad process. And "
            f"the fix is surprisingly straightforward."
        ),
        "What Most Teams Get Wrong About Interview Fairness": (
            "Most teams think fairness means 'being nice to everyone.' That's "
            "not how bias works.\n\n"
            "Bias in hiring is structural. It lives in the process, not the people. "
            "When questions change from candidate to candidate, when scoring is left "
            "to intuition, when interviewers aren't calibrated against each other — "
            "the result isn't fairness. It's noise dressed as judgment.\n\n"
            "**Here's what the research actually says:**\n"
            "• Structured interviews are 2x more predictive of job performance than unstructured ones\n"
            "• The same interviewers evaluating the same candidates produce different scores "
            "depending on time of day, mood, and candidate order\n"
            "• Removing personal identifiers from evaluations eliminates the single largest "
            "source of unconscious bias\n\n"
            "Fairness isn't a feeling. It's a design choice."
        ),
        "How Structured Evaluation Removes Bias from the Equation": (
            f"Structured evaluation works because it removes variability. "
            f"The same questions, the same scoring rubric, the same evaluation "
            f"criteria — applied to every candidate, every time.\n\n"
            f"Here's how that plays out in practice with an AI voice interview:\n\n"
            f"1. **Every candidate gets the same starting questions**, tied to "
            f"the competencies the role requires\n"
            f"2. **AI probes answers in real time**, consistent follow-up logic "
            f"applied based on response patterns\n"
            f"3. **Scoring is deterministic** — the same answer gets the same score, "
            f"regardless of who gives it or when\n"
            f"4. **Evaluation happens without PII** — name, age, location, and "
            f"other demographic markers are stripped before assessment"
        ),
        "The Data Behind Fair Screening: What the Numbers Show": (
            "The evidence for structured, consistent screening is hard to ignore.\n\n"
            "A meta-analysis of 85 hiring studies found that structured interviews "
            "improve predictive validity by 0.25 over unstructured formats — "
            "roughly the difference between guessing and forecasting.\n\n"
            "**The demographic impact is even more striking:**\n"
            "• Teams using structured evaluation see 2.3x more diverse shortlists "
            "within 90 days of implementation\n"
            "• Candidates from underrepresented groups report 40% higher satisfaction "
            "with structured vs. unstructured processes\n"
            "• Score variance across demographic groups drops by 60% when PII is "
            "stripped before AI evaluation\n\n"
            "These aren't pilot results. These are production numbers from teams "
            "that made structured screening their default workflow."
        ),
        "Building a PII-Safe Evaluation Pipeline": (
            "Candidate privacy and evaluation fairness are the same problem.\n\n"
            "When an AI model processes a resume that includes a candidate's name, "
            "the model can infer gender, ethnicity, and approximate age. Even if "
            "the model is 'blind' to those attributes, the statistical correlations "
            "in the training data create proxy signals.\n\n"
            "**The fix is architectural:** strip PII before any AI processing "
            "touches the candidate's data. At that point, the model evaluates "
            "only what the candidate produced — their answers, their skills, "
            "their fit against the role criteria.\n\n"
            "This isn't just a compliance checkbox. It's the difference between "
            "an AI that amplifies bias and an AI that eliminates it."
        ),
        "From Application to Shortlist in 30 Minutes: The Workflow": (
            "Speed is often framed as a convenience feature. In hiring, it's a "
            "fairness feature.\n\n"
            "Here's the reality: when screening takes days or weeks, candidates "
            "with existing professional networks and flexible schedules have an "
            "advantage. Candidates juggling jobs, caregiving, or other constraints "
            "fall through the cracks.\n\n"
            "A 30-minute evaluation workflow changes that:\n"
            "• Candidates apply and get assessed immediately — no scheduling wait\n"
            "• AI runs the same interview at 2 PM or 2 AM — consistent experience "
            "regardless of when the candidate applies\n"
            "• The team receives a ranked shortlist with evidence reports — "
            "no manual review bottlenecks\n\n"
            "**Fast pipelines don't cut corners.** They remove the administrative "
            "gatekeeping that makes hiring inequitable."
        ),
        "Why Deterministic Scoring Beats Black-Box Models": (
            "There's a growing trend in HR tech toward AI models that 'just work.' "
            "You feed in resumes, you get out rankings. What happens in between? "
            "Nobody knows.\n\n"
            "That's a problem — not just for compliance, but for quality.\n\n"
            "**Deterministic scoring is the alternative:**\n"
            "• Every scoring rule is written in code, documented, and testable\n"
            "• The same inputs always produce the same outputs\n"
            "• You can audit any decision by tracing the score back to the specific "
            "rules that produced it\n"
            "• There's no model drift, no retraining surprises, no 'the model changed "
            "its mind this quarter'\n\n"
            "Black-box models optimize for accuracy. Deterministic systems optimize "
            "for accountability. In hiring, accountability matters more."
        ),
        "The Business Case for Fairer Interviews": (
            f"None of this is theoretical. Teams that adopt structured, AI-powered "
            f"screening see measurable results:\n\n"
            f"• **60-70% reduction** in time-to-shortlist\n"
            f"• **3x improvement** in pipeline diversity at the shortlist stage\n"
            f"• **Higher candidate satisfaction** — candidates report feeling "
            f"evaluated fairly when the process is consistent\n"
            f"• **Lower administrative burden** — hiring teams shift from scheduling "
            f"to decision-making\n\n"
            f"The question isn't whether your team can afford to implement "
            f"fairer interviews. It's whether you can afford not to."
        ),
    }

    # Add SEO keyword to at least one section
    if seo_keyword:
        insert_in = outline[2]["heading"] if len(outline) > 2 else outline[0]["heading"]
        if insert_in in section_contents:
            section_contents[insert_in] += (
                f"\n\nThis is where {seo_keyword} gets addressed directly. "
                f"When evaluation is consistent and transparent, the concerns "
                f"around {seo_keyword} don't disappear — they get resolved."
            )

    # Build sections with content
    sections = []
    total_words = 0
    words_per_section = target_max // max(len(outline), 1)

    for i, item in enumerate(outline):
        heading = item["heading"]
        content = section_contents.get(heading, (
            f"Content for {heading}. "
            f"This section covers key aspects of {topic.lower()} "
            f"and provides actionable insights for hiring teams."
        ))

        # If not enough sections to reach target, expand content
        if len(outline) <= 5 and i < len(outline):
            extra_paragraphs = [
                f"\n\nFor hiring teams evaluating their approach to {topic.lower()}, "
                f"the key takeaway is clear: consistency is the foundation of fairness. "
                f"Every candidate deserves the same evaluation, regardless of when they "
                f"apply, who reviews their materials, or what their background looks like.",
                f"\n\nThe teams that get this right share a common pattern. They invest "
                f"in the process first — the scoring criteria, the question design, the "
                f"evaluation workflow — and let the technology amplify that foundation. "
                f"Technology without process is just automation. Process with technology "
                f"is transformation.",
                f"\n\n{stat} This isn't an edge case. It's the norm. And it's fixable.",
            ]
            idx = i % len(extra_paragraphs)
            content += extra_paragraphs[idx]

        word_count = len(content.split())
        total_words += word_count

        sections.append({
            "heading": heading,
            "content": content,
            "word_count": word_count,
        })

    # Balance total word count by adjusting last section
    if total_words < target_min and sections:
        deficit = target_min - total_words
        padding = (
            f"\n\n{topic} isn't just another hiring trend. It represents a "
            f"fundamental shift in how teams think about evaluation. The teams "
            f"adopting structured, AI-powered screening today are building a "
            f"competitive advantage that will compound over time."
        )
        sections[-1]["content"] += padding
        added = len(padding.split())
        sections[-1]["word_count"] += added
        total_words += added

    return sections


def make_obsidian_outline(outline: list[dict], topic: str, brand: str,
                           seo_keyword: str, date_str: str) -> str:
    """Format outline as Obsidian markdown document."""
    lines = [
        f"# Blog: {topic}",
        f"**Brand:** {brand}",
        f"**SEO Keyword:** {seo_keyword}" if seo_keyword else "",
        f"**Date:** {date_str}",
        "",
        "---",
        "",
        "## Outline",
        "",
    ]
    for item in outline:
        lines.extend([
            f"### {item['heading']}",
            "",
            f"**Purpose:** {item['purpose']}",
            "",
        ])
    return "\n".join(line for line in lines if line is not None).rstrip("\n") + "\n"


def make_obsidian_draft(sections: list[dict], topic: str, brand: str,
                         seo_keyword: str, date_str: str, total_words: int) -> str:
    """Format full draft as Obsidian markdown document."""
    lines = [
        f"# Blog: {topic}",
        f"**Brand:** {brand}",
    ]
    if seo_keyword:
        lines.append(f"**SEO Keyword:** {seo_keyword}")
    lines.extend([
        f"**Date:** {date_str}",
        f"**Total Words:** {total_words}",
        "",
        "---",
        "",
    ])
    for section in sections:
        lines.extend([
            f"## {section['heading']}",
            "",
            section["content"],
            "",
        ])
    return "\n".join(lines).rstrip("\n") + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate blog outlines and full drafts grounded in a brand's voice."
    )
    parser.add_argument("--brand", required=True, help="Brand name (matches vault directory)")
    parser.add_argument("--topic", required=True, help="Topic for the blog post")
    parser.add_argument("--seo-keyword", default="", help="Primary SEO keyword to include")
    parser.add_argument(
        "--outline-only", action="store_true",
        help="Generate outline only (no expanded section content)"
    )
    parser.add_argument(
        "--length", choices=LENGTH_OPTIONS, default="medium",
        help="Target post length: short (800-1200), medium (1500-2500), long (3000+)"
    )
    parser.add_argument("--demo", action="store_true", help="Use hardcoded demo content (no LLM call)")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print JSON to stdout and skip file writes"
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    vault_root = VAULT_ROOT
    brand_path = os.path.join(vault_root, args.brand)

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

    # Load writing-skills.md — required for real mode; checked here so error is consistent
    load_writing_skills(args.brand, vault_root)

    date_str = date.today().isoformat()
    slug = slugify(args.topic)

    if args.demo:
        outline = generate_demo_outline(args.topic, args.seo_keyword, args.length)

        if args.outline_only:
            output = {
                "brand": args.brand,
                "content_type": "blog",
                "topic": args.topic,
                "seo_keyword": args.seo_keyword,
                "outline": outline,
                "dry_run": args.dry_run,
            }
        else:
            sections = generate_demo_sections(
                args.topic, args.seo_keyword, outline, args.length
            )
            total_word_count = sum(s["word_count"] for s in sections)
            output = {
                "brand": args.brand,
                "content_type": "blog",
                "topic": args.topic,
                "seo_keyword": args.seo_keyword,
                "outline": outline,
                "sections": sections,
                "total_word_count": total_word_count,
                "dry_run": args.dry_run,
            }
    else:
        print("Real mode requires LLM integration. Use --demo for sample output.", file=sys.stderr)
        output = {
            "brand": args.brand,
            "content_type": "blog",
            "topic": args.topic,
            "seo_keyword": args.seo_keyword,
            "outline": [],
            "dry_run": args.dry_run,
        }
        if not args.outline_only:
            output["sections"] = []
            output["total_word_count"] = 0

    print(json.dumps(output, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("[dry-run] No files written.", file=sys.stderr)
        return

    if args.demo:
        generated_dir = os.path.join(brand_path, "generated")
        os.makedirs(generated_dir, exist_ok=True)

        filename = f"{date_str}-blog-{slug}.md"
        filepath = os.path.join(generated_dir, filename)

        if args.outline_only:
            doc = make_obsidian_outline(
                outline, args.topic, args.brand, args.seo_keyword, date_str
            )
        else:
            doc = make_obsidian_draft(
                sections, args.topic, args.brand, args.seo_keyword,
                date_str, output["total_word_count"]
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"Written to {filepath}", file=sys.stderr)


if __name__ == "__main__":
    main()
