{{ config(materialized='table') }}

SELECT
    NULLIF(usage_id,'')::text as usage_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(subscription_id,'')::text as subscription_id,
    NULLIF(usage_date,'')::date as usage_date,
    NULLIF(data_used_gb,'')::real as data_used_gb,
    NULLIF(session_count,'')::int as session_count,
    NULLIF(uptime_hours,'')::real as uptime_hours,
    NULLIF(created_at,'')::date as created_at
FROM {{ source('bronze','fiber_usage')}}