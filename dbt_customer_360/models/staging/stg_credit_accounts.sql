{{ config(materialized='table') }}

select
    NULLIF(credit_account_id,'')::text                     as credit_account_id,
    NULLIF(customer_id,'')::text                           as customer_id,
    NULLIF(product_type,'')::text                          as product_type,
    NULLIF(credit_limit, '')::real              as credit_limit,
    NULLIF(amount_borrowed, '')::real           as amount_borrowed,
    NULLIF(amount_repaid, '')::real             as amount_repaid,
    NULLIF(outstanding_balance, '')::real       as outstanding_balance,
    NULLIF(interest_rate, '')::real             as interest_rate,
    NULLIF(opened_date, '')::date               as opened_date,
    NULLIF(due_date, '')::date                  as due_date,
    NULLIF(status,'')::text                                as status,
    NULLIF(created_at, '')::date                as created_at,
    NULLIF(updated_at, '')::date                as updated_at

from {{ source('bronze', 'credit_accounts') }}
