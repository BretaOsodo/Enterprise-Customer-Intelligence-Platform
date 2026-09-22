{{ config(materialized='table') }}

SELECT
    NULLIF(transaction_id,'')::text as transaction_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(transaction_type,'')::text as transaction_type,
    NULLIF(transaction_date,'')::text as transaction_date,
    NULLIF(amount,'')::real as amount,
    NULLIF(fee,'')::real as fee,
    NULLIF(balance_before,'')::real as balance_before,
    NULLIF(counterparty_id,'')::text as counterparty_id,
    NULLIF(merchant_id,'')::text as merchant_id,
    NULLIF(channel,'')::text as channel,
    NULLIF(transaction_status,'')::text as transaction_status,
    NULLIF(location,'')::text as location,
    NULLIF(created_at,'')::date as created_at
FROM {{ source('bronze','financial_transactions')}}