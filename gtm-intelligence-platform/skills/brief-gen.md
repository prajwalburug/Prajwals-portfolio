# Skill: Account Brief Generation

Generate a structured account brief in the following format:

## Header
{Company Name}
-------------------------------
ICP Fit Score:  {score}/100
Active Signals: {count}
Competitor Flags: {flag_count}
Researched:     {timestamp}

## Top Signals

=> {Signal Title} - {recency}
  {description}
  Source: {source} . Weight: {weight}x

[Repeat for top 3-5 signals]

## Competitive Intel

{Competitor name} is the incumbent/switching from/not present.
Key observations about competitive landscape.
Switching signals detected: yes/no

## Recommended Angle

One sentence describing the engagement recommendation.

## Estimated ACV

${amount} if available, or estimated from deal stage + company size.

## Playbook

Based on signals and ICP score, recommend one of:
- [Outbound] - Contact immediately
- [Nurture] - Add to sequence, send relevant content
- [Monitor] - Track signals, no action
