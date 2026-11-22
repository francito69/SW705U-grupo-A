"""M2 - Agenda: disponibilidad, agendamiento sin solapamientos (RF-002) y ciclo de la cita."""

import threading
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import tiempo
from app.core.errores import Conflicto, NoEncontrado, ReglaNegocio
from app.core.texto import normalizar
from app.modulos.auditoria import service as auditoria
from app.modulos.hce.models import Paciente
from app.modulos.notificaciones import service as notificaciones

from .models import ESTADOS_ACTIVOS, Cita, Consultorio, Especialidad, Medico

DURACION_MINUTOS = 30
DURACION = timedelta(minutes=DURACION_MINUTOS)
TURNOS = (("MAÑANA", time(8, 0), time(13, 0)), ("TARDE", time(14, 0), time(19, 0)))
HORIZONTE_DIAS = 90
DOMINGO = 6
CAMPOS_AUDITADOS = (
    "id_paciente",
    "id_medico",
    "id_consultorio",
    "fecha_hora_inicio",
    "fecha_hora_fin",
    "estado",
    "canal_agendamiento",
    "id_cita_origen",
)

# Sección crítica de agendamiento en este proceso; en PostgreSQL la garantía final
# la dan las restricciones EXCLUDE no_solapamiento_medico y no_solapamiento_consultorio.
_candado_agenda = threading.Lock()


def turnos_del_dia(fecha: date) -> list[tuple[str, datetime, datetime]]:
    if fecha.weekday() == DOMINGO:
        return []
    bloques = []
    for nombre, hora_inicio, hora_fin in TURNOS:
        actual = datetime.combine(fecha, hora_inicio)
        limite = datetime.combine(fecha, hora_fin)
        while actual + DURACION <= limite:
            bloques.append((nombre, actual, actual + DURACION))
            actual += DURACION
    return bloques


def validar_horario(inicio: datetime) -> datetime:
    if inicio.tzinfo is not None:
        inicio = inicio.astimezone(tiempo.ZONA_LIMA).replace(tzinfo=None)
    if inicio.second or inicio.microsecond or inicio.minute % DURACION_MINUTOS:
        raise ReglaNegocio("La cita debe empezar en un bloque de 30 minutos (por ejemplo 09:00 o 09:30)")
    if inicio <= tiempo.ahora():
        raise ReglaNegocio("No se puede agendar una cita en una fecha u hora pasada")
    if inicio.date() > tiempo.hoy() + timedelta(days=HORIZONTE_DIAS):
        raise ReglaNegocio(f"Solo se puede agendar con hasta {HORIZONTE_DIAS} días de anticipación")
    if inicio not in {bloque[1] for bloque in turnos_del_dia(inicio.date())}:
        raise ReglaNegocio(
            "Fuera del horario de atención: lunes a sábado de 08:00 a 13:00 y de 14:00 a 19:00"
        )
    return inicio


def listar_especialidades(db: Session) -> list[tuple[Especialidad, int]]:
    filas = db.execute(
        select(Especialidad, func.count(Medico.id_medico))
        .outerjoin(
            Medico,
            (Medico.id_especialidad == Especialidad.id_especialidad) & Medico.activo.is_(True),
        )
        .group_by(Especialidad.id_especialidad)
        .order_by(Especialidad.nombre)
    ).all()
    return [(fila[0], fila[1]) for fila in filas]


def obtener_especialidad(db: Session, id_especialidad: int) -> Especialidad:
    especialidad = db.get(Especialidad, id_especialidad)
    if especialidad is None:
        raise NoEncontrado(f"No existe la especialidad {id_especialidad}")
    return especialidad


def listar_medicos(db: Session, id_especialidad: int | None = None) -> list[Medico]:
    consulta = select(Medico).where(Medico.activo.is_(True))
    if id_especialidad:
        consulta = consulta.where(Medico.id_especialidad == id_especialidad)
    return list(db.scalars(consulta.order_by(Medico.apellidos, Medico.nombres)))


def obtener_medico(db: Session, id_medico: int) -> Medico:
    medico = db.get(Medico, id_medico)
    if medico is None:
        raise NoEncontrado(f"No existe el médico {id_medico}")
    return medico


def medicos_por_ids(db: Session, ids: set[int]) -> dict[int, Medico]:
    if not ids:
        return {}
    return {m.id_medico: m for m in db.scalars(select(Medico).where(Medico.id_medico.in_(ids)))}


