"""T3 - NotificationService: encola en el outbox y despacha con reintentos (HU07)."""

import logging
import re
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import tiempo

from .models import OutboxNotificacion

logger = logging.getLogger("sira.notificaciones")

MAX_INTENTOS = 3


class ErrorEnvio(Exception):
    pass


class AdaptadorSimulado:
    """Pasarela SMS/correo simulada: valida el destinatario y deja el mensaje en el log."""

    def enviar(self, canal: str, destinatario: str, mensaje: str) -> None:
        if canal in ("SMS", "WHATSAPP") and not re.fullmatch(r"9\d{8}", destinatario):
            raise ErrorEnvio(f"El número {destinatario} no es un celular válido para {canal}")
        if canal == "EMAIL" and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", destinatario):
            raise ErrorEnvio(f"El correo {destinatario} no es válido")
        logger.info("[%s] %s <- %s", canal, destinatario, mensaje)


def encolar(
    db: Session,
    *,
    id_cita: int | None,
    tipo_evento: str,
    canal: str,
    destinatario: str,
    mensaje: str,
    programado_para: datetime,
) -> OutboxNotificacion:
    notificacion = OutboxNotificacion(
        id_cita=id_cita,
        tipo_evento=tipo_evento,
        canal=canal,
        destinatario=destinatario,
        mensaje=mensaje,
        programado_para=programado_para,
    )
    db.add(notificacion)
    return notificacion


def descartar_pendientes(db: Session, id_cita: int, motivo: str) -> int:
    pendientes = db.scalars(
        select(OutboxNotificacion).where(
            OutboxNotificacion.id_cita == id_cita, OutboxNotificacion.estado == "PENDIENTE"
        )
    ).all()
    for notificacion in pendientes:
        notificacion.estado = "FALLIDO"
        notificacion.error_detalle = f"Descartada: {motivo}"
        notificacion.procesado_en = tiempo.ahora()
    return len(pendientes)


def procesar_pendientes(db: Session, adaptador=None, limite: int = 100) -> dict:
    adaptador = adaptador or AdaptadorSimulado()
    ahora = tiempo.ahora()
    pendientes = db.scalars(
        select(OutboxNotificacion)
        .where(OutboxNotificacion.estado == "PENDIENTE", OutboxNotificacion.programado_para <= ahora)
        .order_by(OutboxNotificacion.programado_para, OutboxNotificacion.id_notificacion)
        .limit(limite)
    ).all()
    resultado = {"procesadas": len(pendientes), "enviadas": 0, "reintentos": 0, "fallidas": 0}
    for notificacion in pendientes:
        notificacion.intentos += 1
        try:
            adaptador.enviar(notificacion.canal, notificacion.destinatario, notificacion.mensaje)
        except ErrorEnvio as error:
            notificacion.error_detalle = str(error)
            if notificacion.intentos >= MAX_INTENTOS:
                notificacion.estado = "FALLIDO"
                notificacion.procesado_en = ahora
                resultado["fallidas"] += 1
            else:
                # Reintento exponencial: 2, 4, 8... minutos después.
                notificacion.programado_para = ahora + timedelta(minutes=2**notificacion.intentos)
                resultado["reintentos"] += 1
        else:
            notificacion.estado = "ENVIADO"
            notificacion.procesado_en = ahora
            notificacion.error_detalle = None
            resultado["enviadas"] += 1
    return resultado


def listar(
    db: Session, *, estado: str | None = None, id_cita: int | None = None, limite: int = 100
) -> list[OutboxNotificacion]:
    consulta = select(OutboxNotificacion)
    if estado:
        consulta = consulta.where(OutboxNotificacion.estado == estado)
    if id_cita:
        consulta = consulta.where(OutboxNotificacion.id_cita == id_cita)
    return list(
        db.scalars(
            consulta.order_by(
                OutboxNotificacion.programado_para.desc(), OutboxNotificacion.id_notificacion.desc()
            ).limit(limite)
        )
    )


def resumen(db: Session) -> dict[str, int]:
    conteo = {"PENDIENTE": 0, "ENVIADO": 0, "FALLIDO": 0}
    filas = db.execute(
        select(OutboxNotificacion.estado, func.count()).group_by(OutboxNotificacion.estado)
    ).all()
    for estado, cantidad in filas:
        conteo[estado] = cantidad
    return conteo
