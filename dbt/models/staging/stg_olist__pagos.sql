select
    order_id as pedido_id,
    cast(payment_sequential as integer) as secuencia,
    payment_type as tipo_pago,
    cast(payment_installments as integer) as cuotas,
    cast(payment_value as decimal(10, 2)) as importe
from {{ source('olist', 'olist_order_payments_dataset') }}
