"""Datos ficticios para desarrollo, pruebas y demostración (ver database/02-datos-prueba.sql).

Ninguno de estos datos corresponde a personas reales. Además de los registros históricos
del script SQL, se genera una agenda alrededor de la fecha actual para que la
demostración siempre tenga pacientes citados, en espera y en triaje.

Uso: python -m app.seed --reiniciar   (borra y vuelve a crear las tablas del ORM)
"""

import argparse
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import tiempo
from app.modulos.agenda.models import Cita, Consultorio, Especialidad, Medico
from app.modulos.auditoria.models import BitacoraAuditoria
from app.modulos.convenios.models import Convenio, ServicioMedico, TarifarioServicio
from app.modulos.hce.cie10 import CATALOGO_CIE10
from app.modulos.hce.models import (
    Atencion,
    AtencionDiagnostico,
    DiagnosticoCIE10,
    Paciente,
    Prescripcion,
    Triaje,
)
from app.modulos.notificaciones.models import OutboxNotificacion
from app.modulos.seguridad.models import Rol, Usuario
from app.modulos.seguridad.service import hash_password

PASSWORD_DEMO = "Sira2026"

ROLES = (
    ("ADMISION", "Registro de pacientes y agenda de citas"),
    ("MEDICO", "Atención médica, diagnóstico, receta y órdenes de examen"),
    ("ENFERMERA", "Triaje y signos vitales"),
    ("LABORATORIO", "Procesamiento de órdenes y carga de resultados"),
    ("CAJA", "Liquidación, comprobantes y glosas"),
    ("GERENCIA", "Indicadores de gestión y anulaciones clínicas"),
    ("ADMINISTRADOR", "Gestión de usuarios y roles"),
)

CONVENIOS_FICTICIOS = (
    ("PARTICULAR", "Paciente particular", "PARTICULAR", None),
    ("EPS_RIMAC", "Rímac EPS", "EPS", "convenios@rimac-eps.test"),
    ("EPS_PACIFICO", "Pacífico EPS", "EPS", "convenios@pacifico-eps.test"),
    ("EPS_MAPFRE", "Mapfre Perú EPS", "EPS", "convenios@mapfre-eps.test"),
    ("EPS_SANITAS", "Sanitas Perú EPS", "EPS", "convenios@sanitas-eps.test"),
    ("EPS_POSITIVA", "La Positiva EPS", "EPS", "convenios@positiva-eps.test"),
    ("SOAT", "SOAT", "SOAT", "soat@aseguradora.test"),
)

ESPECIALIDADES = (
    "Medicina General",
    "Pediatría",
    "Cardiología",
    "Ginecología",
    "Traumatología",
    "Dermatología",
    "Gastroenterología",
    "Medicina Interna",
)

CONSULTORIOS = (
    ("C01", 1, "Medicina general"),
    ("C02", 1, "Pediatría"),
    ("C03", 1, "Pediatría"),
    ("C04", 1, "Medicina interna"),
    ("C05", 1, "Cardiología"),
    ("C06", 1, "Dermatología"),
    ("C07", 2, "Gastroenterología"),
    ("C08", 2, "Ginecología"),
    ("C09", 2, "Traumatología"),
    ("C10", 2, "Otorrinolaringología"),
    ("C11", 2, "Urología"),
    ("C12", 2, "Endocrinología"),
)

SERVICIOS = (
    ("CON-GEN-01", "Consulta externa de medicina general", "CONSULTA", 80.00),
    ("CON-ESP-01", "Consulta externa de especialidad", "CONSULTA", 140.00),
    ("LAB-HEM-01", "Hemograma completo", "LABORATORIO", 35.00),
    ("LAB-GLU-01", "Glucosa en ayunas", "LABORATORIO", 15.00),
    ("LAB-LIP-01", "Perfil lipídico", "LABORATORIO", 60.00),
    ("LAB-ORI-01", "Examen completo de orina", "LABORATORIO", 20.00),
    ("IMG-RXM-01", "Radiografía de muñeca (2 incidencias)", "IMAGENES", 90.00),
    ("IMG-ECO-01", "Ecografía pélvica", "IMAGENES", 120.00),
    ("PRO-TOP-01", "Atención en tópico de urgencias", "PROCEDIMIENTO", 100.00),
)

# (servicio, convenio, precio, % cobertura, copago fijo, vigente desde, vigente hasta)
TARIFARIOS = (
    ("CON-GEN-01", "PARTICULAR", 80.00, 0, 0, "2026-01-01", None),
    ("CON-ESP-01", "PARTICULAR", 140.00, 0, 0, "2026-01-01", None),
    ("LAB-HEM-01", "PARTICULAR", 35.00, 0, 0, "2026-01-01", None),
    ("CON-GEN-01", "EPS_PACIFICO", 75.00, 80, 20, "2025-01-01", "2026-01-01"),
    ("CON-GEN-01", "EPS_PACIFICO", 80.00, 80, 20, "2026-01-01", None),
    ("CON-ESP-01", "EPS_PACIFICO", 140.00, 85, 25, "2026-01-01", None),
    ("LAB-GLU-01", "EPS_PACIFICO", 15.00, 85, 0, "2026-01-01", None),
    ("LAB-LIP-01", "EPS_PACIFICO", 60.00, 85, 0, "2026-01-01", None),
    ("CON-ESP-01", "EPS_RIMAC", 140.00, 80, 20, "2026-01-01", None),
    ("IMG-ECO-01", "EPS_RIMAC", 120.00, 80, 0, "2026-01-01", None),
    ("CON-GEN-01", "EPS_MAPFRE", 80.00, 75, 15, "2026-01-01", None),
    ("LAB-HEM-01", "EPS_MAPFRE", 35.00, 75, 0, "2026-01-01", None),
    ("PRO-TOP-01", "SOAT", 100.00, 100, 0, "2026-01-01", None),
    ("IMG-RXM-01", "SOAT", 90.00, 100, 0, "2026-01-01", None),
    ("CON-GEN-01", "EPS_RIMAC", 80.00, 80, 20, "2026-01-01", None),
    ("CON-ESP-01", "EPS_MAPFRE", 140.00, 75, 20, "2026-01-01", None),
    ("CON-GEN-01", "EPS_SANITAS", 80.00, 70, 15, "2026-01-01", None),
    ("CON-ESP-01", "EPS_SANITAS", 140.00, 70, 25, "2026-01-01", None),
    ("CON-GEN-01", "EPS_POSITIVA", 80.00, 75, 15, "2026-01-01", None),
    ("CON-ESP-01", "EPS_POSITIVA", 140.00, 75, 20, "2026-01-01", None),
    ("CON-GEN-01", "SOAT", 80.00, 100, 0, "2026-01-01", None),
    ("CON-ESP-01", "SOAT", 140.00, 100, 0, "2026-01-01", None),
)

