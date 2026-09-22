{{ config(materialized='table') }}

SELECT
    NULLIF(usage_id,'')::text as usage_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(msisdn,'')::text as phone_number,
    NULLIF(usage_type,'')::text as usage_type,
    NULLIF(usage_date,'')::date as usage_date,
    NULLIF(start_time,'')::time as start_time,
    NULLIF(duration_seconds,'')::real as duration_seconds,
    NULLIF(sms_count,'')::int as sms_count,
    NULLIF(amount,'')::real as amount,
    NULLIF(plan_type,'')::text as plan_type,
    NULLIF(network_type,'')::text as network_type,
    NULLIF(cell_tower_id,'')::text as cell_tower_id,
    NULLIF(created_at,'')::date as created_at
FROM {{ source('bronze','mobile_usage')}}