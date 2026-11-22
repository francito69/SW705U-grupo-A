from datetime import datetime, timedelta, timezone

import jwt
import pytest

from conftest import CLAVE_PRUEBAS, PASSWORD

pytestmark = pytest.mark.integration

LOGIN = "/api/v1/auth/login"


def test_login_correcto_devuelve_token_y_rol(client):
    respuesta = client.post(LOGIN, json={"username": "med.aramos", "password": PASSWORD})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["usuario"]["rol"] == "MEDICO"
    assert cuerpo["usuario"]["medico"]["especialidad"] == "Medicina General"


def test_clave_incorrecta_responde_401_y_queda_en_bitacora(client, login):
    respuesta = client.post(LOGIN, json={"username": "caja.evargas", "password": "otra-clave"})

    assert respuesta.status_code == 401
    bitacora = client.get(
        "/api/v1/auditoria",
        params={"accion": "ACCESO_DENEGADO", "tabla": "usuarios"},
        headers=login("admin.sira"),
    ).json()
    assert any(r["username"] == "caja.evargas" for r in bitacora["registros"])


def test_usuario_inexistente_responde_401(client):
    respuesta = client.post(LOGIN, json={"username": "nadie.aqui", "password": PASSWORD})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Usuario o contraseña incorrectos"


def test_endpoint_protegido_sin_token_responde_401(client):
    assert client.get("/api/v1/citas").status_code == 401


def test_token_alterado_responde_401(client):
    respuesta = client.get("/api/v1/citas", headers={"Authorization": "Bearer token.falso.123"})

    assert respuesta.status_code == 401


def test_token_expirado_responde_401(client):
    vencido = jwt.encode(
        {"sub": "1", "rol": "ADMISION", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        CLAVE_PRUEBAS,
        algorithm="HS256",
    )

    respuesta = client.get("/api/v1/citas", headers={"Authorization": f"Bearer {vencido}"})

    assert respuesta.status_code == 401
    assert "expiró" in respuesta.json()["detail"]


def test_me_devuelve_el_usuario_autenticado(client, login):
    respuesta = client.get("/api/v1/auth/me", headers=login("enf.rpaz"))

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "ENFERMERA"
    assert respuesta.json()["medico"] is None


def test_usuario_inactivo_no_puede_ingresar(client):
    from app.database import SessionLocal
    from app.modulos.seguridad.service import buscar_por_username

    with SessionLocal() as db:
        buscar_por_username(db, "lab.dchavez").activo = False
        db.commit()

    respuesta = client.post(LOGIN, json={"username": "lab.dchavez", "password": PASSWORD})

    assert respuesta.status_code == 403


def test_cuentas_de_demostracion(client):
    respuesta = client.get("/api/v1/auth/demo")

    assert respuesta.status_code == 200
    assert respuesta.json()["password"] == PASSWORD
    roles = {c["rol"] for c in respuesta.json()["cuentas"]}
    assert {"ADMISION", "MEDICO", "ENFERMERA", "GERENCIA"} <= roles