def medico_de_usuario(db: Session, id_usuario: int) -> Medico | None:
    return db.scalar(select(Medico).where(Medico.id_usuario == id_usuario))


def listar_consultorios(db: Session) -> list[Consultorio]:
    return list(
        db.scalars(select(Consultorio).where(Consultorio.activo.is_(True)).order_by(Consultorio.numero))
    )


def obtener_consultorio(db: Session, id_consultorio: int) -> Consultorio:
    consultorio = db.get(Consultorio, id_consultorio)
    if consultorio is None:
        raise NoEncontrado(f"No existe el consultorio {id_consultorio}")
    return consultorio


def _activas_en_rango(db: Session, desde: datetime, hasta: datetime) -> list[Cita]:
    return list(
        db.scalars(
            select(Cita).where(
                Cita.estado.in_(ESTADOS_ACTIVOS),
                Cita.fecha_hora_inicio < hasta,
                Cita.fecha_hora_fin > desde,
            )
        )
    )


def _cruce(
    db: Session,
    inicio: datetime,
    fin: datetime,
    *,
    excluir: int | None = None,
    **filtro,
) -> Cita | None:
    consulta = select(Cita).where(
        Cita.estado.in_(ESTADOS_ACTIVOS),
        Cita.fecha_hora_inicio < fin,
        Cita.fecha_hora_fin > inicio,
        *(getattr(Cita, campo) == valor for campo, valor in filtro.items()),
    )
    if excluir is not None:
        consulta = consulta.where(Cita.id_cita != excluir)
    return db.scalar(consulta.limit(1))


def consultorios_libres(
    db: Session, inicio: datetime, excluir: int | None = None
) -> list[Consultorio]:
    ocupados = {
        c.id_consultorio
        for c in _activas_en_rango(db, inicio, inicio + DURACION)
        if c.id_cita != excluir
    }
    return [c for c in listar_consultorios(db) if c.id_consultorio not in ocupados]


def consultorio_habitual(db: Session, medico: Medico, consultorios: list[Consultorio]) -> Consultorio | None:
    activos = {c.id_consultorio: c for c in consultorios}
    mas_usado = db.execute(
        select(Cita.id_consultorio, func.count().label("veces"))
        .where(Cita.id_medico == medico.id_medico)
        .group_by(Cita.id_consultorio)
        .order_by(func.count().desc(), Cita.id_consultorio)
        .limit(1)
    ).first()
    if mas_usado is not None and mas_usado[0] in activos:
        return activos[mas_usado[0]]
    especialidad = normalizar(medico.especialidad.nombre)
    return next(
        (c for c in consultorios if c.descripcion and normalizar(c.descripcion) == especialidad), None
    )


def disponibilidad(
    db: Session, fecha: date, id_especialidad: int, id_medico: int | None = None
) -> dict:
    especialidad = obtener_especialidad(db, id_especialidad)
    medicos = [m for m in listar_medicos(db, id_especialidad) if id_medico in (None, m.id_medico)]
    bloques = turnos_del_dia(fecha)
    resultado = {
        "fecha": fecha,
        "id_especialidad": especialidad.id_especialidad,
        "especialidad": especialidad.nombre,
        "duracion_minutos": DURACION_MINUTOS,
        "atiende": bool(bloques),
        "mensaje": None if bloques else "La clínica no atiende los domingos",
        "medicos": [],
    }
    if not bloques:
        return resultado
    if fecha > tiempo.hoy() + timedelta(days=HORIZONTE_DIAS):
        resultado["atiende"] = False
        resultado["mensaje"] = f"Solo se puede agendar con hasta {HORIZONTE_DIAS} días de anticipación"
        return resultado
    inicio_dia = datetime.combine(fecha, time.min)
    activas = _activas_en_rango(db, inicio_dia, inicio_dia + timedelta(days=1))
    consultorios = listar_consultorios(db)
    ahora = tiempo.ahora()
    for medico in medicos:
        habitual = consultorio_habitual(db, medico, consultorios)
        turnos = []
        for turno, inicio, fin in bloques:
            cruzan = [c for c in activas if c.fecha_hora_inicio < fin and c.fecha_hora_fin > inicio]
            propia = next((c for c in cruzan if c.id_medico == medico.id_medico), None)
            ocupados = {c.id_consultorio for c in cruzan}
            sugerido = habitual if habitual and habitual.id_consultorio not in ocupados else None
            if sugerido is None:
                sugerido = next((c for c in consultorios if c.id_consultorio not in ocupados), None)
            if propia is not None:
                estado = "OCUPADO"
            elif inicio <= ahora:
                estado = "PASADO"
            elif sugerido is None:
                estado = "SIN_CONSULTORIO"
            else:
                estado = "LIBRE"
            libre = estado == "LIBRE"
            turnos.append(
                {
                    "turno": turno,
                    "inicio": inicio,
                    "fin": fin,
                    "estado": estado,
                    "id_cita": propia.id_cita if propia else None,
                    "id_consultorio_sugerido": sugerido.id_consultorio if libre else None,
                    "consultorio_sugerido": sugerido.numero if libre else None,
                }
            )
        resultado["medicos"].append(
            {
                "id_medico": medico.id_medico,
                "nombre_completo": medico.nombre_completo,
                "cmp": medico.cmp,
                "especialidad": medico.especialidad.nombre,
                "id_consultorio_habitual": habitual.id_consultorio if habitual else None,
                "consultorio_habitual": habitual.numero if habitual else None,
                "libres": sum(1 for t in turnos if t["estado"] == "LIBRE"),
                "ocupados": sum(1 for t in turnos if t["estado"] == "OCUPADO"),
                "turnos": turnos,
            }
        )
    return resultado


