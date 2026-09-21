{{ config(materialized='view') }}

WITH dedupe AS(
    SELECT *
    FROM (
        SELECT *,
            ROW_NUMBER () OVER (PARTITION BY credit_account_id ORDER BY created_at) AS flag_ship
        FROM {{ ref('stg_credit_accounts') }}
        WHERE customer_id IS NOT NULL
    ) t WHERE flag_ship = 1
),
removing_null as(
SELECT *
FROM dedupe
where customer_id IS NOT NULL
),
clean_data as(
SELECT
	credit_account_id,
	customer_id,
	product_type,
	credit_limit,
	amount_borrowed,
	amount_repaid,
	outstanding_balance,
	interest_rate,
	opened_date,
	due_date,
	status,
	created_at,
	updated_at

FROM removing_null
)
select * from clean_data