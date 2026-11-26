import os
from datetime import date, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient

PASSWORD = "Sira2026"
CLAVE_PRUEBAS = "clave-solo-para-pruebas-automaticas-sira"


def pytest_configure(config):
    # BD SQLite en memoria: cada prueba parte de cero y solo usa datos ficticios.
    # SIRA_TEST_DATABASE_URL permite correr la misma suite contra PostgreSQL.
    os.environ["DATABASE_URL"] = os.getenv("SIRA_TEST_DATABASE_URL", "sqlite://")
    os.environ["SIRA_WORKER"] = "0"
    os.environ["SIRA_BCRYPT_RONDAS"] = "4"
    os.environ["SIRA_SECRET_KEY"] = CLAVE_PRUEBAS
    os.environ["SIRA_MODO_DEMO"] = "1"


@pytest.fixture
def client():
    from app.database import Base, engine
    from app.main import app

    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def login(client):
    """Devuelve las cabeceras de autorización de un usuario ficticio."""
    sesiones = {}

    def _login(username: str) -> dict:
        if username not in sesiones:
            respuesta = client.post("/api/v1/auth/login", json={"username": username, "password": PASSWORD})
            assert respuesta.status_code == 200, respuesta.text
            sesiones[username] = {"Authorization": f"Bearer {respuesta.json()['access_token']}"}
        return sesiones[username]

    return _login


def dia_habil(dias: int = 14) -> date:
    from app.core import tiempo

    fecha = tiempo.hoy() + timedelta(days=dias)
    while fecha.weekday() == 6:
        fecha += timedelta(days=1)
    return fecha


def bloque(dias: int = 14, hora: str = "09:00") -> str:
    return datetime.combine(dia_habil(dias), time.fromisoformat(hora)).isoformat()


def proximo_domingo() -> date:
    from app.core import tiempo

    fecha = tiempo.hoy() + timedelta(days=1)
    while fecha.weekday() != 6:
        fecha += timedelta(days=1)
    return fecha
