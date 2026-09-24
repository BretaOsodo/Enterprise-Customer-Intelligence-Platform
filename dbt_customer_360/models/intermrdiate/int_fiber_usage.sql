{{ config(materialized='view') }}

-- dedupe the data to remove duplicates
WITH dedupe AS(
	SELECT *
	FROM (
			SELECT
				*,
				ROW_NUMBER() OVER(PARTITION BY usage_id ORDER BY created_at) AS flag_ship
			FROM {{ ref('stg_fiber_usage')}}
	)t
	WHERE flag_ship =1
),
-- cleaned data
cleaned_data AS (
	SELECT
		usage_id,
		customer_id,
		subscription_id,
		usage_date,
		(CASE WHEN data_used_gb < 0 THEN NULL ELSE data_used_gb END),
		CASE WHEN session_count < 0 THEN NULL ELSE session_count END,
		CASE WHEN uptime_hours < 0 THEN NULL ELSE uptime_hours END,
		created_at,
		CURRENT_DATE::date AS updated_at
	FROM dedupe
)
SELECT * FROM cleaned_data
WHERE usage_id IS NOT NULL  AND subscription_id IS NOT NULL AND customer_id IS NOT NULL