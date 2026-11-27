"""Pruebas unitarias para HU-07: recordatorio de cita 24 horas antes (casos CP-01 a CP-08)."""

from datetime import datetime

import pytest

from app.citas import CitaRecordatorio
from app.notificaciones import NotificadorSimulado
from app.recordatorios import citas_a_recordar, enviar_recordatorios

AHORA = datetime(2026, 11, 26, 10, 0)


@pytest.mark.parametrize(
    ("caso_id", "minutos", "estado", "recordada", "esperado"),
    [
        ("CP-01", 1440, "reservada", False, True),
        ("CP-02", 1441, "reservada", False, False),
        ("CP-03", 60, "reservada", False, True),
        ("CP-04", 0, "reservada", False, True),
        ("CP-05", -30, "reservada", False, False),
        ("CP-06", 300, "cancelada", False, False),
        ("CP-07", 300, "reservada", True, False),
    ],
)
def test_ventana_de_24_horas_para_recordar(caso_id, minutos, estado, recordada, esperado):
    cita = CitaRecordatorio(
        id_cita=1,
        dni_paciente="71234567",
        minutos_restantes=minutos,
        estado=estado,
        recordada=recordada,
    )
    resultado = citas_a_recordar([cita], AHORA)
    assert (cita in resultado) is esperado, f"Fallo en {caso_id}"


def test_envio_exitoso_marca_cita_como_recordada():
    cita = CitaRecordatorio(
        id_cita=10,
        dni_paciente="71234567",
        minutos_restantes=300,
        estado="reservada",
    )
    notificador = NotificadorSimulado()

    enviados = enviar_recordatorios([cita], AHORA, notificador)

    assert enviados == 1
    assert cita.recordada is True
    assert len(notificador.enviados) == 1
    assert notificador.enviados[0][0] == "71234567"


def test_cp08_envio_fallido_no_marca_cita_como_recordada():
    cita = CitaRecordatorio(
        id_cita=11,
        dni_paciente="74561234",
        minutos_restantes=300,
        estado="reservada",
    )
    notificador = NotificadorSimulado(debe_fallar=True)

    enviados = enviar_recordatorios([cita], AHORA, notificador)

    assert enviados == 0
    assert cita.recordada is False
    assert notificador.enviados == []


def test_no_repeticion_en_segundo_ciclo():
    cita = CitaRecordatorio(
        id_cita=12,
        dni_paciente="79876543",
        minutos_restantes=120,
        estado="reservada",
    )
    notificador = NotificadorSimulado()

    primero = enviar_recordatorios([cita], AHORA, notificador)
    segundo = enviar_recordatorios([cita], AHORA, notificador)

    assert primero == 1
    assert segundo == 0
    assert len(notificador.enviados) == 1