def obtener_cita(db: Session, id_cita: int) -> Cita:
    cita = db.get(Cita, id_cita)
    if cita is None:
        raise NoEncontrado(f"No existe la cita {id_cita}")
    return cita


def listar_citas(
    db: Session,
    *,
    fecha: date | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    id_medico: int | None = None,
    estado: str | None = None,
    id_paciente: int | None = None,
    limite: int = 500,
) -> list[Cita]:
    consulta = select(Cita)
    if fecha:
        inicio = datetime.combine(fecha, time.min)
        consulta = consulta.where(
            Cita.fecha_hora_inicio >= inicio, Cita.fecha_hora_inicio < inicio + timedelta(days=1)
        )
    if desde:
        consulta = consulta.where(Cita.fecha_hora_inicio >= datetime.combine(desde, time.min))
    if hasta:
        consulta = consulta.where(
            Cita.fecha_hora_inicio < datetime.combine(hasta, time.min) + timedelta(days=1)
        )
    if id_medico:
        consulta = consulta.where(Cita.id_medico == id_medico)
    if estado:
        consulta = consulta.where(Cita.estado == estado)
    if id_paciente:
        consulta = consulta.where(Cita.id_paciente == id_paciente)
    if id_paciente and not (fecha or desde or hasta):
        consulta = consulta.order_by(Cita.fecha_hora_inicio.desc(), Cita.id_cita.desc())
    else:
        consulta = consulta.order_by(Cita.fecha_hora_inicio, Cita.id_cita)
    return list(db.scalars(consulta.limit(limite)))


def citas_derivadas(db: Session, ids: set[int]) -> dict[int, int]:
    if not ids:
        return {}
    filas = db.execute(select(Cita.id_cita_origen, Cita.id_cita).where(Cita.id_cita_origen.in_(ids)))
    return {origen: nueva for origen, nueva in filas}


def _verificar_cruces(
    db: Session,
    inicio: datetime,
    fin: datetime,
    medico: Medico,
    consultorio: Consultorio,
    id_paciente: int,
    excluir: int | None = None,
) -> None:
    if _cruce(db, inicio, fin, excluir=excluir, id_medico=medico.id_medico):
        raise Conflicto(
            f"El médico {medico.nombre_completo} ya tiene una cita en ese horario", recurso="medico"
        )
    if _cruce(db, inicio, fin, excluir=excluir, id_consultorio=consultorio.id_consultorio):
        raise Conflicto(
            f"El consultorio {consultorio.numero} ya está ocupado en ese horario", recurso="consultorio"
        )
    if _cruce(db, inicio, fin, excluir=excluir, id_paciente=id_paciente):
        raise Conflicto("El paciente ya tiene otra cita en ese horario", recurso="paciente")


