"""Configuración leída de variables de entorno.

Ningún secreto se escribe en el código: si SIRA_SECRET_KEY no existe se genera una
clave aleatoria al iniciar el proceso (las sesiones se pierden al reiniciar).
"""

import os
import secrets
from dataclasses import dataclass


def _booleano(nombre: str, defecto: bool) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes", "on")


def _entero(nombre: str, defecto: int) -> int:
    valor = os.getenv(nombre)
    return int(valor) if valor else defecto


@dataclass(frozen=True)
class Configuracion:
    secret_key: str
    token_minutos: int
    bcrypt_rondas: int
    worker_activo: bool
    worker_segundos: int
    modo_demo: bool
    cors_origenes: tuple[str, ...]


def cargar() -> Configuracion:
    origenes = os.getenv("SIRA_CORS_ORIGENES", "http://localhost:5173,http://127.0.0.1:5173")
    return Configuracion(
        secret_key=os.getenv("SIRA_SECRET_KEY") or secrets.token_urlsafe(32),
        token_minutos=_entero("SIRA_TOKEN_MINUTOS", 480),
        bcrypt_rondas=_entero("SIRA_BCRYPT_RONDAS", 12),
        worker_activo=_booleano("SIRA_WORKER", True),
        worker_segundos=_entero("SIRA_WORKER_SEGUNDOS", 60),
        modo_demo=_booleano("SIRA_MODO_DEMO", True),
        cors_origenes=tuple(o.strip() for o in origenes.split(",") if o.strip()),
    )


config = cargar()
