"""T2 - AuditService: registra quién hizo qué, sobre qué registro y desde qué IP."""

import ipaddress
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.modulos.seguridad.models import Rol, Usuario

from .models import BitacoraAuditoria


class Actor(Protocol):
    id_usuario: int
    ip: str


def ip_valida(valor: str | None) -> str:
    try:
        return str(ipaddress.ip_address(valor or ""))
    except ValueError:
        return "0.0.0.0"


def _valor_json(valor):
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (list, tuple)):
        return [_valor_json(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _valor_json(v) for k, v in valor.items()}
    return valor


def instantanea(objeto, campos) -> dict:
    return {campo: _valor_json(getattr(objeto, campo)) for campo in campos}


def registrar(
    db: Session,
    actor: Actor,
    tabla: str,
    id_registro: int,
    accion: str,
    *,
    antes: dict | None = None,
    despues: dict | None = None,
    motivo: str | None = None,
) -> None:
    db.add(
        BitacoraAuditoria(
            id_usuario=actor.id_usuario,
            nombre_tabla=tabla,
            id_registro_afectado=id_registro,
            accion=accion,
            direccion_ip=ip_valida(actor.ip),
            datos_anteriores=_valor_json(antes),
            datos_nuevos=_valor_json(despues),
            motivo=motivo,
        )
    )


def listar(
    db: Session,
    *,
    accion: str | None = None,
    tabla: str | None = None,
    usuario: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    limite: int = 50,
    desplazamiento: int = 0,
) -> tuple[int, list[tuple[BitacoraAuditoria, str, str]]]:
    consulta = (
        select(BitacoraAuditoria, Usuario.username, Rol.nombre)
        .join(Usuario, Usuario.id_usuario == BitacoraAuditoria.id_usuario)
        .join(Rol, Rol.id_rol == Usuario.id_rol)
    )
    if accion:
        consulta = consulta.where(BitacoraAuditoria.accion == accion)
    if tabla:
        consulta = consulta.where(BitacoraAuditoria.nombre_tabla == tabla)
    if usuario:
        consulta = consulta.where(Usuario.username.ilike(f"%{usuario}%"))
    if desde:
        consulta = consulta.where(BitacoraAuditoria.fecha_hora >= datetime.combine(desde, datetime.min.time()))
    if hasta:
        consulta = consulta.where(BitacoraAuditoria.fecha_hora <= datetime.combine(hasta, datetime.max.time()))
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    filas = db.execute(
        consulta.order_by(BitacoraAuditoria.fecha_hora.desc(), BitacoraAuditoria.id_auditoria.desc())
        .limit(limite)
        .offset(desplazamiento)
    ).all()
    return total, [(fila[0], fila[1], fila[2]) for fila in filas]
