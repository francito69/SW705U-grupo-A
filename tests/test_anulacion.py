"""HU08 - Anulación lógica de atenciones con bitácora de auditoría."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from conftest import PASSWORD

pytestmark = pytest.mark.integration

MOTIVO = "Atención registrada en el paciente equivocado por error de digitación"


def _anular(client, cabecera, id_atencion=1, motivo=MOTIVO, password=PASSWORD):
    return client.post(
        f"/api/v1/atenciones/{id_atencion}/anular", json={"motivo": motivo, "password": password}, headers=cabecera
    )


def test_gerencia_anula_con_justificacion_y_clave(client, login):
    respuesta = _anular(client, login("ger.rmedina"))

    assert respuesta.status_code == 200
    assert respuesta.json()["anulado"] is True
    hce = client.get("/api/v1/pacientes/1/hce", params={"limite": 50}, headers=login("med.aramos")).json()
    anulada = next(a for a in hce["atenciones"] if a["id_atencion"] == 1)
    assert anulada["anulado"] is True
    assert anulada["motivo_anulacion"] == MOTIVO
    bitacora = client.get("/api/v1/auditoria", params={"accion": "ANULAR"}, headers=login("admin.sira")).json()
    assert bitacora["registros"][0]["motivo"] == MOTIVO
    assert bitacora["registros"][0]["datos_nuevos"] == {"anulado": True}


def test_justificacion_menor_a_20_caracteres_responde_422(client, login):
    respuesta = _anular(client, login("ger.rmedina"), motivo="Error de registro")

    assert respuesta.status_code == 422
    assert "20 caracteres" in respuesta.json()["detail"]


def test_clave_incorrecta_responde_403_y_queda_auditada(client, login):
    respuesta = _anular(client, login("ger.rmedina"), password="no-es-la-clave")

    assert respuesta.status_code == 403
    bitacora = client.get(
        "/api/v1/auditoria", params={"accion": "ACCESO_DENEGADO", "tabla": "atenciones"}, headers=login("admin.sira")
    ).json()
    assert bitacora["registros"][0]["motivo"] == "Clave incorrecta al confirmar la anulación"


def test_medico_no_puede_anular(client, login):
    assert _anular(client, login("med.aramos")).status_code == 403


def test_no_se_anula_dos_veces(client, login):
    gerencia = login("ger.rmedina")
    _anular(client, gerencia)

    assert _anular(client, gerencia).status_code == 409


def test_lista_de_atenciones_para_anular_sin_contenido_clinico(client, login):
    atenciones = client.get("/api/v1/pacientes/1/atenciones", headers=login("ger.rmedina")).json()

    assert atenciones
    assert "motivo_consulta" not in atenciones[0]
    assert "diagnosticos" not in atenciones[0]
    assert client.get("/api/v1/pacientes/1/atenciones", headers=login("caja.evargas")).status_code == 403


def test_el_borrado_fisico_esta_bloqueado_en_la_base(client):
    from app.database import engine

    with engine.connect() as conexion:
        with pytest.raises(DBAPIError, match="anulación lógica"):
            conexion.execute(text("DELETE FROM atenciones WHERE id_atencion = 1"))
        conexion.rollback()
        with pytest.raises(DBAPIError, match="anulación lógica"):
            conexion.execute(text("DELETE FROM pacientes WHERE id_paciente = 7"))
        conexion.rollback()


def test_la_bitacora_es_inmutable(client):
    from app.database import engine

    with engine.connect() as conexion:
        with pytest.raises(DBAPIError, match="inmutable"):
            conexion.execute(text("UPDATE bitacora_auditoria SET motivo = 'x'"))
        conexion.rollback()
        with pytest.raises(DBAPIError, match="inmutable"):
            conexion.execute(text("DELETE FROM bitacora_auditoria"))
        conexion.rollback()
