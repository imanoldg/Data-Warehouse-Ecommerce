import csv

from generar_muestra import generar
from simular_cambios import FICHERO, restaurar, simular


def sedes(directorio):
    with (directorio / FICHERO).open(encoding="utf-8", newline="") as f:
        return {r["seller_id"]: (r["seller_city"], r["seller_state"]) for r in csv.DictReader(f)}


def test_cambia_el_porcentaje_pedido_y_se_puede_deshacer(tmp_path):
    generar(600, tmp_path)
    antes = sedes(tmp_path)

    cambiados = simular(tmp_path, porcentaje=10)
    despues = sedes(tmp_path)

    assert len(cambiados) == round(len(antes) * 0.10)
    assert {v for v in antes if antes[v] != despues[v]} == set(cambiados)
    assert all(antes[v][1] != despues[v][1] for v in cambiados)  # cambia de estado

    restaurar(tmp_path)
    assert sedes(tmp_path) == antes
