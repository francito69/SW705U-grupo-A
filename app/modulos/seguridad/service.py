"""T1 - Hash de contraseñas (bcrypt) y tokens JWT firmados con HMAC-SHA256."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import config

from .models import Usuario

ALGORITMO = "HS256"


def hash_password(password: str, rondas: int | None = None) -> str:
    sal = bcrypt.gensalt(rounds=rondas or config.bcrypt_rondas)
    return bcrypt.hashpw(password.encode("utf-8"), sal).decode("ascii")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        return False


def crear_token(usuario: Usuario) -> str:
    emitido = datetime.now(timezone.utc)
    datos = {
        "sub": str(usuario.id_usuario),
        "rol": usuario.rol.nombre,
        "iat": emitido,
        "exp": emitido + timedelta(minutes=config.token_minutos),
    }
    return jwt.encode(datos, config.secret_key, algorithm=ALGORITMO)


def leer_token(token: str) -> dict:
    return jwt.decode(token, config.secret_key, algorithms=[ALGORITMO])


def buscar_por_username(db: Session, username: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.username == username.strip().lower()))
