from datetime import date, datetime

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import tiempo
from app.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"
    __table_args__ = (
        CheckConstraint("tipo_documento IN ('DNI', 'CE', 'PASAPORTE')", name="ck_pacientes_tipo_doc"),
        CheckConstraint("sexo IN ('M', 'F')", name="ck_pacientes_sexo"),
        UniqueConstraint("tipo_documento", "numero_documento", name="uq_paciente_documento"),
    )

    id_paciente: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(10))
    numero_documento: Mapped[str] = mapped_column(String(15))
    nombres: Mapped[str] = mapped_column(String(100))
    apellido_paterno: Mapped[str] = mapped_column(String(60))
    apellido_materno: Mapped[str] = mapped_column(String(60))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    sexo: Mapped[str] = mapped_column(CHAR(1))
    telefono: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    direccion: Mapped[str | None] = mapped_column(String(200))
    id_convenio: Mapped[int] = mapped_column(ForeignKey("convenios.id_convenio"))
    antecedentes_medicos: Mapped[str | None] = mapped_column(Text)
    alergias: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    @property
    def edad(self) -> int:
        return tiempo.edad(self.fecha_nacimiento)


class Atencion(Base):
    __tablename__ = "atenciones"
    __table_args__ = (
        CheckConstraint(
            "tipo_atencion IN ('CONSULTA_EXTERNA', 'TOPICO_URGENCIA')", name="ck_atenciones_tipo"
        ),
        CheckConstraint("estado IN ('EN_CURSO', 'FINALIZADA')", name="ck_atenciones_estado"),
        CheckConstraint(
            "tipo_atencion = 'TOPICO_URGENCIA' OR id_cita IS NOT NULL", name="chk_atencion_cita"
        ),
        CheckConstraint(
            "estado = 'EN_CURSO' OR (motivo_consulta IS NOT NULL AND finalizada_en IS NOT NULL)",
            name="chk_atencion_finalizada",
        ),
        CheckConstraint(
            "(anulado = FALSE AND motivo_anulacion IS NULL AND anulado_por IS NULL "
            "AND anulado_en IS NULL) OR (anulado = TRUE AND length(motivo_anulacion) >= 20 "
            "AND anulado_por IS NOT NULL AND anulado_en IS NOT NULL)",
            name="chk_atencion_anulacion",
        ),
        Index(
            "idx_atenciones_paciente_fecha",
            "id_paciente",
            text("creado_en DESC"),
            postgresql_where=text("anulado = FALSE"),
            sqlite_where=text("anulado = 0"),
        ),
    )

    id_atencion: Mapped[int] = mapped_column(primary_key=True)
    id_paciente: Mapped[int] = mapped_column(ForeignKey("pacientes.id_paciente"))
    id_medico: Mapped[int] = mapped_column(ForeignKey("medicos.id_medico"))
    id_cita: Mapped[int | None] = mapped_column(ForeignKey("citas.id_cita"), unique=True)
    tipo_atencion: Mapped[str] = mapped_column(
        String(20), default="CONSULTA_EXTERNA", server_default="CONSULTA_EXTERNA"
    )
    estado: Mapped[str] = mapped_column(String(12), default="EN_CURSO", server_default="EN_CURSO")
    motivo_consulta: Mapped[str | None] = mapped_column(Text)
    anamnesis: Mapped[str | None] = mapped_column(Text)
    indicaciones: Mapped[str | None] = mapped_column(Text)
    inicio_consulta: Mapped[datetime | None] = mapped_column(DateTime)
    finalizada_en: Mapped[datetime | None] = mapped_column(DateTime)
    anulado: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    motivo_anulacion: Mapped[str | None] = mapped_column(Text)
    anulado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"))
    anulado_en: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )

    paciente: Mapped[Paciente] = relationship()
    triaje: Mapped["Triaje | None"] = relationship(back_populates="atencion", uselist=False)
    diagnosticos: Mapped[list["AtencionDiagnostico"]] = relationship(
        back_populates="atencion", order_by="AtencionDiagnostico.tipo"
    )
    prescripciones: Mapped[list["Prescripcion"]] = relationship(
        back_populates="atencion", order_by="Prescripcion.id_prescripcion"
    )

    @property
    def fecha(self) -> datetime:
        return self.inicio_consulta or self.creado_en


