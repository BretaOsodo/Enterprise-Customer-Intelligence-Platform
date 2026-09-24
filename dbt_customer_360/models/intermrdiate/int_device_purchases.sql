{{ config(materialized='view') }}

with dedupe as (
    select *
    from (
        select
            *,
            row_number() over (partition by device_id order by created_at) as flag_ship
        from {{ ref('stg_device_purchases') }}
    ) t
    where flag_ship = 1
)

select
    device_id,
    customer_id,
    INITCAP(manufacturer) as manufacturer,
    model,
    purchase_date,
    purchase_amount::decimal(10,2) as purchase_amount,
    INITCAP(TRIM(payment_method)) AS payment_method,
    INITCAP(financing_status) AS financial_status,
    created_at,
    '{{ run_started_at }}'::date as updated_at
from dedupe
where device_id is not null and customer_id is not null