from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core import tiempo
from app.core.errores import NoEncontrado
from app.database import get_db
from app.modulos.agenda import service as agenda
from app.modulos.agenda.schemas import (
    CitaCancelar,
    CitaCrear,
    CitaReprogramar,
    CitaSalida,
    ConsultorioSalida,
    CopagoEstimado,
    Disponibilidad,
    EspecialidadSalida,
    MedicoSalida,
)
from app.modulos.convenios import service as convenios
from app.modulos.hce import service as hce
from app.modulos.seguridad.dependencias import Contexto, contexto_actual, requiere_roles

from . import composicion

router = APIRouter(tags=["M2 · Agenda y citas"])

LECTURA_CITAS = ("ADMISION", "ENFERMERA", "MEDICO", "GERENCIA")
SOLO_ADMISION = requiere_roles("ADMISION")
ESTADOS_CITA = ("CONFIRMADA", "EN_ESPERA", "ATENDIDA", "CANCELADA", "REPROGRAMADA", "NO_ASISTIO")


@router.get("/especialidades", response_model=list[EspecialidadSalida], summary="Especialidades")
def listar_especialidades(_: Contexto = Depends(contexto_actual), db: Session = Depends(get_db)):
    return [
        EspecialidadSalida(id_especialidad=e.id_especialidad, nombre=e.nombre, medicos_activos=n)
        for e, n in agenda.listar_especialidades(db)
    ]


@router.get("/medicos", response_model=list[MedicoSalida], summary="Médicos activos")
def listar_medicos(
    id_especialidad: int | None = None,
    _: Contexto = Depends(contexto_actual),
    db: Session = Depends(get_db),
):
    return agenda.listar_medicos(db, id_especialidad)


@router.get(
    "/consultorios",
    response_model=list[ConsultorioSalida],
    summary="Consultorios (opcionalmente solo los libres en un bloque)",
)
def listar_consultorios(
    libres_en: datetime | None = Query(default=None, description="Inicio del bloque de 30 minutos"),
    excluir_cita: int | None = Query(default=None, description="Cita que se está reprogramando"),
    _: Contexto = Depends(contexto_actual),
    db: Session = Depends(get_db),
):
    if libres_en is None:
        return agenda.listar_consultorios(db)
    return agenda.consultorios_libres(db, libres_en, excluir=excluir_cita)


@router.get(
    "/citas/disponibilidad",
    response_model=Disponibilidad,
    summary="Matriz de turnos libres y ocupados por médico (paso 2 del agendamiento)",
)
def disponibilidad(
    fecha: date,
    id_especialidad: int,
    id_medico: int | None = None,
    _: Contexto = Depends(SOLO_ADMISION),
    db: Session = Depends(get_db),
):
    return agenda.disponibilidad(db, fecha, id_especialidad, id_medico)


@router.get(
    "/citas/copago-estimado",
    response_model=CopagoEstimado,
    summary="Copago estimado según el convenio del paciente (paso 3)",
)
def copago_estimado(
    id_paciente: int,
    id_medico: int,
    fecha: date | None = None,
    _: Contexto = Depends(SOLO_ADMISION),
    db: Session = Depends(get_db),
):
    paciente = hce.obtener_paciente(db, id_paciente)
    medico = agenda.obtener_medico(db, id_medico)
    codigo = "CON-GEN-01" if medico.especialidad.nombre == "Medicina General" else "CON-ESP-01"
    estimado = convenios.estimar_copago(db, paciente.id_convenio, codigo, fecha or tiempo.hoy())
    if not estimado:
        raise NoEncontrado("No hay un servicio de consulta configurado para estimar el copago")
    return estimado


@router.get("/citas", response_model=list[CitaSalida], summary="Citas por fecha, médico, estado o paciente")
def listar_citas(
    fecha: date | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    id_medico: int | None = None,
    estado: str | None = Query(default=None, pattern="^(" + "|".join(ESTADOS_CITA) + ")$"),
    id_paciente: int | None = None,
    ctx: Contexto = Depends(requiere_roles(*LECTURA_CITAS)),
    db: Session = Depends(get_db),
):
    if ctx.rol == "MEDICO":
        id_medico = composicion.medico_actual(db, ctx).id_medico
    if not any((fecha, desde, hasta, id_paciente)):
        fecha = tiempo.hoy()
    citas = agenda.listar_citas(
        db, fecha=fecha, desde=desde, hasta=hasta, id_medico=id_medico, estado=estado, id_paciente=id_paciente
    )
    return composicion.citas_salida(db, citas, ctx.es_clinico)


