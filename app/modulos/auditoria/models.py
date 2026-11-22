from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core import tiempo
from app.database import Base

ACCIONES = ("SELECT", "INSERT", "UPDATE", "ANULAR", "ACCESO_DENEGADO")


class BitacoraAuditoria(Base):
    __tablename__ = "bitacora_auditoria"
    __table_args__ = (
        CheckConstraint(
            "accion IN ('SELECT', 'INSERT', 'UPDATE', 'ANULAR', 'ACCESO_DENEGADO')",
            name="ck_bitacora_accion",
        ),
        CheckConstraint("accion <> 'ANULAR' OR motivo IS NOT NULL", name="chk_auditoria_motivo"),
    )

    id_auditoria: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer(), "sqlite"), primary_key=True
    )
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    nombre_tabla: Mapped[str] = mapped_column(String(50))
    id_registro_afectado: Mapped[int] = mapped_column(Integer)
    accion: Mapped[str] = mapped_column(String(16))
    direccion_ip: Mapped[str] = mapped_column(String(45).with_variant(INET(), "postgresql"))
    datos_anteriores: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    datos_nuevos: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    motivo: Mapped[str | None] = mapped_column(Text)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )
