# Skill: MEDDIC Analysis from Gong Transcripts

You are analyzing sales call transcripts to extract MEDDIC qualification signals.

## When to Use
- A deal stage changes (e.g., discovery → demo)
- A new Gong call is recorded
- A rep requests "score this deal"
- Weekly MEDDIC refresh for active pipeline

## Pipeline

### Step 1: Fetch Transcripts
Call `get_transcript(company="Company Name")` to retrieve all recent calls sorted by date descending. If a specific call is needed, pass `call_id`.

### Step 2: Extract MEDDIC Dimensions
From the full_transcript speaker turns, extract signals for each dimension:

| Dimension | Signal Indicators | What to Look For |
|-----------|-------------------|------------------|
| **M - Metrics** | Budget talk, ROI quantification, cost savings | Numbers: "save 40%", "reduce by $2M", "payback in 6 months" |
| **E - Economic Buyer** | Budget authority, signing authority | "Sarah signs the check", "need CFO approval", "budget holder" |
| **D1 - Decision Criteria** | Must-haves, requirements, integration needs | "needs SOC2", "must integrate with Salesforce", "requires API" |
| **D2 - Decision Process** | Procurement steps, timeline, stages | "board review in Q3", "evaluation committee", "procurement process" |
| **I - Identified Pain** | Problem statements, frustration, risk | "manual process is broken", "not scaling", "losing deals" |
| **C - Champion** | Advocacy language, internal push | "we need this", "exactly what we need", "org chart access" |

### Step 3: Score Each Dimension
Use `code/meddic_scorer.py` to score dimensions 0-10:
- **0-4 (Gap)**: Low confidence — signal weak or absent
- **5-7 (Developing)**: Some evidence but incomplete
- **8-10 (Strong)**: Clear, documented, and validated

### Step 4: Generate Gaps & NBA
Pass scored dimensions to `code/meddic_scorer.py`. It returns:
- Top gap (highest risk-weighted dimension below 5)
- Gap count and status per dimension
- Best action template filled with deal context

### Step 5: Hand Off to Deal Scorer
Pass the MEDDIC results to `code/deal_scorer.py` via `score_opp` for the composite deal health score.

## MEDDIC Red Flags

| Red Flag | What It Means | Action |
|----------|---------------|--------|
| No economic buyer identified | No one can approve budget | Champion intro call |
| "We'll figure out the process" | No procurement roadmap | Map stages now |
| Champion has no authority | Advocate without influence | Find executive sponsor |
| Pain not quantified | Risk = feature discussion | Build dollar-based ROI |
| Decision criteria = competitor checklist | Prospect is comparing | Differentiate hard |

## Rules
- Score from transcript evidence only, not intuition
- Flag unknown explicitly — "EB not mentioned" is valid
- Lower score == more urgency, not failure
- Never skip the risk-weighted gap ranking for NBA