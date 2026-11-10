"""Datos ficticios mínimos para desarrollo y pruebas (ver database/02-datos-prueba.sql)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

CONVENIOS_FICTICIOS = [
    ("PARTICULAR", "Paciente particular", "PARTICULAR"),
    ("EPS_RIMAC", "Rímac EPS", "EPS"),
    ("EPS_PACIFICO", "Pacífico EPS", "EPS"),
    ("EPS_MAPFRE", "Mapfre Perú EPS", "EPS"),
    ("EPS_SANITAS", "Sanitas Perú EPS", "EPS"),
    ("EPS_POSITIVA", "La Positiva EPS", "EPS"),
    ("SOAT", "SOAT", "SOAT"),
]


def sembrar_convenios(db: Session) -> None:
    if db.scalars(select(models.Convenio)).first() is not None:
        return
    for codigo, nombre, tipo in CONVENIOS_FICTICIOS:
        db.add(
            models.Convenio(
                codigo_convenio=codigo, nombre_institucion=nombre, tipo_convenio=tipo
            )
        )
    db.commit()
