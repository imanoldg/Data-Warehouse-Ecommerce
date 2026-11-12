-- Hechos a nivel de linea de pedido: la granularidad mas fina del modelo.
-- El vendedor se une "en el tiempo": la version vigente en el momento de la compra.
select
    {{ clave_surrogada(['i.pedido_id', 'i.numero_linea']) }} as item_sk,
    i.pedido_id,
    i.numero_linea,
    {{ clave_surrogada(['c.cliente_unico_id']) }} as cliente_sk,
    i.producto_id,
    v.vendedor_sk,
    cast(p.comprado_en as date) as fecha_compra,
    p.estado as estado_pedido,
    i.precio,
    i.flete,
    i.precio + i.flete as importe_total
from {{ ref('stg_olist__items_pedido') }} as i
inner join {{ ref('stg_olist__pedidos') }} as p on i.pedido_id = p.pedido_id
inner join {{ ref('stg_olist__clientes') }} as c on p.cliente_id = c.cliente_id
left join {{ ref('dim_vendedores') }} as v
    on i.vendedor_id = v.vendedor_id
    and p.comprado_en >= v.valido_desde
    and p.comprado_en < v.valido_hasta