USUARIOS = (
    ("admision.rquispe", "rquispe@sanrafael.test", "ADMISION"),
    ("admision.lflores", "lflores@sanrafael.test", "ADMISION"),
    ("med.jvaldivia", "jvaldivia@sanrafael.test", "MEDICO"),
    ("med.cmendoza", "cmendoza@sanrafael.test", "MEDICO"),
    ("med.aramos", "aramos@sanrafael.test", "MEDICO"),
    ("med.psoto", "psoto@sanrafael.test", "MEDICO"),
    ("med.mmorales", "mmorales@sanrafael.test", "MEDICO"),
    ("med.ltorres", "ltorres@sanrafael.test", "MEDICO"),
    ("enf.rpaz", "rpaz@sanrafael.test", "ENFERMERA"),
    ("enf.mcastro", "mcastro@sanrafael.test", "ENFERMERA"),
    ("lab.jhuaman", "jhuaman@sanrafael.test", "LABORATORIO"),
    ("lab.dchavez", "dchavez@sanrafael.test", "LABORATORIO"),
    ("caja.evargas", "evargas@sanrafael.test", "CAJA"),
    ("caja.ksilva", "ksilva@sanrafael.test", "CAJA"),
    ("ger.rmedina", "rmedina@sanrafael.test", "GERENCIA"),
    ("admin.sira", "admin@sanrafael.test", "ADMINISTRADOR"),
    ("med.gnunez", "gnunez@sanrafael.test", "MEDICO"),
    ("med.vcardenas", "vcardenas@sanrafael.test", "MEDICO"),
    ("med.esalinas", "esalinas@sanrafael.test", "MEDICO"),
)

CUENTAS_DEMO = (
    ("admision.rquispe", "ADMISION", "Admisión: pacientes, agenda y citas"),
    ("enf.rpaz", "ENFERMERA", "Enfermería: triaje y tópico de urgencias"),
    ("med.aramos", "MEDICO", "Medicina General · Dr. Alberto Ramos"),
    ("med.jvaldivia", "MEDICO", "Pediatría · Dr. Jorge Valdivia"),
    ("med.cmendoza", "MEDICO", "Cardiología · Dr. Carlos Mendoza"),
    ("ger.rmedina", "GERENCIA", "Dirección médica: anulaciones y bitácora"),
    ("admin.sira", "ADMINISTRADOR", "Bitácora y notificaciones"),
    ("caja.evargas", "CAJA", "Caja (sin acceso a la HCE)"),
)

# (cmp, nombres, apellidos, especialidad, teléfono, correo, usuario, consultorio habitual)
MEDICOS = (
    ("39412", "Jorge", "Valdivia Ríos", "Pediatría", "987600001", "jvaldivia@sanrafael.test", "med.jvaldivia", "C02"),
    ("48921", "Carlos", "Mendoza Salas", "Cardiología", "987600002", "cmendoza@sanrafael.test", "med.cmendoza", "C05"),
    ("31877", "Alberto", "Ramos Peña", "Medicina General", "987600003", "aramos@sanrafael.test", "med.aramos", "C01"),
    ("52310", "Patricia", "Soto Lazo", "Dermatología", "987600004", "psoto@sanrafael.test", "med.psoto", "C06"),
    ("44108", "Mónica", "Morales Vidal", "Ginecología", "987600005", "mmorales@sanrafael.test", "med.mmorales", "C08"),
    ("50733", "Luis", "Torres Campos", "Traumatología", "987600006", "ltorres@sanrafael.test", "med.ltorres", "C09"),
    ("46215", "Gabriela", "Núñez Arce", "Medicina General", "987600007", "gnunez@sanrafael.test", "med.gnunez", "C03"),
    ("41987", "Víctor", "Cárdenas Ruiz", "Gastroenterología", "987600008", "vcardenas@sanrafael.test", "med.vcardenas", "C07"),
    ("47730", "Eduardo", "Salinas Prado", "Medicina Interna", "987600009", "esalinas@sanrafael.test", "med.esalinas", "C04"),
)

