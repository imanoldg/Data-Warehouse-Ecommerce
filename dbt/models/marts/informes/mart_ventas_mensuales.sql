-- Ventas por mes y categoria. Excluye pedidos cancelados o no disponibles.
select
    d.anio_mes,
    pr.categoria_en as categoria,
    count(distinct f.pedido_id) as num_pedidos,
    count(*) as unidades,
    sum(f.precio) as ventas,
    sum(f.flete) as flete,
    round(sum(f.precio) / count(distinct f.pedido_id), 2) as ticket_medio
from {{ ref('fct_items_pedido') }} as f
inner join {{ ref('dim_fechas') }} as d on f.fecha_compra = d.fecha
inner join {{ ref('dim_productos') }} as pr on f.producto_id = pr.producto_id
where f.estado_pedido not in ('canceled', 'unavailable')
group by d.anio_mes, pr.categoria_en
