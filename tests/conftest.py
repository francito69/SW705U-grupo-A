import os

import pytest
from fastapi.testclient import TestClient


def pytest_configure(config):
    # BD SQLite en memoria: cada prueba parte de cero y solo usa datos ficticios.
    os.environ["DATABASE_URL"] = "sqlite://"


@pytest.fixture
def client():
    from app.database import Base, engine
    from app.main import app

    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as cliente:
        yield cliente
