-- Dimension de vendedores con historico (SCD tipo 2): una fila por VERSION de cada vendedor.
--
-- El snapshot fecha cada version cuando se detecta el cambio (hoy), pero los pedidos son de
-- 2016-2018. La primera version de cada vendedor se da por valida "desde siempre" (1900),
-- para que los pedidos antiguos encuentren la version vigente cuando se hicieron.
select
    dbt_scd_id as vendedor_sk,
    vendedor_id,
    codigo_postal,
    ciudad,
    estado,
    case
        when row_number() over (partition by vendedor_id order by valido_desde) = 1
            then timestamp '1900-01-01'
        else valido_desde
    end as valido_desde,
    valido_hasta,
    valido_hasta = timestamp '9999-12-31' as es_actual
from {{ ref('snap_vendedores') }}
