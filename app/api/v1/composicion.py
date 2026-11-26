"""Composición de respuestas que combinan datos de varios módulos (SAD 5.1.3, regla 4).

Cada módulo expone sus servicios; aquí se juntan sin crear dependencias cíclicas.
"""

from sqlalchemy.orm import Session

from app.core.errores import Prohibido
from app.modulos.agenda import service as agenda
from app.modulos.agenda.models import Cita, Medico
from app.modulos.agenda.schemas import (
    AtencionDeCita,
    CitaSalida,
    ConsultorioSalida,
    PacienteCita,
    TriajeBreve,
)
from app.modulos.convenios import service as convenios
from app.modulos.hce import service as hce
from app.modulos.hce.models import Atencion, Paciente, Triaje
from app.modulos.hce.schemas import (
    AtencionEnCurso,
    AtencionResumen,
    AtencionSalida,
    ConvenioResumen,
    DiagnosticoSalida,
    MedicoResumen,
    PacienteSalida,
    PrescripcionSalida,
    TriajeSalida,
)

ORDEN_DIAGNOSTICO = {"PRINCIPAL": 0, "SECUNDARIO": 1, "PRESUNTIVO": 2}


def medico_actual(db: Session, ctx) -> Medico:
    medico = agenda.medico_de_usuario(db, ctx.id_usuario)
    if medico is None:
        raise Prohibido("Su usuario no está vinculado a un médico")
    return medico


def medico_resumen(medico: Medico | None) -> MedicoResumen | None:
    if medico is None:
        return None
    return MedicoResumen(
        id_medico=medico.id_medico,
        nombre_completo=medico.nombre_completo,
        especialidad=medico.especialidad.nombre,
        cmp=medico.cmp,
    )


def pacientes_salida(db: Session, pacientes: list[Paciente], clinico: bool) -> list[PacienteSalida]:
    mapa = convenios.mapa_convenios(db)
    salida = []
    for paciente in pacientes:
        convenio = mapa.get(paciente.id_convenio)
        datos = PacienteSalida.model_validate(paciente).model_copy(
            update={"convenio": ConvenioResumen.model_validate(convenio) if convenio else None}
        )
        if not clinico:
            datos = datos.model_copy(update={"alergias": None, "antecedentes_medicos": None})
        salida.append(datos)
    return salida


def paciente_salida(db: Session, paciente: Paciente, clinico: bool) -> PacienteSalida:
    return pacientes_salida(db, [paciente], clinico)[0]


def triaje_salida(triaje: Triaje | None) -> TriajeSalida | None:
    if triaje is None:
        return None
    return TriajeSalida.model_validate(
        {
            **{c.key: getattr(triaje, c.key) for c in Triaje.__table__.columns},
            "imc": hce.imc(triaje),
            "alertas": hce.alertas_triaje(triaje),
        }
    )


def _datos_resumen(atencion: Atencion, medicos: dict[int, Medico]) -> dict:
    return {
        "id_atencion": atencion.id_atencion,
        "id_paciente": atencion.id_paciente,
        "id_cita": atencion.id_cita,
        "tipo_atencion": atencion.tipo_atencion,
        "estado": atencion.estado,
        "fecha": atencion.fecha,
        "medico": medico_resumen(medicos.get(atencion.id_medico)),
        "anulado": atencion.anulado,
        "motivo_anulacion": atencion.motivo_anulacion,
        "anulado_en": atencion.anulado_en,
    }


def atenciones_resumen(db: Session, atenciones: list[Atencion]) -> list[AtencionResumen]:
    medicos = agenda.medicos_por_ids(db, {a.id_medico for a in atenciones})
    return [AtencionResumen(**_datos_resumen(a, medicos)) for a in atenciones]