@contextmanager
def _transaccion_agenda(db: Session):
    """Sección crítica del agendamiento: valida, inserta y confirma en un solo bloque.

    Si otra reserva gana la carrera, PostgreSQL rechaza el INSERT con la restricción
    EXCLUDE y aquí se traduce a HTTP 409 sin dejar datos a medias (RN-01).
    """
    with _candado_agenda:
        try:
            yield
            db.commit()
        except IntegrityError as error:
            db.rollback()
            texto = str(error.orig)
            if "no_solapamiento_consultorio" in texto:
                raise Conflicto("El consultorio ya está ocupado en ese horario", recurso="consultorio") from None
            if "no_solapamiento_medico" in texto:
                raise Conflicto("El médico ya tiene una cita en ese horario", recurso="medico") from None
            raise Conflicto("El horario ya no está disponible, elija otro") from None


def _datos_mensaje(cita: Cita) -> dict:
    return {
        "especialidad": cita.medico.especialidad.nombre,
        "fecha": tiempo.formato_fecha(cita.fecha_hora_inicio),
        "hora": tiempo.formato_hora(cita.fecha_hora_inicio),
        "consultorio": cita.consultorio.numero,
    }


def _notificar(db: Session, cita: Cita, paciente: Paciente, plantilla: str, recordatorio: bool) -> None:
    datos = _datos_mensaje(cita)
    mensajes = {
        "confirmada": "Clínica San Rafael: su cita de {especialidad} quedó confirmada para el "
        "{fecha} a las {hora} en el consultorio {consultorio}.",
        "reprogramada": "Clínica San Rafael: su cita de {especialidad} fue reprogramada para el "
        "{fecha} a las {hora} en el consultorio {consultorio}.",
        "cancelada": "Clínica San Rafael: su cita de {especialidad} del {fecha} a las {hora} fue "
        "cancelada. Comuníquese con admisión si desea reprogramarla.",
    }
    ahora = tiempo.ahora()
    notificaciones.encolar(
        db,
        id_cita=cita.id_cita,
        tipo_evento="CONFIRMACION_CITA",
        canal="SMS",
        destinatario=paciente.telefono,
        mensaje=mensajes[plantilla].format(**datos),
        programado_para=ahora,
    )
    momento = cita.fecha_hora_inicio - timedelta(hours=24)
    if recordatorio and momento > ahora:
        notificaciones.encolar(
            db,
            id_cita=cita.id_cita,
            tipo_evento="RECORDATORIO_24H",
            canal="SMS",
            destinatario=paciente.telefono,
            mensaje="Clínica San Rafael: recuerde su cita de {especialidad} el {fecha} a las {hora} "
            "en el consultorio {consultorio}.".format(**datos),
            programado_para=momento,
        )


def _preparar(db: Session, paciente: Paciente, id_medico: int, id_consultorio: int, inicio: datetime):
    if not paciente.activo:
        raise ReglaNegocio("El paciente está inactivo")
    medico = obtener_medico(db, id_medico)
    if not medico.activo:
        raise ReglaNegocio(f"El médico {medico.nombre_completo} no está activo")
    consultorio = obtener_consultorio(db, id_consultorio)
    if not consultorio.activo:
        raise ReglaNegocio(f"El consultorio {consultorio.numero} no está activo")
    inicio = validar_horario(inicio)
    return medico, consultorio, inicio, inicio + DURACION


def crear_cita(
    db: Session,
    actor,
    *,
    paciente: Paciente,
    id_medico: int,
    id_consultorio: int,
    inicio: datetime,
    canal: str,
    enviar_recordatorio: bool,
) -> Cita:
    medico, consultorio, inicio, fin = _preparar(db, paciente, id_medico, id_consultorio, inicio)
    with _transaccion_agenda(db):
        _verificar_cruces(db, inicio, fin, medico, consultorio, paciente.id_paciente)
        cita = Cita(
            id_paciente=paciente.id_paciente,
            id_medico=medico.id_medico,
            id_consultorio=consultorio.id_consultorio,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado="CONFIRMADA",
            canal_agendamiento=canal,
            creado_por=actor.id_usuario,
        )
        db.add(cita)
        db.flush()
        auditoria.registrar(
            db, actor, "citas", cita.id_cita, "INSERT", despues=auditoria.instantanea(cita, CAMPOS_AUDITADOS)
        )
        _notificar(db, cita, paciente, "confirmada", enviar_recordatorio)
    return cita


