"""Contrato de notificacion y notificador simulado para recordatorios (HU-07)."""

from typing import Protocol


class Notificador(Protocol):
    """Contrato desacoplado para el envio de mensajes al paciente."""

    def enviar(self, dni: str, mensaje: str) -> bool:
        ...


class NotificadorSimulado:
    """Notificador en memoria para pruebas unitarias y de integracion."""

    def __init__(self, debe_fallar: bool = False) -> None:
        self.debe_fallar = debe_fallar
        self.enviados: list[tuple[str, str]] = []

    def enviar(self, dni: str, mensaje: str) -> bool:
        if self.debe_fallar:
            return False
        self.enviados.append((dni, mensaje))
        return True
