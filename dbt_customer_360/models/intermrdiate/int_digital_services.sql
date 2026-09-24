{{ config(materialized='view')}}
with dedupe as (
select *
FROM (
	SELECT *,
		ROW_NUMBER() OVER (PARTITION BY subscription_id ORDER BY created_at) AS flag_ship
	FROM {{ ref('stg_digital_services') }}
)t where flag_ship=1
),
cleaned_data as (
	SELECT
		subscription_id,
		customer_id,
		INITCAP(TRIM(CASE
			WHEN service_type ='NONE' THEN NULL
			WHEN service_type='???' THEN NULL
			WHEN service_type='N/A' THEN NULL
			WHEN service_type='INVALID' THEN NULL
		ELSE service_type
		END )),
		subscription_date,
		(CASE WHEN monthly_fee < 0 THEN NULL ELSE monthly_fee END)::decimal(10,2) as monthly_fee,
		(CASE WHEN usage_count < 0 THEN NULL ELSE usage_count END )::INT as usage_count,
		INITCAP(TRIM(status)) as status,
		last_activity_date,
		created_at,
		updated_at
	FROM dedupe

)
select * from cleaned_data
WHERE subscription_id IS NOT NULL AND customer_id IS NOT NULL
