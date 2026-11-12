-- La pregunta de negocio: ¿cuanto baja la nota de un cliente cuando el pedido llega tarde?
-- Solo pedidos entregados, agrupados por el estado (region) del cliente.
select
    c.estado,
    count(*) as pedidos_entregados,
    round(avg(f.dias_hasta_entrega), 1) as dias_entrega_medio,
    round(100.0 * avg(cast(f.entregado_a_tiempo as integer)), 1) as pct_a_tiempo,
    round(avg(f.nota_resena), 2) as nota_media,
    round(avg(f.nota_resena) filter (where f.entregado_a_tiempo), 2) as nota_media_a_tiempo,
    round(avg(f.nota_resena) filter (where not f.entregado_a_tiempo), 2) as nota_media_con_retraso
from {{ ref('fct_pedidos') }} as f
inner join {{ ref('dim_clientes') }} as c on f.cliente_sk = c.cliente_sk
where f.es_entregado
group by c.estado
