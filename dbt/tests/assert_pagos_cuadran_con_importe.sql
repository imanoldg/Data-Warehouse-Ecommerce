-- Aviso si un pedido se ha pagado por un importe distinto del de sus productos + flete
-- (mas de 1 real de diferencia). En el dataset real pasa en algunos pedidos, por
-- redondeos y vouchers, asi que avisa en lugar de parar el pipeline.
{{ config(severity='warn') }}

select pedido_id, importe_total, importe_pagado
from {{ ref('fct_pedidos') }}
where importe_pagado is not null
  and num_items > 0
  and abs(importe_pagado - importe_total) > 1
