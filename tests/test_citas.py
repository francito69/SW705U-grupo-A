"""HU02 - Agendamiento con bloqueo transaccional de solapamientos."""

from datetime import datetime, timedelta

import pytest

from conftest import bloque, dia_habil, proximo_domingo

pytestmark = pytest.mark.integration

URL = "/api/v1/citas"
RAMOS, NUNEZ, MENDOZA = 3, 7, 2
C01, C03, C10 = 1, 3, 10


def _cita(paciente=13, medico=RAMOS, consultorio=C01, inicio=None, **extra):
    return {
        "id_paciente": paciente,
        "id_medico": medico,
        "id_consultorio": consultorio,
        "fecha_hora_inicio": inicio or bloque(),
        **extra,
    }


def test_disponibilidad_muestra_los_turnos_del_dia(client, login):
    respuesta = client.get(
        f"{URL}/disponibilidad",
        params={"fecha": dia_habil().isoformat(), "id_especialidad": 1},
        headers=login("admision.rquispe"),
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["atiende"] is True
    ramos = next(m for m in cuerpo["medicos"] if m["id_medico"] == RAMOS)
    assert ramos["consultorio_habitual"] == "C01"
    assert len(ramos["turnos"]) == 20
    assert ramos["turnos"][0]["inicio"].endswith("08:00:00")
    assert {t["estado"] for t in ramos["turnos"]} == {"LIBRE"}


def test_domingo_no_hay_atencion(client, login):
    respuesta = client.get(
        f"{URL}/disponibilidad",
        params={"fecha": proximo_domingo().isoformat(), "id_especialidad": 1},
        headers=login("admision.rquispe"),
    )

    assert respuesta.json()["atiende"] is False
    assert respuesta.json()["medicos"] == []


def test_agenda_una_cita_confirmada_y_encola_notificaciones(client, login):
    admision = login("admision.rquispe")

    respuesta = client.post(URL, json=_cita(), headers=admision)

    assert respuesta.status_code == 201
    cita = respuesta.json()
    assert cita["estado"] == "CONFIRMADA"
    assert cita["consultorio"]["numero"] == "C01"
    assert cita["paciente"]["alergias"] is None
    bandeja = client.get(
        "/api/v1/notificaciones", params={"id_cita": cita["id_cita"]}, headers=admision
    ).json()
    tipos = {n["tipo_evento"]: n for n in bandeja["notificaciones"]}
    assert set(tipos) == {"CONFIRMACION_CITA", "RECORDATORIO_24H"}
    inicio = datetime.fromisoformat(cita["fecha_hora_inicio"])
    assert datetime.fromisoformat(tipos["RECORDATORIO_24H"]["programado_para"]) == inicio - timedelta(hours=24)


def test_sin_recordatorio_si_se_desactiva(client, login):
    admision = login("admision.rquispe")

    cita = client.post(URL, json=_cita(enviar_recordatorio=False), headers=admision).json()

    bandeja = client.get("/api/v1/notificaciones", params={"id_cita": cita["id_cita"]}, headers=admision).json()
    assert [n["tipo_evento"] for n in bandeja["notificaciones"]] == ["CONFIRMACION_CITA"]


def test_solapamiento_de_medico_responde_409_y_no_duplica(client, login):
    admision = login("admision.rquispe")
    assert client.post(URL, json=_cita(), headers=admision).status_code == 201

    respuesta = client.post(URL, json=_cita(paciente=17, consultorio=C10), headers=admision)

    assert respuesta.status_code == 409
    assert respuesta.json()["recurso"] == "medico"
    del_dia = client.get(URL, params={"fecha": dia_habil().isoformat()}, headers=admision).json()
    assert len(del_dia) == 1


def test_solapamiento_de_consultorio_responde_409(client, login):
    admision = login("admision.rquispe")
    client.post(URL, json=_cita(), headers=admision)

    respuesta = client.post(URL, json=_cita(paciente=17, medico=NUNEZ, consultorio=C01), headers=admision)

    assert respuesta.status_code == 409
    assert respuesta.json()["recurso"] == "consultorio"


def test_paciente_no_puede_tener_dos_citas_a_la_vez(client, login):
    admision = login("admision.rquispe")
    client.post(URL, json=_cita(), headers=admision)

    respuesta = client.post(URL, json=_cita(medico=NUNEZ, consultorio=C03), headers=admision)

    assert respuesta.status_code == 409
    assert respuesta.json()["recurso"] == "paciente"


def test_si_dos_reservas_compiten_la_base_responde_409(client, login, monkeypatch):
    from sqlalchemy.exc import IntegrityError

    from app.database import engine
    from app.modulos.agenda import service as agenda

    admision = login("admision.rquispe")
    assert client.post(URL, json=_cita(), headers=admision).status_code == 201
    monkeypatch.setattr(agenda, "_verificar_cruces", lambda *args, **kwargs: None)
    if engine.dialect.name != "postgresql":
        # SQLite no tiene EXCLUDE: se simula el rechazo que da PostgreSQL en la carrera.
        def rechazar(self, *args, **kwargs):
            raise IntegrityError("INSERT", {}, Exception('exclusion constraint "no_solapamiento_medico"'))

        monkeypatch.setattr("sqlalchemy.orm.Session.flush", rechazar)

    respuesta = client.post(URL, json=_cita(paciente=17, consultorio=C10), headers=admision)

    assert respuesta.status_code == 409
    assert respuesta.json()["recurso"] == "medico"
    monkeypatch.undo()
    del_dia = client.get(URL, params={"fecha": dia_habil().isoformat()}, headers=admision).json()
    assert len(del_dia) == 1


def test_turno_ocupado_aparece_en_la_disponibilidad(client, login):
    admision = login("admision.rquispe")
    cita = client.post(URL, json=_cita(inicio=bloque(hora="10:30")), headers=admision).json()

    disponibilidad = client.get(
        f"{URL}/disponibilidad",
        params={"fecha": dia_habil().isoformat(), "id_especialidad": 1, "id_medico": RAMOS},
        headers=admision,
    ).json()

    turno = next(t for t in disponibilidad["medicos"][0]["turnos"] if t["inicio"].endswith("10:30:00"))
    assert turno["estado"] == "OCUPADO"
    assert turno["id_cita"] == cita["id_cita"]
    nunez = client.get(
        f"{URL}/disponibilidad",
        params={"fecha": dia_habil().isoformat(), "id_especialidad": 1, "id_medico": NUNEZ},
        headers=admision,
    ).json()
    libre = next(t for t in nunez["medicos"][0]["turnos"] if t["inicio"].endswith("10:30:00"))
    assert libre["estado"] == "LIBRE"
    assert libre["consultorio_sugerido"] == "C03"


def test_consultorios_libres_en_un_bloque(client, login):
    admision = login("admision.rquispe")
    client.post(URL, json=_cita(), headers=admision)

    libres = client.get("/api/v1/consultorios", params={"libres_en": bloque()}, headers=admision).json()

    assert "C01" not in [c["numero"] for c in libres]
    assert len(libres) == 11


def test_rechaza_horario_pasado(client, login):
    ayer = (datetime.now() - timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

    respuesta = client.post(URL, json=_cita(inicio=ayer.isoformat()), headers=login("admision.rquispe"))

    assert respuesta.status_code == 422
    assert "pasada" in respuesta.json()["detail"]


def test_rechaza_bloques_fuera_de_turno(client, login):
    admision = login("admision.rquispe")

    for hora in ("13:30", "07:00", "19:00"):
        respuesta = client.post(URL, json=_cita(inicio=bloque(hora=hora)), headers=admision)
        assert respuesta.status_code == 422
        assert "horario de atención" in respuesta.json()["detail"]
    descuadrado = client.post(URL, json=_cita(inicio=bloque(hora="09:15")), headers=admision)
    assert "bloque de 30 minutos" in descuadrado.json()["detail"]


def test_rechaza_domingo_y_mas_de_90_dias(client, login):
    admision = login("admision.rquispe")
    domingo = datetime.combine(proximo_domingo(), datetime.min.time()).replace(hour=9).isoformat()

    assert client.post(URL, json=_cita(inicio=domingo), headers=admision).status_code == 422
    lejano = client.post(URL, json=_cita(inicio=bloque(dias=120)), headers=admision)
    assert "90 días" in lejano.json()["detail"]


def test_acepta_hora_con_zona_horaria(client, login):
    utc = datetime.fromisoformat(bloque(hora="09:00")) + timedelta(hours=5)

    respuesta = client.post(URL, json=_cita(inicio=utc.isoformat() + "Z"), headers=login("admision.rquispe"))

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha_hora_inicio"].endswith("09:00:00")


def test_medico_o_consultorio_inexistente_responde_404(client, login):
    admision = login("admision.rquispe")

    assert client.post(URL, json=_cita(medico=999), headers=admision).status_code == 404
    assert client.post(URL, json=_cita(consultorio=999), headers=admision).status_code == 404
    assert client.post(URL, json=_cita(paciente=999), headers=admision).status_code == 404


def test_solo_admision_agenda(client, login):
    respuesta = client.post(URL, json=_cita(), headers=login("enf.rpaz"))

    assert respuesta.status_code == 403


def test_copago_estimado_segun_convenio(client, login):
    admision = login("admision.rquispe")

    def copago(paciente, medico):
        return client.get(
            f"{URL}/copago-estimado", params={"id_paciente": paciente, "id_medico": medico}, headers=admision
        ).json()

    pacifico_general = copago(1, RAMOS)
    assert (pacifico_general["precio"], pacifico_general["copago"]) == (80.0, 32.0)
    pacifico_especialidad = copago(3, MENDOZA)
    assert (pacifico_especialidad["monto_cubierto"], pacifico_especialidad["copago"]) == (97.75, 42.25)
    assert copago(4, RAMOS)["copago"] == 80.0
    assert copago(9, RAMOS)["copago"] == 0.0


def test_lista_las_citas_de_hoy(client, login):
    citas = client.get(URL, headers=login("admision.rquispe")).json()

    estados = {c["estado"] for c in citas}
    assert {"CONFIRMADA", "EN_ESPERA", "ATENDIDA", "CANCELADA", "NO_ASISTIO"} <= estados


def test_medico_solo_ve_su_agenda(client, login):
    citas = client.get(URL, headers=login("med.jvaldivia")).json()

    assert citas
    assert {c["medico"]["id_medico"] for c in citas} == {1}
    assert any(c["paciente"]["alergias"] == "Amoxicilina" for c in citas)


def test_citas_de_un_paciente_y_detalle(client, login):
    admision = login("admision.rquispe")

    citas = client.get(URL, params={"id_paciente": 10}, headers=admision).json()
    reprogramada = next(c for c in citas if c["estado"] == "REPROGRAMADA")

    assert reprogramada["id_cita_nueva"] is not None
    detalle = client.get(f"{URL}/{reprogramada['id_cita_nueva']}", headers=admision).json()
    assert detalle["id_cita_origen"] == reprogramada["id_cita"]
    assert client.get(f"{URL}/9999", headers=admision).status_code == 404


def test_catalogos_de_la_agenda(client, login):
    cabecera = login("enf.rpaz")

    especialidades = client.get("/api/v1/especialidades", headers=cabecera).json()
    medicos = client.get("/api/v1/medicos", params={"id_especialidad": 1}, headers=cabecera).json()

    assert {"nombre": "Medicina General", "id_especialidad": 1, "medicos_activos": 2} in especialidades
    assert [m["apellidos"] for m in medicos] == ["Núñez Arce", "Ramos Peña"]
    assert len(client.get("/api/v1/consultorios", headers=cabecera).json()) == 12
