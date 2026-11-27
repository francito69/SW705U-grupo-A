"""Contratos de entrada y salida de M2."""

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.modulos.hce.schemas import MedicoResumen

Canal = Literal["ADMISION", "PORTAL_WEB", "TELEFONICO"]
EstadoTurno = Literal["LIBRE", "OCUPADO", "PASADO", "SIN_CONSULTORIO"]


def _motivo(valor):
    texto = re.sub(r"\s+", " ", valor).strip() if isinstance(valor, str) else ""
    if len(texto) < 5:
        raise ValueError("Indique el motivo (al menos 5 caracteres)")
    return texto


class EspecialidadSalida(BaseModel):
    id_especialidad: int
    nombre: str
    medicos_activos: int


class MedicoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_medico: int
    cmp: str
    nombres: str
    apellidos: str
    nombre_completo: str
    id_especialidad: int
    especialidad: str
    activo: bool

    @field_validator("especialidad", mode="before")
    @classmethod
    def _nombre_especialidad(cls, valor):
        return getattr(valor, "nombre", valor)


class ConsultorioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_consultorio: int
    numero: str
    piso: int
    descripcion: str | None


class TurnoSalida(BaseModel):
    turno: Literal["MAÑANA", "TARDE"]
    inicio: datetime
    fin: datetime
    estado: EstadoTurno
    id_cita: int | None
    id_consultorio_sugerido: int | None
    consultorio_sugerido: str | None


class MedicoDisponibilidad(BaseModel):
    id_medico: int
    nombre_completo: str
    cmp: str
    especialidad: str
    id_consultorio_habitual: int | None
    consultorio_habitual: str | None
    libres: int
    ocupados: int
    turnos: list[TurnoSalida]


class Disponibilidad(BaseModel):
    fecha: date
    id_especialidad: int
    especialidad: str
    duracion_minutos: int
    atiende: bool
    mensaje: str | None
    medicos: list[MedicoDisponibilidad]


class CitaCrear(BaseModel):
    id_paciente: int
    id_medico: int
    id_consultorio: int
    fecha_hora_inicio: datetime = Field(description="Inicio del bloque de 30 minutos (hora de Lima)")
    canal_agendamiento: Canal = "ADMISION"
    enviar_recordatorio: bool = Field(default=True, description="Recordatorio por SMS 24 h antes")


class CitaCancelar(BaseModel):
    motivo: str = Field(max_length=500)

    @field_validator("motivo", mode="before")
    @classmethod
    def _validar_motivo(cls, valor):
        return _motivo(valor)


class CitaReprogramar(BaseModel):
    fecha_hora_inicio: datetime
    id_medico: int | None = Field(default=None, description="Por defecto, el mismo médico")
    id_consultorio: int
    motivo: str = Field(max_length=500)
    enviar_recordatorio: bool = True

    @field_validator("motivo", mode="before")
    @classmethod
    def _validar_motivo(cls, valor):
        return _motivo(valor)


class PacienteCita(BaseModel):
    id_paciente: int
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    edad: int
    sexo: str
    telefono: str
    convenio: str | None
    alergias: str | None = Field(default=None, description="Solo para roles clínicos")


class TriajeBreve(BaseModel):
    presion_sistolica: int
    presion_diastolica: int
    temperatura: float
    frecuencia_cardiaca: int
    saturacion_oxigeno: int | None
    registrado_en: datetime


class AtencionDeCita(BaseModel):
    id_atencion: int
    estado: str
    anulado: bool
    triaje: TriajeBreve | None
    alertas: list[str]


class CitaSalida(BaseModel):
    id_cita: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
    motivo_cancelacion: str | None
    hora_llegada: datetime | None
    id_cita_origen: int | None
    id_cita_nueva: int | None
    canal_agendamiento: str
    creado_en: datetime
    paciente: PacienteCita
    medico: MedicoResumen
    consultorio: ConsultorioSalida
    atencion: AtencionDeCita | None


class CopagoEstimado(BaseModel):
    codigo_servicio: str
    nombre_servicio: str
    id_convenio: int
    convenio: str
    tipo_convenio: str
    precio: float
    porcentaje_cobertura: float
    copago_fijo: float
    monto_cubierto: float
    copago: float
    tarifario_vigente: bool
