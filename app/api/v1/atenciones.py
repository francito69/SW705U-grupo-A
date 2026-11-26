from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, Prohibido, ReglaNegocio
from app.database import get_db
from app.modulos.agenda import service as agenda
from app.modulos.auditoria import service as auditoria
from app.modulos.hce import service as hce
from app.modulos.hce.schemas import (
    AnularAtencion,
    AtencionEnCurso,
    AtencionResumen,
    AtencionSalida,
    Cie10Salida,
    FinalizarAtencion,
    TriajeCrear,
    UrgenciaCrear,
)
from app.modulos.seguridad import service as seguridad
from app.modulos.seguridad.dependencias import Contexto, contexto_actual, requiere_roles

from . import composicion

router = APIRouter(tags=["M1 · Triaje y atención médica"])

SOLO_MEDICO = requiere_roles("MEDICO", tabla="atenciones", parametro_id="id_atencion")
SIGNOS = {"id_cita", "id_paciente", "id_medico"}


@router.get(
    "/diagnosticos-cie10",
    response_model=list[Cie10Salida],
    summary="Buscar en el catálogo CIE-10 por código o descripción",
)
def buscar_cie10(
    q: str | None = Query(default=None, max_length=60),
    limite: int = Query(default=20, ge=1, le=50),
    _: Contexto = Depends(contexto_actual),
    db: Session = Depends(get_db),
):
    return hce.buscar_cie10(db, q, limite)


@router.post(
    "/triajes",
    status_code=201,
    response_model=AtencionSalida,
    summary="Registrar triaje de un paciente citado (HU05)",
    responses={409: {"description": "La cita no está en espera o ya tiene triaje"}},
)
def registrar_triaje(
    datos: TriajeCrear,
    ctx: Contexto = Depends(requiere_roles("ENFERMERA", tabla="triajes")),
    db: Session = Depends(get_db),
):
    cita = agenda.obtener_cita(db, datos.id_cita)
    if cita.estado == "CONFIRMADA":
        raise Conflicto("Primero registre la llegada del paciente en admisión")
    if cita.estado != "EN_ESPERA":
        raise Conflicto(f"La cita no está en espera (estado actual: {cita.estado})")
    atencion = hce.registrar_triaje(
        db,
        ctx,
        id_paciente=cita.id_paciente,
        id_medico=cita.id_medico,
        id_cita=cita.id_cita,
        signos=datos.model_dump(exclude=SIGNOS),
    )
    db.commit()
    return composicion.atencion_salida(db, atencion)


@router.post(
    "/urgencias",
    status_code=201,
    response_model=AtencionSalida,
    summary="Registrar ingreso a tópico de urgencias con triaje obligatorio",
)
def registrar_urgencia(
    datos: UrgenciaCrear,
    ctx: Contexto = Depends(requiere_roles("ENFERMERA", tabla="atenciones")),
    db: Session = Depends(get_db),
):
    paciente = hce.obtener_paciente(db, datos.id_paciente)
    medico = agenda.obtener_medico(db, datos.id_medico)
    if not medico.activo:
        raise ReglaNegocio(f"El médico {medico.nombre_completo} no está activo")
    atencion = hce.registrar_triaje(
        db,
        ctx,
        id_paciente=paciente.id_paciente,
        id_medico=medico.id_medico,
        id_cita=None,
        signos=datos.model_dump(exclude=SIGNOS),
    )
    db.commit()
    return composicion.atencion_salida(db, atencion)


@router.get(
    "/atenciones/en-curso",
    response_model=list[AtencionEnCurso],
    summary="Urgencias de tópico asignadas al médico autenticado",
)
def atenciones_en_curso(
    ctx: Contexto = Depends(requiere_roles("MEDICO", tabla="atenciones")),
    db: Session = Depends(get_db),
):
    medico = composicion.medico_actual(db, ctx)
    return composicion.atenciones_en_curso(db, hce.atenciones_en_curso(db, medico.id_medico))


@router.get("/atenciones/{id_atencion}", response_model=AtencionSalida, summary="Detalle de una atención")
def obtener_atencion(
    id_atencion: int,
    ctx: Contexto = Depends(SOLO_MEDICO),
    db: Session = Depends(get_db),
):
    atencion = hce.obtener_atencion(db, id_atencion)
    auditoria.registrar(db, ctx, "atenciones", id_atencion, "SELECT")
    db.commit()
    return composicion.atencion_salida(db, atencion)


@router.post(
    "/atenciones/{id_atencion}/iniciar",
    response_model=AtencionSalida,
    summary="Marcar el inicio de la consulta (tiempo de espera)",
)
def iniciar_consulta(
    id_atencion: int,
    ctx: Contexto = Depends(SOLO_MEDICO),
    db: Session = Depends(get_db),
):
    medico = composicion.medico_actual(db, ctx)
    atencion = hce.iniciar_consulta(db, ctx, id_atencion, medico.id_medico)
    db.commit()
    return composicion.atencion_salida(db, atencion)


@router.post(
    "/atenciones/{id_atencion}/finalizar",
    response_model=AtencionSalida,
    summary="Registrar diagnóstico CIE-10 y receta, y cerrar la atención (HU04)",
    responses={
        409: {"description": "Atención ya cerrada o posible alergia sin confirmar"},
        422: {"description": "Falta un diagnóstico CIE-10 válido"},
    },
)
def finalizar_atencion(
    id_atencion: int,
    datos: FinalizarAtencion,
    ctx: Contexto = Depends(SOLO_MEDICO),
    db: Session = Depends(get_db),
):
    medico = composicion.medico_actual(db, ctx)
    atencion = hce.finalizar_atencion(db, ctx, id_atencion, medico.id_medico, datos.model_dump())
    if atencion.id_cita is not None:
        agenda.marcar_atendida(db, ctx, atencion.id_cita)
    db.commit()
    return composicion.atencion_salida(db, atencion)


@router.post(
    "/atenciones/{id_atencion}/anular",
    response_model=AtencionResumen,
    summary="Anulación lógica con justificación y clave del usuario (HU08)",
    responses={403: {"description": "Rol sin permiso o clave incorrecta"}, 409: {"description": "Ya anulada"}},
)
def anular_atencion(
    id_atencion: int,
    datos: AnularAtencion,
    ctx: Contexto = Depends(requiere_roles("GERENCIA", tabla="atenciones", parametro_id="id_atencion")),
    db: Session = Depends(get_db),
):
    if not seguridad.verificar_password(datos.password, ctx.usuario.password_hash):
        auditoria.registrar(
            db,
            ctx,
            "atenciones",
            id_atencion,
            "ACCESO_DENEGADO",
            motivo="Clave incorrecta al confirmar la anulación",
        )
        db.commit()
        raise Prohibido("La clave no es correcta")
    atencion = hce.anular_atencion(db, ctx, id_atencion, datos.motivo)
    db.commit()
    return composicion.atenciones_resumen(db, [atencion])[0]
