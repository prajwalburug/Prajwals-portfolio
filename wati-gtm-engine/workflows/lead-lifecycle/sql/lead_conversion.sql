-- Lead Conversion Analysis
-- Tracks source-to-meeting conversion rates over time
-- Run against HubSpot data exported to SQL

WITH lead_sources AS (
    SELECT
        c.id AS contact_id,
        COALESCE(c.lead_source, c.hs_analytics_source, 'unknown') AS source,
        c.created_at AS lead_created_at,
        icp.total_score AS qualification_score,
        icp.classification
    FROM contacts c
    LEFT JOIN contact_icp_scores icp ON c.id = icp.contact_id
    WHERE c.created_at >= DATEADD('month', -3, CURRENT_DATE)
),

meetings AS (
    SELECT
        m.contact_id,
        MIN(m.meeting_date) AS first_meeting_date
    FROM meetings m
    GROUP BY m.contact_id
),

source_metrics AS (
    SELECT
        ls.source,
        COUNT(DISTINCT ls.contact_id) AS total_leads,
        COUNT(DISTINCT ls.contact_id) FILTER (
            WHERE ls.classification = 'HOT'
        ) AS hot_leads,
        COUNT(DISTINCT ls.contact_id) FILTER (
            WHERE ls.classification IN ('WARM', 'NURTURE')
        ) AS warm_nurture_leads,
        COUNT(DISTINCT ls.contact_id) FILTER (
            WHERE m.first_meeting_date IS NOT NULL
        ) AS leads_with_meetings,
        ROUND(
            COUNT(DISTINCT ls.contact_id) FILTER (
                WHERE m.first_meeting_date IS NOT NULL
            ) * 100.0 / NULLIF(COUNT(DISTINCT ls.contact_id), 0),
            1
        ) AS conversion_rate_pct,
        ROUND(
            AVG(DATEDIFF('day', ls.lead_created_at, m.first_meeting_date)),
            1
        ) AS avg_days_to_meeting
    FROM lead_sources ls
    LEFT JOIN meetings m ON ls.contact_id = m.contact_id
    GROUP BY ls.source
)

SELECT
    source,
    total_leads,
    hot_leads,
    warm_nurture_leads,
    leads_with_meetings,
    conversion_rate_pct,
    CASE
        WHEN avg_days_to_meeting IS NULL THEN 'N/A'
        ELSE CAST(avg_days_to_meeting AS VARCHAR) || ' days'
    END AS avg_days_to_meeting,
    ROUND(
        100.0 * hot_leads / NULLIF(total_leads, 0),
        1
    ) AS pct_hot_leads,
    CASE
        WHEN total_leads > 0 AND conversion_rate_pct IS NOT NULL
        THEN RANK() OVER (ORDER BY conversion_rate_pct DESC)
        ELSE NULL
    END AS conversion_rank
FROM source_metrics
ORDER BY total_leads DESC;

-- Qualification Score Distribution
SELECT
    CASE
        WHEN qualification_score >= 70 THEN 'HOT (70-100)'
        WHEN qualification_score >= 40 THEN 'WARM (40-69)'
        WHEN qualification_score >= 10 THEN 'NURTURE (10-39)'
        ELSE 'DISQUALIFIED (<10)'
    END AS score_tier,
    COUNT(*) AS lead_count,
    ROUND(AVG(qualification_score), 1) AS avg_score,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(),
        1
    ) AS pct_of_total
FROM contact_icp_scores
WHERE created_at >= DATEADD('month', -3, CURRENT_DATE)
GROUP BY 1
ORDER BY MIN(qualification_score) DESC;

-- Source Quality Index
SELECT
    source,
    total_leads,
    conversion_rate_pct,
    avg_days_to_meeting,
    ROUND(conversion_rate_pct / NULLIF(avg_days_to_meeting, 0), 2) AS quality_index
FROM source_metrics
WHERE total_leads >= 5
ORDER BY quality_index DESC;
