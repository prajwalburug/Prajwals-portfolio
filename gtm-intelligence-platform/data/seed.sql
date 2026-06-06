INSERT INTO accounts (name, domain, industry, headcount, revenue_range, funding_total, funding_round, funding_date, tech_stack)
VALUES
    ('Meridian Capital Partners', 'meridiancap.com', 'Financial Services', 245, '$50M-$100M', 42000000, 'Series B', '2026-05-15', '["Salesforce", "Excel", "Slack", "Notion"]'),
    ('Apex Analytics', 'apexanalytics.io', 'SaaS - Analytics', 89, '$10M-$25M', 12000000, 'Series A', '2026-04-01', '["HubSpot", "Tableau", "Snowflake", "Slack", "Notion", "Jira"]'),
    ('NorthStar Equity Group', 'northstarequity.com', 'Financial Services - Asset Management', 512, '$100M-$250M', NULL, NULL, NULL, '["Salesforce", "Excel", "Bloomberg Terminal", "Allvue"]');

INSERT INTO deals (account_id, name, stage, amount, owner, probability)
SELECT id, name || ' - Q3 Pipeline', 'qualification', CASE name WHEN 'Meridian Capital Partners' THEN 2400000 WHEN 'Apex Analytics' THEN 600000 WHEN 'NorthStar Equity Group' THEN 5000000 END, 'Jessica Ryan', CASE name WHEN 'Meridian Capital Partners' THEN 40 WHEN 'Apex Analytics' THEN 25 WHEN 'NorthStar Equity Group' THEN 10 END
FROM accounts;

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
