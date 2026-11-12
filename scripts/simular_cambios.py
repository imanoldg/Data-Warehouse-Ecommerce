"""Simula que algunos vendedores se mudan de ciudad, para ver el SCD tipo 2 en accion.

El dataset de Olist es una foto fija: no trae cambios en el tiempo. Este script reescribe
olist_sellers_dataset.csv cambiando la ciudad y el estado de una parte de los vendedores.
Si despues ejecutas "dbt snapshot", dbt cierra la version antigua de cada vendedor
(valido_hasta) y abre una nueva.

    python scripts/simular_cambios.py --dir data/muestra --porcentaje 10

Guarda una copia del fichero original (.original.csv) la primera vez; con --restaurar la
vuelve a poner en su sitio.
"""

from __future__ import annotations

import argparse
import csv
import random
import shutil
from pathlib import Path

NUEVAS_SEDES = [
    ("rio de janeiro", "RJ"),
    ("belo horizonte", "MG"),
    ("curitiba", "PR"),
    ("porto alegre", "RS"),
    ("salvador", "BA"),
    ("recife", "PE"),
]
FICHERO = "olist_sellers_dataset.csv"


def simular(directorio: Path, porcentaje: float, semilla: int = 7) -> list[str]:
    """Cambia la sede de un porcentaje de vendedores. Devuelve los seller_id cambiados."""
    ruta = directorio / FICHERO
    copia = directorio / FICHERO.replace(".csv", ".original.csv")
    if not copia.exists():
        shutil.copyfile(ruta, copia)

    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        columnas = lector.fieldnames
        filas = list(lector)

    rng = random.Random(semilla)
    n = max(1, round(len(filas) * porcentaje / 100))
    cambiados = []
    for fila in rng.sample(filas, n):
        ciudad, estado = rng.choice([s for s in NUEVAS_SEDES if s[1] != fila["seller_state"]])
        fila["seller_city"], fila["seller_state"] = ciudad, estado
        fila["seller_zip_code_prefix"] = f"{rng.randint(10000, 99999)}"
        cambiados.append(fila["seller_id"])

    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    return cambiados


def restaurar(directorio: Path) -> None:
    copia = directorio / FICHERO.replace(".csv", ".original.csv")
    if copia.exists():
        shutil.move(copia, directorio / FICHERO)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", type=Path, default=Path("data/muestra"))
    parser.add_argument("--porcentaje", type=float, default=10)
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--restaurar", action="store_true", help="Deshace los cambios")
    args = parser.parse_args()

    if args.restaurar:
        restaurar(args.dir)
        print("Fichero de vendedores restaurado")
    else:
        cambiados = simular(args.dir, args.porcentaje, args.semilla)
        print(f"{len(cambiados)} vendedores cambiados de sede. Ahora ejecuta: dbt snapshot")


if __name__ == "__main__":
    main()
