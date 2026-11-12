"""Consultas del dashboard sobre el warehouse de DuckDB.

Estan separadas de la interfaz para poder probarlas con pytest sin abrir Streamlit.
Cada funcion recibe una conexion de DuckDB y devuelve un DataFrame de pandas.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RUTA_WAREHOUSE = Path(os.environ.get("DUCKDB_PATH", RAIZ / "data" / "warehouse.duckdb"))
PEDIDOS_VALIDOS = "estado not in ('canceled', 'unavailable')"


def num(valor: float, decimales: int = 0) -> str:
    """Formato espanol: punto de miles y coma decimal (1.234,56)."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def conectar(ruta: Path = RUTA_WAREHOUSE) -> duckdb.DuckDBPyConnection:
    # Solo lectura: el dashboard nunca modifica el warehouse, y asi no lo bloquea.
    return duckdb.connect(str(ruta), read_only=True)


def kpis(con: duckdb.DuckDBPyConnection) -> pd.Series:
    return (
        con.sql(f"""
        select
            count(*) as pedidos,
            sum(valor_productos) as ventas,
            sum(valor_productos) / count(*) as ticket_medio,
            avg(nota_resena) as nota_media,
            100.0 * avg(cast(entregado_a_tiempo as integer)) as pct_a_tiempo
        from core.fct_pedidos
        where {PEDIDOS_VALIDOS}
    """)
        .df()
        .iloc[0]
    )


def ventas_mensuales(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.sql("""
        select anio_mes as mes, sum(ventas) as ventas, sum(num_pedidos) as pedidos
        from informes.mart_ventas_mensuales
        group by anio_mes
        order by anio_mes
    """).df()


def top_categorias(con: duckdb.DuckDBPyConnection, n: int = 10) -> pd.DataFrame:
    return con.sql(f"""
        select categoria, sum(ventas) as ventas
        from informes.mart_ventas_mensuales
        group by categoria
        order by ventas desc
        limit {int(n)}
    """).df()


def nota_por_puntualidad(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.sql("""
        select
            case when entregado_a_tiempo then 'A tiempo' else 'Con retraso' end as entrega,
            count(*) as pedidos,
            avg(nota_resena) as nota_media
        from core.fct_pedidos
        where es_entregado and nota_resena is not null
        group by entrega
        order by entrega
    """).df()


def entregas_por_estado(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.sql("""
        select *
        from informes.mart_entregas_por_estado
        order by pedidos_entregados desc
    """).df()


def calidad_datos(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Problemas conocidos del dataset y cuantas filas afecta cada uno."""
    return con.sql("""
        select 'Pedidos "delivered" sin fecha de entrega' as problema, count(*) as filas
        from staging.stg_olist__pedidos
        where estado = 'delivered' and entregado_en is null
        union all
        select 'Productos sin categoria', count(*)
        from core.dim_productos where categoria = 'sin_categoria'
        union all
        select 'Clientes con mas de un customer_id (recurrentes)', count(*)
        from core.dim_clientes where es_recurrente
        union all
        select 'Vendedores con mas de una version (SCD2)', count(*)
        from (select vendedor_id from core.dim_vendedores group by 1 having count(*) > 1)
    """).df()