# (tipo, número, nombres, ap. paterno, ap. materno, nacimiento, sexo, teléfono, correo, dirección,
#  convenio, antecedentes, alergias)
PACIENTES = (
    ("DNI", "45892014", "María Elena", "Quispe", "Rojas", "1982-04-15", "F", "987650001", "maria.quispe@correo.test", "Av. San Luis 2150, San Borja", "EPS_PACIFICO", "Hipertensión arterial controlada", "Penicilina y sulfas"),
    ("DNI", "78945612", "Lucas", "Bustamante", "Vega", "2020-05-04", "M", "987650002", "elena.vega@correo.test", "Jr. Las Begonias 340, San Borja", "EPS_PACIFICO", None, None),
    ("DNI", "41258963", "José", "Herrera", "Díaz", "1972-03-12", "M", "987650003", "jose.herrera@correo.test", "Av. Aviación 3120, San Borja", "EPS_PACIFICO", "Dislipidemia", None),
    ("DNI", "77895214", "Ana", "López", "Vega", "2020-02-10", "F", "987650004", "maria.vega@correo.test", "Calle Los Geranios 115, Surquillo", "PARTICULAR", None, None),
    ("DNI", "10254879", "Raúl", "Castillo", "Medina", "1958-07-21", "M", "987650005", "raul.castillo@correo.test", "Av. Javier Prado Este 2480, San Borja", "EPS_RIMAC", "Diabetes mellitus tipo 2", "Ácido acetilsalicílico"),
    ("DNI", "08521496", "Carmen", "Sandoval", "Ruiz", "1988-09-03", "F", "987650006", "carmen.sandoval@correo.test", "Jr. Fray Angélico 560, San Borja", "EPS_RIMAC", None, None),
    ("DNI", "71452398", "Felipe", "Paredes", "Guzmán", "1984-01-30", "M", "987650007", None, "Av. Primavera 1780, Surco", "PARTICULAR", None, None),
    ("DNI", "72631548", "Rosa", "Huamán", "Díaz", "1995-11-08", "F", "987650008", "rosa.huaman@correo.test", "Calle Morelli 230, San Borja", "EPS_MAPFRE", "Gastritis crónica", None),
    ("DNI", "70819324", "Luis", "Mendoza", "Paredes", "1990-06-17", "M", "987650009", "luis.mendoza@correo.test", "Av. Canadá 1450, La Victoria", "SOAT", None, None),
    ("CE", "001234567", "Valentina", "Rossi", "Bianchi", "1979-12-02", "F", "987650010", "valentina.rossi@correo.test", "Av. Del Parque Norte 480, San Isidro", "EPS_SANITAS", None, "Látex"),
    ("DNI", "46281937", "Jorge Luis", "Ccori", "Mamani", "1987-05-11", "M", "987650011", "jorge.ccori@correo.test", "Jr. Tasso 410, San Borja", "EPS_RIMAC", None, None),
    ("DNI", "40517823", "Elena Patricia", "Campos", "Ruiz", "1959-02-23", "F", "987650012", "elena.campos@correo.test", "Av. Las Artes Norte 920, San Borja", "EPS_PACIFICO", "Diabetes mellitus tipo 2 desde 2015", "Sulfas"),
    ("DNI", "73019458", "Diego Alonso", "Ramírez", "Soto", "2001-09-14", "M", "987650013", "diego.ramirez@correo.test", "Calle Rousseau 155, San Borja", "PARTICULAR", None, None),
    ("DNI", "09765432", "Teresa", "Gamarra", "Lazo", "1949-06-30", "F", "987650014", None, "Av. Boulevard 1020, Surco", "EPS_MAPFRE", "Hipertensión arterial; artrosis de rodilla", "Ibuprofeno"),
    ("DNI", "75391846", "Sofía Valeria", "Torres", "Quispe", "2016-03-08", "F", "987650015", "familia.torres@correo.test", "Jr. Mariano Odicio 230, Surquillo", "EPS_POSITIVA", None, "Amoxicilina"),
    ("DNI", "44826193", "Miguel Ángel", "Chávez", "Ríos", "1979-12-19", "M", "987650016", "miguel.chavez@correo.test", "Av. Angamos Este 2310, Surquillo", "EPS_SANITAS", "Asma bronquial", None),
    ("DNI", "70264519", "Lucía Fernanda", "Salazar", "Núñez", "1998-07-02", "F", "987650017", "lucia.salazar@correo.test", "Calle Bach 340, San Borja", "EPS_RIMAC", None, None),
    ("DNI", "42197536", "Pedro Pablo", "Huerta", "Vargas", "1968-10-27", "M", "987650018", "pedro.huerta@correo.test", "Av. Canadá 3150, San Borja", "SOAT", "Contusión lumbar por accidente de tránsito (SOAT)", None),
)


def _ts(texto: str) -> datetime:
    return datetime.fromisoformat(texto)


def sembrar_convenios(db: Session) -> None:
    if db.scalars(select(Convenio)).first() is not None:
        return
    for codigo, nombre, tipo, contacto in CONVENIOS_FICTICIOS:
        db.add(
            Convenio(
                codigo_convenio=codigo,
                nombre_institucion=nombre,
                tipo_convenio=tipo,
                contacto_operativo=contacto,
            )
        )
    db.commit()


