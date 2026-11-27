"""Modelo simplificado de citas para el servicio de recordatorios."""

from dataclasses import dataclass

ESTADOS_VALIDOS = ("reservada", "cancelada", "atendida")
CANAL_DEFECTO = "SMS"


@dataclass
class CitaRecordatorio:
    """Representa una cita medica para evaluacion de recordatorios."""

    id_cita: int
    dni_paciente: str
    minutos_restantes: int
    estado: str = "reservada"
    canal: str = CANAL_DEFECTO
