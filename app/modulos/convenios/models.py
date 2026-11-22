from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, String, func, true
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Convenio(Base):
    __tablename__ = "convenios"
    __table_args__ = (
        CheckConstraint("tipo_convenio IN ('PARTICULAR', 'EPS', 'SOAT')", name="ck_convenios_tipo"),
    )

    id_convenio: Mapped[int] = mapped_column(primary_key=True)
    codigo_convenio: Mapped[str] = mapped_column(String(20), unique=True)
    nombre_institucion: Mapped[str] = mapped_column(String(100))
    tipo_convenio: Mapped[str] = mapped_column(String(12))
    contacto_operativo: Mapped[str | None] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())


class ServicioMedico(Base):
    __tablename__ = "servicios_medicos"
    __table_args__ = (
        CheckConstraint(
            "tipo_servicio IN ('CONSULTA', 'LABORATORIO', 'IMAGENES', 'PROCEDIMIENTO')",
            name="ck_servicios_tipo",
        ),
        CheckConstraint("precio_base_particular >= 0", name="ck_servicios_precio"),
    )

    id_servicio: Mapped[int] = mapped_column(primary_key=True)
    codigo_servicio: Mapped[str] = mapped_column(String(20), unique=True)
    nombre_servicio: Mapped[str] = mapped_column(String(150))
    tipo_servicio: Mapped[str] = mapped_column(String(15))
    precio_base_particular: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())


class TarifarioServicio(Base):
    __tablename__ = "tarifarios_servicios"
    __table_args__ = (
        CheckConstraint("precio_convenido >= 0", name="ck_tarifario_precio"),
        CheckConstraint("porcentaje_cobertura BETWEEN 0 AND 100", name="ck_tarifario_cobertura"),
        CheckConstraint("copago_fijo >= 0", name="ck_tarifario_copago"),
        CheckConstraint(
            "vigente_hasta IS NULL OR vigente_hasta > vigente_desde", name="chk_tarifario_vigencia"
        ),
    )

    id_tarifario: Mapped[int] = mapped_column(primary_key=True)
    id_servicio: Mapped[int] = mapped_column(ForeignKey("servicios_medicos.id_servicio"))
    id_convenio: Mapped[int] = mapped_column(ForeignKey("convenios.id_convenio"))
    precio_convenido: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    porcentaje_cobertura: Mapped[float] = mapped_column(Numeric(5, 2, asdecimal=False))
    copago_fijo: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), default=0, server_default="0"
    )
    vigente_desde: Mapped[date] = mapped_column(Date)
    vigente_hasta: Mapped[date | None] = mapped_column(Date)


_tabla = TarifarioServicio.__table__
_tabla.append_constraint(
    ExcludeConstraint(
        (_tabla.c.id_servicio, "="),
        (_tabla.c.id_convenio, "="),
        (func.daterange(_tabla.c.vigente_desde, _tabla.c.vigente_hasta), "&&"),
        using="gist",
        name="no_solapamiento_tarifario",
    ).ddl_if(dialect="postgresql")
)
