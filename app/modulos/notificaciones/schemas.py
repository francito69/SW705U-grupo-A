from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificacionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_notificacion: int
    id_cita: int | None
    tipo_evento: str
    canal: str
    destinatario: str
    mensaje: str
    programado_para: datetime
    estado: str
    intentos: int
    error_detalle: str | None
    procesado_en: datetime | None
    creado_en: datetime


class BandejaNotificaciones(BaseModel):
    resumen: dict[str, int]
    notificaciones: list[NotificacionSalida]


class ResultadoProceso(BaseModel):
    procesadas: int
    enviadas: int
    reintentos: int
    fallidas: int
