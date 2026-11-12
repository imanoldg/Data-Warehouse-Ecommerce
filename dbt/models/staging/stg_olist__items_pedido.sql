select
    order_id as pedido_id,
    cast(order_item_id as integer) as numero_linea,
    product_id as producto_id,
    seller_id as vendedor_id,
    try_cast(shipping_limit_date as timestamp) as limite_envio_en,
    cast(price as decimal(10, 2)) as precio,
    cast(freight_value as decimal(10, 2)) as flete
from {{ source('olist', 'olist_order_items_dataset') }}
