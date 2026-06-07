INSERT INTO accounts (name, domain, industry, headcount, revenue_range, funding_total, funding_round, funding_date, tech_stack)
VALUES
    ('Meridian Capital Partners', 'meridiancap.com', 'Financial Services', 245, '$50M-$100M', 42000000, 'Series B', '2026-05-15', '["Salesforce", "Excel", "Slack", "Notion"]'),
    ('Apex Analytics', 'apexanalytics.io', 'SaaS - Analytics', 89, '$10M-$25M', 12000000, 'Series A', '2026-04-01', '["HubSpot", "Tableau", "Snowflake", "Slack", "Notion", "Jira"]'),
    ('NorthStar Equity Group', 'northstarequity.com', 'Financial Services - Asset Management', 512, '$100M-$250M', NULL, NULL, NULL, '["Salesforce", "Excel", "Bloomberg Terminal", "Allvue"]');

INSERT INTO deals (account_id, name, stage, amount, owner, probability, deal_health_score, meddic_scores, meddic_gaps, nba_text)
SELECT id, name || ' - Q3 Pipeline', 'qualification', CASE name WHEN 'Meridian Capital Partners' THEN 2400000 WHEN 'Apex Analytics' THEN 600000 WHEN 'NorthStar Equity Group' THEN 5000000 END, 'Jessica Ryan', CASE name WHEN 'Meridian Capital Partners' THEN 40 WHEN 'Apex Analytics' THEN 25 WHEN 'NorthStar Equity Group' THEN 10 END, 63, '{"metrics": 3, "economic_buyer": 2, "decision_criteria": 6, "decision_process": 2, "identified_pain": 8, "champion": 7}', '[{"dimension": "economic_buyer", "score": 2, "weight": 1.5, "risk": "critical"}, {"dimension": "decision_process", "score": 2, "weight": 1.2, "risk": "high"}, {"dimension": "metrics", "score": 3, "weight": 1.0, "risk": "medium"}]', 'Ask Marcus Webb to arrange a 20-min CFO intro call this week. Economic buyer Sarah Chen is the #1 gap.'
FROM accounts WHERE name = 'Meridian Capital Partners';

INSERT INTO deals (account_id, name, stage, amount, owner, probability, deal_health_score, meddic_scores, meddic_gaps, nba_text)
SELECT id, name || ' - Q3 Pipeline', 'discovery', CASE name WHEN 'Meridian Capital Partners' THEN 600000 WHEN 'Apex Analytics' THEN 350000 WHEN 'NorthStar Equity Group' THEN 1200000 END, 'Tom Rivera', 25, 45, '{"metrics": 5, "economic_buyer": 4, "decision_criteria": 5, "decision_process": 1, "identified_pain": 7, "champion": 6}', '[{"dimension": "decision_process", "score": 1, "weight": 1.2, "risk": "high"}, {"dimension": "economic_buyer", "score": 4, "weight": 1.5, "risk": "high"}, {"dimension": "metrics", "score": 5, "weight": 1.0, "risk": "medium"}]', 'Ask Sarah Kim to clarify procurement process and identify who has final budget authority.'
FROM accounts WHERE name = 'Apex Analytics';

INSERT INTO deals (account_id, name, stage, amount, owner, probability, deal_health_score, meddic_scores, meddic_gaps, nba_text)
SELECT id, name || ' - Q4 Pipeline', 'qualification', CASE name WHEN 'Meridian Capital Partners' THEN 5000000 WHEN 'Apex Analytics' THEN 2000000 WHEN 'NorthStar Equity Group' THEN 8000000 END, 'Jessica Ryan', 10, 30, '{"metrics": 2, "economic_buyer": 1, "decision_criteria": 3, "decision_process": 1, "identified_pain": 4, "champion": 2}', '[{"dimension": "economic_buyer", "score": 1, "weight": 1.5, "risk": "critical"}, {"dimension": "decision_process", "score": 1, "weight": 1.2, "risk": "high"}, {"dimension": "identified_pain", "score": 4, "weight": 1.5, "risk": "high"}]', 'Initial discovery needed — no champion identified, no pain quantified. Schedule exploratory call with VP level contact.'
FROM accounts WHERE name = 'NorthStar Equity Group';