def sembrar_catalogos(db: Session) -> None:
    sembrar_convenios(db)
    if db.scalars(select(Rol)).first() is None:
        db.add_all(Rol(nombre=n, descripcion=d) for n, d in ROLES)
    if db.scalars(select(Especialidad)).first() is None:
        db.add_all(Especialidad(nombre=n) for n in ESPECIALIDADES)
    if db.scalars(select(Consultorio)).first() is None:
        db.add_all(Consultorio(numero=n, piso=p, descripcion=d) for n, p, d in CONSULTORIOS)
    # Si la base viene de database/02-datos-prueba.sql, solo se completa lo que falta.
    codigos = set(db.scalars(select(DiagnosticoCIE10.codigo)))
    db.add_all(DiagnosticoCIE10(codigo=c, descripcion=d) for c, d in CATALOGO_CIE10 if c not in codigos)
    servicios = {s.codigo_servicio: s for s in db.scalars(select(ServicioMedico))}
    for codigo, nombre, tipo, precio in SERVICIOS:
        if codigo not in servicios:
            servicios[codigo] = ServicioMedico(
                codigo_servicio=codigo, nombre_servicio=nombre, tipo_servicio=tipo, precio_base_particular=precio
            )
            db.add(servicios[codigo])
    db.flush()
    convenios = {c.codigo_convenio: c for c in db.scalars(select(Convenio))}
    con_tarifa = {
        (servicio, convenio)
        for servicio, convenio in db.execute(select(TarifarioServicio.id_servicio, TarifarioServicio.id_convenio))
    }
    for servicio, convenio, precio, cobertura, fijo, desde, hasta in TARIFARIOS:
        if (servicios[servicio].id_servicio, convenios[convenio].id_convenio) in con_tarifa:
            continue
        db.add(
            TarifarioServicio(
                id_servicio=servicios[servicio].id_servicio,
                id_convenio=convenios[convenio].id_convenio,
                precio_convenido=precio,
                porcentaje_cobertura=cobertura,
                copago_fijo=fijo,
                vigente_desde=date.fromisoformat(desde),
                vigente_hasta=date.fromisoformat(hasta) if hasta else None,
            )
        )
    db.commit()


class _Demo:
    """Arma la demostración guardando referencias por clave (no por id fijo)."""

    def __init__(self, db: Session):
        self.db = db
        self.ahora = tiempo.ahora()
        self.hoy = self.ahora.date()
        roles = {r.nombre: r for r in db.scalars(select(Rol))}
        clave = hash_password(PASSWORD_DEMO)
        self.usuarios = {}
        for username, email, rol in USUARIOS:
            usuario = Usuario(username=username, email=email, password_hash=clave, id_rol=roles[rol].id_rol)
            db.add(usuario)
            self.usuarios[username] = usuario
        db.flush()
        especialidades = {e.nombre: e for e in db.scalars(select(Especialidad))}
        self.consultorios = {c.numero: c for c in db.scalars(select(Consultorio))}
        self.medicos = {}
        self.habitual = {}
        for cmp, nombres, apellidos, esp, telefono, email, username, consultorio in MEDICOS:
            medico = Medico(
                cmp=cmp,
                nombres=nombres,
                apellidos=apellidos,
                id_especialidad=especialidades[esp].id_especialidad,
                telefono=telefono,
                email=email,
                id_usuario=self.usuarios[username].id_usuario,
            )
            db.add(medico)
            self.medicos[username] = medico
            self.habitual[username] = consultorio
        convenios = {c.codigo_convenio: c for c in db.scalars(select(Convenio))}
        self.pacientes = []
        for tipo, numero, nom, pat, mat, nac, sexo, tel, email, dire, conv, ant, ale in PACIENTES:
            paciente = Paciente(
                tipo_documento=tipo,
                numero_documento=numero,
                nombres=nom,
                apellido_paterno=pat,
                apellido_materno=mat,
                fecha_nacimiento=date.fromisoformat(nac),
                sexo=sexo,
                telefono=tel,
                email=email,
                direccion=dire,
                id_convenio=convenios[conv].id_convenio,
                antecedentes_medicos=ant,
                alergias=ale,
            )
            db.add(paciente)
            self.pacientes.append(paciente)
        db.flush()

    def p(self, numero: int) -> Paciente:
        return self.pacientes[numero - 1]

    def u(self, username: str) -> int:
        return self.usuarios[username].id_usuario

    def cita(
        self,
        paciente: int,
        medico: str,
        inicio: datetime,
        estado: str,
        *,
        consultorio: str | None = None,
        llegada: datetime | None = None,
        motivo: str | None = None,
        origen: Cita | None = None,
        canal: str = "ADMISION",
        creado_por: str = "admision.rquispe",
    ) -> Cita:
        if estado in ("EN_ESPERA", "ATENDIDA") and llegada is None:
            llegada = min(inicio - timedelta(minutes=10), self.ahora)
        cita = Cita(
            id_paciente=self.p(paciente).id_paciente,
            id_medico=self.medicos[medico].id_medico,
            id_consultorio=self.consultorios[consultorio or self.habitual[medico]].id_consultorio,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=inicio + timedelta(minutes=30),
            estado=estado,
            motivo_cancelacion=motivo,
            hora_llegada=llegada,
            id_cita_origen=origen.id_cita if origen else None,
            canal_agendamiento=canal,
            creado_por=self.u(creado_por),
            creado_en=min(inicio - timedelta(days=2), self.ahora),
        )
        self.db.add(cita)
        self.db.flush()
        return cita

    def atencion(
        self,
        paciente: int,
        medico: str,
        cita: Cita | None,
        creado_en: datetime,
        *,
        estado: str = "FINALIZADA",
        motivo: str | None = None,
        anamnesis: str | None = None,
        indicaciones: str | None = None,
        inicio: datetime | None = None,
        fin: datetime | None = None,
        triaje: tuple | None = None,
        enfermera: str = "enf.rpaz",
        diagnosticos: tuple = (),
        recetas: tuple = (),
        anulacion: tuple | None = None,
    ) -> Atencion:
        atencion = Atencion(
            id_paciente=self.p(paciente).id_paciente,
            id_medico=self.medicos[medico].id_medico,
            id_cita=cita.id_cita if cita else None,
            tipo_atencion="CONSULTA_EXTERNA" if cita else "TOPICO_URGENCIA",
            estado=estado,
            motivo_consulta=motivo,
            anamnesis=anamnesis,
            indicaciones=indicaciones,
            inicio_consulta=inicio,
            finalizada_en=fin,
            creado_en=creado_en,
        )
        if anulacion:
            atencion.anulado = True
            atencion.motivo_anulacion, usuario, atencion.anulado_en = anulacion
            atencion.anulado_por = self.u(usuario)
        self.db.add(atencion)
        self.db.flush()
        if triaje:
            sis, dia, temp, fc, fr, sat, peso, talla, obs = triaje[:9]
            registrado = triaje[9] if len(triaje) > 9 else creado_en + timedelta(minutes=3)
            self.db.add(
                Triaje(
                    id_atencion=atencion.id_atencion,
                    presion_sistolica=sis,
                    presion_diastolica=dia,
                    temperatura=temp,
                    frecuencia_cardiaca=fc,
                    frecuencia_respiratoria=fr,
                    saturacion_oxigeno=sat,
                    peso=peso,
                    talla=talla,
                    observaciones=obs,
                    id_enfermera=self.u(enfermera),
                    registrado_en=registrado,
                )
            )
        for codigo, tipo in diagnosticos:
            self.db.add(AtencionDiagnostico(id_atencion=atencion.id_atencion, codigo_cie10=codigo, tipo=tipo))
        for medicamento, presentacion, frecuencia, duracion in recetas:
            self.db.add(
                Prescripcion(
                    id_atencion=atencion.id_atencion,
                    medicamento=medicamento,
                    presentacion=presentacion,
                    frecuencia=frecuencia,
                    duracion=duracion,
                )
            )
        return atencion

    def outbox(self, cita: Cita | None, tipo: str, canal: str, destino: str, mensaje: str, programado: datetime,
               estado: str = "PENDIENTE", intentos: int = 0, error: str | None = None,
               procesado: datetime | None = None) -> None:
        self.db.add(
            OutboxNotificacion(
                id_cita=cita.id_cita if cita else None,
                tipo_evento=tipo,
                canal=canal,
                destinatario=destino,
                mensaje=mensaje,
                programado_para=programado,
                estado=estado,
                intentos=intentos,
                error_detalle=error,
                procesado_en=procesado,
                creado_en=min(programado, self.ahora),
            )
        )


