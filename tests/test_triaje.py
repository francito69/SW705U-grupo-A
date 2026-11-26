"""HU05 - Registro de triaje y signos vitales por enfermería."""

import pytest

pytestmark = pytest.mark.integration

URL = "/api/v1/triajes"

SIGNOS = {
    "presion_sistolica": 120,
    "presion_diastolica": 80,
    "temperatura": 36.8,
    "frecuencia_cardiaca": 76,
    "frecuencia_respiratoria": 16,
    "saturacion_oxigeno": 98,
    "peso": 70.5,
    "talla": 1.70,
    "observaciones": "Refiere dolor lumbar",
}


def _en_espera_sin_triaje(client, login):
    citas = client.get("/api/v1/citas", params={"estado": "EN_ESPERA"}, headers=login("enf.rpaz")).json()
    return next(c for c in citas if c["atencion"] is None)


def test_enfermera_registra_triaje_y_el_medico_lo_ve(client, login):
    cita = _en_espera_sin_triaje(client, login)

    respuesta = client.post(URL, json={"id_cita": cita["id_cita"], **SIGNOS}, headers=login("enf.rpaz"))

    assert respuesta.status_code == 201
    atencion = respuesta.json()
    assert atencion["estado"] == "EN_CURSO"
    assert atencion["triaje"]["imc"] == 24.4
    assert atencion["triaje"]["alertas"] == []
    medico = "med.aramos" if cita["medico"]["id_medico"] == 3 else "med.jvaldivia"
    hce = client.get(f"/api/v1/pacientes/{cita['paciente']['id_paciente']}/hce", headers=login(medico)).json()
    assert hce["atenciones"][0]["triaje"]["presion_sistolica"] == 120


def test_presion_alta_marca_alerta_en_la_lista_de_espera(client, login):
    cita = _en_espera_sin_triaje(client, login)
    signos = {**SIGNOS, "presion_sistolica": 150, "presion_diastolica": 95}

    respuesta = client.post(URL, json={"id_cita": cita["id_cita"], **signos}, headers=login("enf.rpaz"))

    assert "Presión arterial elevada (150/95 mmHg)" in respuesta.json()["triaje"]["alertas"]
    en_espera = client.get("/api/v1/citas", params={"estado": "EN_ESPERA"}, headers=login("enf.rpaz")).json()
    marcada = next(c for c in en_espera if c["id_cita"] == cita["id_cita"])
    assert marcada["atencion"]["alertas"]


def test_fiebre_y_saturacion_baja_marcan_alerta(client, login):
    cita = _en_espera_sin_triaje(client, login)
    signos = {**SIGNOS, "temperatura": 38.6, "saturacion_oxigeno": 90}

    alertas = client.post(URL, json={"id_cita": cita["id_cita"], **signos}, headers=login("enf.rpaz")).json()[
        "triaje"
    ]["alertas"]

    assert "Fiebre (38.6 °C)" in alertas
    assert "Saturación baja (90 %)" in alertas


def test_valores_fuera_de_rango_responden_422(client, login):
    cita = _en_espera_sin_triaje(client, login)
    enfermera = login("enf.rpaz")

    fuera = client.post(URL, json={"id_cita": cita["id_cita"], **SIGNOS, "temperatura": 50}, headers=enfermera)
    invertida = client.post(
        URL,
        json={"id_cita": cita["id_cita"], **SIGNOS, "presion_sistolica": 70, "presion_diastolica": 80},
        headers=enfermera,
    )

    assert fuera.status_code == 422
    assert fuera.json()["detail"].startswith("Temperatura")
    assert invertida.status_code == 422
    assert "sistólica" in invertida.json()["detail"]


def test_no_se_registra_dos_veces(client, login):
    cita = _en_espera_sin_triaje(client, login)
    enfermera = login("enf.rpaz")
    client.post(URL, json={"id_cita": cita["id_cita"], **SIGNOS}, headers=enfermera)

    respuesta = client.post(URL, json={"id_cita": cita["id_cita"], **SIGNOS}, headers=enfermera)

    assert respuesta.status_code == 409


def test_requiere_que_el_paciente_haya_llegado(client, login):
    confirmada = next(
        c
        for c in client.get("/api/v1/citas", params={"estado": "CONFIRMADA"}, headers=login("enf.rpaz")).json()
    )

    respuesta = client.post(URL, json={"id_cita": confirmada["id_cita"], **SIGNOS}, headers=login("enf.rpaz"))

    assert respuesta.status_code == 409
    assert "llegada" in respuesta.json()["detail"]


def test_cita_atendida_no_admite_triaje(client, login):
    atendida = next(
        c for c in client.get("/api/v1/citas", params={"estado": "ATENDIDA"}, headers=login("enf.rpaz")).json()
    )

    respuesta = client.post(URL, json={"id_cita": atendida["id_cita"], **SIGNOS}, headers=login("enf.rpaz"))

    assert respuesta.status_code == 409


def test_solo_enfermeria_registra_triaje(client, login):
    cita = _en_espera_sin_triaje(client, login)

    respuesta = client.post(URL, json={"id_cita": cita["id_cita"], **SIGNOS}, headers=login("med.aramos"))

    assert respuesta.status_code == 403


def test_urgencia_de_topico_queda_asignada_al_medico(client, login):
    respuesta = client.post(
        "/api/v1/urgencias",
        json={"id_paciente": 5, "id_medico": 3, **SIGNOS, "temperatura": 38.9},
        headers=login("enf.mcastro"),
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["tipo_atencion"] == "TOPICO_URGENCIA"
    en_curso = client.get("/api/v1/atenciones/en-curso", headers=login("med.aramos")).json()
    nueva = next(a for a in en_curso if a["id_atencion"] == respuesta.json()["id_atencion"])
    assert nueva["paciente"]["alergias"] == "Ácido acetilsalicílico"
    assert nueva["triaje"]["alertas"] == ["Fiebre (38.9 °C)"]


def test_urgencia_con_medico_inexistente_responde_404(client, login):
    respuesta = client.post(
        "/api/v1/urgencias", json={"id_paciente": 5, "id_medico": 99, **SIGNOS}, headers=login("enf.rpaz")
    )

    assert respuesta.status_code == 404
