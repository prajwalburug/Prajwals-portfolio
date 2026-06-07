# GTM Intelligence Platform

**Production-grade MCP-native AI agents for revenue intelligence.**

A platform architecture (3 agents planned) with 2 fully implemented agents:

1. **Agent 1** — Account Research & Competitive Intelligence
2. **Agent 2** — Deal Intelligence & Opportunity Scoring (MEDDIC + deal health + NBA)

Demonstrates MCP server architecture, weighted signal scoring, MEDDIC qualification analysis, composite deal health scoring, skills-based agent orchestration, and enterprise GTM data modeling.

## Architecture

```
Agent Layer --> Skills Layer --> MCP Server --> Data Layer
   (Claude)      (.md prompts)   (9 tools)      (PG + Vector + Redis + Files)

         Agent 2 chain handoff to Agent 3 (structured JSON, no prose re-parsing)
```

## Agent 1: Account Research & Competitive Intelligence

### Pipeline

1. **Trigger** - New CRM account, deal stage change, manual prompt, weekly cron
2. **CRM Context Pull** - `search_deals` for existing history
3. **Enrichment Pass** - `enrich_account` (Clay) + `search_web` (news, jobs, exec changes)
4. **Signal Scoring** - Weighted intent model (funding 3x, exec 2.5x, hiring 2x, tech 1.5x)
5. **Competitive Intel** - Identify incumbent, switching signals, G2 reviews
6. **Brief Generation** - Structured brief + drafted outreach email
7. **Write-Back** - Brief to file store, score to DB, cache to Redis

### Output

```
Meridian Capital Partners
--------------------------------------------------
ICP Fit Score:  87/100    Active Signals: 4
Competitor Flags: 1       Researched: 2026-06-03

=> Series B $42M - 19d ago    Weight: 3.0x
=> New CFO Sarah Chen - 44d ago  Weight: 2.5x
=> 3 open senior roles - 9d ago  Weight: 2.0x

Competitor: piloting Allvue (no lock-in)
Engagement: HIGH - Contact immediately
```

## Agent 2: Deal Intelligence & Opportunity Scoring

Analyzes sales call transcripts to extract MEDDIC qualification signals, scores deal health across 6 weighted factors, and generates next best actions (NBA) for sales reps.

### Pipeline

1. **Trigger** — Deal stage change, new Gong call recorded, manual score request
2. **Context Assembly** — Pull deal owner, stage, ACV, ICP score from Agent 1 handoff
3. **Transcript Fetch** — `get_transcript` retrieves last 3 calls with full speaker-turn text
4. **MEDDIC Analysis** — Keyword-heuristic extraction across 6 dimensions (Metrics, EB, DC1, DC2, Pain, Champion)
5. **Gap Detection** — Dimensions scored 0-10; below 5 = gap; ranked by risk weight (EB 1.5x, champion/pain 1.3x, process 1.2x)
6. **Similar Deal Search** — Mock pgvector similarity against 3 closed-won deals for pattern matching
7. **Composite Health Score** — 6-factor weighted engine (MEDDIC 40%, ICP 20%, velocity 15%, engagement 10%, ACV fit 10%, comp risk 5%)
8. **Write-Back** — `score_opp` writes `__c` custom fields only (governance), structured JSON handoff to Agent 3

### Interactive Scorer

```bash
# CLI with dimension scores
python code/meddic_scorer.py --metrics 3 --eb 2 --dc 6 --dp 2 --pain 8 --champion 7

# REPL — live recalc on every change
python code/meddic_scorer.py --metrics 3 --eb 2 --dc 6 --dp 2 --pain 8 --champion 7 --interactive

# Full agent 2 pipeline
python code/agent2.py --company "Meridian Capital Partners" --deal-id deal-001 --dry-run
```

### Output

```
Meridian Capital Partners  |  deal-001
============================================================
Deal Health:  70/100  (AT_RISK)
MEDDIC:       53/100 completeness  (2 gaps)
Owner:        Jessica Ryan  |  Stage: qualification (25d)  |  $2,400,000 ACV
Transcribed:  3 calls  |  call-meridian-004, call-meridian-003, call-meridian-002

M - Metrics          7/10
E - Economic buyer   8/10
D1 - Decision crit.  4/10 GAP (medium)
D2 - Decision proc.  2/10 GAP (high)   <-- top risk-weighted gap
I - Identified pain  5/10
C - Champion         6/10

NBA: Ask Marcus Webb to walk through procurement process step by step.
```

### Governance

`score_opp` enforces write-once-to-custom-fields discipline: all outputs use `__c` suffixed keys (`deal_health_score__c`, `nba_text__c`, `meddic_top_gap__c`). Never writes to canonical CRM fields (StageName, CloseDate, Amount).