def _historico_script(d: _Demo) -> dict[int, Cita]:
    """Registros históricos idénticos a database/02-datos-prueba.sql."""
    c = {}
    c[1] = d.cita(1, "med.aramos", _ts("2026-10-12 09:00"), "ATENDIDA", llegada=_ts("2026-10-12 08:50"))
    c[2] = d.cita(3, "med.cmendoza", _ts("2026-10-14 09:00"), "ATENDIDA", llegada=_ts("2026-10-14 08:45"))
    c[3] = d.cita(2, "med.jvaldivia", _ts("2026-10-14 09:00"), "EN_ESPERA", llegada=_ts("2026-10-14 08:40"),
                  canal="TELEFONICO", creado_por="admision.lflores")
    c[4] = d.cita(6, "med.mmorales", _ts("2026-10-13 10:00"), "ATENDIDA", llegada=_ts("2026-10-13 09:52"))
    c[5] = d.cita(7, "med.aramos", _ts("2026-10-13 11:00"), "NO_ASISTIO", canal="TELEFONICO",
                  creado_por="admision.lflores")
    c[6] = d.cita(8, "med.psoto", _ts("2026-10-15 15:00"), "CANCELADA",
                  motivo="Solicitud de la paciente por viaje", creado_por="admision.lflores")
    c[7] = d.cita(10, "med.cmendoza", _ts("2026-10-15 10:00"), "REPROGRAMADA",
                  motivo="La paciente solicitó cambio de horario")
    c[8] = d.cita(10, "med.cmendoza", _ts("2026-10-16 10:00"), "CONFIRMADA", origen=c[7])
    c[9] = d.cita(4, "med.jvaldivia", _ts("2026-10-15 08:00"), "CONFIRMADA", canal="TELEFONICO",
                  creado_por="admision.lflores")
    c[10] = d.cita(5, "med.cmendoza", _ts("2026-10-16 11:00"), "CONFIRMADA")
    c[11] = d.cita(8, "med.aramos", _ts("2026-10-12 10:00"), "ATENDIDA", llegada=_ts("2026-10-12 09:50"),
                   creado_por="admision.lflores")

    d.atencion(1, "med.aramos", c[1], _ts("2026-10-12 08:55"),
               motivo="Dolor de garganta y congestión nasal desde hace tres días",
               anamnesis="Afebril. Faringe congestiva sin exudado. Murmullo vesicular conservado.",
               indicaciones="Reposo relativo por 48 horas e hidratación abundante",
               inicio=_ts("2026-10-12 09:05"), fin=_ts("2026-10-12 09:25"),
               triaje=(118, 76, 36.9, 82, 16, 98, 62.00, 1.58, "Odinofagia leve", _ts("2026-10-12 08:58")),
               diagnosticos=(("J00", "PRINCIPAL"),),
               recetas=(("Paracetamol", "500 mg tableta", "Cada 8 horas", "3 días"),
                        ("Clorfenamina", "4 mg tableta", "Cada 12 horas", "5 días")))
    d.atencion(3, "med.cmendoza", c[2], _ts("2026-10-14 08:50"),
               motivo="Cefalea matutina y mareos leves desde hace tres días",
               anamnesis="Niega dolor torácico. Ruidos cardiacos rítmicos, sin soplos.",
               indicaciones="Dieta hiposódica, control de presión arterial en casa y control en 30 días",
               inicio=_ts("2026-10-14 09:10"), fin=_ts("2026-10-14 09:35"),
               triaje=(120, 80, 36.8, 74, 18, 98, 75.00, 1.70, "Refiere cefalea de intensidad moderada",
                       _ts("2026-10-14 09:00")),
               diagnosticos=(("I10", "PRINCIPAL"), ("R51", "SECUNDARIO")),
               recetas=(("Losartán potásico", "50 mg tableta", "Cada 24 horas, con el desayuno", "30 días"),
                        ("Paracetamol", "500 mg tableta", "Cada 8 horas si hay dolor de cabeza", "3 días")))
    d.atencion(2, "med.jvaldivia", c[3], _ts("2026-10-14 08:45"), estado="EN_CURSO", enfermera="enf.mcastro",
               triaje=(100, 65, 37.2, 96, 22, 99, 21.50, 1.15, "Acompañado por su madre", _ts("2026-10-14 08:50")),
               diagnosticos=(("J06.9", "PRESUNTIVO"),))
    d.atencion(6, "med.mmorales", c[4], _ts("2026-10-13 09:55"), enfermera="enf.mcastro",
               motivo="Control ginecológico anual",
               anamnesis="Asintomática. Examen ginecológico sin hallazgos patológicos.",
               indicaciones="Control anual y ecografía pélvica de rutina",
               inicio=_ts("2026-10-13 10:05"), fin=_ts("2026-10-13 10:30"),
               triaje=(112, 72, 36.5, 70, 16, 99, 58.30, 1.62, None, _ts("2026-10-13 09:58")),
               diagnosticos=(("Z01.4", "PRINCIPAL"),))
    d.atencion(9, "med.ltorres", None, _ts("2026-10-13 18:05"),
               motivo="Dolor en muñeca derecha tras accidente de tránsito",
               anamnesis="Dolor a la movilización de la muñeca derecha, sin deformidad visible.",
               indicaciones="Inmovilización con férula, frío local y control en 7 días",
               inicio=_ts("2026-10-13 18:20"), fin=_ts("2026-10-13 18:50"),
               triaje=(145, 92, 36.7, 98, 20, 97, 80.20, 1.75, "Presión elevada; dolor intenso en muñeca",
                       _ts("2026-10-13 18:10")),
               diagnosticos=(("S63.5", "PRINCIPAL"),),
               recetas=(("Ibuprofeno", "400 mg tableta", "Cada 8 horas, después de comer", "5 días"),
                        ("Diclofenaco", "Gel al 1 %", "Cada 12 horas sobre la zona afectada", "7 días")))
    d.atencion(1, "med.aramos", None, _ts("2026-10-12 10:00"), motivo="Dolor de garganta y congestión nasal",
               inicio=_ts("2026-10-12 10:00"), fin=_ts("2026-10-12 10:10"),
               diagnosticos=(("J00", "PRINCIPAL"),),
               anulacion=("Registro duplicado por error de digitación; la atención válida es la del "
                          "12/10/2026 a las 09:00", "ger.rmedina", _ts("2026-10-12 12:00")))
    d.atencion(8, "med.aramos", c[11], _ts("2026-10-12 09:55"), enfermera="enf.mcastro",
               motivo="Dolor epigástrico después de las comidas desde hace una semana",
               anamnesis="Abdomen blando, depresible, doloroso a la palpación en epigastrio.",
               indicaciones="Dieta blanda fraccionada, evitar irritantes y control en 15 días",
               inicio=_ts("2026-10-12 10:05"), fin=_ts("2026-10-12 10:25"),
               triaje=(110, 70, 36.6, 76, 16, 98, 55.00, 1.60, None, _ts("2026-10-12 09:58")),
               diagnosticos=(("K29.7", "PRINCIPAL"),),
               recetas=(("Omeprazol", "20 mg cápsula", "Cada 24 horas, antes del desayuno", "14 días"),))

    d.outbox(c[8], "RECORDATORIO_24H", "SMS", "987650010",
             "Clínica San Rafael: recuerde su cita de Cardiología el 16/10/2026 a las 10:00 en el consultorio C05.",
             _ts("2026-10-15 10:00"))
    d.outbox(c[10], "RECORDATORIO_24H", "EMAIL", "raul.castillo@correo.test",
             "Clínica San Rafael: recuerde su cita de Cardiología el 16/10/2026 a las 11:00 en el consultorio C05.",
             _ts("2026-10-15 11:00"))
    d.outbox(c[9], "RECORDATORIO_24H", "SMS", "987650004",
             "Clínica San Rafael: recuerde la cita de Pediatría el 15/10/2026 a las 08:00 en el consultorio C02.",
             _ts("2026-10-14 08:00"), "ENVIADO", 1, procesado=_ts("2026-10-14 08:00:05"))
    d.outbox(c[2], "RECORDATORIO_24H", "WHATSAPP", "987650003",
             "Clínica San Rafael: recuerde su cita de Cardiología el 14/10/2026 a las 09:00 en el consultorio C05.",
             _ts("2026-10-13 09:00"), "ENVIADO", 1, procesado=_ts("2026-10-13 09:00:04"))
    d.outbox(c[5], "RECORDATORIO_24H", "SMS", "987650007",
             "Clínica San Rafael: recuerde su cita de Medicina General el 13/10/2026 a las 11:00 en el consultorio C01.",
             _ts("2026-10-12 11:00"), "FALLIDO", 3, "Tiempo de espera agotado con el proveedor de SMS")
    d.outbox(None, "AVISO_RESULTADO", "EMAIL", "jose.herrera@correo.test",
             "Clínica San Rafael: sus resultados de laboratorio ya están disponibles. Consúltelos con su médico tratante.",
             _ts("2026-10-14 12:45"), "ENVIADO", 1, procesado=_ts("2026-10-14 12:45:03"))
    d.outbox(c[8], "CONFIRMACION_CITA", "SMS", "987650010",
             "Clínica San Rafael: su cita de Cardiología fue reprogramada para el 16/10/2026 a las 10:00.",
             _ts("2026-10-14 08:30"), "ENVIADO", 1, procesado=_ts("2026-10-14 08:30:02"))
    return c


