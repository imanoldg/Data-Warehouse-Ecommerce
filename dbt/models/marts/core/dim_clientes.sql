-- Un cliente real por fila (customer_unique_id), no un customer_id por pedido.
-- Si se ha mudado, la ubicacion es la de su ultimo pedido.
with por_pedido as (

    select
        c.cliente_unico_id,
        c.codigo_postal,
        c.ciudad,
        c.estado,
        p.pedido_id,
        p.comprado_en
    from {{ ref('stg_olist__clientes') }} as c
    left join {{ ref('stg_olist__pedidos') }} as p on c.cliente_id = p.cliente_id

)

select
    {{ clave_surrogada(['cliente_unico_id']) }} as cliente_sk,
    cliente_unico_id,
    arg_max(codigo_postal, comprado_en) as codigo_postal,
    arg_max(ciudad, comprado_en) as ciudad,
    arg_max(estado, comprado_en) as estado,
    cast(min(comprado_en) as date) as primera_compra,
    cast(max(comprado_en) as date) as ultima_compra,
    count(pedido_id) as num_pedidos,
    count(pedido_id) > 1 as es_recurrente
from por_pedido
group by cliente_unico_id
