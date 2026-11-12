-- Las versiones de un vendedor no pueden solaparse: si lo hicieran, una linea de pedido
-- podria unirse a dos versiones a la vez y duplicar las ventas.
select a.vendedor_id, a.vendedor_sk, b.vendedor_sk as solapa_con
from {{ ref('dim_vendedores') }} as a
inner join {{ ref('dim_vendedores') }} as b
    on a.vendedor_id = b.vendedor_id
    and a.vendedor_sk < b.vendedor_sk
    and a.valido_desde < b.valido_hasta
    and b.valido_desde < a.valido_hasta
