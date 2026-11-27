"""Servicio de recordatorios de citas 24 horas antes (HU-07)."""

from datetime import datetime

from backend.citas import HORAS_ANTES_RECORDATORIO, CitaRecordatorio
from backend.notificaciones import Notificador

VENTANA_MINUTOS = HORAS_ANTES_RECORDATORIO * 60


def _es_elegible(cita: CitaRecordatorio) -> bool:
    """Verifica si una cita reservada y no recordada cae en la ventana de 24 h."""
    en_ventana = 0 <= cita.minutos_restantes <= VENTANA_MINUTOS
    return cita.estado == "reservada" and not cita.recordada and en_ventana


def citas_a_recordar(citas: list[CitaRecordatorio], ahora: datetime) -> list[CitaRecordatorio]:
    """Filtra las citas que deben recibir recordatorio en el instante dado."""
    _ = ahora
    return [c for c in citas if _es_elegible(c)]


def enviar_recordatorios(
    citas: list[CitaRecordatorio],
    ahora: datetime,
    notificador: Notificador,
) -> int:
    """Envia recordatorios a las citas elegibles y marca las enviadas con exito."""
    enviados = 0
    for cita in citas_a_recordar(citas, ahora):
        mensaje = f"Recordatorio: tiene una cita en {cita.minutos_restantes} minutos."
        if notificador.enviar(cita.dni_paciente, mensaje):
            cita.recordada = True
            enviados += 1
    return enviados
