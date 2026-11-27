"""Hora oficial del sistema (RN-05: huso America/Lima, UTC-5 sin horario de verano).

Las columnas son TIMESTAMP sin zona, por eso se guarda la hora local de Lima sin tzinfo.
Los servicios llaman a tiempo.ahora() para que las pruebas puedan fijar la hora.
"""

from datetime import date, datetime, timedelta, timezone

ZONA_LIMA = timezone(timedelta(hours=-5), "America/Lima")


def ahora() -> datetime:
    return datetime.now(ZONA_LIMA).replace(tzinfo=None, microsecond=0)


def hoy() -> date:
    return ahora().date()


def calcular_edad(fecha_nacimiento: date, referencia: date) -> int:
    """Años cumplidos en la fecha de referencia; un nacido el 29/02 cumple el 01/03 en años no bisiestos."""
    if fecha_nacimiento > referencia:
        raise ValueError("La fecha de nacimiento es posterior a la fecha de referencia")
    años = referencia.year - fecha_nacimiento.year
    if (referencia.month, referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        años -= 1
    return años


def edad(fecha_nacimiento: date, referencia: date | None = None) -> int:
    return calcular_edad(fecha_nacimiento, referencia or hoy())


def formato_fecha(valor: datetime | date) -> str:
    return valor.strftime("%d/%m/%Y")


def formato_hora(valor: datetime) -> str:
    return valor.strftime("%H:%M")
