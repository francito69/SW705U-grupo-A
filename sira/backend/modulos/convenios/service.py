"""M4 - Convenios y tarifarios: estimación de copago según RN-03."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .models import Convenio, ServicioMedico, TarifarioServicio

CENTIMOS = Decimal("0.01")


def listar_convenios(db: Session) -> list[Convenio]:
    consulta = select(Convenio).where(Convenio.activo.is_(True)).order_by(Convenio.id_convenio)
    return list(db.scalars(consulta))


def obtener_convenio(db: Session, id_convenio: int) -> Convenio | None:
    return db.get(Convenio, id_convenio)


def mapa_convenios(db: Session) -> dict[int, Convenio]:
    return {c.id_convenio: c for c in db.scalars(select(Convenio))}


def tarifario_vigente(
    db: Session, id_servicio: int, id_convenio: int, fecha: date
) -> TarifarioServicio | None:
    return db.scalar(
        select(TarifarioServicio).where(
            TarifarioServicio.id_servicio == id_servicio,
            TarifarioServicio.id_convenio == id_convenio,
            TarifarioServicio.vigente_desde <= fecha,
            or_(TarifarioServicio.vigente_hasta.is_(None), TarifarioServicio.vigente_hasta > fecha),
        )
    )


def calcular_copago(precio: float, porcentaje_cobertura: float, copago_fijo: float) -> tuple[float, float]:
    """Copago = deducible fijo + coaseguro sobre el saldo; el resto lo cubre la aseguradora."""
    precio_d = Decimal(str(precio))
    fijo = min(Decimal(str(copago_fijo)), precio_d)
    coaseguro = (precio_d - fijo) * (Decimal(100) - Decimal(str(porcentaje_cobertura))) / Decimal(100)
    copago = (fijo + coaseguro).quantize(CENTIMOS, rounding=ROUND_HALF_UP)
    return float(precio_d - copago), float(copago)


def estimar_copago(db: Session, id_convenio: int, codigo_servicio: str, fecha: date) -> dict:
    servicio = db.scalar(select(ServicioMedico).where(ServicioMedico.codigo_servicio == codigo_servicio))
    convenio = db.get(Convenio, id_convenio)
    if servicio is None or convenio is None:
        return {}
    tarifario = tarifario_vigente(db, servicio.id_servicio, id_convenio, fecha)
    if tarifario is None:
        precio, cobertura, fijo = servicio.precio_base_particular, 0.0, 0.0
    else:
        precio, cobertura, fijo = (
            tarifario.precio_convenido,
            tarifario.porcentaje_cobertura,
            tarifario.copago_fijo,
        )
    cubierto, copago = calcular_copago(precio, cobertura, fijo)
    return {
        "codigo_servicio": servicio.codigo_servicio,
        "nombre_servicio": servicio.nombre_servicio,
        "id_convenio": convenio.id_convenio,
        "convenio": convenio.nombre_institucion,
        "tipo_convenio": convenio.tipo_convenio,
        "precio": float(precio),
        "porcentaje_cobertura": float(cobertura),
        "copago_fijo": float(fijo),
        "monto_cubierto": cubierto,
        "copago": copago,
        "tarifario_vigente": tarifario is not None,
    }