@router.post(
    "/citas",
    status_code=201,
    response_model=CitaSalida,
    summary="Agendar una cita con bloqueo de solapamientos (HU02)",
    responses={
        409: {"description": "Médico, consultorio o paciente ya ocupado en ese horario"},
        422: {"description": "Horario no válido (pasado, domingo o fuera de turno)"},
    },
)
def agendar_cita(datos: CitaCrear, ctx: Contexto = Depends(SOLO_ADMISION), db: Session = Depends(get_db)):
    paciente = hce.obtener_paciente(db, datos.id_paciente)
    cita = agenda.crear_cita(
        db,
        ctx,
        paciente=paciente,
        id_medico=datos.id_medico,
        id_consultorio=datos.id_consultorio,
        inicio=datos.fecha_hora_inicio,
        canal=datos.canal_agendamiento,
        enviar_recordatorio=datos.enviar_recordatorio,
    )
    return composicion.cita_salida(db, cita, clinico=False)


@router.get("/citas/{id_cita}", response_model=CitaSalida, summary="Detalle de una cita")
def obtener_cita(
    id_cita: int,
    ctx: Contexto = Depends(requiere_roles(*LECTURA_CITAS)),
    db: Session = Depends(get_db),
):
    return composicion.cita_salida(db, agenda.obtener_cita(db, id_cita), ctx.es_clinico)


@router.post(
    "/citas/{id_cita}/check-in",
    response_model=CitaSalida,
    summary="Registrar la llegada del paciente (pasa a la cola de triaje)",
    responses={409: {"description": "La cita no está confirmada"}},
)
def registrar_llegada(id_cita: int, ctx: Contexto = Depends(SOLO_ADMISION), db: Session = Depends(get_db)):
    cita = agenda.registrar_llegada(db, ctx, id_cita)
    db.commit()
    return composicion.cita_salida(db, cita, clinico=False)


@router.post(
    "/citas/{id_cita}/cancelar",
    response_model=CitaSalida,
    summary="Cancelar con motivo obligatorio y liberar el turno (HU06)",
    responses={409: {"description": "La cita no está confirmada"}},
)
def cancelar_cita(
    id_cita: int,
    datos: CitaCancelar,
    ctx: Contexto = Depends(SOLO_ADMISION),
    db: Session = Depends(get_db),
):
    cita = agenda.obtener_cita(db, id_cita)
    paciente = hce.obtener_paciente(db, cita.id_paciente)
    cita = agenda.cancelar(db, ctx, id_cita, datos.motivo, paciente)
    db.commit()
    return composicion.cita_salida(db, cita, clinico=False)


@router.post(
    "/citas/{id_cita}/reprogramar",
    status_code=201,
    response_model=CitaSalida,
    summary="Reprogramar: anula la reserva previa y crea la nueva cita enlazada (HU06)",
    responses={409: {"description": "Nuevo horario ocupado o cita no confirmada"}},
)
def reprogramar_cita(
    id_cita: int,
    datos: CitaReprogramar,
    ctx: Contexto = Depends(SOLO_ADMISION),
    db: Session = Depends(get_db),
):
    original = agenda.obtener_cita(db, id_cita)
    paciente = hce.obtener_paciente(db, original.id_paciente)
    nueva = agenda.reprogramar(
        db,
        ctx,
        id_cita,
        paciente=paciente,
        id_medico=datos.id_medico,
        id_consultorio=datos.id_consultorio,
        inicio=datos.fecha_hora_inicio,
        motivo=datos.motivo,
        enviar_recordatorio=datos.enviar_recordatorio,
    )
    return composicion.cita_salida(db, nueva, clinico=False)


@router.post(
    "/citas/{id_cita}/no-asistio",
    response_model=CitaSalida,
    summary="Registrar la inasistencia del paciente (indicador de no-show)",
)
def registrar_inasistencia(id_cita: int, ctx: Contexto = Depends(SOLO_ADMISION), db: Session = Depends(get_db)):
    cita = agenda.registrar_inasistencia(db, ctx, id_cita)
    db.commit()
    return composicion.cita_salida(db, cita, clinico=False)