class Triaje(Base):
    __tablename__ = "triajes"
    __table_args__ = (
        CheckConstraint("presion_sistolica BETWEEN 50 AND 300", name="ck_triajes_sistolica"),
        CheckConstraint("presion_diastolica BETWEEN 30 AND 200", name="ck_triajes_diastolica"),
        CheckConstraint("temperatura BETWEEN 30.0 AND 45.0", name="ck_triajes_temperatura"),
        CheckConstraint("frecuencia_cardiaca BETWEEN 30 AND 250", name="ck_triajes_fc"),
        CheckConstraint("frecuencia_respiratoria BETWEEN 8 AND 60", name="ck_triajes_fr"),
        CheckConstraint("saturacion_oxigeno BETWEEN 50 AND 100", name="ck_triajes_sat"),
        CheckConstraint("peso BETWEEN 1 AND 350", name="ck_triajes_peso"),
        CheckConstraint("talla BETWEEN 0.30 AND 2.50", name="ck_triajes_talla"),
        CheckConstraint("presion_sistolica > presion_diastolica", name="chk_triaje_presion"),
    )

    id_triaje: Mapped[int] = mapped_column(primary_key=True)
    id_atencion: Mapped[int] = mapped_column(ForeignKey("atenciones.id_atencion"), unique=True)
    presion_sistolica: Mapped[int] = mapped_column(SmallInteger)
    presion_diastolica: Mapped[int] = mapped_column(SmallInteger)
    temperatura: Mapped[float] = mapped_column(Numeric(4, 1, asdecimal=False))
    frecuencia_cardiaca: Mapped[int] = mapped_column(SmallInteger)
    frecuencia_respiratoria: Mapped[int | None] = mapped_column(SmallInteger)
    saturacion_oxigeno: Mapped[int | None] = mapped_column(SmallInteger)
    peso: Mapped[float] = mapped_column(Numeric(5, 2, asdecimal=False))
    talla: Mapped[float] = mapped_column(Numeric(3, 2, asdecimal=False))
    observaciones: Mapped[str | None] = mapped_column(Text)
    id_enfermera: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    registrado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: tiempo.ahora(), server_default=func.current_timestamp()
    )

    atencion: Mapped[Atencion] = relationship(back_populates="triaje")


class DiagnosticoCIE10(Base):
    __tablename__ = "diagnosticos_cie10"

    codigo: Mapped[str] = mapped_column(String(10), primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(255))


class AtencionDiagnostico(Base):
    __tablename__ = "atencion_diagnosticos"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('PRINCIPAL', 'SECUNDARIO', 'PRESUNTIVO')", name="ck_atencion_diag_tipo"
        ),
        Index(
            "uq_diagnostico_principal",
            "id_atencion",
            unique=True,
            postgresql_where=text("tipo = 'PRINCIPAL'"),
            sqlite_where=text("tipo = 'PRINCIPAL'"),
        ),
    )

    id_atencion: Mapped[int] = mapped_column(
        ForeignKey("atenciones.id_atencion"), primary_key=True
    )
    codigo_cie10: Mapped[str] = mapped_column(
        ForeignKey("diagnosticos_cie10.codigo"), primary_key=True
    )
    tipo: Mapped[str] = mapped_column(String(12))

    atencion: Mapped[Atencion] = relationship(back_populates="diagnosticos")
    diagnostico: Mapped[DiagnosticoCIE10] = relationship(lazy="joined")


class Prescripcion(Base):
    __tablename__ = "prescripciones"
    __table_args__ = (Index("idx_prescripciones_atencion", "id_atencion"),)

    id_prescripcion: Mapped[int] = mapped_column(primary_key=True)
    id_atencion: Mapped[int] = mapped_column(ForeignKey("atenciones.id_atencion"))
    medicamento: Mapped[str] = mapped_column(String(120))
    presentacion: Mapped[str] = mapped_column(String(80))
    frecuencia: Mapped[str] = mapped_column(String(80))
    duracion: Mapped[str] = mapped_column(String(40))

    atencion: Mapped[Atencion] = relationship(back_populates="prescripciones")
