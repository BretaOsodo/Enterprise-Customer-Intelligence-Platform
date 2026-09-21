{{ config(materialized="table") }}
select
    customer_id::text  as customer_id,
    first_name::text as first_name,
    last_name::text as last_name,
    full_name::text as full_name,
    gender::text as gender,
    NULLIF(date_of_birth,'')::date as date_of_birth,
    phone_number::text as phone_number,
    email::text as email,
    county::text as county,
    town::text as town,
    customer_type::text as customer_type,
    NULLIF(registration_date,'')::date as registration_date,
    customer_status::text as customer_status,
    NULLIF(created_at,'')::date as created_at,
    NULLIF(updated_at,'')::date as updated_at,
    segment::text as segment


from {{ source('bronze', 'customers') }}