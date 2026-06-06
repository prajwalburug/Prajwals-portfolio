# Skill: Signal Weighting & Scoring

## Weight Table

| Signal Type | Base Weight | Why |
|-------------|-------------|-----|
| funding | 3.0x | Capital availability drives spending |
| executive_change | 2.5x | New leadership reviews existing vendors |
| hiring | 2.0x | Team build-out signals investment |
| tech_adoption | 1.5x | Stack changes create displacement opportunities |
| review_activity | 1.0x | Active evaluation is a warm signal |

## Recency Boost

| Age | Boost |
|-----|-------|
| <= 7 days | 2.0x |
| 8-30 days | 1.5x |
| 31-60 days | 1.2x |
| 61-90 days | 1.0x |
| > 90 days | 0.5x |

## Score Interpretation

| Score | Priority | Action |
|-------|----------|--------|
| 80-100 | HIGH | Contact immediately - active buying window |
| 50-79 | MEDIUM | Nurture with relevant content, monitor signals |
| 0-49 | LOW | Monitor only, no outbound effort |

## Usage

Pass signals to `code/signal_scorer.py` or describe scores using the weight table and recency boost above. Scores normalize to 0-100.
