"""Genera una muestra SINTETICA con el mismo formato que el dataset de Olist (Kaggle).

Sirve para la CI, los tests y para probar el proyecto sin descargar nada. Reproduce a
proposito los problemas de calidad conocidos del dataset real, para que los modelos de dbt
tengan que resolverlos igual:

  * un mismo cliente real (customer_unique_id) aparece con varios customer_id;
  * productos sin categoria y categorias sin traduccion al ingles;
  * resenas con el mismo review_id en varios pedidos, y pedidos con varias resenas;
  * pedidos "delivered" sin fecha de entrega;
  * pagos repartidos en varias lineas (vouchers).

    python scripts/generar_muestra.py                 # 3000 pedidos en data/muestra
    python scripts/generar_muestra.py --pedidos 500 --salida otra/carpeta
"""

from __future__ import annotations

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ESTADOS_BR = {
    "SP": ["sao paulo", "campinas", "guarulhos", "santos"],
    "RJ": ["rio de janeiro", "niteroi"],
    "MG": ["belo horizonte", "uberlandia"],
    "RS": ["porto alegre", "caxias do sul"],
    "PR": ["curitiba", "londrina"],
    "BA": ["salvador"],
    "PE": ["recife"],
    "AM": ["manaus"],
}
PESO_ESTADOS = {"SP": 40, "RJ": 13, "MG": 12, "RS": 6, "PR": 5, "BA": 4, "PE": 2, "AM": 1}
# Dias de transporte tipicos: mas lejos de Sao Paulo, mas dias
DIAS_TRANSPORTE = {"SP": 6, "RJ": 10, "MG": 9, "RS": 12, "PR": 9, "BA": 16, "PE": 18, "AM": 24}

CATEGORIAS = {
    "cama_mesa_banho": "bed_bath_table",
    "beleza_saude": "health_beauty",
    "esporte_lazer": "sports_leisure",
    "informatica_acessorios": "computers_accessories",
    "moveis_decoracao": "furniture_decor",
    "utilidades_domesticas": "housewares",
    "relogios_presentes": "watches_gifts",
    "telefonia": "telephony",
    "brinquedos": "toys",
    "pc_gamer": None,  # en el dataset real tampoco tiene traduccion
}
PRECIO_MEDIO = {
    "cama_mesa_banho": 90,
    "beleza_saude": 120,
    "esporte_lazer": 110,
    "informatica_acessorios": 160,
    "moveis_decoracao": 95,
    "utilidades_domesticas": 85,
    "relogios_presentes": 200,
    "telefonia": 70,
    "brinquedos": 105,
    "pc_gamer": 900,
}
ESTADOS_PEDIDO = [
    ("delivered", 96.5),
    ("shipped", 1.1),
    ("canceled", 0.7),
    ("unavailable", 0.6),
    ("invoiced", 0.4),
    ("processing", 0.4),
    ("created", 0.1),
    ("approved", 0.2),
]
FORMATO = "%Y-%m-%d %H:%M:%S"
INICIO, FIN = datetime(2017, 1, 1), datetime(2018, 8, 31)


def ident(rng: random.Random) -> str:
    return uuid.UUID(int=rng.getrandbits(128)).hex


def fmt(momento: datetime | None) -> str:
    return momento.strftime(FORMATO) if momento else ""


def elegir(rng: random.Random, pesos: dict[str, float]) -> str:
    return rng.choices(list(pesos), weights=list(pesos.values()))[0]


def escribir(ruta: Path, cabecera: list[str], filas: list[list]) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(cabecera)
        w.writerows(filas)


