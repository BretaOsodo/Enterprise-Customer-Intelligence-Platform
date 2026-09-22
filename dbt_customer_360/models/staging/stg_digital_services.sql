{{ config(materialized='table') }}

SELECT
    NULLIF(subscription_id,'')::text as subscription_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(service_type,'')::text as service_type,
    NULLIF(subscription_date,'')::date as subscription_date,
    NULLIF(monthly_fee,'')::real as monthly_fee,
    NULLIF(usage_count,'')::real as usage_count,
    NULLIF(status,'')::text as status,
    NULLIF(last_activity_date,'')::date as last_activity_date,
    NULLIF(created_at,'')::date as created_at,
    NULLIF(updated_at,'')::date as updated_at
FROM {{ source('bronze','digital_services') }}