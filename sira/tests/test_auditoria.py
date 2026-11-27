"""T2 - Consulta de la bitácora de auditoría."""

import pytest

pytestmark = pytest.mark.integration

URL = "/api/v1/auditoria"


def test_filtra_por_accion(client, login):
    bitacora = client.get(URL, params={"accion": "ANULAR"}, headers=login("admin.sira")).json()

    assert bitacora["total"] >= 1
    assert {r["accion"] for r in bitacora["registros"]} == {"ANULAR"}


def test_pagina_los_resultados(client, login):
    pagina = client.get(URL, params={"limite": 2, "desplazamiento": 1}, headers=login("ger.rmedina")).json()

    assert len(pagina["registros"]) == 2
    assert pagina["total"] >= 6


def test_filtra_por_rango_de_fechas(client, login):
    bitacora = client.get(
        URL, params={"desde": "2026-10-14", "hasta": "2026-10-14"}, headers=login("admin.sira")
    ).json()

    assert bitacora["total"] == 5
    assert all(r["fecha_hora"].startswith("2026-10-14") for r in bitacora["registros"])


def test_solo_gerencia_y_administrador(client, login):
    assert client.get(URL, headers=login("med.aramos")).status_code == 403
    assert client.get(URL, headers=login("admision.rquispe")).status_code == 403
