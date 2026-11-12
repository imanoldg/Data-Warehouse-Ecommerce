select
    seller_id as vendedor_id,
    lpad(seller_zip_code_prefix, 5, '0') as codigo_postal,
    seller_city as ciudad,
    upper(seller_state) as estado
from {{ source('olist', 'olist_sellers_dataset') }}
