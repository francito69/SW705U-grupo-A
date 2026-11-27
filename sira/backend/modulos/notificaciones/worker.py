"""Trabajador en segundo plano del outbox: despierta cada N segundos (SAD 5.2.2)."""

import asyncio
import logging

from backend.database import SessionLocal

from . import service

logger = logging.getLogger("sira.notificaciones")


def procesar_una_vez() -> dict:
    with SessionLocal() as db:
        resultado = service.procesar_pendientes(db)
        db.commit()
    if resultado["procesadas"]:
        logger.info("Outbox: %s", resultado)
    return resultado


async def bucle(intervalo_segundos: int) -> None:
    while True:
        try:
            await asyncio.to_thread(procesar_una_vez)
        except Exception:
            logger.exception("Error al procesar el outbox; se reintentará en el siguiente ciclo")
        await asyncio.sleep(intervalo_segundos)
