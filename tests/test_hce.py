"""HU01 - Consulta de la historia clínica electrónica unificada."""

import time

URL = "/api/v1/pacientes/{}/hce"


def test_medico_consulta_la_hce_cronologica_multiespecialidad(client, login):
    respuesta = client.get(URL.format(1), params={"limite": 50}, headers=login("med.aramos"))

    assert respuesta.status_code == 200
    hce = respuesta.json()
    assert hce["paciente"]["alergias"] == "Penicilina y sulfas"
    assert hce["paciente"]["antecedentes_medicos"] == "Hipertensión arterial controlada"
    fechas = [a["fecha"] for a in hce["atenciones"]]
    assert fechas == sorted(fechas, reverse=True)
    especialidades = {a["medico"]["especialidad"] for a in hce["atenciones"]}
    assert {"Medicina General", "Cardiología", "Dermatología"} <= especialidades
    con_receta = next(a for a in hce["atenciones"] if a["prescripciones"])
    assert con_receta["diagnosticos"][0]["descripcion"]


def test_la_atencion_anulada_se_conserva_marcada(client, login):
    hce = client.get(URL.format(1), params={"limite": 50}, headers=login("med.aramos")).json()

    anulada = next(a for a in hce["atenciones"] if a["anulado"])
    assert anulada["motivo_anulacion"].startswith("Registro duplicado")


def test_la_hce_se_pagina_de_10_en_10(client, login):
    pagina = client.get(URL.format(1), params={"limite": 2}, headers=login("med.aramos")).json()

    assert len(pagina["atenciones"]) == 2
    assert pagina["total_atenciones"] > 2


def test_caja_recibe_403_y_el_intento_queda_en_la_bitacora(client, login):
    respuesta = client.get(URL.format(3), headers=login("caja.evargas"))

    assert respuesta.status_code == 403
    bitacora = client.get(
        "/api/v1/auditoria",
        params={"accion": "ACCESO_DENEGADO", "tabla": "pacientes", "usuario": "caja"},
        headers=login("admin.sira"),
    ).json()
    reciente = bitacora["registros"][0]
    assert reciente["id_registro_afectado"] == 3
    assert reciente["direccion_ip"]


def test_admision_y_enfermeria_no_acceden_a_la_hce(client, login):
    assert client.get(URL.format(1), headers=login("admision.rquispe")).status_code == 403
    assert client.get(URL.format(1), headers=login("enf.rpaz")).status_code == 403


def test_cada_consulta_de_la_hce_queda_auditada(client, login):
    client.get(URL.format(1), headers=login("med.cmendoza"))

    bitacora = client.get(
        "/api/v1/auditoria", params={"accion": "SELECT", "usuario": "cmendoza"}, headers=login("admin.sira")
    ).json()
    assert bitacora["registros"][0]["nombre_tabla"] == "pacientes"
    assert bitacora["registros"][0]["id_registro_afectado"] == 1


def test_hce_de_paciente_inexistente_responde_404(client, login):
    assert client.get(URL.format(9999), headers=login("med.aramos")).status_code == 404


def test_la_hce_responde_en_menos_de_2_segundos(client, login):
    medico = login("med.aramos")

    inicio = time.perf_counter()
    respuesta = client.get(URL.format(1), headers=medico)

    assert respuesta.status_code == 200
    assert time.perf_counter() - inicio < 2
