from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.modulos.auditoria import service as auditoria
from backend.modulos.auditoria.schemas import PaginaAuditoria, RegistroAuditoria
from backend.modulos.convenios import service as convenios
from backend.modulos.hce.schemas import ConvenioResumen
from backend.modulos.notificaciones import service as notificaciones
from backend.modulos.notificaciones.schemas import BandejaNotificaciones, ResultadoProceso
from backend.modulos.seguridad.dependencias import Contexto, contexto_actual, requiere_roles

router_convenios = APIRouter(tags=["M4 · Convenios"])
router_auditoria = APIRouter(tags=["T2 · Auditoría"])
router_notificaciones = APIRouter(tags=["T3 · Notificaciones"])

ROLES_BANDEJA = requiere_roles("ADMISION", "ADMINISTRADOR")


@router_convenios.get(
    "/convenios",
    response_model=list[ConvenioResumen],
    summary="Listar convenios activos",
    responses={200: {"description": "Convenios disponibles para registrar pacientes"}},
)
def listar_convenios(_: Contexto = Depends(contexto_actual), db: Session = Depends(get_db)):
    return convenios.listar_convenios(db)


@router_auditoria.get(
    "/auditoria",
    response_model=PaginaAuditoria,
    summary="Consultar la bitácora de auditoría (solo lectura)",
)
def consultar_bitacora(
    accion: str | None = Query(default=None, pattern="^(SELECT|INSERT|UPDATE|ANULAR|ACCESO_DENEGADO)$"),
    tabla: str | None = Query(default=None, max_length=50),
    usuario: str | None = Query(default=None, max_length=50),
    desde: date | None = None,
    hasta: date | None = None,
    limite: int = Query(default=50, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    _: Contexto = Depends(requiere_roles("GERENCIA", "ADMINISTRADOR")),
    db: Session = Depends(get_db),
):
    total, filas = auditoria.listar(
        db,
        accion=accion,
        tabla=tabla,
        usuario=usuario,
        desde=desde,
        hasta=hasta,
        limite=limite,
        desplazamiento=desplazamiento,
    )
    return PaginaAuditoria(
        total=total,
        registros=[
            RegistroAuditoria(
                id_auditoria=registro.id_auditoria,
                fecha_hora=registro.fecha_hora,
                id_usuario=registro.id_usuario,
                username=username,
                rol=rol,
                accion=registro.accion,
                nombre_tabla=registro.nombre_tabla,
                id_registro_afectado=registro.id_registro_afectado,
                direccion_ip=str(registro.direccion_ip),
                datos_anteriores=registro.datos_anteriores,
                datos_nuevos=registro.datos_nuevos,
                motivo=registro.motivo,
            )
            for registro, username, rol in filas
        ],
    )


@router_notificaciones.get(
    "/notificaciones",
    response_model=BandejaNotificaciones,
    summary="Bandeja del outbox de notificaciones (HU07)",
)
def bandeja(
    estado: str | None = Query(default=None, pattern="^(PENDIENTE|ENVIADO|FALLIDO)$"),
    id_cita: int | None = None,
    limite: int = Query(default=100, ge=1, le=500),
    _: Contexto = Depends(ROLES_BANDEJA),
    db: Session = Depends(get_db),
):
    return BandejaNotificaciones(
        resumen=notificaciones.resumen(db),
        notificaciones=notificaciones.listar(db, estado=estado, id_cita=id_cita, limite=limite),
    )


@router_notificaciones.post(
    "/notificaciones/procesar",
    response_model=ResultadoProceso,
    summary="Ejecutar ahora el trabajador del outbox (el automático corre cada 60 s)",
)
def procesar_ahora(_: Contexto = Depends(ROLES_BANDEJA), db: Session = Depends(get_db)):
    resultado = notificaciones.procesar_pendientes(db)
    db.commit()
    return resultado
