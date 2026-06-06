# GTM Intelligence Platform — Design Spec

## Overview

A production-grade GTM Engineering portfolio project demonstrating the architecture, engineering standards, and business impact expected from a Senior Revenue Operations / GTM Engineering professional. The platform showcases MCP-native AI agents for Account Research & Competitive Intelligence, Deal Intelligence & Opportunity Scoring, and Pipeline Health & Forecasting.

**Phase 1 implementation:** Agent 1 — Account Research & Competitive Intelligence.

## Architecture

```
User prompt ──► Agent (Claude API) ──► Skills (prompt templates)
                              │
                    ┌─────────┴──────────┐
                    │  MCP Server Tools   │
                    │  search_web         │
                    │  enrich_account     │
                    │  get_signals        │
                    │  search_deals       │
                    │  summarize_text     │
                    │  generate_email     │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │     Data Layer      │
                    │  PostgreSQL         │
                    │  pgvector           │
                    │  File Store (docs)  │
                    │  Redis Cache        │
                    └────────────────────┘
```

### Four-Layer Model

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Agent Layer | Orchestrates research loop, invokes skills, calls MCP tools | Python + Claude API Sonnet |
| Skills Layer | Reusable prompt templates for specific GTM tasks | Markdown `.md` files |
| MCP Server Layer | Typed, discoverable tools the agent can invoke | Python `mcp` SDK |
| Data Layer | Persistence, vector search, caching, document storage | PostgreSQL + pgvector + Redis + File Store |

## Agent 1: Account Research & Competitive Intelligence

### Trigger Sources
- New account created in CRM
- Deal stage change (any stage)
- Manual prompt: "Research Acme Corp"
- Scheduled weekly refresh for active pipeline accounts

### Pipeline (7 Steps)

#### Step 1: Trigger
Agent fires on any of: Salesforce webhook, cron job, manual prompt.

#### Step 2: CRM Context Pull
Agent calls `search_deals` MCP tool to retrieve existing account history — past interactions, deal stage, owner, open opps. Reads `account://` resource for past briefs. Builds context window before any external calls.

**Tools used:** `search_deals`, `account://` resource

#### Step 3: Enrichment Pass
Parallel calls to `enrich_account` (firmographics: headcount, revenue, tech stack, funding) and `search_web` (recent news, job postings, executive changes, press releases).

**Tools used:** `enrich_account` (Clay mock), `search_web`

#### Step 4: Signal Scoring
`get_signals` returns intent data. The `signal-scoring.md` skill applies weighted logic:
- Funding event: **3.0x**
- Executive change: **2.5x**
- Hiring surge (3+ roles): **2.0x**
- Tech stack match: **1.5x**
- Review activity / competitor usage: **1.0x**

Produces a normalized 0–100 ICP fit score.

**Tools used:** `get_signals`, `signal-scoring.md` skill

#### Step 5: Competitive Intel Overlay
Searches for competitor mentions in web results and review sites. Extracts switching signals and pain points. Identifies the incumbent vendor if present.

**Tools used:** `search_web`, `summarize_text`

#### Step 6: Brief Generation
`brief-gen.md` skill synthesizes all context into a structured account brief:
- Company snapshot (headcount, revenue, funding, tech stack)
- Top 3 active signals with timestamps and weights
- Competitive landscape (incumbent, switching signals)
- Recommended engagement angle
- Drafted first-touch email

**Tools used:** `brief-gen.md` skill, `generate_email`

#### Step 7: Write-Back
Brief is written to the file store (`{manager}/{account}/{date}/brief.md`). Key fields (score, signals, incumbent) are written to PostgreSQL. Cache is warmed in Redis with 24hr TTL.

**Data layer writes:** File store, PostgreSQL, Redis

### Output Mock

What a rep sees:

```
Meridian Capital Partners
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ICP Fit Score:  87/100
Active Signals: 4
Competitor Flags: 2
Researched:     2 minutes ago
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
Top Signals

► Series B closed $42M — 3 weeks ago
  Actively hiring VP of Operations and RevOps Lead.
  Source: TechCrunch + LinkedIn Jobs · Weight: 3.0×

► New CFO Sarah Chen (ex-Blackstone) — 6 weeks ago
  Likely driving process review and vendor evaluation.
  Source: LinkedIn · Weight: 2.5×

► Tech stack: Salesforce + manual Excel workflows
  No fund admin platform detected — greenfield opportunity.
  Source: Clay enrichment + BuiltWith · Weight: 1.5×

► 3 open senior roles (VP Ops, RevOps Lead, Data Engineer)
  Team build-out signals investment in operations infrastructure.
  Source: LinkedIn Jobs · Weight: 2.0×
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
Competitive Intel

Currently piloting Allvue (G2 review, 2 months ago).
No contract lock-in signal detected — active evaluation phase.
Incumbent weakness: Allvue lacks AI-powered workflow automation.
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
Estimated ACV:  $2.4M
Buy Window:     Q3 (post-Series B)
[Draft Outreach] [Comp Strategy] [Add to Sequence]
```

## MCP Server Tools

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `search_web` | Search news, jobs, reviews for a company | `company: str`, `query: str` | `list[SearchResult]` |
| `enrich_account` | Firmographic enrichment (Clay mock) | `company: str`, `domain: str` | `AccountEnrichment` |
| `get_signals` | Intent signals for an account | `company: str`, `days_back: int` | `list[Signal]` |
| `search_deals` | Query CRM deals by account/filters | `account_id: str` or `filters: dict` | `list[Deal]` |
| `summarize_text` | Compress long content to key points | `text: str`, `max_points: int` | `Summary` |
| `generate_email` | Draft personalized outreach | `context: dict`, `tone: str` | `EmailDraft` |
| `calc_forecast` | Weighted forecast from deal list | `deals: list[Deal]`, `method: str` | `Forecast` |

## MCP Resources

| Resource URI | Description |
|-------------|-------------|
| `account://{id}` | Full account profile with briefs |
| `deals://{id}` | Deal detail with history |
| `transcript://{call_id}` | Gong call transcript (mock) |

## Skills Layer

| Skill File | Purpose |
|-----------|---------|
| `skills/account-research.md` | Top-level agent skill. Orchestrates the full research loop — trigger → context → enrich → score → compete → brief → write-back |
| `skills/signal-scoring.md` | Weighting logic for intent signals with normalization to 0-100 |
| `skills/brief-gen.md` | Output format spec for the account brief |

Skills are plain markdown files that act as system prompts. They encode the agent's behavior, output format, and decision rules. Loadable into Claude Code, OpenCode, or any MCP-compatible AI.

## Prompt Library

| Prompt File | Purpose |
|------------|---------|
| `prompts/search.prompt` | Template for constructing web search queries from account context |
| `prompts/summarize.prompt` | Template for compressing long articles into signal bullet points |
| `prompts/email-draft.prompt` | Template for personalized first-touch email generation |

## Data Layer

### PostgreSQL Schema

```sql
-- Core tables
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    industry TEXT,
    headcount INT,
    revenue_range TEXT,
    funding_total NUMERIC,
    funding_round TEXT,
    funding_date DATE,
    tech_stack JSONB,
    icp_score INT,
    last_researched_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    name TEXT,
    stage TEXT,
    amount NUMERIC,
    owner TEXT,
    probability INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    signal_type TEXT,  -- funding, executive_change, hiring, tech_adoption, review
    source TEXT,
    title TEXT,
    description TEXT,
    weight DECIMAL(3,1),
    detected_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    icp_score INT,
    signal_summary JSONB,
    competitive_intel JSONB,
    recommended_angle TEXT,
    email_draft TEXT,
    file_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector embeddings (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE account_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id),
    embedding VECTOR(1536),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### File Store Structure

```
briefs/
└── {manager_name}/
    └── {account_name}/
        ├── YYYY-MM-DD--brief.md
        ├── YYYY-MM-DD--email-draft.md
        └── YYYY-MM-DD--research-notes.md
