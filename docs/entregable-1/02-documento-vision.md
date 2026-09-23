# 👁️ Documento de Visión — Sistema SIRA

---

## 2.1. Declaración de Visión

> **Para** el personal clínico y administrativo de la Clínica San Rafael S.A.C.
> **Que** necesita una vista única, oportuna y segura de la información del paciente y de la operación diaria,
> **El** **Sistema de Información Clínico-Administrativo (SIRA)**
> **Es una** plataforma web integrada
> **Que** consolida la historia clínica electrónica, la agenda multiespecialidad, el circuito de laboratorio e imágenes, la facturación por convenios y los reportes gerenciales, con acceso restringido por rol y trazabilidad completa;
> **A diferencia de** las historias clínicas en papel y Excel, la agenda telefónica y la conciliación manual con aseguradoras, que fragmentan el expediente del paciente, saturan la atención telefónica, demoran los resultados hasta 48 horas y dejan a la dirección sin indicadores.

---

## 2.2. Perfiles de Usuario (Stakeholders)

| Perfil                            | Necesidad Principal                                                                                                                                                                                 | Módulo Relacionado                                                                |
| :-------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| **Admisión / Recepción**  | Registrar y localizar al paciente sin duplicar expedientes, verificar su convenio vigente y programar, reprogramar o cancelar citas sobre la disponibilidad consolidada de médicos y consultorios. | **M2** (principal), **M1**                                             |
| **Médico tratante**        | Abrir el expediente completo del paciente antes de la consulta, registrar la atención con diagnóstico CIE-10, indicaciones y receta, y generar órdenes de laboratorio o imágenes.               | **M1** (principal), **M3**, **M2**                               |
| **Enfermera**               | Registrar el triaje y los signos vitales al inicio de la atención y consultar alergias, medicación vigente e indicaciones, sin acceso al expediente clínico completo.                            | **M1** (acceso restringido por rol)                                          |
| **Personal de laboratorio** | Recibir la orden médica digital, registrar su ejecución, cargar el resultado y que el sistema notifique automáticamente al médico tratante y al paciente.                                       | **M3** (principal)                                                           |
| **Cajero / Facturación**   | Emitir el comprobante aplicando el tarifario del convenio correspondiente, calcular el copago del paciente y registrar y dar seguimiento a las glosas de las EPS.                                   | **M4** (principal)                                                           |
| **Gerencia médica**        | Disponer de indicadores de ocupación de consultorios, tiempos de espera, ingresos por especialidad y convenio, e inasistencia, para decidir sobre horarios, personal y convenios.                  | **M5** (principal)                                                           |
| **Paciente**                | Agendar sin esperar en la línea telefónica, recibir confirmación y recordatorio de su cita y consultar sus resultados sin acudir presencialmente.                                                | **M6** (deseable); receptor de notificaciones de **M2** y **M3** |

---

## 2.3. Factibilidad

**Técnica:** El volumen del caso (8 000 pacientes en una sede) es manejable por una base de datos relacional sobre infraestructura modesta, y el requisito de apertura del expediente en menos de 2 segundos se alcanza con indexación y paginación. Los tres puntos de mayor exigencia tienen tratamiento previsto: el motor de disponibilidad de la agenda se resuelve con validación de solapamiento en la base de datos, el tarifario con un modelo servicio–convenio–vigencia, y la confidencialidad con control de acceso por rol y bitácora de auditoría. El equipo cuenta con la formación en modelado de datos, desarrollo web y control de versiones de los cursos prerrequisito.

**Operativa:** Los problemas son reconocidos por la propia dirección médica, que ya reporta errores de medicación y demoras de cobranza, y el sistema no elimina puestos sino que redistribuye tareas manuales. El punto de mayor fricción es la transición desde el papel, dada la distinta alfabetización digital del personal; por ello la usabilidad se trata como requisito, con flujos de pocos pasos, terminología clínica y validaciones que impiden el error, además de manual por rol y marcha blanca antes de retirar el registro en papel.

**Económica:** La infraestructura se limita a servicios en la nube de nivel gratuito o de costo moderado, sin inversión en servidores propios. Del lado del beneficio, reducir la inasistencia del 18 % recupera capacidad de consulta hoy desperdiciada sobre 12 consultorios, acortar el agendamiento de 20 a menos de 3 minutos libera horas del personal de admisión, y el seguimiento sistemático de glosas reduce la facturación a EPS que hoy se pierde o se cobra con retraso. A ello se suma la prevención de errores de medicación y el cumplimiento demostrable de la Ley N.° 29733.
