"""GTM Intelligence Platform MCP Server.

Exposes typed tools and resources for GTM agents. Run as:
    python code/mcp_server.py

Connects via stdio transport for Claude Code integration.
"""

from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    Resource,
)

# Import local modules
sys.path.insert(0, os.path.dirname(__file__))
from clay_mock import enrich_account as clay_enrich
from gong_mock import get_transcript as gong_transcript
from signal_scorer import score_signals, recommend_engagement_priority

server = Server("gtm-intelligence")


# ── Tool Implementations ──

def search_web(company: str, query: str) -> list[dict]:
    """Mock web search. In production, calls Firecrawl or Exa API."""
    results_map = {
        "meridian capital": [
            {"title": "Meridian Capital Raises $42M Series B", "source": "TechCrunch", "date": "2026-05-16", "snippet": "Meridian Capital Partners announced a $42M Series B round led by Accel...", "url": "https://techcrunch.com/..."},
            {"title": "Meridian Capital Hires Sarah Chen as CFO", "source": "LinkedIn News", "date": "2026-04-18", "snippet": "Meridian Capital Partners has appointed Sarah Chen, former Blackstone VP, as CFO...", "url": "https://linkedin.com/..."},
            {"title": "Meridian Capital Hiring VP of Operations", "source": "LinkedIn Jobs", "date": "2026-05-28", "snippet": "Meridian Capital Partners is looking for a VP of Operations to lead scale-up efforts...", "url": "https://linkedin.com/jobs/..."},
            {"title": "G2 Review: Allvue vs Alternatives", "source": "G2", "date": "2026-04-02", "snippet": "User from financial services firm reports evaluating Allvue for fund administration...", "url": "https://g2.com/products/allvue/..."},
        ],
    }
    key = company.lower().strip()
    for k, v in results_map.items():
        if k in key or key in k:
            return v
    return []


def get_signals(company: str, days_back: int = 90) -> dict:
    """Get intent signals for a company. Merges mock data."""
    signals_db = {
        "meridian capital partners": [
            {"signal_type": "funding", "source": "TechCrunch", "title": "Series B closed $42M", "description": "Actively hiring VP of Operations and RevOps Lead", "weight": 3.0, "detected_at": "2026-05-15T09:00:00Z"},
            {"signal_type": "executive_change", "source": "LinkedIn", "title": "New CFO Sarah Chen (ex-Blackstone)", "description": "Joined 6 weeks ago. Likely driving process review.", "weight": 2.5, "detected_at": "2026-04-20T14:00:00Z"},
            {"signal_type": "hiring", "source": "LinkedIn Jobs", "title": "3 open senior roles", "description": "VP Ops, RevOps Lead, Data Engineer", "weight": 2.0, "detected_at": "2026-05-25T10:00:00Z"},
            {"signal_type": "tech_adoption", "source": "Clay + BuiltWith", "title": "No fund admin platform detected", "description": "Salesforce + manual Excel workflows — greenfield opportunity", "weight": 1.5, "detected_at": "2026-06-01T08:00:00Z"},
        ],
        "apex analytics": [
            {"signal_type": "funding", "source": "Crunchbase", "title": "Series A $12M closed", "description": "Scaling engineering and GTM teams", "weight": 3.0, "detected_at": "2026-04-01T10:00:00Z"},
            {"signal_type": "hiring", "source": "LinkedIn Jobs", "title": "Hiring Head of Sales", "description": "First dedicated sales leader signals go-to-market investment", "weight": 2.0, "detected_at": "2026-05-10T14:00:00Z"},
        ],
    }

    key = company.lower().strip()
    for k, v in signals_db.items():
        if k in key or key in k:
            scored = score_signals(v, days_back)
            return {"company": company, "signals": v, "scored": scored}
    return {"company": company, "signals": [], "scored": {"total_score": 0, "breakdown": [], "summary": "No signals found"}}


def search_deals(account_id: str = "", company: str = "", filters: dict | None = None) -> list[dict]:
    """Search CRM deals by account or filters."""
    deals_db = {
        "meridian capital partners": [{"id": "deal-001", "account": "Meridian Capital Partners", "name": "Meridian Capital - Q3 Pipeline", "stage": "qualification", "amount": 2400000, "owner": "Jessica Ryan", "probability": 40, "created_at": "2026-03-15", "updated_at": "2026-05-20"}],
        "apex analytics": [{"id": "deal-002", "account": "Apex Analytics", "name": "Apex Analytics - Q3 Pipeline", "stage": "discovery", "amount": 600000, "owner": "Tom Rivera", "probability": 25, "created_at": "2026-04-10", "updated_at": "2026-05-25"}],
        "northstar equity group": [{"id": "deal-003", "account": "NorthStar Equity Group", "name": "NorthStar - Q4 Pipeline", "stage": "qualification", "amount": 5000000, "owner": "Jessica Ryan", "probability": 10, "created_at": "2026-05-01", "updated_at": "2026-05-28"}],
    }

    if company:
        key = company.lower().strip()
        for k, v in deals_db.items():
            if k in key or key in k:
                return v
    return []


