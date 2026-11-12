select
    order_id as pedido_id,
    customer_id as cliente_id,
    order_status as estado,
    try_cast(order_purchase_timestamp as timestamp) as comprado_en,
    try_cast(order_approved_at as timestamp) as aprobado_en,
    try_cast(order_delivered_carrier_date as timestamp) as enviado_en,
    try_cast(order_delivered_customer_date as timestamp) as entregado_en,
    try_cast(order_estimated_delivery_date as timestamp)::date as fecha_estimada_entrega
from {{ source('olist', 'olist_orders_dataset') }}
