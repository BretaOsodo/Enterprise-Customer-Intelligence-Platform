{{ config(materialized='view')
 }}
-- dedupe the data
WITH dedupe AS(
    SELECT *
    FROM (
        SELECT *,
            ROW_NUMBER () OVER (PARTITION BY customer_id ORDER BY created_at) AS flag_ship
        FROM {{ ref('stg_customers') }}
        WHERE customer_id IS NOT NULL
    ) t WHERE flag_ship = 1
),
nullifying_the_data as(
	select
		nullif(customer_id,'') as customer_id,
		nullif(first_name,'') as first_name,
		nullif(last_name,'') as last_name,
		nullif(full_name,'')as full_name,
		nullif(gender,'') as gender,
		date_of_birth,
		nullif(phone_number,'') as phone_number,
		nullif(email,'') as email,
		nullif(county,'') as county,
		nullif(town,'') as town,
		nullif(customer_type,'') as customer_type,
		registration_date,
		nullif(customer_status,'') as customer_status,
		created_at,
		updated_at,
		flag_ship
	from dedupe
),
masking_email as(
select *,
    case
        when email is null or email='' then null
        when position('@' in email) =0 then null -- no@ at all, malformed
        else left(email,2) || '***@' || split_part(email,'@',2)
    end as email_masked
from nullifying_the_data
),
removing_null as (
SELECT
    customer_id,
    first_name,
    last_name,
    full_name,
    INITCAP (case
		when gender='F' then 'Female'
		when gender ='M' then 'Male'
	else gender
	end) as gender,
    date_of_birth,
    phone_number,
    email,
    county,
    town,
    INITCAP(case
		when customer_type='???' then null
		when customer_type='INVALID' then null
		when customer_type='N/A' then null
		when customer_type='NONE' then null
		when customer_type='UNKNOWN' then null
	else customer_type
	end) as customer_type,
	registration_date,
	INITCAP(case
 	when customer_status ='???' then null
	 when customer_status='INVALID' then null
	 when customer_status='N/A' then null
	 when customer_status='NONE' then null
	 when customer_status= 'UNKNOWN' then null
	else customer_status
	end) as customer_status,
    created_at,
    updated_at,
    email_masked
FROM masking_email
WHERE customer_id IS NOT NULL
)
SELECT * FROM removing_null