def reprogramar(
    db: Session,
    actor,
    id_cita: int,
    *,
    paciente: Paciente,
    id_medico: int | None,
    id_consultorio: int,
    inicio: datetime,
    motivo: str,
    enviar_recordatorio: bool,
) -> Cita:
    original = obtener_cita(db, id_cita)
    if original.estado != "CONFIRMADA":
        raise Conflicto(f"Solo se reprograman citas confirmadas (estado actual: {original.estado})")
    medico, consultorio, inicio, fin = _preparar(
        db, paciente, id_medico or original.id_medico, id_consultorio, inicio
    )
    with _transaccion_agenda(db):
        _verificar_cruces(db, inicio, fin, medico, consultorio, paciente.id_paciente, excluir=original.id_cita)
        original.estado = "REPROGRAMADA"
        original.motivo_cancelacion = motivo
        db.flush()
        nueva = Cita(
            id_paciente=original.id_paciente,
            id_medico=medico.id_medico,
            id_consultorio=consultorio.id_consultorio,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado="CONFIRMADA",
            id_cita_origen=original.id_cita,
            canal_agendamiento=original.canal_agendamiento,
            creado_por=actor.id_usuario,
        )
        db.add(nueva)
        db.flush()
        notificaciones.descartar_pendientes(db, original.id_cita, "la cita fue reprogramada")
        _notificar(db, nueva, paciente, "reprogramada", enviar_recordatorio)
        auditoria.registrar(
            db,
            actor,
            "citas",
            original.id_cita,
            "UPDATE",
            antes={"estado": "CONFIRMADA"},
            despues={"estado": "REPROGRAMADA", "id_cita_nueva": nueva.id_cita},
            motivo=motivo,
        )
        auditoria.registrar(
            db, actor, "citas", nueva.id_cita, "INSERT", despues=auditoria.instantanea(nueva, CAMPOS_AUDITADOS)
        )
    return nueva


def _cambiar_estado(db: Session, actor, cita: Cita, nuevo: str, motivo: str | None = None) -> Cita:
    anterior = cita.estado
    cita.estado = nuevo
    db.flush()
    auditoria.registrar(
        db, actor, "citas", cita.id_cita, "UPDATE", antes={"estado": anterior}, despues={"estado": nuevo}, motivo=motivo
    )
    return cita


def cancelar(db: Session, actor, id_cita: int, motivo: str, paciente: Paciente) -> Cita:
    cita = obtener_cita(db, id_cita)
    if cita.estado != "CONFIRMADA":
        raise Conflicto(f"Solo se cancelan citas confirmadas (estado actual: {cita.estado})")
    cita.motivo_cancelacion = motivo
    _cambiar_estado(db, actor, cita, "CANCELADA", motivo)
    notificaciones.descartar_pendientes(db, cita.id_cita, "la cita fue cancelada")
    _notificar(db, cita, paciente, "cancelada", recordatorio=False)
    return cita


def registrar_llegada(db: Session, actor, id_cita: int) -> Cita:
    cita = obtener_cita(db, id_cita)
    if cita.estado != "CONFIRMADA":
        raise Conflicto(f"Solo se registra la llegada de citas confirmadas (estado actual: {cita.estado})")
    if cita.fecha_hora_inicio.date() != tiempo.hoy():
        raise ReglaNegocio("La llegada solo se registra el mismo día de la cita")
    cita.hora_llegada = tiempo.ahora()
    _cambiar_estado(db, actor, cita, "EN_ESPERA")
    notificaciones.descartar_pendientes(db, cita.id_cita, "el paciente ya llegó a la clínica")
    return cita


def registrar_inasistencia(db: Session, actor, id_cita: int) -> Cita:
    cita = obtener_cita(db, id_cita)
    if cita.estado != "CONFIRMADA":
        raise Conflicto(f"Solo se marca la inasistencia de citas confirmadas (estado actual: {cita.estado})")
    if cita.fecha_hora_inicio > tiempo.ahora():
        raise ReglaNegocio("La inasistencia se registra cuando ya pasó la hora de la cita")
    _cambiar_estado(db, actor, cita, "NO_ASISTIO")
    notificaciones.descartar_pendientes(db, cita.id_cita, "el paciente no asistió")
    return cita


def marcar_atendida(db: Session, actor, id_cita: int) -> None:
    cita = obtener_cita(db, id_cita)
    if cita.estado == "EN_ESPERA":
        _cambiar_estado(db, actor, cita, "ATENDIDA")