def _dia_habil(fecha: date, paso: int) -> date:
    while fecha.weekday() == 6:
        fecha += timedelta(days=paso)
    return fecha


def _agenda_actual(d: _Demo) -> None:
    """Agenda alrededor de hoy: historia reciente, el día en curso y los próximos días."""
    hoy = d.hoy

    def h(dia: date, hora: str) -> datetime:
        return datetime.combine(dia, time.fromisoformat(hora))

    hace35 = _dia_habil(hoy - timedelta(days=35), -1)
    cita = d.cita(1, "med.cmendoza", h(hace35, "10:00"), "ATENDIDA")
    d.atencion(1, "med.cmendoza", cita, h(hace35, "09:55"),
               motivo="Control de hipertensión arterial",
               anamnesis="Refiere buena adherencia al tratamiento. Niega cefalea y dolor torácico.",
               indicaciones="Continuar tratamiento, dieta hiposódica y control en tres meses",
               inicio=h(hace35, "10:05"), fin=h(hace35, "10:25"),
               triaje=(132, 84, 36.6, 76, 16, 98, 64.00, 1.58, None),
               diagnosticos=(("I10", "PRINCIPAL"),),
               recetas=(("Losartán potásico", "50 mg tableta", "Cada 24 horas, con el desayuno", "90 días"),))
    hace90 = _dia_habil(hoy - timedelta(days=90), -1)
    cita = d.cita(1, "med.psoto", h(hace90, "16:00"), "ATENDIDA")
    d.atencion(1, "med.psoto", cita, h(hace90, "15:55"),
               motivo="Lesiones rojizas y descamativas en mejillas desde hace dos semanas",
               anamnesis="Placas eritematosas con descamación fina en ambas mejillas. Sin signos de infección.",
               indicaciones="Hidratación de la piel, evitar jabones perfumados y control en un mes",
               inicio=h(hace90, "16:05"), fin=h(hace90, "16:20"),
               triaje=(124, 80, 36.4, 72, 16, 99, 63.00, 1.58, None),
               diagnosticos=(("L20.9", "PRINCIPAL"),),
               recetas=(("Hidrocortisona", "Crema al 1 %", "Cada 12 horas sobre las lesiones", "7 días"),))
    hace14 = _dia_habil(hoy - timedelta(days=14), -1)
    cita = d.cita(12, "med.aramos", h(hace14, "09:00"), "ATENDIDA")
    d.atencion(12, "med.aramos", cita, h(hace14, "08:55"),
               motivo="Control de diabetes mellitus tipo 2",
               anamnesis="Glucosa capilar en ayunas de 148 mg/dL. Refiere poliuria leve.",
               indicaciones="Dieta para diabético, caminatas de 30 minutos y control con hemoglobina glicosilada",
               inicio=h(hace14, "09:05"), fin=h(hace14, "09:25"),
               triaje=(130, 82, 36.5, 78, 16, 98, 69.00, 1.55, None),
               diagnosticos=(("E11.9", "PRINCIPAL"),),
               recetas=(("Metformina", "850 mg tableta", "Cada 12 horas, con los alimentos", "30 días"),))

    cita = d.cita(13, "med.aramos", h(hoy, "08:00"), "ATENDIDA")
    d.atencion(13, "med.aramos", cita, h(hoy, "07:55"),
               motivo="Dolor de garganta y fiebre desde ayer",
               anamnesis="Faringe eritematosa con placas blanquecinas. Adenopatías cervicales dolorosas.",
               indicaciones="Abundantes líquidos, reposo y control si la fiebre persiste más de 48 horas",
               inicio=h(hoy, "08:05"), fin=h(hoy, "08:25"),
               triaje=(118, 74, 38.2, 92, 18, 98, 70.00, 1.74, "Fiebre desde ayer"),
               diagnosticos=(("J03.9", "PRINCIPAL"),),
               recetas=(("Amoxicilina", "500 mg cápsula", "Cada 8 horas", "10 días"),
                        ("Paracetamol", "500 mg tableta", "Cada 8 horas si hay fiebre", "3 días")))
    d.cita(11, "med.aramos", h(hoy, "08:30"), "NO_ASISTIO")
    cita = d.cita(1, "med.aramos", h(hoy, "09:00"), "EN_ESPERA")
    d.atencion(1, "med.aramos", cita, min(h(hoy, "08:52"), d.ahora), estado="EN_CURSO",
               triaje=(152, 96, 36.7, 84, 17, 97, 64.50, 1.58, "Refiere cefalea occipital desde la mañana"))
    cita = d.cita(12, "med.aramos", h(hoy, "09:30"), "EN_ESPERA", creado_por="admision.lflores")
    d.atencion(12, "med.aramos", cita, min(h(hoy, "09:22"), d.ahora), estado="EN_CURSO", enfermera="enf.mcastro",
               triaje=(126, 78, 36.5, 74, 16, 98, 68.20, 1.55, "Trae resultados de glucosa en ayunas"))
    d.cita(7, "med.aramos", h(hoy, "10:00"), "EN_ESPERA", canal="TELEFONICO")
    d.cita(14, "med.aramos", h(hoy, "10:30"), "CONFIRMADA")
    d.cita(17, "med.aramos", h(hoy, "11:00"), "CONFIRMADA", canal="TELEFONICO")
    d.cita(8, "med.aramos", h(hoy, "12:00"), "CANCELADA", motivo="Solicitud de la paciente por motivos laborales")
    cita = d.cita(15, "med.jvaldivia", h(hoy, "09:00"), "EN_ESPERA")
    d.atencion(15, "med.jvaldivia", cita, min(h(hoy, "08:50"), d.ahora), estado="EN_CURSO",
               triaje=(100, 62, 38.7, 118, 24, 97, 31.40, 1.36, "Fiebre de dos días y tos; acompañada por su madre"))
    d.cita(4, "med.jvaldivia", h(hoy, "10:00"), "CONFIRMADA")
    d.cita(2, "med.jvaldivia", h(hoy, "11:00"), "EN_ESPERA", creado_por="admision.lflores")
    cita = d.cita(3, "med.cmendoza", h(hoy, "09:30"), "EN_ESPERA")
    d.atencion(3, "med.cmendoza", cita, min(h(hoy, "09:20"), d.ahora), estado="EN_CURSO",
               triaje=(138, 88, 36.6, 78, 16, 98, 76.00, 1.70, "Control de dislipidemia"))
    d.cita(5, "med.cmendoza", h(hoy, "10:30"), "CONFIRMADA")
    d.cita(18, "med.gnunez", h(hoy, "14:00"), "CONFIRMADA")
    d.cita(6, "med.gnunez", h(hoy, "15:00"), "CONFIRMADA", canal="TELEFONICO")
    d.cita(10, "med.psoto", h(hoy, "16:00"), "CONFIRMADA")
    d.atencion(16, "med.aramos", None, min(h(hoy, "10:40"), d.ahora), estado="EN_CURSO",
               triaje=(134, 82, 36.9, 104, 26, 91, 82.00, 1.72, "Sibilancias y dificultad para respirar"))

    manana = _dia_habil(hoy + timedelta(days=1), 1)
    pasado = _dia_habil(manana + timedelta(days=1), 1)
    proximas = (
        (16, "med.aramos", h(manana, "09:00")),
        (9, "med.aramos", h(manana, "10:00")),
        (14, "med.cmendoza", h(manana, "11:00")),
        (2, "med.jvaldivia", h(manana, "08:30")),
        (17, "med.mmorales", h(manana, "15:00")),
        (18, "med.ltorres", h(manana, "16:00")),
        (8, "med.vcardenas", h(pasado, "09:30")),
        (12, "med.esalinas", h(pasado, "10:00")),
        (6, "med.psoto", h(pasado, "11:30")),
        (11, "med.gnunez", h(pasado, "17:00")),
    )
    for paciente, medico, inicio in proximas:
        cita = d.cita(paciente, medico, inicio, "CONFIRMADA")
        datos = {
            "especialidad": d.medicos[medico].especialidad.nombre if d.medicos[medico].especialidad else "",
            "fecha": tiempo.formato_fecha(inicio),
            "hora": tiempo.formato_hora(inicio),
            "consultorio": d.habitual[medico],
        }
        telefono = d.p(paciente).telefono
        d.outbox(cita, "CONFIRMACION_CITA", "SMS", telefono,
                 "Clínica San Rafael: su cita de {especialidad} quedó confirmada para el {fecha} a las {hora} "
                 "en el consultorio {consultorio}.".format(**datos),
                 cita.creado_en, "ENVIADO", 1, procesado=cita.creado_en)
        d.outbox(cita, "RECORDATORIO_24H", "SMS", telefono,
                 "Clínica San Rafael: recuerde su cita de {especialidad} el {fecha} a las {hora} "
                 "en el consultorio {consultorio}.".format(**datos),
                 inicio - timedelta(hours=24))


