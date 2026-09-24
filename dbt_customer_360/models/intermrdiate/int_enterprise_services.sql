{{ config(materialized='view') }}
WITH dedupe AS (
	SELECT *
	FROM (
		SELECT *,
				ROW_NUMBER() OVER (PARTITION BY service_id ORDER BY created_at) AS flag_ship
		FROM {{ ref('stg_enterprise_services') }}
	)t WHERE flag_ship=1
),
cleaned_data AS(
	SELECT
		service_id,
		customer_id,
		business_id,
		INITCAP(TRIM(CASE
			WHEN service_type='???' THEN NULL
			WHEN service_type='N/A' THEN NULL
			WHEN service_type='INVALID' THEN NULL
			WHEN service_type='NONE' THEN NULL
			WHEN service_type='UNKNOWN' THEN NULL
		ELSE service_type
		END)),
		start_date,
		(CASE WHEN monthly_fee < 0 THEN NULL ELSE monthly_fee END)::decimal(10,2) AS monthly_fee,
		(CASE WHEN monthly_fee < 0 THEN NULL ELSE billing_amount END)::decimal(10,2) AS billing_amount,
		INITCAP(TRIM(status)) AS status,
		contract_end_date,
		created_at,
		'{{ run_started_at }}'::date as updated_at
	FROM dedupe
)

SELECT * FROM cleaned_data
WHERE service_id IS NOT NULL AND customer_id IS NOT NULL
