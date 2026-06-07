# Skill: Deal Health Scoring

You are scoring deal health using a composite model that weighs 6 factors.

## When to Use
- After MEDDIC analysis is complete
- Before forecast calls or pipeline reviews
- When a rep asks "how healthy is this deal?"
- Weekly pipeline scoring refresh

## Composite Score (0-100)

| Factor | Weight | Source | Description |
|--------|--------|--------|-------------|
| MEDDIC Completeness | 40% | `meddic_scorer.py` | 6 dimensions scored 0-10, averaged, scaled to 100 |
| Account ICP Fit | 20% | `Agent 1` signal scorer | ICP score 0-100 from Clay enrichment + signals |
| Stage Velocity | 15% | CRM data | Days in stage vs benchmark; faster == healthier |
| Engagement Recency | 10% | Gong call history | Days since last prospect call; < 7d is ideal |
| ACV Fit | 10% | CRM data | $500K-$5M is optimal for enterprise GTM |
| Competitive Risk | 5% | CRM data | Active competitor = 50/100 on this factor |

## Health Labels

| Score | Label | Action Required |
|-------|-------|-----------------|
| 80-100 | **Healthy** | Continue progressing, focus on closing |
| 50-79 | **At Risk** | Address top gaps, re-engage champion |
| 0-49 | **Critical** | Urgent intervention required, consider stage change |

## Interpretation Rules

1. **Score is a diagnostic, not a verdict.** A score < 50 doesn't mean "lose the deal" — it means "needs attention."
2. **MEDDIC drives the score.** 40% weight reflects that reps under-document MEDDIC more than any other factor.
3. **Velocity matters.** A deal in `qualification` for 60 days (benchmark: 45) loses velocity points. Escalate or disqualify.
4. **Engagement is a leading indicator.** If days_since_last_call > 14, the deal is cooling. Act before it stalls.
5. **ICP is a deal-level multiplier.** A perfect MEDDIC score on a bad-fit account still produces a capped score.

## Handoff

Call `score_opp(deal_id, meddic_scores, deal_context)` in `mcp_server.py` to compute and write the score. This writes to `__c` custom fields only — it never touches canonical CRM data.

Returns:
- `deal_health_score__c` (0-100)
- `deal_health_label__c` (healthy / at_risk / critical)
- `meddic_completeness__c` (0-100)
- `meddic_gap_count__c`
- `meddic_top_gap__c` (dimension key, e.g., "economic_buyer")
- `meddic_gaps__c` (JSON string of gap details)
- `nba_text__c` (next best action sentence)
- `last_scored_at__c` (ISO timestamp)

## Rules
- Never override health labels — trust the composite math
- Never skip warning interpretation — warnings are the actionable part
- Never score without MEDDIC input — 40% weight needs actual values