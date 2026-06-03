-- Pipeline Velocity & Conversion Analysis
-- Tracks deal progression speed and stage-to-stage conversion rates
-- Run against HubSpot data exported to SQL

WITH stage_transitions AS (
    SELECT
        d.id AS deal_id,
        d.deal_name,
        d.amount,
        d.stage,
        d.created_at AS deal_created,
        d.closed_at AS deal_closed,
        hs.stage_name,
        hs.entered_at,
        hs.exited_at,
        DATEDIFF('day', hs.entered_at, COALESCE(hs.exited_at, CURRENT_DATE)) AS days_in_stage
    FROM deals d
    LEFT JOIN deal_stage_history hs ON d.id = hs.deal_id
    WHERE d.created_at >= DATEADD('month', -6, CURRENT_DATE)
),

stage_velocity AS (
    SELECT
        stage_name,
        COUNT(DISTINCT deal_id) AS deals_entered,
        COUNT(DISTINCT deal_id) FILTER (WHERE exited_at IS NOT NULL) AS deals_exited,
        ROUND(AVG(days_in_stage), 1) AS avg_days_in_stage,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_in_stage), 1) AS median_days_in_stage,
        MIN(days_in_stage) AS min_days,
        MAX(days_in_stage) AS max_days,
        COUNT(DISTINCT deal_id) FILTER (WHERE days_in_stage > 30) AS stale_deals
    FROM stage_transitions
    GROUP BY stage_name
),

conversion_funnel AS (
    SELECT
        stage_name,
        deals_entered,
        LAG(deals_entered) OVER (ORDER BY MIN(stage_order)) AS deals_in_previous_stage,
        ROUND(
            100.0 * deals_entered / NULLIF(LAG(deals_entered) OVER (ORDER BY MIN(stage_order)), 0),
            1
        ) AS conversion_rate_pct
    FROM (
        SELECT
            stage_name,
            COUNT(DISTINCT deal_id) AS deals_entered,
            CASE stage_name
                WHEN 'discovery' THEN 1
                WHEN 'qualification' THEN 2
                WHEN 'demo' THEN 3
                WHEN 'proposal' THEN 4
                WHEN 'negotiation' THEN 5
                WHEN 'closed_won' THEN 6
                WHEN 'closed_lost' THEN 7
                ELSE 99
            END AS stage_order
        FROM stage_transitions
        GROUP BY stage_name
    ) sub
    GROUP BY stage_name, deals_entered
)

-- Pipeline Velocity by Stage
SELECT
    '--- Pipeline Velocity (Days in Stage) ---' AS report_section;

SELECT
    stage_name,
    deals_entered,
    avg_days_in_stage,
    median_days_in_stage,
    stale_deals,
    ROUND(100.0 * stale_deals / NULLIF(deals_entered, 0), 1) AS pct_stale
FROM stage_velocity
ORDER BY avg_days_in_stage DESC;

-- Stage Conversion Funnel
SELECT '--- Stage Conversion Funnel ---' AS report_section;

SELECT
    stage_name,
    deals_entered,
    conversion_rate_pct || '%' AS conversion_from_previous
FROM conversion_funnel
ORDER BY
    CASE stage_name
        WHEN 'discovery' THEN 1
        WHEN 'qualification' THEN 2
        WHEN 'demo' THEN 3
        WHEN 'proposal' THEN 4
        WHEN 'negotiation' THEN 5
        WHEN 'closed_won' THEN 6
        WHEN 'closed_lost' THEN 7
        ELSE 99
    END;

-- At-Risk Deal Summary
SELECT '--- Currently At-Risk Deals ---' AS report_section;

SELECT
    d.deal_name,
    d.amount,
    d.stage,
    sv.avg_days_in_stage AS stage_avg_days,
    hs.days_in_stage AS deal_days_in_stage,
    ROUND(hs.days_in_stage - sv.avg_days_in_stage, 1) AS days_over_average,
    CASE
        WHEN hs.days_in_stage > sv.avg_days_in_stage * 1.5 THEN 'HIGH'
        WHEN hs.days_in_stage > sv.avg_days_in_stage THEN 'MEDIUM'
        ELSE 'LOW'
    END AS velocity_risk
FROM stage_transitions hs
JOIN stage_velocity sv ON hs.stage_name = sv.stage_name
JOIN deals d ON hs.deal_id = d.id
WHERE hs.exited_at IS NULL
    AND hs.days_in_stage > sv.avg_days_in_stage
ORDER BY days_over_average DESC
LIMIT 20;

-- Pipeline Health Summary
SELECT '--- Pipeline Health Summary ---' AS report_section;

SELECT
    COUNT(DISTINCT d.id) AS total_open_deals,
    ROUND(SUM(d.amount), 0) AS total_pipeline_value,
    ROUND(AVG(d.amount), 0) AS avg_deal_size,
    ROUND(AVG(pr.risk_score), 1) AS avg_risk_score,
    COUNT(DISTINCT d.id) FILTER (WHERE pr.risk_level = 'HIGH') AS high_risk_deals,
    COUNT(DISTINCT d.id) FILTER (WHERE pr.risk_level = 'MEDIUM') AS medium_risk_deals,
    COUNT(DISTINCT d.id) FILTER (WHERE pr.risk_level = 'LOW') AS low_risk_deals
FROM deals d
LEFT JOIN pipeline_risk_scores pr ON d.id = pr.deal_id
WHERE d.stage NOT IN ('closed_won', 'closed_lost');
