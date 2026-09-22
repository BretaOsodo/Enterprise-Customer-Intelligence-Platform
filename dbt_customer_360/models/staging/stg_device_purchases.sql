{{ config(materialized='table') }}

SELECT
    NULLIF(purchase_id,'')::text as purchase_id,
    NULLIF(customer_id,'')::text as customer_id,
    NULLIF(device_id,'')::text as device_id,
    NULLIF(manufacturer,'')::text as manufacturer,
    NULLIF(model,'')::text as model,
    NULLIF(purchase_date,'')::date as purchase_date,
    NULLIF(purchase_amount,'')::real as purchase_amount,
    NULLIF(payment_method,'')::text as payment_method,
    NULLIF(financing_status,'')::text as financing_status,
    NULLIF(created_at,'')::date as created_at

FROM {{ source('bronze','device_purchases') }}