"""Operaciones de acceso a datos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def listar_convenios(db: Session) -> list[models.Convenio]:
    consulta = (
        select(models.Convenio)
        .where(models.Convenio.activo.is_(True))
        .order_by(models.Convenio.id_convenio)
    )
    return list(db.scalars(consulta))