def atenciones_salida(db: Session, atenciones: list[Atencion]) -> list[AtencionSalida]:
    medicos = agenda.medicos_por_ids(db, {a.id_medico for a in atenciones})
    salida = []
    for atencion in atenciones:
        diagnosticos = sorted(atencion.diagnosticos, key=lambda d: ORDEN_DIAGNOSTICO.get(d.tipo, 9))
        salida.append(
            AtencionSalida(
                **_datos_resumen(atencion, medicos),
                creado_en=atencion.creado_en,
                inicio_consulta=atencion.inicio_consulta,
                finalizada_en=atencion.finalizada_en,
                motivo_consulta=atencion.motivo_consulta,
                anamnesis=atencion.anamnesis,
                indicaciones=atencion.indicaciones,
                triaje=triaje_salida(atencion.triaje),
                diagnosticos=[
                    DiagnosticoSalida(
                        codigo=d.codigo_cie10, descripcion=d.diagnostico.descripcion, tipo=d.tipo
                    )
                    for d in diagnosticos
                ],
                prescripciones=[PrescripcionSalida.model_validate(p) for p in atencion.prescripciones],
            )
        )
    return salida


def atencion_salida(db: Session, atencion: Atencion) -> AtencionSalida:
    return atenciones_salida(db, [atencion])[0]


def atenciones_en_curso(db: Session, atenciones: list[Atencion]) -> list[AtencionEnCurso]:
    pacientes = pacientes_salida(db, [a.paciente for a in atenciones], clinico=True)
    return [
        AtencionEnCurso(
            id_atencion=a.id_atencion,
            tipo_atencion=a.tipo_atencion,
            creado_en=a.creado_en,
            paciente=p,
            triaje=triaje_salida(a.triaje),
        )
        for a, p in zip(atenciones, pacientes)
    ]


def citas_salida(db: Session, citas: list[Cita], clinico: bool) -> list[CitaSalida]:
    pacientes = hce.pacientes_por_ids(db, {c.id_paciente for c in citas})
    atenciones = hce.resumen_por_citas(db, {c.id_cita for c in citas})
    derivadas = agenda.citas_derivadas(db, {c.id_cita for c in citas if c.estado == "REPROGRAMADA"})
    mapa_convenios = convenios.mapa_convenios(db)
    salida = []
    for cita in citas:
        paciente = pacientes[cita.id_paciente]
        convenio = mapa_convenios.get(paciente.id_convenio)
        atencion = atenciones.get(cita.id_cita)
        resumen_atencion = None
        if atencion is not None:
            triaje = atencion.triaje
            resumen_atencion = AtencionDeCita(
                id_atencion=atencion.id_atencion,
                estado=atencion.estado,
                anulado=atencion.anulado,
                triaje=TriajeBreve.model_validate(triaje, from_attributes=True) if triaje else None,
                alertas=hce.alertas_triaje(triaje) if triaje else [],
            )
        salida.append(
            CitaSalida(
                id_cita=cita.id_cita,
                fecha_hora_inicio=cita.fecha_hora_inicio,
                fecha_hora_fin=cita.fecha_hora_fin,
                estado=cita.estado,
                motivo_cancelacion=cita.motivo_cancelacion,
                hora_llegada=cita.hora_llegada,
                id_cita_origen=cita.id_cita_origen,
                id_cita_nueva=derivadas.get(cita.id_cita),
                canal_agendamiento=cita.canal_agendamiento,
                creado_en=cita.creado_en,
                paciente=PacienteCita(
                    id_paciente=paciente.id_paciente,
                    tipo_documento=paciente.tipo_documento,
                    numero_documento=paciente.numero_documento,
                    nombre_completo=paciente.nombre_completo,
                    edad=paciente.edad,
                    sexo=paciente.sexo,
                    telefono=paciente.telefono,
                    convenio=convenio.nombre_institucion if convenio else None,
                    alergias=paciente.alergias if clinico else None,
                ),
                medico=medico_resumen(cita.medico),
                consultorio=ConsultorioSalida.model_validate(cita.consultorio),
                atencion=resumen_atencion,
            )
        )
    return salida


def cita_salida(db: Session, cita: Cita, clinico: bool) -> CitaSalida:
    return citas_salida(db, [cita], clinico)[0]
