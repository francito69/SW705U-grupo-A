"""HU06 - Reprogramación y cancelación justificada; llegada e inasistencia."""

from conftest import bloque, dia_habil

URL = "/api/v1/citas"


def _agendar(client, cabecera, paciente=13, medico=3, consultorio=1, hora="09:00"):
    respuesta = client.post(
        URL,
        json={
            "id_paciente": paciente,
            "id_medico": medico,
            "id_consultorio": consultorio,
            "fecha_hora_inicio": bloque(hora=hora),
        },
        headers=cabecera,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _bandeja(client, cabecera, id_cita):
    return client.get("/api/v1/notificaciones", params={"id_cita": id_cita}, headers=cabecera).json()[
        "notificaciones"
    ]


def test_cancelar_exige_motivo(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    respuesta = client.post(f"{URL}/{cita['id_cita']}/cancelar", json={"motivo": " "}, headers=admision)

    assert respuesta.status_code == 422
    assert "motivo" in respuesta.json()["detail"].lower()


def test_cancelar_libera_el_turno_y_guarda_el_motivo(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    cancelada = client.post(
        f"{URL}/{cita['id_cita']}/cancelar", json={"motivo": "Solicitud del paciente"}, headers=admision
    )

    assert cancelada.status_code == 200
    assert cancelada.json()["estado"] == "CANCELADA"
    assert cancelada.json()["motivo_cancelacion"] == "Solicitud del paciente"
    otra = _agendar(client, admision, paciente=17)
    assert otra["fecha_hora_inicio"] == cita["fecha_hora_inicio"]


def test_cancelar_descarta_el_recordatorio_y_avisa_al_paciente(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    client.post(f"{URL}/{cita['id_cita']}/cancelar", json={"motivo": "Inasistencia del médico"}, headers=admision)

    bandeja = _bandeja(client, admision, cita["id_cita"])
    recordatorio = next(n for n in bandeja if n["tipo_evento"] == "RECORDATORIO_24H")
    assert recordatorio["estado"] == "FALLIDO"
    assert recordatorio["error_detalle"].startswith("Descartada")
    assert any("cancelada" in n["mensaje"] for n in bandeja if n["estado"] == "PENDIENTE")


def test_no_se_cancela_una_cita_atendida(client, login):
    admision = login("admision.rquispe")
    atendida = next(c for c in client.get(URL, headers=admision).json() if c["estado"] == "ATENDIDA")

    respuesta = client.post(f"{URL}/{atendida['id_cita']}/cancelar", json={"motivo": "Error"}, headers=admision)

    assert respuesta.status_code == 409


def test_reprogramar_crea_la_nueva_cita_enlazada(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    respuesta = client.post(
        f"{URL}/{cita['id_cita']}/reprogramar",
        json={"fecha_hora_inicio": bloque(dias=15, hora="11:00"), "id_consultorio": 1, "motivo": "Viaje del paciente"},
        headers=admision,
    )

    assert respuesta.status_code == 201
    nueva = respuesta.json()
    assert nueva["id_cita_origen"] == cita["id_cita"]
    assert nueva["medico"]["id_medico"] == 3
    original = client.get(f"{URL}/{cita['id_cita']}", headers=admision).json()
    assert original["estado"] == "REPROGRAMADA"
    assert original["id_cita_nueva"] == nueva["id_cita"]
    assert original["motivo_cancelacion"] == "Viaje del paciente"
    pendientes = [n["tipo_evento"] for n in _bandeja(client, admision, nueva["id_cita"])]
    assert sorted(pendientes) == ["CONFIRMACION_CITA", "RECORDATORIO_24H"]
    viejas = _bandeja(client, admision, cita["id_cita"])
    assert next(n for n in viejas if n["tipo_evento"] == "RECORDATORIO_24H")["estado"] == "FALLIDO"


def test_reprogramar_a_un_turno_ocupado_no_cambia_nada(client, login):
    admision = login("admision.rquispe")
    _agendar(client, admision, paciente=13, hora="09:00")
    segunda = _agendar(client, admision, paciente=17, hora="10:00")

    respuesta = client.post(
        f"{URL}/{segunda['id_cita']}/reprogramar",
        json={"fecha_hora_inicio": bloque(hora="09:00"), "id_consultorio": 2, "motivo": "Cambio de horario"},
        headers=admision,
    )

    assert respuesta.status_code == 409
    assert client.get(f"{URL}/{segunda['id_cita']}", headers=admision).json()["estado"] == "CONFIRMADA"


def test_reprogramar_dos_veces_la_misma_cita_responde_409(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)
    cuerpo = {"fecha_hora_inicio": bloque(dias=16), "id_consultorio": 1, "motivo": "Cambio de horario"}
    client.post(f"{URL}/{cita['id_cita']}/reprogramar", json=cuerpo, headers=admision)

    respuesta = client.post(f"{URL}/{cita['id_cita']}/reprogramar", json=cuerpo, headers=admision)

    assert respuesta.status_code == 409


def test_llegada_del_paciente_pasa_a_espera(client, login):
    admision = login("admision.rquispe")
    confirmada = next(c for c in client.get(URL, headers=admision).json() if c["estado"] == "CONFIRMADA")

    respuesta = client.post(f"{URL}/{confirmada['id_cita']}/check-in", headers=admision)

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "EN_ESPERA"
    assert respuesta.json()["hora_llegada"] is not None
    repetida = client.post(f"{URL}/{confirmada['id_cita']}/check-in", headers=admision)
    assert repetida.status_code == 409


def test_llegada_solo_el_dia_de_la_cita(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    respuesta = client.post(f"{URL}/{cita['id_cita']}/check-in", headers=admision)

    assert respuesta.status_code == 422


def test_registrar_inasistencia(client, login):
    admision = login("admision.rquispe")
    vencida = next(
        c
        for c in client.get(URL, params={"desde": "2026-10-15", "hasta": "2026-10-16"}, headers=admision).json()
        if c["estado"] == "CONFIRMADA"
    )

    respuesta = client.post(f"{URL}/{vencida['id_cita']}/no-asistio", headers=admision)

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "NO_ASISTIO"
    assert client.post(f"{URL}/{vencida['id_cita']}/no-asistio", headers=admision).status_code == 409


def test_inasistencia_de_una_cita_futura_responde_422(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)

    assert client.post(f"{URL}/{cita['id_cita']}/no-asistio", headers=admision).status_code == 422


def test_cambios_de_estado_quedan_en_la_bitacora(client, login):
    admision = login("admision.rquispe")
    cita = _agendar(client, admision)
    client.post(f"{URL}/{cita['id_cita']}/cancelar", json={"motivo": "Solicitud del paciente"}, headers=admision)

    bitacora = client.get(
        "/api/v1/auditoria", params={"tabla": "citas", "desde": dia_habil(-30).isoformat()}, headers=login("admin.sira")
    ).json()

    acciones = [(r["accion"], r["id_registro_afectado"]) for r in bitacora["registros"]]
    assert ("INSERT", cita["id_cita"]) in acciones
    assert ("UPDATE", cita["id_cita"]) in acciones