def generar(n_pedidos: int, salida: Path, semilla: int = 42) -> dict[str, int]:
    rng = random.Random(semilla)
    salida.mkdir(parents=True, exist_ok=True)

    # Vendedores (concentrados en SP, como en el dataset real)
    vendedores = []
    for _ in range(max(20, n_pedidos // 30)):
        estado = elegir(rng, {"SP": 60, "PR": 10, "MG": 10, "RJ": 8, "RS": 7, "BA": 5})
        vendedores.append(
            [ident(rng), f"{rng.randint(10000, 99999)}", rng.choice(ESTADOS_BR[estado]), estado]
        )

    # Productos: ~2 % sin categoria
    productos = []
    for _ in range(max(50, n_pedidos // 4)):
        # pc_gamer es una categoria muy pequena en el dataset real
        pesos = [0.3 if c == "pc_gamer" else 10 for c in CATEGORIAS]
        cat = rng.choices(list(CATEGORIAS), weights=pesos)[0] if rng.random() > 0.02 else ""
        productos.append(
            [
                ident(rng),
                cat,
                rng.randint(20, 60) if cat else "",
                rng.randint(100, 3000) if cat else "",
                rng.randint(1, 6) if cat else "",
                rng.randint(100, 20000),
                rng.randint(15, 80),
                rng.randint(2, 60),
                rng.randint(10, 60),
            ]
        )

    # Clientes: ~3 % repiten compra con un customer_id nuevo (igual que en Olist)
    clientes_unicos: list[tuple[str, str, str, str]] = []
    clientes, pedidos, items, pagos, resenas = [], [], [], [], []
    resena_compartida: str | None = None

    for _ in range(n_pedidos):
        if clientes_unicos and rng.random() < 0.03:
            unico, cp, ciudad, estado = rng.choice(clientes_unicos)
        else:
            estado = elegir(rng, PESO_ESTADOS)
            unico, cp, ciudad = (
                ident(rng),
                f"{rng.randint(10000, 99999)}",
                rng.choice(ESTADOS_BR[estado]),
            )
            clientes_unicos.append((unico, cp, ciudad, estado))
        cliente_id = ident(rng)
        clientes.append([cliente_id, unico, cp, ciudad, estado])

        pedido_id = ident(rng)
        estado_pedido = rng.choices(
            [e for e, _ in ESTADOS_PEDIDO], weights=[p for _, p in ESTADOS_PEDIDO]
        )[0]
        compra = INICIO + timedelta(seconds=rng.randint(0, int((FIN - INICIO).total_seconds())))
        aprobado = compra + timedelta(minutes=rng.randint(10, 2000))
        enviado = aprobado + timedelta(hours=rng.randint(12, 96))
        dias = max(1, int(rng.gauss(DIAS_TRANSPORTE[estado], 3)))
        retraso = rng.random() < 0.08  # ~8 % llega tarde
        entregado = enviado + timedelta(days=dias + (rng.randint(3, 15) if retraso else 0))
        estimado = (compra + timedelta(days=DIAS_TRANSPORTE[estado] + 12)).replace(
            hour=0, minute=0, second=0
        )

        if estado_pedido == "delivered":
            f_aprob, f_env = aprobado, enviado
            # 0,3 % "delivered" sin fecha de entrega: un problema real del dataset
            f_entrega = entregado if rng.random() > 0.003 else None
        elif estado_pedido in ("shipped",):
            f_aprob, f_env, f_entrega = aprobado, enviado, None
        elif estado_pedido in ("created",):
            f_aprob, f_env, f_entrega = None, None, None
        else:
            f_aprob, f_env, f_entrega = aprobado, None, None
        pedidos.append(
            [
                pedido_id,
                cliente_id,
                estado_pedido,
                fmt(compra),
                fmt(f_aprob),
                fmt(f_env),
                fmt(f_entrega),
                fmt(estimado),
            ]
        )

        # Lineas del pedido: el 10 % lleva varias
        n_items = 1 if rng.random() < 0.9 else rng.randint(2, 4)
        total = 0.0
        vendedor = rng.choice(vendedores)
        for n in range(1, n_items + 1):
            producto = rng.choice(productos)
            cat = producto[1] or "utilidades_domesticas"
            precio = round(max(5.0, rng.gauss(PRECIO_MEDIO[cat], PRECIO_MEDIO[cat] * 0.4)), 2)
            flete = round(max(0.0, rng.gauss(20, 8)), 2)
            total += precio + flete
            items.append(
                [
                    pedido_id,
                    n,
                    producto[0],
                    vendedor[0],
                    fmt(aprobado + timedelta(days=3)),
                    f"{precio:.2f}",
                    f"{flete:.2f}",
                ]
            )

        # Pagos: tarjeta en cuotas, boleto, o tarjeta + voucher en varias lineas
        tipo = elegir(rng, {"credit_card": 74, "boleto": 19, "voucher": 5, "debit_card": 2})
        if tipo == "voucher":
            voucher = round(min(total, rng.uniform(10, 60)), 2)
            pagos.append([pedido_id, 1, "voucher", 1, f"{voucher:.2f}"])
            pagos.append([pedido_id, 2, "credit_card", 1, f"{total - voucher:.2f}"])
        else:
            cuotas = rng.randint(1, 10) if tipo == "credit_card" else 1
            pagos.append([pedido_id, 1, tipo, cuotas, f"{total:.2f}"])

        # Resenas: la nota baja mucho si el pedido llega tarde
        if estado_pedido in ("delivered", "shipped", "canceled") and rng.random() < 0.99:
            if retraso:
                nota = rng.choices([1, 2, 3, 4, 5], weights=[45, 15, 15, 12, 13])[0]
            else:
                nota = rng.choices([1, 2, 3, 4, 5], weights=[6, 3, 8, 20, 63])[0]
            creada = (entregado if f_entrega else compra + timedelta(days=20)).replace(
                hour=0, minute=0, second=0
            )
            resena_id = ident(rng)
            # ~0,5 %: el mismo review_id en dos pedidos (pasa en el dataset real)
            if resena_compartida and rng.random() < 0.005:
                resena_id, resena_compartida = resena_compartida, None
            elif rng.random() < 0.01:
                resena_compartida = resena_id
            comentario = rng.choice(
                ["", "", "Produto chegou antes do prazo", 'Muito bom, "recomendo"', "Atrasou"]
            )
            resenas.append(
                [
                    resena_id,
                    pedido_id,
                    nota,
                    "",
                    comentario,
                    fmt(creada),
                    fmt(creada + timedelta(hours=rng.randint(5, 72))),
                ]
            )
            # ~0,5 %: el cliente cambia su resena (dos resenas para el mismo pedido)
            if rng.random() < 0.005:
                nueva = creada + timedelta(days=rng.randint(1, 10))
                resenas.append(
                    [
                        ident(rng),
                        pedido_id,
                        rng.randint(1, 5),
                        "",
                        "Atualizando minha avaliacao",
                        fmt(nueva),
                        fmt(nueva + timedelta(hours=12)),
                    ]
                )

    escribir(
        salida / "olist_customers_dataset.csv",
        [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ],
        clientes,
    )
    escribir(
        salida / "olist_orders_dataset.csv",
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        pedidos,
    )
    escribir(
        salida / "olist_order_items_dataset.csv",
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
        items,
    )
    escribir(
        salida / "olist_order_payments_dataset.csv",
        ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
        pagos,
    )
    escribir(
        salida / "olist_order_reviews_dataset.csv",
        [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ],
        resenas,
    )
    # Las erratas "lenght" son las del dataset original
    escribir(
        salida / "olist_products_dataset.csv",
        [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
        productos,
    )
    escribir(
        salida / "olist_sellers_dataset.csv",
        ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
        vendedores,
    )
    escribir(
        salida / "product_category_name_translation.csv",
        ["product_category_name", "product_category_name_english"],
        [[pt, en] for pt, en in CATEGORIAS.items() if en],
    )
    return {"pedidos": len(pedidos), "items": len(items), "resenas": len(resenas)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pedidos", type=int, default=3000)
    parser.add_argument("--salida", type=Path, default=Path("data/muestra"))
    parser.add_argument("--semilla", type=int, default=42)
    args = parser.parse_args()
    print(generar(args.pedidos, args.salida, args.semilla), "->", args.salida)


if __name__ == "__main__":
    main()
