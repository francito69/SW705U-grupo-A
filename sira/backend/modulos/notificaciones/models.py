from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.core import tiempo
from backend.database import Base

TIPOS_EVENTO = ("RECORDATORIO_24H", "CONFIRMACION_CITA", "AVISO_RESULTADO")
CANALES = ("SMS", "EMAIL", "WHATSAPP")
ESTADOS = ("PENDIENTE", "ENVIADO", "FALLIDO")


class OutboxNotificacion(Base):
    __tablename__ = "outbox_notificaciones"
    __table_args__ = (
        CheckConstraint(
            "tipo_evento IN ('RECORDATORIO_24H', 'CONFIRMACION_CITA', 'AVISO_RESULTADO')",
            name="ck_outbox_tipo",
        ),
        CheckConstraint("canal IN ('SMS', 'EMAIL', 'WHATSAPP')", name="ck_outbox_canal"),
        CheckConstraint("estado IN ('PENDIENTE', 'ENVIADO', 'FALLIDO')", name="ck_outbox_estado"),
        CheckConstraint("intentos >= 0", name="ck_outbox_intentos"),
    )

    id_notificacion: Mapped[int] = mapped_column(primary_key=True)
    id_cita: Mapped[int | None] = mapped_column(ForeignKey("citas.id_cita"))
    tipo_evento: Mapped[str] = mapped_column(String(20))
    canal: Mapped[str] = mapped_column(String(10))
    destinatario: Mapped[str] = mapped_column(String(150))
    mensaje: Mapped[str] = mapped_column(Text)
    programado_para: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(10), default="PENDIENTE", server_default="PENDIENTE")
    intentos: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0")
    error_detalle: Mapped[str | None] = mapped_column(Text)
    procesado_en: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )
