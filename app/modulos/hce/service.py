"""M1 - Reglas de la historia clínica: filiación, triaje, atención y anulación lógica."""

import re

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core import tiempo
from app.core.errores import Conflicto, NoEncontrado, Prohibido, ReglaNegocio
from app.core.texto import normalizar
from app.modulos.auditoria import service as auditoria

from .models import Atencion, AtencionDiagnostico, DiagnosticoCIE10, Paciente, Prescripcion, Triaje

CAMPOS_FILIACION = (
    "nombres",
    "apellido_paterno",
    "apellido_materno",
    "fecha_nacimiento",
    "sexo",
    "telefono",
    "email",
    "direccion",
    "id_convenio",
)
CAMPOS_ANTECEDENTES = ("alergias", "antecedentes_medicos")
CAMPOS_TRIAJE = (
    "presion_sistolica",
    "presion_diastolica",
    "temperatura",
    "frecuencia_cardiaca",
    "frecuencia_respiratoria",
    "saturacion_oxigeno",
    "peso",
    "talla",
    "observaciones",
)

# Familias de fármacos para advertir alergias cruzadas (advertencia, no diagnóstico).
FAMILIAS_ALERGIA = {
    "penicilina": (
        "penicilina",
        "amoxicilina",
        "ampicilina",
        "dicloxacilina",
        "oxacilina",
        "piperacilina",
        "benzatinica",
    ),
    "amoxicilina": ("amoxicilina", "ampicilina", "penicilina"),
    "sulfa": ("sulfametoxazol", "cotrimoxazol", "sulfadiazina", "sulfasalazina"),
    "aine": (
        "ibuprofeno",
        "naproxeno",
        "diclofenaco",
        "ketorolaco",
        "meloxicam",
        "piroxicam",
        "aspirina",
        "acido acetilsalicilico",
    ),
    "acetilsalicilico": ("aspirina", "acido acetilsalicilico"),
    "aspirina": ("aspirina", "acido acetilsalicilico"),
    "cefalosporina": ("cefalexina", "cefuroxima", "ceftriaxona", "cefazolina", "cefadroxilo"),
    "quinolona": ("ciprofloxacino", "levofloxacino", "moxifloxacino"),
    "macrolido": ("azitromicina", "claritromicina", "eritromicina"),
}
PALABRAS_GENERICAS = {"clorhidrato", "sulfato", "cloruro", "tableta", "capsula", "jarabe", "potasico"}


def _patron_flexible(token: str) -> str:
    # Las vocales se vuelven comodín para que "huaman" encuentre "Huamán".
    return "%" + re.sub(r"[aeiouáéíóúü]", "_", token.lower()) + "%"


def buscar_pacientes(
    db: Session,
    *,
    q: str | None = None,
    tipo_documento: str | None = None,
    numero_documento: str | None = None,
    limite: int = 20,
) -> list[Paciente]:
    consulta = select(Paciente).where(Paciente.activo.is_(True))
    if numero_documento:
        consulta = consulta.where(Paciente.numero_documento == numero_documento.strip())
    if tipo_documento:
        consulta = consulta.where(Paciente.tipo_documento == tipo_documento)
    for token in (q or "").split():
        patron = _patron_flexible(token)
        consulta = consulta.where(
            or_(
                Paciente.numero_documento.startswith(token),
                Paciente.nombres.ilike(patron),
                Paciente.apellido_paterno.ilike(patron),
                Paciente.apellido_materno.ilike(patron),
            )
        )
    consulta = consulta.order_by(
        Paciente.apellido_paterno, Paciente.apellido_materno, Paciente.nombres
    ).limit(limite)
    return list(db.scalars(consulta))


def obtener_paciente(db: Session, id_paciente: int) -> Paciente:
    paciente = db.get(Paciente, id_paciente)
    if paciente is None:
        raise NoEncontrado(f"No existe el paciente {id_paciente}")
    return paciente


def pacientes_por_ids(db: Session, ids: set[int]) -> dict[int, Paciente]:
    if not ids:
        return {}
    return {p.id_paciente: p for p in db.scalars(select(Paciente).where(Paciente.id_paciente.in_(ids)))}


def _buscar_documento(db: Session, tipo: str, numero: str) -> Paciente | None:
    return db.scalar(
        select(Paciente).where(Paciente.tipo_documento == tipo, Paciente.numero_documento == numero)
    )


def registrar_paciente(db: Session, actor, datos: dict) -> Paciente:
    existente = _buscar_documento(db, datos["tipo_documento"], datos["numero_documento"])
    if existente is not None:
        raise Conflicto("Paciente ya registrado", id_paciente=existente.id_paciente)
    paciente = Paciente(**datos)
    db.add(paciente)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existente = _buscar_documento(db, datos["tipo_documento"], datos["numero_documento"])
        raise Conflicto(
            "Paciente ya registrado", id_paciente=existente.id_paciente if existente else None
        ) from None
    auditoria.registrar(
        db,
        actor,
        "pacientes",
        paciente.id_paciente,
        "INSERT",
        despues=auditoria.instantanea(paciente, ("tipo_documento", "numero_documento") + CAMPOS_FILIACION),
    )
    return paciente


def _aplicar_cambios(db: Session, actor, paciente: Paciente, cambios: dict, campos) -> Paciente:
    antes, despues = {}, {}
    for campo, valor in cambios.items():
        if campo in campos and getattr(paciente, campo) != valor:
            antes[campo] = getattr(paciente, campo)
            despues[campo] = valor
            setattr(paciente, campo, valor)
    if despues:
        db.flush()
        auditoria.registrar(
            db, actor, "pacientes", paciente.id_paciente, "UPDATE", antes=antes, despues=despues
        )
    return paciente


def actualizar_filiacion(db: Session, actor, id_paciente: int, cambios: dict) -> Paciente:
    return _aplicar_cambios(db, actor, obtener_paciente(db, id_paciente), cambios, CAMPOS_FILIACION)


def actualizar_antecedentes(db: Session, actor, id_paciente: int, cambios: dict) -> Paciente:
    return _aplicar_cambios(db, actor, obtener_paciente(db, id_paciente), cambios, CAMPOS_ANTECEDENTES)


def _con_detalle(consulta):
    return consulta.options(
        selectinload(Atencion.triaje),
        selectinload(Atencion.diagnosticos),
        selectinload(Atencion.prescripciones),
    )


def historia_clinica(
    db: Session, actor, id_paciente: int, limite: int, desplazamiento: int
) -> tuple[Paciente, int, list[Atencion]]:
    paciente = obtener_paciente(db, id_paciente)
    total = db.scalar(
        select(func.count()).select_from(Atencion).where(Atencion.id_paciente == id_paciente)
    )
    atenciones = db.scalars(
        _con_detalle(select(Atencion))
        .where(Atencion.id_paciente == id_paciente)
        .order_by(Atencion.creado_en.desc(), Atencion.id_atencion.desc())
        .limit(limite)
        .offset(desplazamiento)
    ).all()
    auditoria.registrar(
        db, actor, "pacientes", id_paciente, "SELECT", motivo="Consulta de la historia clínica"
    )
    return paciente, total or 0, list(atenciones)


def atenciones_de_paciente(db: Session, id_paciente: int) -> list[Atencion]:
    obtener_paciente(db, id_paciente)
    return list(
        db.scalars(
            select(Atencion)
            .where(Atencion.id_paciente == id_paciente)
            .order_by(Atencion.creado_en.desc(), Atencion.id_atencion.desc())
        )
    )


def obtener_atencion(db: Session, id_atencion: int) -> Atencion:
    atencion = db.scalar(_con_detalle(select(Atencion)).where(Atencion.id_atencion == id_atencion))
    if atencion is None:
        raise NoEncontrado(f"No existe la atención {id_atencion}")
    return atencion


def resumen_por_citas(db: Session, ids_cita: set[int]) -> dict[int, Atencion]:
    if not ids_cita:
        return {}
    atenciones = db.scalars(
        select(Atencion).options(selectinload(Atencion.triaje)).where(Atencion.id_cita.in_(ids_cita))
    )
    return {a.id_cita: a for a in atenciones}


def atenciones_en_curso(db: Session, id_medico: int) -> list[Atencion]:
    return list(
        db.scalars(
            select(Atencion)
            .options(selectinload(Atencion.triaje), selectinload(Atencion.paciente))
            .where(
                Atencion.id_medico == id_medico,
                Atencion.estado == "EN_CURSO",
                Atencion.anulado.is_(False),
                Atencion.tipo_atencion == "TOPICO_URGENCIA",
            )
            .order_by(Atencion.creado_en)
        )
    )


def alertas_triaje(triaje: Triaje) -> list[str]:
    alertas = []
    if triaje.presion_sistolica >= 140 or triaje.presion_diastolica >= 90:
        alertas.append(
            f"Presión arterial elevada ({triaje.presion_sistolica}/{triaje.presion_diastolica} mmHg)"
        )
    if triaje.temperatura >= 38.5:
        alertas.append(f"Fiebre ({triaje.temperatura:.1f} °C)")
    if triaje.saturacion_oxigeno is not None and triaje.saturacion_oxigeno < 92:
        alertas.append(f"Saturación baja ({triaje.saturacion_oxigeno} %)")
    return alertas


def imc(triaje: Triaje) -> float:
    return round(triaje.peso / (triaje.talla**2), 1)


def registrar_triaje(
    db: Session,
    actor,
    *,
    id_paciente: int,
    id_medico: int,
    id_cita: int | None,
    signos: dict,
) -> Atencion:
    """Crea la atención en curso (si aún no existe) y le asocia el triaje."""
    atencion = None
    if id_cita is not None:
        atencion = db.scalar(select(Atencion).where(Atencion.id_cita == id_cita))
        if atencion is not None and atencion.triaje is not None:
            raise Conflicto("El paciente ya tiene triaje registrado", id_atencion=atencion.id_atencion)
    if atencion is None:
        atencion = Atencion(
            id_paciente=id_paciente,
            id_medico=id_medico,
            id_cita=id_cita,
            tipo_atencion="CONSULTA_EXTERNA" if id_cita is not None else "TOPICO_URGENCIA",
            estado="EN_CURSO",
        )
        db.add(atencion)
        db.flush()
        auditoria.registrar(
            db,
            actor,
            "atenciones",
            atencion.id_atencion,
            "INSERT",
            despues={"tipo_atencion": atencion.tipo_atencion, "id_cita": id_cita, "estado": "EN_CURSO"},
        )
    triaje = Triaje(id_atencion=atencion.id_atencion, id_enfermera=actor.id_usuario, **signos)
    db.add(triaje)
    db.flush()
    db.refresh(atencion)
    auditoria.registrar(db, actor, "triajes", triaje.id_triaje, "INSERT", despues=signos)
    return atencion


def _validar_propietario(atencion: Atencion, id_medico: int) -> None:
    if atencion.id_medico != id_medico:
        raise Prohibido("La atención está asignada a otro médico")
    if atencion.anulado:
        raise Conflicto("La atención está anulada")


def iniciar_consulta(db: Session, actor, id_atencion: int, id_medico: int) -> Atencion:
    atencion = obtener_atencion(db, id_atencion)
    _validar_propietario(atencion, id_medico)
    if atencion.estado == "EN_CURSO" and atencion.inicio_consulta is None:
        atencion.inicio_consulta = tiempo.ahora()
        db.flush()
        auditoria.registrar(
            db,
            actor,
            "atenciones",
            atencion.id_atencion,
            "UPDATE",
            despues={"inicio_consulta": atencion.inicio_consulta},
        )
    return atencion


def coincidencias_alergia(alergias: str | None, medicamentos: list[str]) -> list[dict]:
    if not alergias:
        return []
    terminos = [t.strip() for t in re.split(r"[,;/\n]| y ", normalizar(alergias)) if len(t.strip()) >= 4]
    coincidencias = []
    for medicamento in medicamentos:
        nombre = normalizar(medicamento)
        palabras = set(nombre.split())
        for termino in terminos:
            directa = termino in nombre or any(
                p in palabras for p in termino.split() if len(p) >= 6 and p not in PALABRAS_GENERICAS
            )
            familia = any(
                clave in termino and any(farmaco in nombre for farmaco in farmacos)
                for clave, farmacos in FAMILIAS_ALERGIA.items()
            )
            if directa or familia:
                coincidencias.append({"medicamento": medicamento, "alergia": termino})
                break
    return coincidencias


