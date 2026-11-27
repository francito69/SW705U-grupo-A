"""Contratos de entrada y salida de M1."""

import re
from datetime import date, datetime
from typing import Literal

import email_validator
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from backend.core import tiempo

# Los correos ficticios usan el dominio reservado .test (RFC 2606), que se acepta a propósito.
if "test" in email_validator.SPECIAL_USE_DOMAIN_NAMES:
    email_validator.SPECIAL_USE_DOMAIN_NAMES.remove("test")

TipoDocumento = Literal["DNI", "CE", "PASAPORTE"]
TipoDiagnostico = Literal["PRINCIPAL", "SECUNDARIO", "PRESUNTIVO"]

FORMATOS_DOCUMENTO = {
    "DNI": (r"[0-9]{8}", "El DNI debe tener 8 dígitos"),
    "CE": (r"[0-9]{9,12}", "El carné de extranjería debe tener entre 9 y 12 dígitos"),
    "PASAPORTE": (r"[A-Z0-9]{6,12}", "El pasaporte debe tener entre 6 y 12 letras o números"),
}


def _texto(valor):
    if isinstance(valor, str):
        valor = re.sub(r"\s+", " ", valor).strip()
        return valor or None
    return valor


class _Filiacion(BaseModel):
    @field_validator("nombres", "apellido_paterno", "apellido_materno", "direccion", "email", mode="before", check_fields=False)
    @classmethod
    def _limpiar(cls, valor):
        return _texto(valor)

    @field_validator("telefono", mode="before", check_fields=False)
    @classmethod
    def _validar_telefono(cls, valor):
        if valor is None:
            return valor
        numero = re.sub(r"[\s-]", "", str(valor)).removeprefix("+51")
        if not re.fullmatch(r"9[0-9]{8}", numero):
            raise ValueError("El celular debe tener 9 dígitos y empezar con 9")
        return numero

    @field_validator("fecha_nacimiento", check_fields=False)
    @classmethod
    def _validar_nacimiento(cls, valor):
        if valor is None:
            return valor
        if valor > tiempo.hoy():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        if tiempo.edad(valor) > 120:
            raise ValueError("La fecha de nacimiento no es válida")
        return valor


class PacienteCrear(_Filiacion):
    tipo_documento: TipoDocumento
    numero_documento: str
    nombres: str = Field(min_length=2, max_length=100)
    apellido_paterno: str = Field(min_length=1, max_length=60)
    apellido_materno: str = Field(min_length=1, max_length=60)
    fecha_nacimiento: date
    sexo: Literal["M", "F"]
    telefono: str
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    id_convenio: int

    @field_validator("numero_documento", mode="before")
    @classmethod
    def _limpiar_documento(cls, valor):
        return str(valor).strip().upper() if valor is not None else valor

    @model_validator(mode="after")
    def _validar_documento(self):
        patron, mensaje = FORMATOS_DOCUMENTO[self.tipo_documento]
        if not re.fullmatch(patron, self.numero_documento):
            raise ValueError(mensaje)
        return self


class PacienteActualizar(_Filiacion):
    nombres: str | None = Field(default=None, min_length=2, max_length=100)
    apellido_paterno: str | None = Field(default=None, min_length=1, max_length=60)
    apellido_materno: str | None = Field(default=None, min_length=1, max_length=60)
    fecha_nacimiento: date | None = None
    sexo: Literal["M", "F"] | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    id_convenio: int | None = None


class AntecedentesActualizar(BaseModel):
    alergias: str | None = Field(default=None, max_length=500)
    antecedentes_medicos: str | None = Field(default=None, max_length=2000)

    @field_validator("alergias", "antecedentes_medicos", mode="before")
    @classmethod
    def _limpiar(cls, valor):
        return _texto(valor)


class ConvenioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_convenio: int
    codigo_convenio: str
    nombre_institucion: str
    tipo_convenio: str


class PacienteSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_paciente: int
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    nombre_completo: str
    fecha_nacimiento: date
    edad: int
    sexo: str
    telefono: str
    email: str | None
    direccion: str | None
    id_convenio: int
    convenio: ConvenioResumen | None = None
    creado_en: datetime
    alergias: str | None = Field(default=None, description="Solo para roles clínicos")
    antecedentes_medicos: str | None = Field(default=None, description="Solo para roles clínicos")


class SignosVitales(BaseModel):
    presion_sistolica: int = Field(ge=50, le=300)
    presion_diastolica: int = Field(ge=30, le=200)
    temperatura: float = Field(ge=30, le=45)
    frecuencia_cardiaca: int = Field(ge=30, le=250)
    frecuencia_respiratoria: int | None = Field(default=None, ge=8, le=60)
    saturacion_oxigeno: int | None = Field(default=None, ge=50, le=100)
    peso: float = Field(ge=1, le=350, description="Kilogramos")
    talla: float = Field(ge=0.3, le=2.5, description="Metros")
    observaciones: str | None = Field(default=None, max_length=1000)

    @field_validator("observaciones", mode="before")
    @classmethod
    def _limpiar(cls, valor):
        return _texto(valor)

    @model_validator(mode="after")
    def _validar_presion(self):
        if self.presion_sistolica <= self.presion_diastolica:
            raise ValueError("La presión sistólica debe ser mayor que la diastólica")
        self.temperatura = round(self.temperatura, 1)
        self.peso = round(self.peso, 2)
        self.talla = round(self.talla, 2)
        return self