INSERT INTO signals (account_id, signal_type, source, title, description, weight, detected_at)
SELECT id, 'funding', 'TechCrunch + LinkedIn Jobs', 'Series B closed $42M', 'Actively hiring VP of Operations and RevOps Lead', 3.0, '2026-05-15 09:00:00+00'
FROM accounts WHERE name = 'Meridian Capital Partners';

INSERT INTO signals (account_id, signal_type, source, title, description, weight, detected_at)
SELECT id, 'executive_change', 'LinkedIn', 'New CFO Sarah Chen (ex-Blackstone)', 'Joined 6 weeks ago. Likely driving process review.', 2.5, '2026-04-20 14:00:00+00'
FROM accounts WHERE name = 'Meridian Capital Partners';

INSERT INTO signals (account_id, signal_type, source, title, description, weight, detected_at)
SELECT id, 'hiring', 'LinkedIn Jobs', '3 open senior roles', 'VP Ops, RevOps Lead, Data Engineer — team build-out signals ops investment', 2.0, '2026-05-25 10:00:00+00'
FROM accounts WHERE name = 'Meridian Capital Partners';

INSERT INTO signals (account_id, signal_type, source, title, description, weight, detected_at)
SELECT id, 'tech_adoption', 'Clay enrichment + BuiltWith', 'No fund admin platform detected', 'Currently using Salesforce + manual Excel workflows. Greenfield opportunity.', 1.5, '2026-06-01 08:00:00+00'
FROM accounts WHERE name = 'Meridian Capital Partners';

INSERT INTO similar_deals (company, outcome, acv, days_to_close, meddic_profile, winning_patterns)
VALUES
    ('Atlas PE Partners', 'closed_won', 3100000, 94, '{"metrics": 8, "economic_buyer": 9, "decision_criteria": 7, "decision_process": 8, "identified_pain": 9, "champion": 8}', '{"key_winning_factors": ["CFO was primary sponsor from stage 2", "ROI document delivered before eval board", "Champion shared internal budget memo"], "objections_handled": ["Integration complexity mitigated with phased rollout", "Price objection addressed with 3-year TCO comparison"], "champion_strategies": ["CFO introduced CEO at stage 3 social event", "Champion ran internal lunch-and-learn without vendor present"], "average_days_to_close": 94, "eb_engaged_by_stage": 2}'),
    ('Silver Lake Portfolio Co', 'closed_won', 1800000, 76, '{"metrics": 7, "economic_buyer": 8, "decision_criteria": 8, "decision_process": 7, "identified_pain": 8, "champion": 9}', '{"key_winning_factors": ["VP Ops became executive sponsor", "Board-level pain (regulatory deadline) created urgency", "Competitor evaluation disqualified on integration"], "objections_handled": ["Switching cost justified with 18-month payback model", "Implementation disruption mitigated with parallel run"], "champion_strategies": ["Champion organized exec briefing with procurement team", "Shared competitor pricing during negotiation"], "average_days_to_close": 76, "eb_engaged_by_stage": 2}'),
    ('Bain Capital Tech', 'closed_won', 4200000, 112, '{"metrics": 9, "economic_buyer": 7, "decision_criteria": 8, "decision_process": 6, "identified_pain": 9, "champion": 7}', '{"key_winning_factors": ["Strongest pain story—LPs threatening to withdraw capital", "CFO engaged at stage 3 after champion intro", "Multi-year contract with expansion clause won board favor"], "objections_handled": ["Risk of platform migration addressed with dedicated CSM", "Integration timeline concern reduced with phased approach"], "champion_strategies": ["Champion built internal ROI calculator shared with procurement", "Provided competitive intel on incumbent pricing"], "average_days_to_close": 112, "eb_engaged_by_stage": 3}');
