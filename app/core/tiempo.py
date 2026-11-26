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


def edad(fecha_nacimiento: date, referencia: date | None = None) -> int:
    ref = referencia or hoy()
    años = ref.year - fecha_nacimiento.year
    if (ref.month, ref.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        años -= 1
    return años


def formato_fecha(valor: datetime | date) -> str:
    return valor.strftime("%d/%m/%Y")


def formato_hora(valor: datetime) -> str:
    return valor.strftime("%H:%M")