def summarize_text(text: str, max_points: int = 5) -> dict:
    """Compress long text to key bullet points."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 20]
    points = sentences[:max_points]
    return {"original_length": len(text), "summary_points": points, "point_count": len(points)}


def generate_email(context: dict, tone: str = "professional") -> dict:
    """Generate a personalized outreach email based on context."""
    company = context.get("company", "")
    signals = context.get("signals", [])
    recommended_angle = context.get("recommended_angle", "")

    signal_types = [s.get("signal_type", "") for s in signals]
    has_funding = "funding" in signal_types
    has_exec = "executive_change" in signal_types

    subject = f"Thoughts on scaling {company}'s operations?"
    if has_funding:
        subject = f"Congrats on the {company} growth — a thought on operations"

    greeting = f"Hi {{contact_name}},"
    body = f"I noticed {company} has been making moves recently"
    if has_funding:
        body += f" — the recent funding round is exciting"
    if has_exec:
        body += f", and welcoming a new CFO is a great time to evaluate operational infrastructure"
    body += ".\n\n"
    body += "Many firms at your stage find that manual processes don't scale as AUM grows. We help teams automate fund administration workflows so your team focuses on investments, not spreadsheets.\n\n"
    body += "Would you be open to a 15-minute conversation to see if this is relevant?"

    return {
        "subject": subject,
        "greeting": greeting,
        "body": body,
        "tone": tone,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── MCP Definitions ──

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_web",
            description="Search news, job posts, press releases, and review sites for a company",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name to search for"},
                    "query": {"type": "string", "description": "Optional search query refinement"},
                },
                "required": ["company"],
            },
        ),
        Tool(
            name="enrich_account",
            description="Enrich account with firmographic data (Clay mock)",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name to enrich"},
                    "domain": {"type": "string", "description": "Company domain (optional)"},
                },
                "required": ["company"],
            },
        ),
        Tool(
            name="get_signals",
            description="Get intent signals for an account with scored ICP fit",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name"},
                    "days_back": {"type": "number", "description": "How many days back to scan for signals"},
                },
                "required": ["company"],
            },
        ),
        Tool(
            name="search_deals",
            description="Search CRM deals by account or filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name to find deals for"},
                    "account_id": {"type": "string", "description": "Account ID (alternative to company name)"},
                },
            },
        ),
        Tool(
            name="summarize_text",
            description="Compress long content to key bullet points",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to summarize"},
                    "max_points": {"type": "number", "description": "Maximum number of summary points"},
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="generate_email",
            description="Generate personalized outreach email from account context",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "object", "description": "Account context dict with company, signals, recommended_angle"},
                    "tone": {"type": "string", "description": "professional | casual | urgent"},
                },
                "required": ["context"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "search_web":
            result = search_web(arguments["company"], arguments.get("query", ""))
        elif name == "enrich_account":
            result = clay_enrich(arguments["company"], arguments.get("domain", ""))
        elif name == "get_signals":
            result = get_signals(arguments["company"], arguments.get("days_back", 90))
        elif name == "search_deals":
            result = search_deals(arguments.get("account_id", ""), arguments.get("company", ""))
        elif name == "summarize_text":
            result = summarize_text(arguments["text"], arguments.get("max_points", 5))
        elif name == "generate_email":
            result = generate_email(arguments["context"], arguments.get("tone", "professional"))
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e), "tool": name}, indent=2))]


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="account://meridian-capital-partners",
            name="Meridian Capital Partners",
            description="Account profile for Meridian Capital Partners",
            mimeType="application/json",
        ),
    ]


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="research_account",
            description="Full account research workflow: enrich -> score -> generate brief",
            arguments=[
                PromptArgument(name="company", description="Company name to research", required=True),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    if name == "research_account":
        company = arguments.get("company", "Unknown") if arguments else "Unknown"
        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Research the account {company}. Follow this pipeline:\n"
                        f"1. Pull CRM context with search_deals\n"
                        f"2. Enrich account with enrich_account\n"
                        f"3. Search web for news/signals\n"
                        f"4. Get signals and score them\n"
                        f"5. Check competitive landscape\n"
                        f"6. Generate structured brief\n"
                        f"7. Generate outreach email\n\n"
                        f"Return a complete account brief with: company snapshot, top 3 signals, "
                        f"competitive landscape, recommended angle, ICP score, and drafted email.",
                    ),
                )
            ],
        )


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
