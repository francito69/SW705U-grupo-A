"""HU04 - Registro de atención médica con diagnóstico CIE-10 y prescripción."""

URL = "/api/v1/atenciones"

CONSULTA = {
    "motivo_consulta": "Control de diabetes mellitus tipo 2",
    "anamnesis": "Glucosa capilar en ayunas de 132 mg/dL. Sin síntomas de alarma.",
    "indicaciones": "Dieta para diabético y caminatas diarias",
    "diagnosticos": [{"codigo_cie10": "e11.9", "tipo": "PRINCIPAL"}, {"codigo_cie10": "I10", "tipo": "SECUNDARIO"}],
    "prescripciones": [
        {"medicamento": "Metformina", "presentacion": "850 mg tableta", "frecuencia": "Cada 12 horas", "duracion": "30 días"}
    ],
}


def _atencion_de(client, login, paciente: int, medico: str = "med.aramos") -> dict:
    citas = client.get("/api/v1/citas", headers=login(medico)).json()
    return next(c for c in citas if c["paciente"]["id_paciente"] == paciente and c["atencion"])


def test_finaliza_la_atencion_y_la_cita_queda_atendida(client, login):
    medico = login("med.aramos")
    cita = _atencion_de(client, login, paciente=12)
    id_atencion = cita["atencion"]["id_atencion"]

    iniciada = client.post(f"{URL}/{id_atencion}/iniciar", headers=medico)
    respuesta = client.post(f"{URL}/{id_atencion}/finalizar", json=CONSULTA, headers=medico)

    assert iniciada.json()["inicio_consulta"] is not None
    assert respuesta.status_code == 200
    atencion = respuesta.json()
    assert atencion["estado"] == "FINALIZADA"
    assert [d["codigo"] for d in atencion["diagnosticos"]] == ["E11.9", "I10"]
    assert atencion["prescripciones"][0]["medicamento"] == "Metformina"
    assert client.get(f"/api/v1/citas/{cita['id_cita']}", headers=medico).json()["estado"] == "ATENDIDA"


def test_sin_diagnostico_cie10_no_se_guarda(client, login):
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]

    respuesta = client.post(
        f"{URL}/{id_atencion}/finalizar", json={**CONSULTA, "diagnosticos": []}, headers=login("med.aramos")
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["errores"][0]["campo"] == "diagnosticos"
    assert "catálogo oficial" in respuesta.json()["detail"]


def test_codigo_fuera_del_catalogo_responde_422(client, login):
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]
    consulta = {**CONSULTA, "diagnosticos": [{"codigo_cie10": "X99.9", "tipo": "PRINCIPAL"}]}

    respuesta = client.post(f"{URL}/{id_atencion}/finalizar", json=consulta, headers=login("med.aramos"))

    assert respuesta.status_code == 422
    assert "X99.9" in respuesta.json()["detail"]


def test_solo_un_diagnostico_principal(client, login):
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]
    dobles = [{"codigo_cie10": "E11.9", "tipo": "PRINCIPAL"}, {"codigo_cie10": "I10", "tipo": "PRINCIPAL"}]

    respuesta = client.post(
        f"{URL}/{id_atencion}/finalizar", json={**CONSULTA, "diagnosticos": dobles}, headers=login("med.aramos")
    )

    assert respuesta.status_code == 422


def test_atencion_finalizada_queda_bloqueada(client, login):
    medico = login("med.aramos")
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]
    client.post(f"{URL}/{id_atencion}/finalizar", json=CONSULTA, headers=medico)

    respuesta = client.post(f"{URL}/{id_atencion}/finalizar", json=CONSULTA, headers=medico)

    assert respuesta.status_code == 409
    assert "bloqueados" in respuesta.json()["detail"]


def test_otro_medico_no_puede_cerrar_la_atencion(client, login):
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]

    respuesta = client.post(f"{URL}/{id_atencion}/finalizar", json=CONSULTA, headers=login("med.cmendoza"))

    assert respuesta.status_code == 403
    assert client.post(f"{URL}/{id_atencion}/iniciar", headers=login("med.cmendoza")).status_code == 403


def test_alerta_de_alergia_exige_confirmacion(client, login):
    medico = login("med.aramos")
    id_atencion = _atencion_de(client, login, paciente=1)["atencion"]["id_atencion"]
    consulta = {
        **CONSULTA,
        "diagnosticos": [{"codigo_cie10": "J03.9", "tipo": "PRINCIPAL"}],
        "prescripciones": [
            {"medicamento": "Amoxicilina", "presentacion": "500 mg cápsula", "frecuencia": "Cada 8 horas", "duracion": "7 días"}
        ],
    }

    advertencia = client.post(f"{URL}/{id_atencion}/finalizar", json=consulta, headers=medico)
    confirmada = client.post(
        f"{URL}/{id_atencion}/finalizar", json={**consulta, "confirmar_alergias": True}, headers=medico
    )

    assert advertencia.status_code == 409
    assert advertencia.json()["coincidencias"][0]["alergia"] == "penicilina"
    assert confirmada.status_code == 200


def test_detalle_de_atencion_solo_para_medicos(client, login):
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]

    assert client.get(f"{URL}/{id_atencion}", headers=login("med.aramos")).status_code == 200
    assert client.get(f"{URL}/{id_atencion}", headers=login("enf.rpaz")).status_code == 403
    assert client.get(f"{URL}/99999", headers=login("med.aramos")).status_code == 404


def test_enfermeria_no_cierra_atenciones(client, login):
    id_atencion = _atencion_de(client, login, paciente=12)["atencion"]["id_atencion"]

    respuesta = client.post(f"{URL}/{id_atencion}/finalizar", json=CONSULTA, headers=login("enf.rpaz"))

    assert respuesta.status_code == 403


def test_usuario_medico_sin_ficha_de_medico(client, login):
    from sqlalchemy import update

    from app.database import SessionLocal
    from app.modulos.agenda.models import Medico
    from app.modulos.seguridad.service import buscar_por_username

    with SessionLocal() as db:
        usuario = buscar_por_username(db, "med.esalinas")
        db.execute(update(Medico).where(Medico.id_usuario == usuario.id_usuario).values(id_usuario=None))
        db.commit()

    respuesta = client.get(f"{URL}/en-curso", headers=login("med.esalinas"))

    assert respuesta.status_code == 403


def test_busqueda_cie10_por_codigo_y_sin_tildes(client, login):
    medico = login("med.aramos")

    por_codigo = client.get("/api/v1/diagnosticos-cie10", params={"q": "i10"}, headers=medico).json()
    por_texto = client.get("/api/v1/diagnosticos-cie10", params={"q": "hipertension"}, headers=medico).json()
    sin_filtro = client.get("/api/v1/diagnosticos-cie10", params={"limite": 5}, headers=medico).json()

    assert por_codigo[0]["codigo"] == "I10"
    assert "I10" in [d["codigo"] for d in por_texto]
    assert len(sin_filtro) == 5
