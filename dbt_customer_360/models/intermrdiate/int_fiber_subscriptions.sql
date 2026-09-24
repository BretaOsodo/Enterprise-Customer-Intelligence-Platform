{{ config(materialized='view') }}
WITH dedupe AS (
	SELECT *
	FROM (
		SELECT *,
				ROW_NUMBER() OVER (PARTITION BY subscription_id ORDER BY created_at) AS flag_ship
		FROM {{ ref('stg_fiber_subscriptions') }}
	)t WHERE flag_ship=1
),
cleaned_data as(
	SELECT
		subscription_id,
		customer_id,
		CASE
			WHEN plan_id ='UNKNOWN' THEN NULL
			WHEN plan_id='INVALID' THEN NULL
		ELSE plan_id
		END,
		plan_name,
		installation_date,
		(CASE WHEN monthly_fee < 0 THEN NULL ELSE monthly_fee END)::decimal(10,2) as monthly_fee,
		(CASE WHEN monthly_fee < 0 THEN NULL ELSE speed_mbps END)::decimal(10,2) as speed_mbps,
		INITCAP(TRIM(status)),
		contract_end_date,
		created_at,
		updated_at
	FROM dedupe

)
SELECT * FROM cleaned_data
WHERE subscription_id IS NOT NULL AND customer_id IS NOT NULL