```

Example:
```
briefs/jessica-ryan/
└── meridian-capital-partners/
    ├── 2026-06-03--brief.md
    ├── 2026-06-03--email-draft.md
    └── 2026-05-28--research-notes.md
```

### Redis Cache Keys

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `brief:{account_id}` | 24h | Cached brief JSON for dashboard |
| `score:{account_id}` | 24h | Cached ICP score |
| `rate_limit:{ip}` | 1m | API rate limiting |
| `session:{session_id}` | 1h | Agent conversation state |

## Directory Layout

```
gtm-intelligence-platform/
├── code/
│   ├── mcp_server.py           # MCP server with all tool definitions
│   ├── signal_scorer.py        # Weighted intent signal scoring
│   ├── clay_mock.py            # Mock Clay enrichment (mirrors real API shape)
│   ├── gong_mock.py            # Mock Gong transcript data
│   ├── agent.py                # Agent orchestrator (calls Claude API + skills)
│   └── seed_data.py            # Demo data generator
├── skills/
│   ├── account-research.md     # Top-level agent skill
│   ├── signal-scoring.md       # Signal weighting prompt
│   └── brief-gen.md            # Brief output format prompt
├── prompts/
│   ├── search.prompt           # Web search query construction
│   ├── summarize.prompt        # Long content compression
│   └── email-draft.prompt      # Outreach email generation
├── data/
│   ├── fixtures/
│   │   ├── clay-accounts.json  # Sample Clay enrichment output
│   │   └── gong-calls.json     # Sample Gong transcripts
│   ├── schema.sql              # PostgreSQL schema
│   └── seed.sql                # Demo data
├── mcp.json                    # MCP server config for Claude Code
├── .env.example
├── requirements.txt
└── README.md
```

## Engineering Standards

### Error Handling Strategy
- All MCP tools return typed error responses with error codes
- Retry logic: 3 retries with exponential backoff (1s, 4s, 16s) on transient failures
- Fallback: if Clay mock unavailable, return demo data with warning header
- Circuit breaker: after 5 consecutive failures on any tool, disable for 60s
- All errors logged to stderr with structured format: `[ERROR] tool=search_web account=meridian-capital status=429 retry=2/3`

### Monitoring & Observability
- Every tool call logs: tool name, input hash, duration, success/failure
- Agent step tracing: `[AGENT] step=3/7 tool=enrich_account duration=1.2s result=200`
- Weekly brief staleness check: accounts not researched in 7+ days flagged
- Rate limit tracking in Redis for API cost control

### Security Model
- API keys in `.env` only, never in code
- No PII stored in signals or briefs (company-level data only)
- Session isolation via Redis session keys
- Tool permission boundaries: search tools are read-only, write tools require explicit agent consent

### Demo Mode
- Every agent and tool supports `--demo` flag producing realistic output without external APIs
- Demo data in `data/fixtures/` mirrors real API shapes
- `--dry-run` on write operations previews output without persisting

## Stack Choices (Reasoned)

| Choice | Why |
|--------|-----|
| Claude API Sonnet | Function calling + long context handles full research payload. Balances speed and reasoning depth. |
| MCP Server | Typed, discoverable tools. MCP is in the Juniper Square JD. Tool layer is portable: swap Clay for Apollo without touching agent logic. |
| Clay (mocked) | Clay is in the Juniper JD directly. Mock proves understanding of the data model. |
| pgvector | "Find me accounts similar to our last 5 closed-won deals" — killer rep feature. No separate vector DB needed. |
| Redis | Enrichment calls are expensive. Caching brief for 24hrs prevents 10 API calls per rep per account. |
| File store | Juniper JD explicitly mentions "folder structures organized by sales manager and deal context." |
| Web search (live) | CRM data is stale on entry. Live signals move conversations forward. |
| Signal scoring engine | Weighted intent model gives reps a single ICP fit number. QBR-ready metric. |
