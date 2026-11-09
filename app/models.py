"""Modelos ORM alineados con database/01-esquema.sql."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Convenio(Base):
    __tablename__ = "convenios"

    id_convenio: Mapped[int] = mapped_column(primary_key=True)
    codigo_convenio: Mapped[str] = mapped_column(String(20), unique=True)
    nombre_institucion: Mapped[str] = mapped_column(String(100))
    tipo_convenio: Mapped[str] = mapped_column(String(12))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
