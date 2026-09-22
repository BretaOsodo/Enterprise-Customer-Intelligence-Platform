{{ config(materialized='view',
    indexes=[
    {'columns': ['credit_account_id','customer_id'], 'unique':True},
    {'columns':['customer_id','credit_limit','status','opened_date','product_type','due_date'],'type':'btree'}
    ])
 }}

with cleaned_columns as(
select
	credit_account_id,
	customer_id,
	credit_limit::decimal(20,2) as credit_limit,
	amount_borrowed::decimal(20,2) as amount_borrowed,
	amount_repaid::decimal(20,2) as amount_repaid,
	outstanding_balance::decimal(20,2) as outstanding_balance,
	interest_rate::decimal(5,2) as interest_rate,
	opened_date,
	due_date,
	case
		WHEN status ='NONE' THEN NULL
		WHEN status='???' THEN NULL
		WHEN status='INVALID' THEN NULL
		WHEN status  ='N/A' THEN NULL
		WHEN status = 'UNKOWN' THEN NULL
	ELSE lower(status)
	END as status,
	created_at,
	updated_at,
	case
		when product_type='NONE' THEN NULL
		when product_type='N/A' THEN NULL
		when product_type='INVALID' THEN NULL
		WHEN product_type='???' THEN NULL
	ELSE lower(product_type)
	END as product_type
FROM {{ ref('stg_credit_accounts') }}
),
deduped_data as (
select
	*
FROM (
select
	*,
	ROW_NUMBER() OVER(PARTITION BY credit_account_id ORDER BY created_at) as flag_ship
FROM cleaned_columns
) t
WHERE flag_ship = 1 and customer_id NOT LIKE ('INVALID%')
)

SELECT
    credit_account_id,
    customer_id,
    credit_limit,
    product_type,
    amount_borrowed,
    amount_repaid,
    outstanding_balance,
    interest_rate,
    opened_date,
    due_date,
    status,
    created_at,
    updated_at
FROM deduped_data