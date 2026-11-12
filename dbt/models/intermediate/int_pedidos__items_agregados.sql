-- Totales de cada pedido a partir de sus lineas.
select
    pedido_id,
    count(*) as num_items,
    count(distinct producto_id) as num_productos,
    count(distinct vendedor_id) as num_vendedores,
    sum(precio) as valor_productos,
    sum(flete) as valor_flete,
    sum(precio + flete) as importe_total
from {{ ref('stg_olist__items_pedido') }}
group by pedido_id