def _bitacora_script(d: _Demo) -> None:
    filas = (
        ("med.cmendoza", "atenciones", 2, "SELECT", "10.20.1.15", None, None, None, "2026-10-14 09:10"),
        ("med.cmendoza", "atenciones", 2, "UPDATE", "10.20.1.15", {"estado": "EN_CURSO"},
         {"estado": "FINALIZADA"}, None, "2026-10-14 09:35"),
        ("caja.evargas", "pacientes", 3, "ACCESO_DENEGADO", "10.20.3.21", None, None,
         "Rol CAJA sin permiso para consultar la HCE", "2026-10-14 09:40"),
        ("ger.rmedina", "atenciones", 6, "ANULAR", "10.20.5.10", {"anulado": False}, {"anulado": True},
         "Registro duplicado por error de digitación", "2026-10-12 12:00"),
        ("enf.rpaz", "triajes", 2, "INSERT", "10.20.2.11", None, None, None, "2026-10-14 09:00"),
        ("lab.jhuaman", "resultados", 1, "INSERT", "10.20.4.30", None, None, None, "2026-10-14 12:40"),
    )
    for usuario, tabla, registro, accion, ip, antes, despues, motivo, fecha in filas:
        d.db.add(
            BitacoraAuditoria(
                id_usuario=d.u(usuario),
                nombre_tabla=tabla,
                id_registro_afectado=registro,
                accion=accion,
                direccion_ip=ip,
                datos_anteriores=antes,
                datos_nuevos=despues,
                motivo=motivo,
                fecha_hora=_ts(fecha),
            )
        )


def sembrar_demo(db: Session) -> None:
    if db.scalars(select(Usuario)).first() is not None:
        return
    demo = _Demo(db)
    _historico_script(demo)
    _agenda_actual(demo)
    _bitacora_script(demo)
    db.commit()


def sembrar(db: Session, demo: bool = True) -> None:
    sembrar_catalogos(db)
    if demo:
        sembrar_demo(db)


def _main() -> None:
    from app.database import Base, SessionLocal, engine
    import app.modulos  # noqa: F401

    parser = argparse.ArgumentParser(description="Carga los datos ficticios de SIRA")
    parser.add_argument("--reiniciar", action="store_true", help="Borra y vuelve a crear las tablas del ORM")
    args = parser.parse_args()
    if args.reiniciar:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        sembrar(db)
    print("Datos de demostración cargados.")


if __name__ == "__main__":
    _main()
