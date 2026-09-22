{{ config(materialized='table') }}

SELECT
    NULLIF(service_id,'')::text as service_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(business_id,'')::text as business_id,
    NULLIF(service_type,'')::text as service_type,
    NULLIF(start_date,'')::date as start_date,
    NULLIF(monthly_fee,'')::real as monthly_fee,
    NULLIF(billing_amount,'')::real as billing_amount,
    NULLIF(status,'')::text as status,
    NULLIF(contract_end_date,'')::date as contract_end_date,
    NULLIF(created_at,'')::date as created_at
FROM {{ source('bronze','enterprise_services') }}