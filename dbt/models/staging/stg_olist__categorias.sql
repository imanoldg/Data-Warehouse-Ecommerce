select
    product_category_name as categoria,
    product_category_name_english as categoria_en
from {{ source('olist', 'product_category_name_translation') }}
