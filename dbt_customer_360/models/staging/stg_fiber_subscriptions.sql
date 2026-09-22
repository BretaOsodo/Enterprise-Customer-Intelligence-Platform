{{ config(materialized='table') }}

SELECT
    NULLIF(subscription_id,'')::text as subscription_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(plan_id,'')::text as plan_id,
    NULLIF(plan_name,'')::text as plan_name,
    NULLIF(installation_date,'')::date as installation_date,
    NULLIF(monthly_fee,'')::real as monthly_fee,
    NULLIF(speed_mbps,'')::real as speed_mbps,
    NULLIF(status,'')::text as status,
    NULLIF(contract_end_date,'')::date as contract_end_date,
    NULLIF(created_at,'')::date as created_at,
    NULLIF(updated_at,'')::date as updated_at
FROM {{ source('bronze','fiber_subscriptions') }}