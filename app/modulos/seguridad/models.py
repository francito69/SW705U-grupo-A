from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import tiempo
from app.database import Base

ROLES = ("ADMISION", "MEDICO", "ENFERMERA", "LABORATORIO", "CAJA", "GERENCIA", "ADMINISTRADOR")


class Rol(Base):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "nombre IN ('ADMISION', 'MEDICO', 'ENFERMERA', 'LABORATORIO', "
            "'CAJA', 'GERENCIA', 'ADMINISTRADOR')",
            name="ck_roles_nombre",
        ),
    )

    id_rol: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(150))


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )

    rol: Mapped[Rol] = relationship(lazy="joined")
