# GTM Intelligence Platform

**Production-grade MCP-native AI agents for revenue intelligence.**

A platform architecture (3 agents planned) with 1 fully implemented agent: Account Research & Competitive Intelligence. Demonstrates MCP server architecture, weighted signal scoring, skills-based agent orchestration, and enterprise GTM data modeling.

## Architecture

```
Agent Layer --> Skills Layer --> MCP Server --> Data Layer
   (Claude)      (.md prompts)   (6 tools)      (PG + Vector + Redis + Files)
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

## Stack

| Component | Implementation |
|-----------|---------------|
| Agent Orchestration | Python + Claude API Sonnet |
| MCP Server | Python `mcp` SDK (stdio transport) |
| Signal Scoring | Weighted rule engine with recency boost |
| Data Layer | PostgreSQL + pgvector + Redis + File Store |
| Clay (mock) | JSON fixtures mirroring real API shape |
| Gong (mock) | Sample transcripts with MEDDPICC structure |
| Skills | Portable markdown prompt templates |
| Claude Code Config | `mcp.json` for direct IDE integration |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent (dry-run - no files written)
python code/agent.py --company "Meridian Capital Partners" --dry-run

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
    agent.py            # Agent orchestrator (7-step pipeline)
    mcp_server.py       # MCP server with 6 GTM tools
    signal_scorer.py    # Weighted + recency signal scoring
    clay_mock.py        # Clay enrichment mock
    gong_mock.py        # Gong transcript mock
    seed_data.py        # Demo data generator
  skills/
    account-research.md # Research pipeline skill
    signal-scoring.md   # Weighting logic skill
    brief-gen.md        # Brief output format skill
  prompts/
    search.prompt       # Web search query construction
    summarize.prompt    # Long content compression
    email-draft.prompt  # Outreach email generation
  data/
    fixtures/           # Clay + Gong sample data
    schema.sql          # PostgreSQL schema
    seed.sql            # Demo database seed
  mcp.json              # Claude Code configuration
  .env.example
  requirements.txt
  README.md
```

---

*Built as part of a GTM engineering portfolio. Demonstrates Senior GTM Engineer capabilities: MCP architecture, enterprise data modeling, weighted scoring systems, agent orchestration, and skills-based AI workflows.*