### Chain Handoff → Agent 3

Agent 2 writes structured `handoff_to_agent3` JSON with typed fields (ints, arrays, strings):

```json
{
  "source_agent": "agent2",
  "handoff_type": "deal_scored",
  "target_agent": "agent3",
  "deal_id": "deal-001",
  "deal_health_score": 70,
  "meddic_completeness": 53,
  "meddic_top_gap": "decision_process",
  "nba_text": "Ask Marcus Webb to walk through procurement...",
  "warnings": ["Competitor actively engaged..."],
  "transcript_call_ids": ["call-meridian-004", "call-meridian-003", "call-meridian-002"]
}
```

No prose re-parsing needed — Agent 3 reads typed fields directly.

## Stack

| Component | Implementation |
|-----------|---------------|
| Agent Orchestration | Python + Claude API Sonnet |
| MCP Server | Python `mcp` SDK (stdio transport) — 9 tools |
| Signal Scoring | Weighted rule engine with recency boost |
| MEDDIC Scoring | 6-dimension engine (0-10), gap detection, NBA generation |
| Deal Health Scoring | 6-factor composite (MEDDIC 40%, ICP 20%, velocity 15%, engagement 10%, ACV 10%, comp 5%) |
| Governed MCP Tools | Custom-field-only writes (`__c` suffixed) |
| Data Layer | PostgreSQL + pgvector + Redis + File Store |
| Gong (mock) | 5 multi-turn calls with full speaker-turn transcripts |
| Clay (mock) | JSON fixtures mirroring real API shape |
| Skills | 6 portable markdown prompt templates |
| Prompts | 5 templated `.prompt` files |
| Chain Handoff | Structured JSON between agents (no prose re-parsing) |
| Claude Code Config | `mcp.json` for direct IDE integration |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Agent 1 — Account Research
python code/agent.py --company "Meridian Capital Partners" --dry-run

# Agent 2 — Deal Scoring (interactive REPL)
python code/meddic_scorer.py --metrics 3 --eb 2 --dc 6 --dp 2 --pain 8 --champion 7 --interactive

# Agent 2 — Full pipeline
python code/agent2.py --company "Meridian Capital Partners" --deal-id deal-001 --dry-run

# Generate seed data
python code/seed_data.py ./data
```

## MCP Integration

Add to Claude Code's `mcp.json`:

```json
{
  "mcpServers": {
    "gtm-intelligence": {
      "command": "python",
      "args": ["code/mcp_server.py"]
    }
  }
}
```

Then in Claude Code: "Research Meridian Capital Partners" - the agent uses MCP tools to execute the full pipeline.

## Project Structure

```
gtm-intelligence-platform/
  code/
    agent.py            # Agent 1 orchestrator (7-step pipeline)
    agent2.py           # Agent 2 orchestrator (8-step deal scoring pipeline)
    mcp_server.py       # MCP server with 9 GTM tools
    signal_scorer.py    # Weighted + recency signal scoring
    meddic_scorer.py    # MEDDIC analysis + gap detection + NBA + interactive CLI
    deal_scorer.py      # Composite deal health scoring (6 factors)
    clay_mock.py        # Clay enrichment mock
    gong_mock.py        # Gong transcript mock (5 multi-turn calls)
    seed_data.py        # Demo data generator
  skills/
    account-research.md # Agent 1: research pipeline skill
    signal-scoring.md   # Agent 1: weighting logic skill
    brief-gen.md        # Agent 1: brief output format skill
    meddic-analysis.md  # Agent 2: MEDDIC extraction from transcripts
    deal-score.md       # Agent 2: composite health score interpretation
    next-action.md      # Agent 2: gap-to-NBA mapping
  prompts/
    search.prompt       # Agent 1: web search query construction
    summarize.prompt    # Agent 1: long content compression
    email-draft.prompt  # Agent 1: outreach email generation
    meddic-extract.prompt  # Agent 2: LLM-based MEDDIC extraction
    coaching-note.prompt   # Agent 2: rep coaching note generation
  data/
    fixtures/           # Clay + Gong sample data
    schema.sql          # PostgreSQL schema (v2: MEDDIC fields + deal embeddings)
    seed.sql            # Demo database seed (v2: MEDDIC scores + similar deals)
  mcp.json              # Claude Code configuration
  .env.example
  requirements.txt
  README.md
```

---

*Built as part of a GTM engineering portfolio. Demonstrates Senior GTM Engineer capabilities: MCP architecture, enterprise data modeling, weighted scoring systems, agent orchestration, and skills-based AI workflows.*
