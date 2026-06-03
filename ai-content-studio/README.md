# AI Content Studio

**Brand-aligned content generation across LinkedIn, email, and blog — powered by Obsidian + AI.**

A content production system that generates brand-voice content from a central Obsidian vault. Six agents handle research, generation, and repurposing — all reading from a single `writing-skills.md` that captures brand voice, swipe file patterns, and channel rules. That same file is portable to any AI platform (Claude, ChatGPT, Gemini, OpenCode).

## The Problem

Content teams struggle with inconsistent brand voice across channels. Every platform has different rules (LinkedIn character limits, email subject line length, blog SEO), but the underlying message should be the same. Without a system, each piece of content requires re-stating the brand guidelines, manually checking channel rules, and starting from scratch.

## What We Built

A three-layer system:

```
RESEARCH ──► SWIPE FILE ──► GENERATION
                              │
                              └──► writing-skills.md (portable to any AI)
```

| Layer | What It Does | Tool |
|-------|-------------|------|
| Research | Scans LinkedIn, email, competitor content for performance patterns | `research_scout.py` + Firecrawl |
| Swipe File | Living library of hooks, frameworks, subject lines, CTAs, channel rules | Obsidian vault |
| Generation | Produces brand-voice content from topic + angle | 4 Python agents |
| Portability | Compiles brand + swipe file into a single system prompt for any AI | `compile_skills.py` |

## Agents

| Agent | Input | Output |
|-------|-------|--------|
| `compile_skills.py` | `--brand` | `writing-skills.md` (portable brand system prompt) |
| `generate_linkedin.py` | `--brand --topic --angle` | LinkedIn post variants (JSON + .md) |
| `generate_email.py` | `--brand --topic --type` | Email/newsletter variants (JSON + .md) |
| `generate_blog.py` | `--brand --topic --seo-keyword` | Blog outline or full draft (JSON + .md) |
| `repurpose.py` | `--brand --input --channels` | Multi-channel variants from single source |
| `research_scout.py` | `--brand --source` | Performance patterns → `whats-working.md` |

## How It Works

1. **Weekly:** `research_scout.py` scans channels → updates `swipe-file/whats-working.md`
2. **Ongoing:** Human adds hooks, frameworks, CTAs to swipe files in Obsidian
3. **On brand update:** `compile_skills.py` → `writing-skills.md` (load this into any AI)
4. **On request:** `generate_*.py` reads `writing-skills.md` → generates drafts
5. **Output:** Drafts land in Obsidian `generated/` for review + n8n for scheduling

## Why It Works

- **Portable brand voice:** `writing-skills.md` works in Claude Projects, ChatGPT Custom GPTs, Gemini saved prompts, and OpenCode skills — one file, any AI
- **Demo-safe:** All agents have `--demo` mode with realistic sample output — no API keys needed
- **Dry-run safe:** Every agent supports `--dry-run` — preview before writing
- **Research-backed:** Patterns from `research_scout.py` feed the swipe file, which feeds the generation
- **Repurpose-first:** One blog post → LinkedIn thread + email newsletter + blog draft from `repurpose.py`
- **Obsidian-native:** Brand lives in markdown. No database, no API, no vendor lock-in.

## Tech Stack

Python 3 · Firecrawl · Obsidian · n8n · Claude/OpenAI/Gemini (optional, for real mode)

## Quick Start

```bash
# From this directory
pip install firecrawl

# Compile brand voice
python code/compile_skills.py --brand awesome-hires

# Generate content (demo mode — no API key needed)
python code/generate_linkedin.py --brand awesome-hires --topic "AI bias in hiring" --demo
python code/generate_email.py --brand awesome-hires --topic "30-min screening" --type cold --demo
python code/generate_blog.py --brand awesome-hires --topic "Why AI interviews are fairer" --outline-only --demo

# Repurpose content
python code/repurpose.py --brand awesome-hires --channels linkedin,email --demo

# Research
python code/research_scout.py --brand awesome-hires --source linkedin --demo

# Dry-run (no files written)
python code/generate_linkedin.py --brand awesome-hires --topic "test" --demo --dry-run
```

## Architecture

```
                    RESEARCH LAYER
  Firecrawl ──► research_scout.py ──► whats-working.md
                        │
                        ▼
          ┌─────────────────────────────┐
          │      OBSIDIAN VAULT         │
          │  brands/{name}/             │
          │   ├── brand-kit.md          │
          │   ├── writing-skills.md     │
          │   ├── swipe-file/           │
          │   │   ├── hooks.md          │
          │   │   ├── frameworks.md     │
          │   │   ├── subject-lines.md  │
          │   │   ├── cta-library.md    │
          │   │   ├── channel-rules/    │
          │   │   └── whats-working.md  │
          │   └── generated/            │
          └─────────────────────────────┘
                        │
                    compile_skills.py
                        │
                        ▼
                  writing-skills.md ◄──── Load into Claude/ChatGPT/Gemini
                        │
                        ▼
          ┌─────────────────────────────┐
          │    GENERATION AGENTS        │
          │  generate_linkedin.py       │
          │  generate_email.py          │
          │  generate_blog.py           │
          │  repurpose.py               │
          └─────────────────────────────┘
                        │
                   ┌────┴────┐
                   ▼         ▼
              Obsidian/   n8n/
              generated   publish
```

## Project Structure

```
ai-content-studio/
├── code/
│   ├── compile_skills.py        # Brand + swipe → writing-skills.md
│   ├── generate_linkedin.py     # LinkedIn post drafts
│   ├── generate_email.py        # Cold email & newsletter drafts
│   ├── generate_blog.py         # Blog outline → full draft
│   ├── repurpose.py             # Multi-channel repurposing
│   └── research_scout.py        # Firecrawl performance analysis
├── automation/
│   ├── content-studio.json      # n8n generation workflow
│   └── research-scan.json       # n8n weekly research scanner
├── swipe-file/
│   ├── hooks.md                 # 25+ proven hook patterns
│   ├── frameworks.md            # 5 content frameworks (PAS, AIDA, etc.)
│   ├── subject-lines.md         # 40+ subject lines by intent
│   ├── cta-library.md           # CTAs by intent
│   ├── channel-rules/           # LinkedIn/email/blog formatting rules
│   └── whats-working.md         # Research findings (auto-generated)
├── brands/
│   └── awesome-hires/
│       ├── brand-kit.md         # Brand voice, audiences, differentiation
│       └── writing-skills.md    # Portable brand system prompt
└── README.md
```

---

*Built as part of a GTM engineering portfolio. Sample brand: Awesome Hires — AI-powered hiring platform.*
