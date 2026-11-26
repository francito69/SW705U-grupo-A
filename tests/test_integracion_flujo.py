"""Integracion del flujo completo entre M1 y M2 (HU02, HU03, HU04, HU05 y HU06)."""

from datetime import date, datetime, timedelta

import pytest

from app.core import tiempo
from app.modulos.agenda.service import HORIZONTE_DIAS
from conftest import bloque, dia_habil
from test_atenciones import CONSULTA
from test_citas import C01, RAMOS, _cita
from test_pacientes import NUEVO
from test_triaje import SIGNOS

pytestmark = pytest.mark.integration

API = "/api/v1"


def _fijar_ahora(monkeypatch, momento: datetime) -> None:
    monkeypatch.setattr(tiempo, "ahora", lambda: momento)


def _turnos(client, cabecera, fecha: date, id_medico: int = RAMOS) -> dict:
    respuesta = client.get(
        f"{API}/citas/disponibilidad",
        params={"fecha": fecha.isoformat(), "id_especialidad": 1, "id_medico": id_medico},
        headers=cabecera,
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _estado_del_turno(disponibilidad: dict, inicio: str) -> str:
    turnos = disponibilidad["medicos"][0]["turnos"]
    return next(t["estado"] for t in turnos if t["inicio"] == inicio)


def _registrar_y_citar(client, admision, inicio: str) -> tuple[dict, dict]:
    paciente = client.post(f"{API}/pacientes", json=NUEVO, headers=admision)
    assert paciente.status_code == 201, paciente.text
    cita = client.post(
        f"{API}/citas", json=_cita(paciente=paciente.json()["id_paciente"], inicio=inicio), headers=admision
    )
    assert cita.status_code == 201, cita.text
    return paciente.json(), cita.json()


def test_paciente_nuevo_recorre_cita_triaje_y_atencion(client, login, monkeypatch):
    admision, enfermera, medico = login("admision.rquispe"), login("enf.rpaz"), login("med.aramos")
    inicio = bloque(hora="09:00")
    paciente, cita = _registrar_y_citar(client, admision, inicio)

    _fijar_ahora(monkeypatch, datetime.fromisoformat(inicio) - timedelta(minutes=20))
    llegada = client.post(f"{API}/citas/{cita['id_cita']}/check-in", headers=admision)
    triaje = client.post(f"{API}/triajes", json={"id_cita": cita["id_cita"], **SIGNOS}, headers=enfermera)
    id_atencion = triaje.json()["id_atencion"]
    client.post(f"{API}/atenciones/{id_atencion}/iniciar", headers=medico)
    cierre = client.post(f"{API}/atenciones/{id_atencion}/finalizar", json=CONSULTA, headers=medico)

    assert llegada.json()["estado"] == "EN_ESPERA"
    assert triaje.status_code == 201
    assert cierre.json()["estado"] == "FINALIZADA"
    assert client.get(f"{API}/citas/{cita['id_cita']}", headers=medico).json()["estado"] == "ATENDIDA"
    hce = client.get(f"{API}/pacientes/{paciente['id_paciente']}/hce", headers=medico).json()
    assert hce["total_atenciones"] == 1
    assert hce["atenciones"][0]["triaje"]["presion_sistolica"] == SIGNOS["presion_sistolica"]
    assert [d["codigo"] for d in hce["atenciones"][0]["diagnosticos"]] == ["E11.9", "I10"]


def test_alerta_del_triaje_llega_a_la_agenda_del_medico(client, login, monkeypatch):
    admision = login("admision.rquispe")
    inicio = bloque(hora="10:00")
    _, cita = _registrar_y_citar(client, admision, inicio)

    _fijar_ahora(monkeypatch, datetime.fromisoformat(inicio) - timedelta(minutes=15))
    client.post(f"{API}/citas/{cita['id_cita']}/check-in", headers=admision)
    signos = {**SIGNOS, "presion_sistolica": 150, "presion_diastolica": 95}
    client.post(f"{API}/triajes", json={"id_cita": cita["id_cita"], **signos}, headers=login("enf.rpaz"))

    agenda = client.get(f"{API}/citas", headers=login("med.aramos")).json()
    propia = next(c for c in agenda if c["id_cita"] == cita["id_cita"])
    assert propia["estado"] == "EN_ESPERA"
    assert "Presión arterial elevada (150/95 mmHg)" in propia["atencion"]["alertas"]


def test_cancelar_devuelve_el_turno_a_la_disponibilidad(client, login):
    admision = login("admision.rquispe")
    inicio = bloque(hora="11:00")
    _, cita = _registrar_y_citar(client, admision, inicio)
    fecha = datetime.fromisoformat(inicio).date()
    ocupado = _estado_del_turno(_turnos(client, admision, fecha), inicio)

    client.post(f"{API}/citas/{cita['id_cita']}/cancelar", json={"motivo": "Viaje del paciente"}, headers=admision)

    assert ocupado == "OCUPADO"
    assert _estado_del_turno(_turnos(client, admision, fecha), inicio) == "LIBRE"
    otra = client.post(f"{API}/citas", json=_cita(paciente=17, inicio=inicio), headers=admision)
    assert otra.status_code == 201


def test_reprogramar_ocupa_el_nuevo_turno_y_libera_el_anterior(client, login):
    admision = login("admision.rquispe")
    original, nuevo = bloque(hora="15:00"), bloque(hora="16:30")
    _, cita = _registrar_y_citar(client, admision, original)

    respuesta = client.post(
        f"{API}/citas/{cita['id_cita']}/reprogramar",
        json={"fecha_hora_inicio": nuevo, "id_consultorio": C01, "motivo": "Cambio de horario laboral"},
        headers=admision,
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["id_cita_origen"] == cita["id_cita"]
    disponibilidad = _turnos(client, admision, datetime.fromisoformat(original).date())
    assert _estado_del_turno(disponibilidad, original) == "LIBRE"
    assert _estado_del_turno(disponibilidad, nuevo) == "OCUPADO"
    anterior = client.get(f"{API}/citas/{cita['id_cita']}", headers=admision).json()
    assert anterior["estado"] == "REPROGRAMADA"
    assert anterior["id_cita_nueva"] == respuesta.json()["id_cita"]


def _ultimo_dia_habil_del_plazo() -> date:
    fecha = tiempo.hoy() + timedelta(days=HORIZONTE_DIAS)
    while fecha.weekday() == 6:
        fecha -= timedelta(days=1)
    return fecha


def test_el_ultimo_dia_del_plazo_ofrece_turnos_que_se_pueden_agendar(client, login):
    admision = login("admision.rquispe")
    fecha = _ultimo_dia_habil_del_plazo()
    turno = next(t for t in _turnos(client, admision, fecha)["medicos"][0]["turnos"] if t["estado"] == "LIBRE")

    respuesta = client.post(
        f"{API}/citas",
        json=_cita(inicio=turno["inicio"], consultorio=turno["id_consultorio_sugerido"]),
        headers=admision,
    )

    assert respuesta.status_code == 201


def test_fuera_del_plazo_de_90_dias_no_se_ofrecen_turnos_libres(client, login):
    admision = login("admision.rquispe")
    fecha = dia_habil(HORIZONTE_DIAS + 1)

    disponibilidad = _turnos(client, admision, fecha)

    libres = [t for m in disponibilidad["medicos"] for t in m["turnos"] if t["estado"] == "LIBRE"]
    assert libres == []
    assert f"{HORIZONTE_DIAS} días" in disponibilidad["mensaje"]
