"""Dashboard de ventas y entregas del e-commerce.

streamlit run app/dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consultas as q  # noqa: E402
from consultas import num  # noqa: E402

st.set_page_config(page_title="E-commerce: ventas y entregas", layout="wide")


@st.cache_resource
def conexion():
    return q.conectar()


if not q.RUTA_WAREHOUSE.exists():
    st.error(
        f"No encuentro el warehouse en `{q.RUTA_WAREHOUSE}`. "
        "Ejecuta antes `dbt build` (mira el README)."
    )
    st.stop()

con = conexion()

st.title("E-commerce: ventas y entregas")
st.caption("Datos de Olist (Brasil, 2016-2018). Importes en reales brasilenos (BRL).")

k = q.kpis(con)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Pedidos", num(k.pedidos))
c2.metric("Ventas", f"R$ {num(k.ventas)}")
c3.metric("Ticket medio", f"R$ {num(k.ticket_medio, 2)}")
c4.metric("Nota media", f"{num(k.nota_media, 2)} / 5")
c5.metric("Entregados a tiempo", f"{num(k.pct_a_tiempo, 1)} %")

izq, der = st.columns(2)
with izq:
    st.subheader("Ventas por mes")
    st.line_chart(q.ventas_mensuales(con), x="mes", y="ventas", y_label="Ventas (BRL)")
with der:
    st.subheader("Categorias con mas ventas")
    st.bar_chart(
        q.top_categorias(con),
        x="categoria",
        y="ventas",
        horizontal=True,
        sort="-ventas",
        x_label="",
        y_label="Ventas (BRL)",
    )

st.subheader("¿Los retrasos bajan la nota?")
notas = q.nota_por_puntualidad(con).set_index("entrega")
if {"A tiempo", "Con retraso"} <= set(notas.index):
    a_tiempo, tarde = notas.loc["A tiempo"], notas.loc["Con retraso"]
    n1, n2, _ = st.columns([1, 1, 3])
    n1.metric(
        "Nota si llega a tiempo",
        f"{num(a_tiempo.nota_media, 2)} / 5",
        help=f"{num(a_tiempo.pedidos)} pedidos",
    )
    n2.metric(
        "Nota si llega tarde",
        f"{num(tarde.nota_media, 2)} / 5",
        delta=num(tarde.nota_media - a_tiempo.nota_media, 2),
        help=f"{num(tarde.pedidos)} pedidos",
    )

st.subheader("Entregas por estado del cliente")
st.dataframe(
    q.entregas_por_estado(con),
    hide_index=True,
    use_container_width=True,
    column_config={
        "estado": "Estado",
        "pedidos_entregados": "Pedidos entregados",
        "dias_entrega_medio": "Dias de entrega (media)",
        "pct_a_tiempo": st.column_config.NumberColumn("A tiempo (%)", format="%.1f"),
        "nota_media": "Nota media",
        "nota_media_a_tiempo": "Nota a tiempo",
        "nota_media_con_retraso": "Nota con retraso",
    },
)

with st.expander("Calidad de datos: problemas conocidos del dataset y como se tratan"):
    st.dataframe(q.calidad_datos(con), hide_index=True, use_container_width=True)
    st.caption("Cada uno se resuelve en los modelos de dbt; mira el README.")
