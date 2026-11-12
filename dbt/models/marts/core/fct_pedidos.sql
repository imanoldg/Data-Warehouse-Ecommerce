-- Hechos a nivel de pedido: importes, pago, resena y entrega.
with pedidos as (

    select
        p.*,
        c.cliente_unico_id,
        p.estado = 'delivered' and p.entregado_en is not null as es_entregado
    from {{ ref('stg_olist__pedidos') }} as p
    inner join {{ ref('stg_olist__clientes') }} as c on p.cliente_id = c.cliente_id

)

select
    p.pedido_id,
    {{ clave_surrogada(['p.cliente_unico_id']) }} as cliente_sk,
    cast(p.comprado_en as date) as fecha_compra,
    p.estado,
    cast(coalesce(i.num_items, 0) as integer) as num_items,
    cast(coalesce(i.valor_productos, 0) as decimal(12, 2)) as valor_productos,
    cast(coalesce(i.valor_flete, 0) as decimal(12, 2)) as valor_flete,
    cast(coalesce(i.importe_total, 0) as decimal(12, 2)) as importe_total,
    cast(pg.importe_pagado as decimal(12, 2)) as importe_pagado,
    pg.tipo_pago_principal,
    cast(pg.cuotas_max as integer) as cuotas_max,
    cast(r.nota as integer) as nota_resena,
    p.es_entregado,
    cast(case when p.es_entregado then date_diff('day', p.comprado_en, p.entregado_en) end
        as integer) as dias_hasta_entrega,
    cast(case
        when p.es_entregado
            then greatest(date_diff('day', p.fecha_estimada_entrega, cast(p.entregado_en as date)), 0)
    end as integer) as dias_retraso,
    case
        when p.es_entregado then cast(p.entregado_en as date) <= p.fecha_estimada_entrega
    end as entregado_a_tiempo
from pedidos as p
left join {{ ref('int_pedidos__items_agregados') }} as i on p.pedido_id = i.pedido_id
left join {{ ref('int_pedidos__pagos_agregados') }} as pg on p.pedido_id = pg.pedido_id
left join {{ ref('stg_olist__resenas') }} as r on p.pedido_id = r.pedido_id
