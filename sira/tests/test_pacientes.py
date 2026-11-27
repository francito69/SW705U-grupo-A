"""HU03 - Registro y búsqueda de paciente con validación de convenio."""

import pytest

pytestmark = pytest.mark.integration

URL = "/api/v1/pacientes"

NUEVO = {
    "tipo_documento": "DNI",
    "numero_documento": "48123456",
    "nombres": "Carla",
    "apellido_paterno": "Ríos",
    "apellido_materno": "León",
    "fecha_nacimiento": "1993-05-20",
    "sexo": "F",
    "telefono": "987 111 222",
    "email": "carla.rios@correo.test",
    "direccion": "Av. Javier Prado Este 100, San Borja",
    "id_convenio": 2,
}


def test_registra_paciente_nuevo_y_queda_disponible(client, login):
    admision = login("admision.rquispe")

    creado = client.post(URL, json=NUEVO, headers=admision)

    assert creado.status_code == 201
    assert creado.json()["telefono"] == "987111222"
    assert creado.json()["convenio"]["nombre_institucion"] == "Rímac EPS"
    encontrados = client.get(URL, params={"numero_documento": "48123456"}, headers=admision).json()
    assert [p["id_paciente"] for p in encontrados] == [creado.json()["id_paciente"]]


def test_documento_duplicado_responde_409_con_la_ficha_existente(client, login):
    duplicado = {**NUEVO, "numero_documento": "45892014"}

    respuesta = client.post(URL, json=duplicado, headers=login("admision.rquispe"))

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Paciente ya registrado"
    assert respuesta.json()["id_paciente"] == 1


def test_valida_formato_de_celular(client, login):
    respuesta = client.post(URL, json={**NUEVO, "telefono": "12345"}, headers=login("admision.rquispe"))

    assert respuesta.status_code == 422
    assert "celular" in respuesta.json()["detail"]


def test_valida_formato_de_correo(client, login):
    respuesta = client.post(URL, json={**NUEVO, "email": "no-es-correo"}, headers=login("admision.rquispe"))

    assert respuesta.status_code == 422
    assert respuesta.json()["errores"][0]["campo"] == "email"


def test_valida_dni_de_ocho_digitos(client, login):
    respuesta = client.post(URL, json={**NUEVO, "numero_documento": "1234"}, headers=login("admision.rquispe"))

    assert respuesta.status_code == 422
    assert "8 dígitos" in respuesta.json()["detail"]


def test_convenio_inexistente_responde_422(client, login):
    respuesta = client.post(URL, json={**NUEVO, "id_convenio": 999}, headers=login("admision.rquispe"))

    assert respuesta.status_code == 422
    assert "convenio" in respuesta.json()["detail"].lower()


def test_fecha_de_nacimiento_futura_responde_422(client, login):
    respuesta = client.post(
        URL, json={**NUEVO, "fecha_nacimiento": "2999-01-01"}, headers=login("admision.rquispe")
    )

    assert respuesta.status_code == 422


def test_correo_vacio_se_guarda_como_nulo(client, login):
    respuesta = client.post(URL, json={**NUEVO, "email": ""}, headers=login("admision.rquispe"))

    assert respuesta.status_code == 201
    assert respuesta.json()["email"] is None


def test_busca_por_apellido_sin_tildes(client, login):
    encontrados = client.get(URL, params={"q": "huaman"}, headers=login("admision.rquispe")).json()

    assert "Rosa Huamán Díaz" in [p["nombre_completo"] for p in encontrados]


def test_busca_por_inicio_de_documento(client, login):
    encontrados = client.get(URL, params={"q": "4589"}, headers=login("admision.rquispe")).json()

    assert encontrados[0]["numero_documento"] == "45892014"


def test_admision_no_ve_alergias_y_enfermeria_si(client, login):
    admision = client.get(f"{URL}/1", headers=login("admision.rquispe")).json()
    enfermeria = client.get(f"{URL}/1", headers=login("enf.rpaz")).json()

    assert admision["alergias"] is None
    assert enfermeria["alergias"] == "Penicilina y sulfas"


def test_medico_no_puede_registrar_pacientes(client, login):
    respuesta = client.post(URL, json=NUEVO, headers=login("med.aramos"))

    assert respuesta.status_code == 403


def test_paciente_inexistente_responde_404(client, login):
    assert client.get(f"{URL}/9999", headers=login("admision.rquispe")).status_code == 404


def test_actualiza_filiacion_y_queda_auditado(client, login):
    respuesta = client.patch(
        f"{URL}/7",
        json={"email": "felipe.paredes@correo.test", "telefono": "987000111", "nombres": ""},
        headers=login("admision.rquispe"),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == "felipe.paredes@correo.test"
    assert respuesta.json()["nombres"] == "Felipe"
    bitacora = client.get(
        "/api/v1/auditoria", params={"accion": "UPDATE", "tabla": "pacientes"}, headers=login("admin.sira")
    ).json()
    assert bitacora["registros"][0]["datos_nuevos"]["telefono"] == "987000111"


def test_actualizar_con_convenio_inexistente_responde_422(client, login):
    respuesta = client.patch(f"{URL}/7", json={"id_convenio": 500}, headers=login("admision.rquispe"))

    assert respuesta.status_code == 422


def test_medico_actualiza_alergias(client, login):
    respuesta = client.patch(
        f"{URL}/13/antecedentes", json={"alergias": "Metamizol"}, headers=login("med.aramos")
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["alergias"] == "Metamizol"


def test_caja_no_modifica_antecedentes_y_queda_auditado(client, login):
    respuesta = client.patch(
        f"{URL}/13/antecedentes", json={"alergias": "Ninguna"}, headers=login("caja.evargas")
    )

    assert respuesta.status_code == 403
    bitacora = client.get(
        "/api/v1/auditoria", params={"accion": "ACCESO_DENEGADO"}, headers=login("admin.sira")
    ).json()
    assert bitacora["registros"][0]["id_registro_afectado"] == 13
