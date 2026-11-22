"""HU07 - Envío asíncrono de recordatorios con el patrón Outbox."""

import asyncio
from datetime import datetime, timedelta

import pytest

from conftest import bloque

URL = "/api/v1/notificaciones"


def _agendar(client, cabecera):
    respuesta = client.post(
        "/api/v1/citas",
        json={"id_paciente": 13, "id_medico": 3, "id_consultorio": 1, "fecha_hora_inicio": bloque()},
        headers=cabecera,
    )
    return respuesta.json()


def _fijar_ahora(monkeypatch, momento: datetime):
    from app.core import tiempo

    monkeypatch.setattr(tiempo, "ahora", lambda: momento)


def test_el_recordatorio_se_envia_cuando_faltan_24_horas(client, login, monkeypatch):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)
    _fijar_ahora(monkeypatch, datetime.fromisoformat(cita["fecha_hora_inicio"]) - timedelta(hours=23))

    resultado = client.post(f"{URL}/procesar", headers=admision).json()

    assert resultado["enviadas"] >= 2
    bandeja = client.get(URL, params={"id_cita": cita["id_cita"]}, headers=admision).json()
    recordatorio = next(n for n in bandeja["notificaciones"] if n["tipo_evento"] == "RECORDATORIO_24H")
    assert recordatorio["estado"] == "ENVIADO"
    assert recordatorio["procesado_en"] is not None


def test_el_recordatorio_no_sale_antes_de_tiempo(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    client.post(f"{URL}/procesar", headers=admision)

    bandeja = client.get(URL, params={"id_cita": cita["id_cita"]}, headers=admision).json()
    estados = {n["tipo_evento"]: n["estado"] for n in bandeja["notificaciones"]}
    assert estados == {"CONFIRMACION_CITA": "ENVIADO", "RECORDATORIO_24H": "PENDIENTE"}


def test_fallo_del_proveedor_reintenta_y_luego_marca_fallido(client, monkeypatch):
    from sqlalchemy import func, select

    from app.core import tiempo
    from app.database import SessionLocal
    from app.modulos.agenda.models import Cita
    from app.modulos.notificaciones import service

    class ProveedorCaido:
        def enviar(self, canal, destinatario, mensaje):
            raise service.ErrorEnvio("Tiempo de espera agotado con el proveedor de SMS")

    momento = tiempo.ahora()
    contar_citas = select(func.count()).select_from(Cita)
    with SessionLocal() as db:
        notificacion = service.encolar(
            db,
            id_cita=None,
            tipo_evento="CONFIRMACION_CITA",
            canal="SMS",
            destinatario="987650001",
            mensaje="Mensaje de prueba",
            programado_para=momento,
        )
        db.commit()
        citas_antes = db.scalar(contar_citas)
        for intento in range(1, 4):
            _fijar_ahora(monkeypatch, momento + timedelta(hours=intento))
            service.procesar_pendientes(db, adaptador=ProveedorCaido())
            db.commit()
            assert notificacion.intentos == intento
        assert notificacion.estado == "FALLIDO"
        assert "Tiempo de espera" in notificacion.error_detalle
        assert db.scalar(contar_citas) == citas_antes


def test_un_reintento_reprograma_el_envio(client):
    from app.core import tiempo
    from app.database import SessionLocal
    from app.modulos.notificaciones import service

    with SessionLocal() as db:
        notificacion = service.encolar(
            db,
            id_cita=None,
            tipo_evento="AVISO_RESULTADO",
            canal="EMAIL",
            destinatario="correo-mal-escrito",
            mensaje="Sus resultados están listos",
            programado_para=tiempo.ahora(),
        )
        db.commit()

        resultado = service.procesar_pendientes(db)

        assert resultado["reintentos"] == 1
        assert notificacion.estado == "PENDIENTE"
        assert notificacion.programado_para > tiempo.ahora()


def test_adaptador_simulado_valida_destinatarios():
    from app.modulos.notificaciones.service import AdaptadorSimulado, ErrorEnvio

    adaptador = AdaptadorSimulado()
    adaptador.enviar("SMS", "987650001", "ok")
    adaptador.enviar("EMAIL", "persona@correo.test", "ok")
    with pytest.raises(ErrorEnvio):
        adaptador.enviar("WHATSAPP", "12345", "x")


def test_la_bandeja_resume_por_estado(client, login):
    bandeja = client.get(URL, params={"estado": "FALLIDO"}, headers=login("admin.sira")).json()

    assert bandeja["resumen"]["FALLIDO"] >= 1
    assert {n["estado"] for n in bandeja["notificaciones"]} == {"FALLIDO"}


def test_la_bandeja_es_solo_para_admision_y_administrador(client, login):
    assert client.get(URL, headers=login("med.aramos")).status_code == 403


def test_trabajador_en_segundo_plano(client, monkeypatch):
    from app.modulos.notificaciones import worker

    assert worker.procesar_una_vez()["procesadas"] >= 0

    llamadas = []

    def falla():
        llamadas.append(1)
        raise RuntimeError("caída simulada")

    monkeypatch.setattr(worker, "procesar_una_vez", falla)

    async def ejecutar():
        await asyncio.wait_for(worker.bucle(0), timeout=0.2)

    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(ejecutar())
    assert llamadas
