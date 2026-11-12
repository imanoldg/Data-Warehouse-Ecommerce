"""Pruebas de las consultas del dashboard contra el warehouse construido por dbt.

Necesitan haber ejecutado antes "dbt build" (la CI lo hace); si no, se omiten.
"""

import pytest

import consultas as q


@pytest.fixture(scope="module")
def con():
    if not q.RUTA_WAREHOUSE.exists():
        pytest.skip("No hay warehouse: ejecuta antes dbt build")
    conexion = q.conectar()
    yield conexion
    conexion.close()


@pytest.mark.parametrize(
    ("valor", "decimales", "esperado"),
    [(1234567, 0, "1.234.567"), (142.194, 2, "142,19"), (96.53, 1, "96,5"), (-1.89, 2, "-1,89")],
)
def test_formato_espanol(valor, decimales, esperado):
    assert q.num(valor, decimales) == esperado


def test_kpis(con):
    k = q.kpis(con)
    assert k.pedidos > 0
    assert 1 <= k.nota_media <= 5
    assert 0 <= k.pct_a_tiempo <= 100


def test_las_ventas_mensuales_cuadran_con_los_hechos(con):
    mensual = q.ventas_mensuales(con).ventas.sum()
    hechos = con.sql(
        "select sum(precio) from core.fct_items_pedido "
        "where estado_pedido not in ('canceled', 'unavailable')"
    ).fetchall()[0][0]
    assert float(mensual) == pytest.approx(float(hechos))


def test_nota_por_puntualidad(con):
    notas = q.nota_por_puntualidad(con)
    assert set(notas.entrega) == {"A tiempo", "Con retraso"}


def test_el_resto_de_consultas_devuelve_datos(con):
    assert len(q.top_categorias(con, 5)) == 5
    assert len(q.entregas_por_estado(con)) > 0
    assert len(q.calidad_datos(con)) == 4
