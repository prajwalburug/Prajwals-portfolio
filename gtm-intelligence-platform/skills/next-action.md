# Skill: Next Best Action from Deal Gaps

You translate MEDDIC gaps and deal health warnings into structured next best actions (NBA) for sales reps.

## When to Use
- After deal health scoring is complete
- Before a rep makes their next call
- As the output step of Agent 2

## Gap → Action Mapping

| Top Gap | Action | Urgency | Success Metric |
|---------|--------|---------|----------------|
| **economic_buyer** | Champion arranges EB intro call | Critical | EB attends 20-min call within 7 days |
| **champion** | Identify & develop internal advocate | High | Named champion confirms advocacy in next call |
| **decision_process** | Map procurement steps with champion | High | Written procurement timeline shared |
| **identified_pain** | Build dollar-quantified pain model | High | Prospect agrees to $ impact figure |
| **metrics** | Deliver structured ROI document | Medium | ROI doc shared, prospect engages with questions |
| **decision_criteria** | Define top 3 must-haves | Medium | Written criteria list received |

## Warning → Action Mapping

| Warning | Action | Owner |
|---------|--------|-------|
| MEDDIC < 50% | Schedule MEDDIC review call | AE + BDR |
| Stale stage (velocity) | Set next-step deadline this week | AE |
| No contact > 14 days | Re-engagement sequence | BDR |
| Competitor present | Win/loss analysis, differentiation battlecard | Product Marketing |

## NBA Formulation Rules

1. **One NBA per call.** The top gap generates a single, specific action. Do not return a list of 6 things.
2. **Be concrete.** "Ask Marcus to introduce Sarah Chen this week" not "Engage economic buyer."
3. **Include a time bound.** "This week", "by Friday", "before next call."
4. **Name names.** Use champion_name, eb_name, company from deal context.
5. **Explain why.** One sentence connecting the gap to deal outcome. "Missing EB is #1 deal killer."
6. **No filler.** If no gaps exist, return: "No gaps detected. Continue progressing the deal."

## Handoff Format

Return NBA as structured JSON within the deal scorecard:

```json
{
  "nba_text": "Ask Marcus Webb to arrange a 20-min Sarah Chen intro call this week. Missing economic buyer is the #1 deal killer at this stage.",
  "top_gap": "economic_buyer",
  "top_gap_score": 2,
  "top_gap_risk": "critical",
  "action": "Arrange economic buyer intro call",
  "gap_count": 3
}
```

## Rules
- Never generate NFL (next-following action) — only NBA
- Never return multiple NBAs — pick the highest-risk gap
- Never use placeholders like [Company] — resolve all variables