"""Conexión a la base de datos.

La URL se toma de la variable de entorno DATABASE_URL (en producción, PostgreSQL 16+,
por ejemplo postgresql+psycopg://usuario:clave@localhost:5432/sira). Si no existe, se
usa un archivo SQLite local para desarrollo. Las credenciales nunca se escriben en el código.
"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sira_dev.db")


def crear_engine(url: str):
    if url.startswith("sqlite"):
        opciones = {"connect_args": {"check_same_thread": False, "timeout": 15}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            # Una sola conexión compartida para que la BD en memoria persista.
            opciones["poolclass"] = StaticPool
        motor = create_engine(url, **opciones)

        @event.listens_for(motor, "connect")
        def _activar_claves_foraneas(conexion, _registro):
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return motor
    return create_engine(url, pool_pre_ping=True)


engine = crear_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