class TriajeCrear(SignosVitales):
    id_cita: int


class UrgenciaCrear(SignosVitales):
    id_paciente: int
    id_medico: int


class TriajeSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_triaje: int
    id_atencion: int
    presion_sistolica: int
    presion_diastolica: int
    temperatura: float
    frecuencia_cardiaca: int
    frecuencia_respiratoria: int | None
    saturacion_oxigeno: int | None
    peso: float
    talla: float
    imc: float
    observaciones: str | None
    alertas: list[str]
    id_enfermera: int
    registrado_en: datetime


class DiagnosticoEntrada(BaseModel):
    codigo_cie10: str = Field(min_length=3, max_length=10)
    tipo: TipoDiagnostico = "PRINCIPAL"

    @field_validator("codigo_cie10", mode="before")
    @classmethod
    def _mayusculas(cls, valor):
        return str(valor).strip().upper() if valor is not None else valor


class PrescripcionEntrada(BaseModel):
    medicamento: str = Field(min_length=2, max_length=120)
    presentacion: str = Field(min_length=1, max_length=80)
    frecuencia: str = Field(min_length=1, max_length=80)
    duracion: str = Field(min_length=1, max_length=40)

    @field_validator("medicamento", "presentacion", "frecuencia", "duracion", mode="before")
    @classmethod
    def _limpiar(cls, valor):
        return _texto(valor) or ""


class FinalizarAtencion(BaseModel):
    motivo_consulta: str = Field(min_length=3, max_length=2000)
    anamnesis: str | None = Field(default=None, max_length=5000)
    indicaciones: str | None = Field(default=None, max_length=3000)
    diagnosticos: list[DiagnosticoEntrada]
    prescripciones: list[PrescripcionEntrada] = []
    confirmar_alergias: bool = Field(
        default=False, description="El médico revisó la advertencia de alergia y confirma la receta"
    )

    @field_validator("motivo_consulta", "anamnesis", "indicaciones", mode="before")
    @classmethod
    def _limpiar(cls, valor):
        return _texto(valor)

    @field_validator("diagnosticos")
    @classmethod
    def _validar_diagnosticos(cls, valor: list[DiagnosticoEntrada]):
        if not valor:
            raise ValueError("Registre al menos un diagnóstico CIE-10 del catálogo oficial")
        codigos = [d.codigo_cie10 for d in valor]
        if len(set(codigos)) != len(codigos):
            raise ValueError("Hay diagnósticos repetidos")
        if sum(1 for d in valor if d.tipo == "PRINCIPAL") > 1:
            raise ValueError("Solo puede haber un diagnóstico principal")
        return valor


class AnularAtencion(BaseModel):
    motivo: str = Field(max_length=1000)
    password: str = Field(min_length=1, max_length=72, description="Clave del usuario que anula")

    @field_validator("motivo", mode="before")
    @classmethod
    def _validar_motivo(cls, valor):
        texto = _texto(valor) or ""
        if len(texto) < 20:
            raise ValueError("La justificación debe tener al menos 20 caracteres")
        return texto


class AntecedentesSalida(BaseModel):
    alergias: str | None
    antecedentes_medicos: str | None


class DiagnosticoSalida(BaseModel):
    codigo: str
    descripcion: str
    tipo: str


class PrescripcionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_prescripcion: int
    medicamento: str
    presentacion: str
    frecuencia: str
    duracion: str


class MedicoResumen(BaseModel):
    id_medico: int
    nombre_completo: str
    especialidad: str
    cmp: str


class AtencionResumen(BaseModel):
    id_atencion: int
    id_paciente: int
    id_cita: int | None
    tipo_atencion: str
    estado: str
    fecha: datetime
    medico: MedicoResumen | None
    anulado: bool
    motivo_anulacion: str | None
    anulado_en: datetime | None


class AtencionSalida(AtencionResumen):
    creado_en: datetime
    inicio_consulta: datetime | None
    finalizada_en: datetime | None
    motivo_consulta: str | None
    anamnesis: str | None
    indicaciones: str | None
    triaje: TriajeSalida | None
    diagnosticos: list[DiagnosticoSalida]
    prescripciones: list[PrescripcionSalida]


class HistoriaClinica(BaseModel):
    paciente: PacienteSalida
    total_atenciones: int
    atenciones: list[AtencionSalida]


class AtencionEnCurso(BaseModel):
    id_atencion: int
    tipo_atencion: str
    creado_en: datetime
    paciente: PacienteSalida
    triaje: TriajeSalida | None


class Cie10Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    descripcion: str
