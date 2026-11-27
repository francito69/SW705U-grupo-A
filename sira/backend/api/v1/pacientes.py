from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.errores import ReglaNegocio
from backend.database import get_db
from backend.modulos.convenios import service as convenios
from backend.modulos.hce import service as hce
from backend.modulos.hce.schemas import (
    AntecedentesActualizar,
    AtencionResumen,
    HistoriaClinica,
    PacienteActualizar,
    PacienteCrear,
    PacienteSalida,
    TipoDocumento,
)
from backend.modulos.seguridad.dependencias import Contexto, requiere_roles

from . import composicion

router = APIRouter(prefix="/pacientes", tags=["M1 · Pacientes e historia clínica"])

LECTURA = ("ADMISION", "MEDICO", "ENFERMERA", "GERENCIA", "CAJA")
CAMPOS_ANULABLES = ("email", "direccion")


def _validar_convenio(db: Session, id_convenio: int | None) -> None:
    if id_convenio is None:
        return
    convenio = convenios.obtener_convenio(db, id_convenio)
    if convenio is None or not convenio.activo:
        raise ReglaNegocio("El convenio seleccionado no existe o no está activo", campo="id_convenio")


@router.get("", response_model=list[PacienteSalida], summary="Buscar pacientes por documento o nombre")
def buscar_pacientes(
    q: str | None = Query(default=None, max_length=100, description="Documento o nombres y apellidos"),
    tipo_documento: TipoDocumento | None = None,
    numero_documento: str | None = Query(default=None, max_length=15),
    limite: int = Query(default=20, ge=1, le=100),
    ctx: Contexto = Depends(requiere_roles(*LECTURA)),
    db: Session = Depends(get_db),
):
    pacientes = hce.buscar_pacientes(
        db, q=q, tipo_documento=tipo_documento, numero_documento=numero_documento, limite=limite
    )
    return composicion.pacientes_salida(db, pacientes, ctx.es_clinico)


@router.post(
    "",
    status_code=201,
    response_model=PacienteSalida,
    summary="Registrar un paciente nuevo (HU03)",
    responses={
        409: {"description": "Paciente ya registrado; la respuesta incluye su id_paciente"},
        422: {"description": "Datos o convenio no válidos"},
    },
)
def registrar_paciente(
    datos: PacienteCrear,
    ctx: Contexto = Depends(requiere_roles("ADMISION")),
    db: Session = Depends(get_db),
):
    _validar_convenio(db, datos.id_convenio)
    paciente = hce.registrar_paciente(db, ctx, datos.model_dump())
    db.commit()
    return composicion.paciente_salida(db, paciente, clinico=False)


@router.get("/{id_paciente}", response_model=PacienteSalida, summary="Ficha de filiación del paciente")
def obtener_paciente(
    id_paciente: int,
    ctx: Contexto = Depends(requiere_roles(*LECTURA)),
    db: Session = Depends(get_db),
):
    return composicion.paciente_salida(db, hce.obtener_paciente(db, id_paciente), ctx.es_clinico)


@router.patch(
    "/{id_paciente}",
    response_model=PacienteSalida,
    summary="Actualizar datos de filiación",
    responses={404: {"description": "Paciente no encontrado"}},
)
def actualizar_paciente(
    id_paciente: int,
    datos: PacienteActualizar,
    ctx: Contexto = Depends(requiere_roles("ADMISION")),
    db: Session = Depends(get_db),
):
    cambios = {
        campo: valor
        for campo, valor in datos.model_dump(exclude_unset=True).items()
        if valor is not None or campo in CAMPOS_ANULABLES
    }
    _validar_convenio(db, cambios.get("id_convenio"))
    paciente = hce.actualizar_filiacion(db, ctx, id_paciente, cambios)
    db.commit()
    return composicion.paciente_salida(db, paciente, clinico=False)


@router.patch(
    "/{id_paciente}/antecedentes",
    response_model=PacienteSalida,
    summary="Actualizar alergias y antecedentes (personal clínico)",
)
def actualizar_antecedentes(
    id_paciente: int,
    datos: AntecedentesActualizar,
    ctx: Contexto = Depends(requiere_roles("MEDICO", "ENFERMERA", tabla="pacientes", parametro_id="id_paciente")),
    db: Session = Depends(get_db),
):
    paciente = hce.actualizar_antecedentes(db, ctx, id_paciente, datos.model_dump(exclude_unset=True))
    db.commit()
    return composicion.paciente_salida(db, paciente, clinico=True)


@router.get(
    "/{id_paciente}/hce",
    response_model=HistoriaClinica,
    summary="Historia clínica electrónica unificada (HU01)",
    responses={403: {"description": "Rol sin permiso; el intento queda en la bitácora"}},
)
def historia_clinica(
    id_paciente: int,
    limite: int = Query(default=10, ge=1, le=200),
    desplazamiento: int = Query(default=0, ge=0),
    ctx: Contexto = Depends(requiere_roles("MEDICO", tabla="pacientes", parametro_id="id_paciente")),
    db: Session = Depends(get_db),
):
    paciente, total, atenciones = hce.historia_clinica(db, ctx, id_paciente, limite, desplazamiento)
    db.commit()
    return HistoriaClinica(
        paciente=composicion.paciente_salida(db, paciente, clinico=True),
        total_atenciones=total,
        atenciones=composicion.atenciones_salida(db, atenciones),
    )


@router.get(
    "/{id_paciente}/atenciones",
    response_model=list[AtencionResumen],
    summary="Atenciones del paciente sin contenido clínico (para anulaciones)",
)
def atenciones_del_paciente(
    id_paciente: int,
    ctx: Contexto = Depends(requiere_roles("GERENCIA", "MEDICO", tabla="pacientes", parametro_id="id_paciente")),
    db: Session = Depends(get_db),
):
    return composicion.atenciones_resumen(db, hce.atenciones_de_paciente(db, id_paciente))
