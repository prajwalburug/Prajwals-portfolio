# GTM Portfolio — Engineering Revenue Systems

I build go-to-market systems that turn fragmented tools, messy data, and manual workflows into automated, intelligent revenue engines. This portfolio documents those systems — end-to-end architecture, runnable code, and the thinking behind each design.

---

## Case Studies

| # | Project | Workflows | Problem | Tech | Code |
|--|---------|-----------|---------|------|------|
| 1 | **Wati AI-First GTM Engine** | Lead Lifecycle · Pipeline Intelligence · Outbound Detection | Scaling revenue without scaling headcount for a 16K+ customer WhatsApp platform | HubSpot · n8n · Python · LLM · Clay · SQL | [`wati-gtm-engine/`](./wati-gtm-engine) |
| 2 | **AI Content Studio** | Research · Generation · Repurposing · Brand Compilation | Inconsistent brand voice across LinkedIn, email, and blog | Obsidian · Python · Firecrawl · n8n · Claude/ChatGPT | [`ai-content-studio/`](./ai-content-studio) |
| 3 | **GTM Intelligence Platform** | Account Research & Competitive Intelligence | MCP-native AI agents for revenue intelligence | Python · MCP · Claude · PostgreSQL · Clay | [`gtm-intelligence-platform/`](./gtm-intelligence-platform) |

### 1. Wati AI-First GTM Engine

**The Problem:** Wati (16,000+ customers, 190+ countries) needed to scale revenue without adding headcount. Lead triage was manual, pipeline health was reactive, and outbound was spray-and-pray. Fragmented tools meant data lived in silos.

**What We Built:** A unified intelligent GTM engine with 7 agents across three workflows:

| Workflow | Agents | What It Does | Why It Matters | 
|----------|--------|-------------|----------------|
| [Lead Lifecycle](./wati-gtm-engine/workflows/lead-lifecycle) | `qualify_lead.py` | Auto-qualifies inbound leads by ICP fit score using 4 weighted factors | Speed to lead drops from hours to minutes |
| [Pipeline Intelligence](./wati-gtm-engine/workflows/pipeline-intel) | `analyze_pipeline.py`, `next_best_action.py` | Daily deal risk scoring (5 factors) + rules-based action recommendations | Catch at-risk deals before they slip |
| [Outbound Detection](./wati-gtm-engine/workflows/outbound-scout) | `scout_signals.py`, `prioritize_outbound.py`, `build_sequence.py` | Scans 4 signal sources, scores accounts, generates multi-channel sequences | Proactive pipeline, not reactive |

**How It Works:**
```
Lead ──► Qualifier (ICP score: industry×size×title×signal) ──► Route to AE / Nurture
Deals ──► Risk Engine (staleness×activity×threading×amount×sentiment) ──► NBA ──► Slack
Signals ──► Scout (jobs/funding/leadership/tech) ──► Prioritizer ──► Builder ──► SDR
```

**Why It Works:**
- Every agent has `--demo` + `--dry-run` modes — reviewers see real output with zero setup
- All n8n workflows are exportable JSON — import into any instance
- Rule-based scoring (no LLM key needed) — runs fully offline
- Modular by design — each workflow operates independently

**Tech Stack:** Python 3 · n8n · SQL · HubSpot · Slack

<span class="tag">Lead Routing</span> <span class="tag">AI Scoring</span> <span class="tag">HubSpot</span> <span class="tag">n8n</span> <span class="tag">Pipeline Analytics</span> <span class="tag">Outbound</span>

➡️ [Full case study →](./wati-gtm-engine)

### 2. AI Content Studio

**The Problem:** Content teams struggle with inconsistent brand voice across channels. Every platform has different rules (LinkedIn char limits, email subject length, blog SEO), but the underlying message should be the same. Without a system, each piece of content requires re-stating brand guidelines from scratch.

**What We Built:** A three-layer content system — research (Firecrawl) → swipe file (Obsidian) → generation (Python agents). A portable `writing-skills.md` compiles brand voice + swipe file patterns + channel rules into a single file that any AI can ingest.

| Agent | What It Does |
|-------|-------------|
| `compile_skills.py` | Brand kit + swipe file → portable `writing-skills.md` |
| `generate_linkedin.py` | LinkedIn post drafts (2 variants, brand-voice) |
| `generate_email.py` | Cold email & newsletter drafts |
| `generate_blog.py` | Blog outline → full draft with SEO metadata |
| `repurpose.py` | One piece → LinkedIn + email + blog variants |
| `research_scout.py` | Firecrawl-powered performance pattern analysis |

**Why It Works:**
- `writing-skills.md` loads into Claude Projects, ChatGPT Custom GPTs, Gemini — one file, any AI
- All agents have `--demo` + `--dry-run` — see real output with zero setup
- Obsidian-native brand vault — no database, no vendor lock-in
- Research-backed: performance patterns feed the swipe file, which feeds generation

**Tech Stack:** Python 3 · Obsidian · Firecrawl · n8n · Claude/OpenAI/Gemini

➡️ [Full case study →](./ai-content-studio)

### 3. GTM Intelligence Platform

**The Problem:** Sales reps waste hours researching accounts before outreach. Data lives in silos — CRM here, enrichment there, signals everywhere. No single view tells a rep "is this worth my time, and what should I say?"

**What We Built:** An MCP-native agent that automates the full account research pipeline — enrichment, signal scoring, competitive intel, brief generation, and email drafting — in one shot.

**Pipeline (7 steps):**
1. CRM context pull (`search_deals`)
2. Firmographic enrichment (`enrich_account` — Clay mock)
3. Web signal search (`search_web` — news, jobs, exec changes)
4. Weighted intent scoring (funding 3x, exec 2.5x, hiring 2x, tech 1.5x)
5. Competitive intelligence overlay (incumbent detection, switching signals)
6. Structured brief generation + personalized email
7. Write-back to file store + database

**Why It Works:**
- MCP-native: 6 typed tools expose via stdio transport — works in Claude Code, OpenCode, or any MCP client
- Weighted signal scoring engine normalizes multiple signals into a single 0-100 ICP fit score
- Portable skills layer: 3 markdown skills (`account-research.md`, `signal-scoring.md`, `brief-gen.md`) load into any AI
- All tools support `--demo` + `--dry-run` modes
- Clay + Gong mocks mirror real API shapes — proves integration understanding

**Tech Stack:** Python 3 · MCP SDK · Claude API · PostgreSQL + pgvector · Redis · Clay (mock) · Gong (mock)

➡️ [Full case study →](./gtm-intelligence-platform)

---

## About This Portfolio

Each case study follows the same structure:

> **The Problem** → **What We Built** → **How It Works** → **Why It Works** → **Tech Stack**

Every workflow has a standalone README so you can read it end-to-end without jumping between files. Code is runnable in `--demo` mode — no credentials needed.

Built by [Prajwal Burug](https://github.com/prajwalburug).