def finalizar_atencion(db: Session, actor, id_atencion: int, id_medico: int, datos: dict) -> Atencion:
    atencion = obtener_atencion(db, id_atencion)
    _validar_propietario(atencion, id_medico)
    if atencion.estado != "EN_CURSO":
        raise Conflicto("La atención ya fue finalizada: los campos clínicos están bloqueados")

    codigos = [d["codigo_cie10"] for d in datos["diagnosticos"]]
    existentes = set(
        db.scalars(select(DiagnosticoCIE10.codigo).where(DiagnosticoCIE10.codigo.in_(codigos)))
    )
    faltantes = [c for c in codigos if c not in existentes]
    if faltantes:
        raise ReglaNegocio(
            f"Código CIE-10 no válido: {', '.join(faltantes)}. Seleccione un diagnóstico del catálogo oficial",
            campo="diagnosticos",
        )

    medicamentos = [p["medicamento"] for p in datos["prescripciones"]]
    coincidencias = coincidencias_alergia(atencion.paciente.alergias, medicamentos)
    if coincidencias and not datos.get("confirmar_alergias"):
        raise Conflicto(
            "Posible alergia: revise la receta antes de finalizar",
            coincidencias=coincidencias,
            alergias=atencion.paciente.alergias,
        )

    ahora = tiempo.ahora()
    atencion.motivo_consulta = datos["motivo_consulta"]
    atencion.anamnesis = datos.get("anamnesis")
    atencion.indicaciones = datos.get("indicaciones")
    atencion.inicio_consulta = atencion.inicio_consulta or ahora
    atencion.finalizada_en = ahora
    atencion.estado = "FINALIZADA"
    for diagnostico in datos["diagnosticos"]:
        db.add(AtencionDiagnostico(id_atencion=atencion.id_atencion, **diagnostico))
    for prescripcion in datos["prescripciones"]:
        db.add(Prescripcion(id_atencion=atencion.id_atencion, **prescripcion))
    db.flush()
    db.refresh(atencion)
    auditoria.registrar(
        db,
        actor,
        "atenciones",
        atencion.id_atencion,
        "UPDATE",
        antes={"estado": "EN_CURSO"},
        despues={
            "estado": "FINALIZADA",
            "diagnosticos": codigos,
            "prescripciones": len(medicamentos),
            "alergias_confirmadas": bool(coincidencias),
        },
    )
    return atencion


def anular_atencion(db: Session, actor, id_atencion: int, motivo: str) -> Atencion:
    atencion = obtener_atencion(db, id_atencion)
    if atencion.anulado:
        raise Conflicto("La atención ya está anulada")
    atencion.anulado = True
    atencion.motivo_anulacion = motivo
    atencion.anulado_por = actor.id_usuario
    atencion.anulado_en = tiempo.ahora()
    db.flush()
    auditoria.registrar(
        db,
        actor,
        "atenciones",
        atencion.id_atencion,
        "ANULAR",
        antes={"anulado": False},
        despues={"anulado": True},
        motivo=motivo,
    )
    return atencion


def buscar_cie10(db: Session, q: str | None, limite: int = 20) -> list[DiagnosticoCIE10]:
    catalogo = db.scalars(select(DiagnosticoCIE10).order_by(DiagnosticoCIE10.codigo)).all()
    texto = normalizar(q or "")
    if not texto:
        return list(catalogo[:limite])
    tokens = texto.split()
    por_codigo = [d for d in catalogo if normalizar(d.codigo).startswith(texto)]
    por_texto = [
        d
        for d in catalogo
        if d not in por_codigo and all(t in normalizar(f"{d.codigo} {d.descripcion}") for t in tokens)
    ]
    return (por_codigo + por_texto)[:limite]
