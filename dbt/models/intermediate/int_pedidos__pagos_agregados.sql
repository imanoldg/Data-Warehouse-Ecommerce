-- Un pedido puede pagarse en varias lineas (voucher + tarjeta). El "tipo principal" es el
-- del pago de mayor importe.
select
    pedido_id,
    sum(importe) as importe_pagado,
    count(*) as num_pagos,
    max(cuotas) as cuotas_max,
    arg_max(tipo_pago, importe) as tipo_pago_principal
from {{ ref('stg_olist__pagos') }}
group by pedido_id
