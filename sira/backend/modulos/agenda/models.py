from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    func,
    text,
    true,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core import tiempo
from backend.database import Base

ESTADOS_ACTIVOS = ("CONFIRMADA", "EN_ESPERA")


class Especialidad(Base):
    __tablename__ = "especialidades"

    id_especialidad: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)


class Medico(Base):
    __tablename__ = "medicos"

    id_medico: Mapped[int] = mapped_column(primary_key=True)
    cmp: Mapped[str] = mapped_column(String(10), unique=True)
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(120))
    id_especialidad: Mapped[int] = mapped_column(ForeignKey("especialidades.id_especialidad"))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    especialidad: Mapped[Especialidad] = relationship(lazy="joined")

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"


class Consultorio(Base):
    __tablename__ = "consultorios"
    __table_args__ = (CheckConstraint("piso >= 1", name="ck_consultorios_piso"),)

    id_consultorio: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(10), unique=True)
    piso: Mapped[int] = mapped_column(SmallInteger)
    descripcion: Mapped[str | None] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())


class Cita(Base):
    __tablename__ = "citas"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('CONFIRMADA', 'EN_ESPERA', 'ATENDIDA', 'CANCELADA', "
            "'REPROGRAMADA', 'NO_ASISTIO')",
            name="ck_citas_estado",
        ),
        CheckConstraint(
            "canal_agendamiento IN ('ADMISION', 'PORTAL_WEB', 'TELEFONICO')", name="ck_citas_canal"
        ),
        CheckConstraint("fecha_hora_fin > fecha_hora_inicio", name="chk_cita_rango"),
        CheckConstraint(
            "estado NOT IN ('CANCELADA', 'REPROGRAMADA') OR motivo_cancelacion IS NOT NULL",
            name="chk_cita_motivo",
        ),
        CheckConstraint(
            "estado NOT IN ('EN_ESPERA', 'ATENDIDA') OR hora_llegada IS NOT NULL",
            name="chk_cita_llegada",
        ),
        Index("idx_citas_medico_inicio", "id_medico", "fecha_hora_inicio"),
        Index("idx_citas_paciente", "id_paciente"),
    )

    id_cita: Mapped[int] = mapped_column(primary_key=True)
    id_paciente: Mapped[int] = mapped_column(ForeignKey("pacientes.id_paciente"))
    id_medico: Mapped[int] = mapped_column(ForeignKey("medicos.id_medico"))
    id_consultorio: Mapped[int] = mapped_column(ForeignKey("consultorios.id_consultorio"))
    fecha_hora_inicio: Mapped[datetime] = mapped_column(DateTime)
    fecha_hora_fin: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(15), default="CONFIRMADA", server_default="CONFIRMADA")
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text)
    hora_llegada: Mapped[datetime | None] = mapped_column(DateTime)
    id_cita_origen: Mapped[int | None] = mapped_column(ForeignKey("citas.id_cita"), unique=True)
    canal_agendamiento: Mapped[str] = mapped_column(
        String(12), default="ADMISION", server_default="ADMISION"
    )
    creado_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )

    medico: Mapped[Medico] = relationship(lazy="joined")
    consultorio: Mapped[Consultorio] = relationship(lazy="joined")


_tabla = Cita.__table__
for _nombre, _columna in (
    ("no_solapamiento_medico", _tabla.c.id_medico),
    ("no_solapamiento_consultorio", _tabla.c.id_consultorio),
):
    _tabla.append_constraint(
        ExcludeConstraint(
            (_columna, "="),
            (func.tsrange(_tabla.c.fecha_hora_inicio, _tabla.c.fecha_hora_fin), "&&"),
            using="gist",
            name=_nombre,
            where=text("estado IN ('CONFIRMADA', 'EN_ESPERA')"),
        ).ddl_if(dialect="postgresql")
    )
