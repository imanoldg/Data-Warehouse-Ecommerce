-- customer_id es distinto en cada pedido: el cliente real es customer_unique_id.
-- Los codigos postales vienen como numeros y pierden el cero inicial (1037 -> 01037).
select
    customer_id as cliente_id,
    customer_unique_id as cliente_unico_id,
    lpad(customer_zip_code_prefix, 5, '0') as codigo_postal,
    customer_city as ciudad,
    upper(customer_state) as estado
from {{ source('olist', 'olist_customers_dataset') }}
