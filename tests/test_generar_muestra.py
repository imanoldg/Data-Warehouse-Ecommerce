import csv

import pytest

from generar_muestra import generar

CABECERAS_OLIST = {
    "olist_orders_dataset.csv": [
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": [
        "order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date",
        "price", "freight_value",
    ],
    "olist_products_dataset.csv": [
        "product_id", "product_category_name", "product_name_lenght",
        "product_description_lenght", "product_photos_qty", "product_weight_g",
        "product_length_cm", "product_height_cm", "product_width_cm",
    ],
    "olist_customers_dataset.csv": [
        "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city",
        "customer_state",
    ],
}  # fmt: skip


@pytest.fixture(scope="module")
def muestra(tmp_path_factory):
    salida = tmp_path_factory.mktemp("muestra")
    generar(3000, salida, semilla=42)
    return salida


def leer(directorio, nombre):
    with (directorio / nombre).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.mark.parametrize("fichero", CABECERAS_OLIST)
def test_las_cabeceras_son_las_de_olist(muestra, fichero):
    with (muestra / fichero).open(encoding="utf-8") as f:
        assert next(csv.reader(f)) == CABECERAS_OLIST[fichero]


def test_es_reproducible(tmp_path, muestra):
    generar(3000, tmp_path, semilla=42)
    for fichero in CABECERAS_OLIST:
        assert (tmp_path / fichero).read_bytes() == (muestra / fichero).read_bytes()


def test_reproduce_los_problemas_de_calidad_del_dataset_real(muestra):
    pedidos = leer(muestra, "olist_orders_dataset.csv")
    clientes = leer(muestra, "olist_customers_dataset.csv")
    productos = leer(muestra, "olist_products_dataset.csv")
    resenas = leer(muestra, "olist_order_reviews_dataset.csv")
    traducidas = {
        r["product_category_name"] for r in leer(muestra, "product_category_name_translation.csv")
    }

    unicos = [c["customer_unique_id"] for c in clientes]
    assert len(set(unicos)) < len(unicos), "faltan clientes recurrentes"
    assert any(p["product_category_name"] == "" for p in productos), (
        "faltan productos sin categoria"
    )
    assert any(
        p["product_category_name"] and p["product_category_name"] not in traducidas
        for p in productos
    ), "faltan categorias sin traduccion"
    assert any(
        p["order_status"] == "delivered" and p["order_delivered_customer_date"] == ""
        for p in pedidos
    ), "faltan pedidos entregados sin fecha"
    por_pedido = [r["order_id"] for r in resenas]
    assert len(set(por_pedido)) < len(por_pedido), "faltan pedidos con varias resenas"
