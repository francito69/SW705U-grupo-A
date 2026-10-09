### 3\. Especificación de Requerimientos de Software (ERS)

---

#### 3.1\. Propósito y Alcance del Sistema

##### Propósito

El presente documento define la **Especificación de Requerimientos de Software (ERS)** para el **Sistema de Información Clínico-Administrativo (SIRA)** de la Clínica San Rafael S.A.C. (sede San Borja). Su propósito fundamental es formalizar, estructurar y validar los requerimientos funcionales y no funcionales del sistema conforme al estándar internacional **IEEE 29148:2018 (Systems and software engineering — Life cycle processes — Requirements engineering)**, garantizando la trazabilidad integral desde las necesidades del negocio identificadas en el Acta de Constitución y el Documento de Visión hasta el diseño de la arquitectura y la implementación en código.

##### Alcance Organizacional y Técnico

El sistema SIRA automatiza y centraliza la gestión asistencial y administrativa de la sede San Borja, reemplazando los registros fragmentados en papel y hojas de cálculo por una plataforma web segura, modular y de alto rendimiento. Las pruebas de carga, verificación funcional y demostraciones académicas se desarrollarán utilizando un conjunto de datos sintéticos y anonimizados de 8 000 pacientes provisto por el taller.

El alcance del desarrollo se organiza de manera iterativa e incremental en los siguientes módulos:

| Módulo | Denominación Funcional                          | Sprint Asignado        | Prioridad MoSCoW | Alcance Operativo Resumido                                                                                                                                                                                                                                                                          |
| ------ | ----------------------------------------------- | ---------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **M1** | **Historia Clínica Electrónica (HCE) y Triaje** | Sprint 1               | Must have        | Registro y búsqueda unificada de pacientes, filiación, antecedentes, alergias, toma de signos vitales (triaje en sala de espera y tópico de urgencias), atenciones médicas multiespecialidad con diagnósticos CIE-10, prescripción de recetas y anulación lógica auditada.                          |
| **M2** | **Agenda y Citas Médicas**                      | Sprint 1               | Must have        | Calendario maestro para los 12 consultorios, motor de validación con bloqueo estricto de solapamiento de médicos y consultorios, agendamiento en $\\le 3$ pasos, reprogramación, cancelación justificada y trabajador asíncrono de recordatorios automáticos (SMS/correo) con 24 h de anticipación. |
| **M3** | **Laboratorio e Imágenes**                      | Sprint 2               | Must have        | Emisión de órdenes médicas digitales desde la consulta, flujo de estados (solicitado, en proceso, completado), carga y resguardo de resultados digitales en almacenamiento privado y notificación automática al expediente clínico en $\\le 4$ horas.                                               |
| **M4** | **Facturación y Convenios**                     | Sprint 2               | Must have        | Parametrización de tarifarios (Particular, EPS 1–5 y SOAT), cálculo automatizado de coberturas y copagos, emisión de comprobantes de control interno y módulo de registro, sustento y seguimiento del ciclo de vida de glosas.                                                                      |
| **M5** | **Reportes Gerenciales**                        | Sprint 2               | Must have        | Tablero de control (*dashboard*) interactivo para la dirección médica con indicadores operacionales calculados en tiempo real: ocupación de consultorios, tiempos promedio de espera, tasa de inasistencia (*no-show*) e ingresos por convenio/especialidad.                                        |
| **M6** | **Portal del Paciente y Telemedicina Básica**   | Sprint 2 (Condicional) | Could have       | Autoservicio en línea para agendamiento de citas, consulta de resultados propios y sala virtual básica para controles de seguimiento ambulatorio no urgentes (sujeto a la culminación de M1 a M5).                                                                                                  |

---

#### 3.2\. Catálogo Formal de Requisitos Funcionales y No Funcionales (Norma IEEE 29148:2018)

A continuación se presenta el catálogo oficial de requerimientos, estructurado bajo la matriz normalizada de ingeniería de requerimientos del curso:

| ID          | Tipo | Descripción del Requisito                                                                                                                                                                                                      | Fuente / Stakeholder                 | Prioridad (MoSCoW) | Criterio de Aceptación Verificable                                                                                                                                              | Fase del Ciclo de Vida        | ¿Cumple Checklist? |
| ----------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ------------------ |
| **RF-001**  | RF   | El sistema debe registrar, buscar y desplegar la Historia Clínica Electrónica unificada del paciente, consolidando filiación, antecedentes, atenciones multiespecialidad, diagnósticos estandarizados CIE-10 y prescripciones. | Médicos Tratantes / Dirección Médica | **Must**           | Dado un paciente con historial previo, al consultar por DNI/CE, el sistema despliega el expediente cronológico completo en $\\le 2$ segundos sin duplicar historiales.          | Especificación / Diseño       | Sí                 |
| **RF-002**  | RF   | El sistema debe gestionar la disponibilidad de agenda para los 12 consultorios físicos y validar transaccionalmente en tiempo real el bloqueo del 100 % de solapamientos entre médicos, horarios y consultorios.               | Personal de Admisión / Recepción     | **Must**           | Al intentar registrar una cita en un intervalo ocupado por el mismo médico o consultorio, el sistema rechaza la solicitud (HTTP 409) impidiendo la inserción.                   | Especificación / Diseño       | Sí                 |
| **RF-003**  | RF   | El sistema debe programar y enviar notificaciones o recordatorios automáticos de citas por correo electrónico o SMS con un mínimo de 24 horas de anticipación a la fecha y hora de la cita.                                    | Pacientes / Personal de Admisión     | **Must**           | El trabajador asíncrono procesa los registros de la tabla *outbox* y entrega las notificaciones al 100 % de citas programadas para las siguientes 24 horas.                     | Especificación / Diseño       | Sí                 |
| **RF-004**  | RF   | El sistema debe permitir al médico tratante emitir órdenes médicas digitales de laboratorio e imágenes vinculadas a la atención actual dentro de la HCE.                                                                       | Médicos Tratantes                    | **Must**           | La orden generada incluye código único, tipo de examen del catálogo institucional, indicaciones y queda vinculada a la atención en estado "Solicitado".                         | Especificación / Diseño       | Sí                 |
| **RF-005**  | RF   | El sistema debe permitir al personal de laboratorio registrar el procesamiento y adjuntar resultados digitales a la orden, vinculándolos al expediente en $\\le 4$ horas y notificando al médico.                              | Personal de Laboratorio / Médicos    | **Must**           | Al subir el archivo digital y marcar la orden como "Completada", el resultado se asocia a la HCE en $\\le 4$ horas desde la toma y emite alerta de disponibilidad.              | Especificación / Diseño       | Sí                 |
| **RF-006**  | RF   | El sistema debe calcular y emitir comprobantes de liquidación interna aplicando automáticamente el tarifario vigente según el convenio (Particular, EPS 1–5 o SOAT) y determinando el copago.                                  | Cajero / Área de Facturación         | **Must**           | Al liquidar un servicio, el sistema desglosa monto total, porcentaje cubierto por la aseguradora y copago neto a cobrar al paciente según catálogo vigente.                     | Especificación / Diseño       | Sí                 |
| **RF-007**  | RF   | El sistema debe registrar las observaciones o glosas emitidas por aseguradoras/EPS y gestionar su ciclo de vida (registrada, sustentada, aceptada, rechazada y recuperada).                                                    | Facturación y Cobranzas              | **Should**         | Toda glosa registra código de comprobante, motivo, importe observado y permite registrar la respuesta/sustento modificando su estado con trazabilidad.                          | Especificación / Diseño       | Sí                 |
| **RF-008**  | RF   | El sistema debe generar y presentar un cuadro de mando (*dashboard*) con indicadores interactivos de ocupación de consultorios, tiempo promedio de espera, tasa de inasistencia e ingresos.                                    | Gerencia Médica / Dirección          | **Must**           | El tablero filtra métricas por rangos de fechas, especialidades y convenios, renderizando gráficos consolidados en tiempo real en $\\le 3$ segundos.                            | Especificación / Diseño       | Sí                 |
| **RNF-001** | RNF  | **Rendimiento:** La consulta y renderizado de la Historia Clínica Electrónica completa debe realizarse en un tiempo máximo de 2 segundos sobre una base de prueba de hasta 8 000 pacientes.                                    | Rendimiento / Dirección Médica       | **Must**           | Medición de percentil 95 ($P95 \\le 2$ s) en pruebas de carga con JMeter, verificando la presencia y uso de índices sobre identificadores y fechas en PostgreSQL.               | Especificación / Arquitectura | Sí                 |
| **RNF-002** | RNF  | **Seguridad y Privacidad:** El sistema debe restringir accesos mediante RBAC, cifrar el tráfico con HTTPS/TLS 1.3 y auditar operaciones según la Ley N.° 29733 de Protección de Datos Personales.                              | Seguridad / Marco Legal Peruano      | **Must**           | Inspección de red confirma tráfico 100 % cifrado; cada acceso o cambio clínico genera registro inmutable con usuario, fecha, hora, IP y acción ejecutada.                       | Especificación / Arquitectura | Sí                 |
| **RNF-003** | RNF  | **Disponibilidad:** La plataforma debe garantizar una disponibilidad operativa mínima del 99.5 % durante el horario de atención (lunes a sábado de 7:00 a. m. a 9:00 p. m.).                                                   | Disponibilidad / Operaciones         | **Must**           | Uptime mensual registrado: $(\\text{minutos disponibles} / \\text{minutos de atención programados}) \\times 100 \\ge 99.5,%$, excluyendo ventanas de mantenimiento coordinadas. | Especificación / Operaciones  | Sí                 |
| **RNF-004** | RNF  | **Trazabilidad e Integridad:** Se prohíbe el borrado físico (`DELETE`) de información clínica. Toda supresión se efectúa como anulación lógica conservando usuario, fecha, hora y motivo.                                      | Trazabilidad / Auditoría             | **Must**           | Verificación en base de datos: el registro clínico permanece con bandera lógica `anulado = TRUE` y la justificación queda persistida en la bitácora de auditoría.               | Especificación / Arquitectura | Sí                 |
| **RNF-005** | RNF  | **Usabilidad:** La interfaz web debe ser adaptativa (*responsive*) y permitir agendar una cita médica en un máximo de 3 pasos desde la pantalla principal de admisión.                                                         | Usabilidad / Personal de Admisión    | **Must**           | Prueba de usabilidad con operadores de admisión: búsqueda de paciente, selección de bloque horario y confirmación completados en $\\le 3$ pantallas en $\\le 3$ min.            | Especificación / UX-UI        | Sí                 |

---

#### 3.3\. Checklist de Verificación de Calidad de Requisitos (IEEE 29148)

Conforme a las directrices de aseguramiento de calidad del estándar IEEE 29148, cada requerimiento fue evaluado frente a los siete criterios esenciales:

| ID          | Requisito Evaluado    | No Ambiguo | Verificable | Trazable | Necesario | Factible | Atómico | Consistente | Observación / Corrección Técnica Aplicada                                             |
| ----------- | --------------------- | ---------- | ----------- | -------- | --------- | -------- | ------- | ----------- | ------------------------------------------------------------------------------------- |
| **RF-001**  | HCE unificada         | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Especifica los componentes clínicos mínimos requeridos y límite de respuesta.         |
| **RF-002**  | Bloqueo solapamiento  | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Define la validación atómica y transaccional entre médico y consultorio.              |
| **RF-003**  | Recordatorio 24 h     | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Cuantifica la anticipación temporal mínima (24 h) y los canales de salida.            |
| **RF-004**  | Órdenes digitales     | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Delimita la asociación directa entre consulta, diagnóstico y tipo de examen.          |
| **RF-005**  | Carga de resultados   | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Establece umbral objetivo ($\\le 4$ h) y vinculación a repositorio seguro.            |
| **RF-006**  | Facturación convenios | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Detalla las coberturas contempladas en el caso (Particular, EPS 1–5, SOAT).           |
| **RF-007**  | Registro de glosas    | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Modela el flujo formal de estados para el control de cuentas por cobrar.              |
| **RF-008**  | Dashboard gerencial   | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Delimita los 4 indicadores clave exigidos por la dirección médica.                    |
| **RNF-001** | Rendimiento HCE       | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Se corrigió la errata de texto; se fija métrica $P95 \\le 2$ s sobre 8 000 registros. |
| **RNF-002** | RBAC y Ley 29733      | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Alineado con el marco regulatorio nacional de datos sensibles de salud.               |
| **RNF-003** | Disponibilidad 99.5 % | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Acotado estrictamente a la ventana de operación real de la clínica.                   |
| **RNF-004** | Anulación lógica      | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Soporta el no repudio clínico y la integridad histórica de expedientes.               |
| **RNF-005** | Usabilidad en 3 pasos | Sí         | Sí          | Sí       | Sí        | Sí       | Sí      | Sí          | Cuantifica el límite de pasos operativos y diseño adaptativo multidispositivo.        |

---

#### 3.4\. Diagrama de Contexto y Modelo de Actores

##### Límite del Sistema

El límite del sistema SIRA abarca los módulos de software web desplegados en la nube para la sede San Borja, los cuales interactúan con los usuarios internos del establecimiento y el paciente como usuario externo, prescindiendo de integraciones directas por API con entidades gubernamentales (SUNAT) o aseguradoras externas según las exclusiones aprobadas.

```
                          ┌───────────────────────────┐
                          │   Gerencia Médica (M5)    │
                          └─────────────┬─────────────┘
                                        │ Filtros de fecha / Métricas operativas
                                        ▼
┌───────────────────────────┐     ┌───────────┐     ┌───────────────────────────┐
│  Admisión / Caja (M2, M4) ├────►│  SISTEMA  │◄────┤  Médico Tratante (M1, M3) │
│ • Solicitud de citas      │     │   SIRA    │     │ • Consultas HCE / Órdenes │
│ • Liquidación y copagos   │     │ (Monolito │     │ • Prescripciones CIE-10   │
└───────────────────────────┘     │  Modular) │     └───────────────────────────┘
                                  └─────┬─────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           │                            │                            │
           ▼                            ▼                            ▼
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│    Enfermera (M1)      │  │    Laboratorio (M3)    │  │     Paciente (M2)      │
│ • Triaje signos vit.   │  │ • Carga de resultados  │  │ • Confirmación cita    │
│ • Tópico de urgencias  │  │ • Archivos digitales   │  │ • Recordatorios 24 h   │
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘

```

##### Matriz de Flujo de Datos por Actor

| Actor / Entidad Externa     | Tipo de Actor | Descripción del Rol                                                                 | Flujo de Datos Hacia el Sistema (Envía)                                                                              | Flujo de Datos Desde el Sistema (Recibe)                                                                          |
| --------------------------- | ------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Admisión / Recepción**    | Interno       | Operador de ventanilla que registra pacientes y programa citas ambulatorias.        | Datos personales de filiación, documento de identidad, convenio, fecha/hora solicitada y motivo de cancelación.      | Disponibilidad de consultorios en tiempo real, validación de solapamientos y comprobante de agendamiento.         |
| **Médico Tratante**         | Interno       | Profesional de salud que atiende al paciente en consulta externa o tópico.          | Diagnóstico CIE-10, anamnesis, evolución, receta médica, indicaciones y órdenes de laboratorio/imágenes.             | Historial médico unificado cronológico, resultados de signos vitales de triaje y resultados de exámenes adjuntos. |
| **Enfermera**               | Interno       | Personal asistencial encargado del control previo y tópico de urgencias.            | Registro de signos vitales (presión arterial, FC, temperatura, peso, talla, saturación).                             | Lista de pacientes citados del día en sala de espera, datos de filiación y alertas de alergias registradas.       |
| **Personal de Laboratorio** | Interno       | Técnico o patólogo responsable del procesamiento de análisis clínicos e imágenes.   | Registro de recepción de muestra, actualización de estado de orden, informe diagnóstico y archivo digital (PDF/JPG). | Bandeja de órdenes médicas pendientes, datos de la orden y antecedentes clínicos relevantes del examen.           |
| **Cajero / Facturación**    | Interno       | Responsable del cobro de atenciones y gestión de cuentas por cobrar a aseguradoras. | Selección de cobertura/convenio, registro de cobro de copago, ingreso de observaciones o glosas de EPS.              | Tarifario aplicable, desglose de monto cubierto vs. copago, comprobante de liquidación y reporte de glosas.       |
| **Gerencia Médica**         | Interno       | Directores de sede responsables de la eficiencia operativa y convenios.             | Parámetros de consulta temporal, filtros por especialidad médica y por tipo de aseguradora.                          | Tableros dinámicos con indicadores de ocupación, tiempo de espera de pacientes, tasa de inasistencia e ingresos.  |
| **Paciente**                | Externo       | Usuario beneficiario de los servicios de salud de la clínica.                       | Confirmación de asistencia, datos de contacto (correo/celular) y selección de cita en portal (M6 condicional).       | Mensaje de confirmación de cita, recordatorio preventivo con 24 h de anticipación y aviso de resultados listos.   |

---

#### 3.5\. Matriz de Impacto de la Solución

| Ámbito de Impacto              | Actor o Entorno Afectado                       | Tipo (+/-) | Descripción Cualitativa del Impacto                                                                                                            | Medida de Mitigación / Acción Técnica                                                                                      |
| ------------------------------ | ---------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Social / Salud**             | Pacientes de la clínica                        | **+**      | Eliminación de errores de medicación al centralizar antecedentes y alergias; reducción drástica de tiempos de espera en agendamiento.          | Implementar vista obligatoria de alertas clínicas antes de habilitar el guardado de la prescripción.                       |
| **Económico**                  | Clínica San Rafael S.A.C.                      | **+**      | Recuperación de ingresos al reducir la tasa de inasistencia del 18 % y disminuir pérdidas financieras por glosas de EPS no sustentadas.        | Parametrizar tarifarios actualizados y auditar los estados del ciclo de vida de las glosas registradas.                    |
| **Operativo / Social**         | Personal clínico y asistencial                 | **\-**     | Resistencia al cambio frente a la sustitución del papel/Excel y temor a un aumento en los tiempos de digitación durante la consulta médica.    | Diseñar pantallas de atención rápida con catálogos predictivos CIE-10, atajos de teclado y marcha blanca formativa.        |
| **Cultural / Organizacional**  | Médicos de mayor antigüedad y personal técnico | **\-**     | Curva de aprendizaje empinada por disparidad en niveles de alfabetización digital y uso de interfaces computarizadas.                          | Diseñar interfaces adaptativas guiadas en $\\le 3$ pasos, manuales por perfil y soporte presencial las primeras 2 semanas. |
| **Ambiental / Sostenibilidad** | Entorno físico de la clínica                   | **+**      | Desmaterialización casi total del archivo pasivo, eliminando el consumo masivo de papel para historias, recetas físicas y formatos de órdenes. | No requiere mitigación; consolida el cumplimiento de políticas de responsabilidad ambiental y orden institucional.         |

---

#### 3.6\. Registro Formal de Supuestos (Cadena Dato $\\rightarrow$ Criterio $\\rightarrow$ Decisión $\\rightarrow$ Evidencia)

| N.°        | Dato o Información Incompleta                                                             | Criterio Técnico / Académico Aplicado                                                                                       | Decisión de Ingeniería Tomada                                                                                                                | Evidencia Documental                                 |
| ---------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **SUP-01** | El caso no especifica formatos de intercambio electrónico (TEDEF/EDI) con las 5 EPS.      | Principio de viabilidad académica y restricción de presupuesto sin contratos B2B externos en fase de desarrollo.            | Los módulos de convenios, copagos y glosas se gestionan como control y liquidación interna de clínica sin conexión en línea a aseguradoras.  | Acta de Constitución, Exclusión 2; SAD, Sección 5.1. |
| **SUP-02** | El caso menciona tópico de emergencia pero el alcance excluye hospitalización compleja.   | Continuidad asistencial de pacientes que acuden por dolor o cuadro agudo ambulatorio sin requerir cama hospitalaria.        | El tópico de emergencias se modela dentro de M1 y M2 como consulta no programada con triaje de ingreso obligatorio.                          | Plantilla E1, Requisitos de Emergencia; ERS, RF-001. |
| **SUP-03** | El caso menciona imágenes médicas pero no define visualizadores DICOM ni servidores PACS. | Los servidores PACS implican licencias de alto costo y visualizadores diagnósticos nativos fuera del alcance del curso.     | Las imágenes y resultados de laboratorio se adjuntan y resguardan como documentos digitales (PDF/JPG) en almacenamiento seguro.              | Documento de Visión, Sección 2.3; SAD, ADR-02.       |
| **SUP-04** | El caso exige recordatorios 24 h antes pero no se cuenta con proveedor SMS contratado.    | Evitar acoplamiento sincrónico que bloquee la base de datos si falla la red externa o no hay saldo en pasarela de terceros. | Implementar el patrón arquitectónico *Transactional Outbox* con un planificador asíncrono y adaptador agnóstico de mensajería.               | SAD, Sección 5.1 y ADR-04.                           |
| **SUP-05** | La clínica posee archivos históricos en papel y Excel pero con inconsistencias graves.    | Protección de la integridad del nuevo sistema y cumplimiento estricto del cronograma del taller.                            | No realizar migración masiva de expedientes históricos degradados; poblar el sistema con una base sintética de 8 000 registros para pruebas. | Acta de Constitución, Exclusión 3; SAD, Sección 5.4. |

---

#### 3.7\. Historias de Usuario con Criterios de Aceptación (Gherkin / INVEST)

Para dar estricto cumplimiento al lineamiento de la Plantilla del Entregable 1 (**mínimo 8 Historias de Usuario desarrolladas para el Sprint 1: M1 y M2**), el backlog se descompone en unidades de valor clínico y administrativo independientes, estimables y testeables:

##### Historias de Usuario del Sprint 1 (Módulos M1 y M2 — 35 Puntos de Historia)

###### HU01: Consulta de Historia Clínica Electrónica Unificada (8 Puntos)

* **Como** médico tratante,
* **quiero** consultar la historia clínica electrónica unificada y cronológica del paciente,
* **para** conocer sus antecedentes clínicos, alergias y consultas previas en distintas especialidades, evitando duplicidad diagnóstica y errores de medicación.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Consulta exitosa de paciente con historial multiespecialidad.**  
    * **Dado** un médico autenticado en el sistema con rol de "Médico",
    * **cuando** ingresa el tipo y número de documento de un paciente con atenciones en múltiples especialidades y presiona "Buscar",
    * **entonces** el sistema presenta el expediente clínico cronológico completo en un tiempo inferior a 2 segundos, mostrando en la cabecera antecedentes, alergias destacadas y consultas pasadas.
  * **Escenario 2: Restricción de acceso a usuarios sin privilegios clínicos.**  
    * **Dado** un usuario autenticado con rol de "Cajero" o "Admisión",
    * **cuando** intenta ingresar al enlace directo de visualización de la HCE de un paciente,
    * **entonces** el sistema bloquea la visualización, emite un error de acceso no autorizado (HTTP 403) y registra el intento denegado en la bitácora de auditoría.

###### HU02: Agendamiento de Cita con Bloqueo Transaccional de Solapamiento (5 Puntos)

* **Como** personal de admisión,
* **quiero** agendar una cita médica verificando la disponibilidad consolidada de médicos y consultorios,
* **para** evitar cruces de horario, eliminar citas duplicadas y atender al paciente en menos de 3 minutos.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Agendamiento exitoso en horario disponible.**  
    * **Dado** un paciente registrado y un consultorio y médico con disponibilidad libre en el horario elegido,
    * **cuando** el operador de admisión selecciona la fecha, especialidad, médico, consultorio y confirma la cita,
    * **entonces** el sistema persiste la cita en estado "Confirmada", genera un identificador único y emite el comprobante de cita en pantalla en un máximo de 3 pasos.
  * **Escenario 2: Bloqueo transaccional ante intento de solapamiento.**  
    * **Dado** que un consultorio o médico ya posee una cita confirmada en el intervalo de 10:00 a 10:30 a. m.,
    * **cuando** otro operador o solicitud concurrente intenta registrar una cita para el mismo recurso en ese mismo intervalo,
    * **entonces** el servidor rechaza la transacción con código de conflicto (HTTP 409), notifica que el recurso está ocupado y mantiene la agenda intacta sin duplicar registros.

###### HU03: Registro y Búsqueda de Paciente con Validación de Convenio (3 Puntos)

* **Como** personal de admisión,
* **quiero** buscar a un paciente por su documento de identidad y registrarlo si es nuevo asignándole su tipo de cobertura,
* **para** asegurar que sus datos de filiación y aseguradora sean correctos antes de agendar o atenderlo.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Paciente no registrado previamente.**  
    * **Dado** que un operador ingresa un documento de identidad que no existe en el sistema,
    * **cuando** completa los campos obligatorios (nombres, apellidos, fecha de nacimiento, teléfono, correo y convenio asegurador) y presiona "Guardar",
    * **entonces** el sistema crea el registro de paciente, valida el formato del correo y teléfono, y lo deja disponible para citas y atenciones clínicas inmediatas.
  * **Escenario 2: Prevención de expedientes duplicados.**  
    * **Dado** un paciente que ya se encuentra registrado con DNI "12345678",
    * **cuando** el operador intenta registrar nuevamente a una persona con el mismo tipo y número de documento,
    * **entonces** el sistema impide el guardado, emite una advertencia de "Paciente ya registrado" y abre automáticamente la ficha del paciente existente.

###### HU04: Registro de Atención Médica con Diagnóstico CIE-10 y Prescripción (5 Puntos)

* **Como** médico tratante,
* **quiero** registrar los hallazgos de la consulta, diagnóstico CIE-10 y la prescripción farmacológica,
* **para** formalizar la atención en el expediente legal del paciente y emitir la receta médica correspondiente.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Registro completo de atención médica ordinaria.**  
    * **Dado** un médico que tiene abierta la consulta de un paciente con triaje completado,
    * **cuando** ingresa el motivo de consulta, selecciona al menos un diagnóstico codificado bajo el catálogo CIE-10, redacta las indicaciones farmacológicas y hace clic en "Finalizar Atención",
    * **entonces** el sistema almacena la atención en la HCE, asocia la receta con firma digital/médica responsable y bloquea la edición directa de los campos clínicos.
  * **Escenario 2: Validación obligatoria de diagnóstico estandarizado.**  
    * **Dado** que el médico intenta finalizar una atención sin ingresar un código CIE-10 válido,
    * **cuando** presiona "Finalizar Atención",
    * **entonces** el sistema resalta el campo en rojo, impide el guardado y exige seleccionar un código diagnóstico del catálogo oficial.

###### HU05: Registro de Triaje y Signos Vitales por Enfermería (3 Puntos)

* **Como** enfermera,
* **quiero** registrar los signos vitales y medidas antropométricas del paciente en sala de espera o tópico,
* **para** que el médico tratante cuente con parámetros clínicos actualizados antes de iniciar la consulta médica.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Captura de signos vitales para paciente citado.**  
    * **Dado** un paciente que realizó *check-in* en admisión y figura en la lista de espera de enfermería,
    * **cuando** la enfermera ingresa presión arterial, frecuencia cardíaca, temperatura, peso y talla, y guarda el registro,
    * **entonces** los datos quedan enlazados a la atención del día y se visualizan inmediatamente en la cabecera clínica de la interfaz del médico.
  * **Escenario 2: Alerta visual ante parámetros fuera de rango.**  
    * **Dado** que la enfermera registra una presión arterial $\\ge 140/90$ mmHg o temperatura $\\ge 38.5$ °C,
    * **cuando** guarda el registro de triaje,
    * **entonces** el sistema almacena los datos y añade un indicador visual de alerta (etiqueta de color rojo) en la lista de pacientes en espera para priorización clínica.

###### HU06: Reprogramación y Cancelación Justificada de Citas (3 Puntos)

* **Como** personal de admisión,
* **quiero** reprogramar o cancelar una cita médica registrando obligatoriamente el motivo,
* **para** liberar el consultorio en la agenda y mantener la justificación auditable de cada cambio operativo.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Cancelación justificada de cita médica.**  
    * **Dado** un paciente o médico que solicita cancelar una cita programada,
    * **cuando** el operador selecciona la cita, hace clic en "Cancelar Cita", selecciona el motivo ("Solicitud del paciente", "Inasistencia del médico", etc.) y confirma,
    * **entonces** el sistema cambia el estado de la cita a "Cancelada", libera inmediatamente el bloque de horario para nuevas reservas y persiste el motivo en la base de datos.
  * **Escenario 2: Reprogramación sin conflictos.**  
    * **Dado** un paciente que solicita cambiar el horario de su cita confirmada,
    * **cuando** el operador elige un nuevo bloque libre y confirma la reprogramación,
    * **entonces** el sistema anula la reserva previa, crea la nueva cita enlazada y genera un nuevo registro de recordatorio asíncrono en la tabla *outbox*.

###### HU07: Generación y Envío Asíncrono de Recordatorios de Citas a 24 Horas (5 Puntos)

* **Como** sistema SIRA (proceso en segundo plano),
* **quiero** procesar automáticamente las citas programadas para el día siguiente y enviar recordatorios por SMS o correo electrónico,
* **para** reducir la tasa de inasistencia del 18 % y recordar oportunamente al paciente su turno médico.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Envío exitoso del recordatorio con 24 h de anticipación.**  
    * **Dado** que existen citas en estado "Confirmada" cuya fecha y hora de atención se encuentra dentro del rango de las próximas 24 horas,
    * **cuando** el planificador del sistema ejecuta su tarea periódica en segundo plano,
    * **entonces** toma los registros pendientes de la tabla *outbox*, despacha los mensajes mediante el adaptador de correo/SMS y actualiza el estado a "Enviado" con marca temporal.
  * **Escenario 2: Tolerancia a fallos en el servicio externo de mensajería.**  
    * **Dado** que el servicio externo de mensajería no responde o devuelve un error de red,
    * **cuando** el trabajador asíncrono intenta realizar el despacho del recordatorio,
    * **entonces** el sistema no bloquea la base de datos de citas, registra el fallo en la tabla *outbox*, incrementa el contador de reintentos y programa un nuevo intento según la política de reintentos.

###### HU08: Anulación Lógica de Atenciones Clínicas con Bitácora de Auditoría (3 Puntos)

* **Como** médico auditor o director médico,
* **quiero** anular lógicamente un registro clínico erróneo ingresando una justificación formal,
* **para** corregir inconsistencias sin vulnerar la prohibición de borrado físico impuesta por la Ley N.° 29733.
* **Criterios de Aceptación (Gherkin):**  
  * **Escenario 1: Anulación lógica autorizada con motivo obligatorio.**  
    * **Dado** un usuario autenticado con permisos de anulación clínica que selecciona una atención errónea,
    * **cuando** presiona "Anular Registro", digita una justificación de al menos 20 caracteres y confirma con su clave de usuario,
    * **entonces** el sistema actualiza la bandera `anulado = TRUE`, mantiene el registro en la base de datos y añade una entrada inmutable en `bitacora_auditoria` con usuario, fecha, hora, IP y justificación.
  * **Escenario 2: Prohibición estricta de eliminación física en la capa de persistencia.**  
    * **Dado** un intento de ejecución de comando SQL `DELETE` sobre la tabla de atenciones clínicas o historias,
    * **cuando** se ejecuta la instrucción,
    * **entonces** los disparadores y políticas de permisos de la base de datos rechazan la instrucción, manteniendo la integridad histórica y legal de todos los registros de salud.

---

##### Historias de Usuario del Sprint 2 (Módulos M3, M4, M5 y M6 — 36 Puntos de Historia)

###### HU09: Emisión Digital de Órdenes de Laboratorio e Imágenes (5 Puntos)

* **Como** médico tratante,
* **quiero** emitir órdenes digitales de exámenes auxiliares dentro de la consulta médica,
* **para** que el área de laboratorio reciba el requerimiento sin emitir papeles que puedan extraviarse.
* **Criterios de Aceptación:** Al presionar "Agregar Examen", el médico selecciona los análisis requeridos del catálogo, añade indicaciones clínicas y al finalizar la consulta, la orden queda creada en estado "Solicitado", visible instantáneamente para el personal del laboratorio.

###### HU10: Carga y Vinculación de Resultados Digitales en $\\le 4$ Horas (5 Puntos)

* **Como** personal de laboratorio,
* **quiero** adjuntar el resultado digital (PDF/JPG) y registrar el informe diagnóstico de una orden,
* **para** que esté disponible en el expediente clínico del paciente en menos de 4 horas desde la toma de muestra.
* **Criterios de Aceptación:** Dado un examen procesado, el analista ingresa el informe, sube el archivo digital a almacenamiento privado y marca la orden como "Completada"; el sistema vincula el documento a la HCE en $\\le 4$ h y emite una alerta interna al médico tratante.

###### HU11: Facturación por Convenio y Cálculo Automatizado de Copagos (8 Puntos)

* **Como** cajero de la clínica,
* **quiero** generar el comprobante aplicando el tarifario del convenio del paciente (Particular, EPS 1–5 o SOAT),
* **para** cobrar el copago exacto en ventanilla y registrar la liquidación de la aseguradora sin incurrir en glosas.
* **Criterios de Aceptación:** Al liquidar una atención, el sistema detecta el convenio activo, calcula la cobertura porcentual pactada, muestra en pantalla el monto neto de copago que debe abonar el paciente y registra la cuenta por cobrar a la aseguradora.

###### HU12: Registro, Sustento y Seguimiento de Glosas de Aseguradoras (5 Puntos)

* **Como** facturador / personal de cobranzas,
* **quiero** registrar las observaciones monetarias emitidas por las aseguradoras y dar seguimiento a su estado,
* **para** sustentar las objeciones en los plazos fijados y recuperar los montos retenidos por las EPS.
* **Criterios de Aceptación:** El usuario registra la glosa indicando número de factura, importe glosado, código de motivo y fecha de recepción; el sistema asigna el estado "Registrada" y permite anexar el sustento médico para transitar a "Sustentada", "Aceptada" o "Recuperada".

###### HU13: Tablero de Control Gerencial con Indicadores Operativos (5 Puntos)

* **Como** gerencia médica,
* **quiero** visualizar un *dashboard* interactivo con indicadores de ocupación, tiempos de espera, inasistencia e ingresos,
* **para** tomar decisiones estratégicas fundamentadas sobre turnos médicos, consultorios y convenios de aseguradoras.
* **Criterios de Aceptación:** El directivo selecciona un rango de fechas y especialidades; el sistema calcula y dibuja en pantalla gráficos interactivos de ocupación por consultorio, tiempo de espera promedio, porcentaje de *no-show* y facturación acumulada por convenio en $\\le 3$ segundos.

###### HU14: Agendamiento en Línea mediante Portal del Paciente (8 Puntos - Condicional)

* **Como** paciente de la clínica,
* **quiero** consultar la disponibilidad y agendar mi cita médica a través de un portal web,
* **para** obtener un turno médico sin tener que acudir presencialmente ni esperar en la línea telefónica.
* **Criterios de Aceptación:** El paciente autenticado en el portal selecciona especialidad, médico y horario disponible; el sistema valida la disponibilidad, confirma la cita, agenda el envío del recordatorio y emite la confirmación digital en pantalla.

##### Validación de Calidad INVEST del Backlog

* **I (Independiente):** Las historias del Sprint 1 se desacoplan mediante contratos de datos claros; las dependencias técnicas entre HU04 (Atención) y HU09 (Orden) se coordinan mediante eventos de dominio.
* **N (Negociable):** Los criterios de aceptación admiten ajustes en tipos de recordatorios (SMS vs. correo) y formatos de archivo sin alterar la esencia del requerimiento.
* **V (Valioso):** Cada historia entrega valor comprobable directo a un rol (seguridad clínica, reducción de tiempos o control de ingresos).
* **E (Estimable):** Las historias poseen puntajes de complejidad acotados (3 a 8 puntos de historia) en base a la escala Fibonacci.
* **S (Pequeño / Small):** Ninguna historia supera los 8 puntos, lo que garantiza que pueden completarse dentro del ciclo de un sprint de 2 semanas por el equipo de tres integrantes.
* **T (Testeable):** Todos los criterios de aceptación están formalizados en sintaxis Gherkin (Dado/Cuando/Entonces), permitiendo la automatización de pruebas unitarias y de integración en pytest.

---

#### 3.8\. Product Backlog Priorizado y Planificación de Sprints

| Orden Prioridad | ID Historia | Denominación y Resumen de Valor                                 | Módulo SIRA      | Prioridad MoSCoW | Sprint               | Puntos de Historia |
| --------------- | ----------- | --------------------------------------------------------------- | ---------------- | ---------------- | -------------------- | ------------------ |
| **1**           | **HU01**    | Consulta de HCE unificada cronológica por el médico             | M1 - HCE         | Must have        | **Sprint 1**         | 8                  |
| **2**           | **HU02**    | Agendamiento de citas con bloqueo de solapamientos              | M2 - Agenda      | Must have        | **Sprint 1**         | 5                  |
| **3**           | **HU03**    | Registro y búsqueda de paciente nuevo con convenio              | M1 - HCE         | Must have        | **Sprint 1**         | 3                  |
| **4**           | **HU04**    | Registro de atención médica con diagnóstico CIE-10 y receta     | M1 - HCE         | Must have        | **Sprint 1**         | 5                  |
| **5**           | **HU05**    | Registro de triaje y signos vitales por enfermería              | M1 - HCE         | Must have        | **Sprint 1**         | 3                  |
| **6**           | **HU06**    | Reprogramación y cancelación justificada de citas               | M2 - Agenda      | Must have        | **Sprint 1**         | 3                  |
| **7**           | **HU07**    | Generación y envío asíncrono de recordatorios automáticos 24 h  | M2 - Agenda      | Must have        | **Sprint 1**         | 5                  |
| **8**           | **HU08**    | Anulación lógica de atenciones clínicas y bitácora de auditoría | M1 - HCE         | Must have        | **Sprint 1**         | 3                  |
| **9**           | **HU09**    | Emisión digital de órdenes de laboratorio e imágenes            | M3 - Laboratorio | Must have        | **Sprint 2**         | 5                  |
| **10**          | **HU10**    | Carga y vinculación de resultados digitales en $\\le 4$ horas   | M3 - Laboratorio | Must have        | **Sprint 2**         | 5                  |
| **11**          | **HU11**    | Facturación por convenio y cálculo automatizado de copagos      | M4 - Facturación | Must have        | **Sprint 2**         | 8                  |
| **12**          | **HU12**    | Registro, sustento y seguimiento del ciclo de glosas            | M4 - Facturación | Should have      | **Sprint 2**         | 5                  |
| **13**          | **HU13**    | Tablero de control gerencial con indicadores operativos         | M5 - Reportes    | Must have        | **Sprint 2**         | 5                  |
| **14**          | **HU14**    | Agendamiento en línea mediante portal del paciente              | M6 - Portal      | Could have       | **Sprint 2 (Cond.)** | 8                  |

##### Resumen Cuantitativo del Plan de Sprints:

* **Capacidad Estimada Sprint 1 (Semanas 9 a 11):** 35 Puntos de Historia (Módulos M1 y M2 completos).
* **Capacidad Estimada Sprint 2 (Semanas 12 a 14):** 28 Puntos de Historia imprescindibles (M3, M4 y M5).
* **Alcance Condicional / Reserva:** 8 Puntos de Historia (Módulo M6 sujeto a culminación de M1 a M5).
* **Carga Total del Proyecto:** 71 Puntos de Historia.

---

#### 3.9\. Matriz de Trazabilidad Bidireccional

Esta matriz demuestra que cada problema operativo y objetivo de negocio se encuentra respaldado por requerimientos técnicos verificables e historias de usuario en el backlog:

| Problema Identificado en Clínica San Rafael                                           | Objetivo SMART Vinculado | Requerimientos Funcionales y No Funcionales | Historias de Usuario Asociadas | Módulos Responsables             |
| ------------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------- | ------------------------------ | -------------------------------- |
| Historias clínicas en papel dispersas, duplicidad diagnóstica y riesgo de medicación. | **OBJ-01**               | RF-001, RNF-001, RNF-002, RNF-004           | HU01, HU03, HU04, HU05, HU08   | **M1 — HCE y Triaje**            |
| Espera telefónica de 20 min, citas solapadas y tasa de inasistencia del 18 %.         | **OBJ-02**               | RF-002, RF-003, RNF-003, RNF-005            | HU02, HU06, HU07, HU14         | **M2 — Agenda y Citas** (y M6)   |
| Retraso de hasta 48 h en resultados y extravío de informes de laboratorio e imágenes. | **OBJ-03**               | RF-004, RF-005, RNF-002, RNF-004            | HU09, HU10                     | **M3 — Laboratorio e Imágenes**  |
| Facturación manual con 5 EPS y SOAT, liquidaciones erróneas y glosas descontroladas.  | **OBJ-04**               | RF-006, RF-007, RNF-002                     | HU11, HU12                     | **M4 — Facturación y Convenios** |
| Ceguera directiva por ausencia de indicadores operacionales y de flujo de caja.       | **OBJ-04**               | RF-008, RNF-001                             | HU13                           | **M5 — Reportes Gerenciales**    |

---

#### 3.10\. Reglas de Negocio y Restricciones Operativas

* **RN-01: Exclusión Absoluta de Solapamiento Temporal:** Un médico o un consultorio físico no pueden tener más de una cita en estado "Confirmada" en el mismo rango de fecha y hora. Esta regla se valida en la API y se blinda a nivel físico en PostgreSQL mediante una restricción de exclusión (`CONSTRAINT ... EXCLUDE USING gist`).
* **RN-02: Principio de Integridad Clínica y Prohibición de Borrado Físico (Ley N.° 29733):** Queda estrictamente prohibida la ejecución de eliminaciones físicas (`DELETE`) sobre registros de pacientes, atenciones, diagnósticos, recetas o resultados. Cualquier anulación se efectúa mediante baja lógica (`anulado = TRUE`) registrando usuario, fecha, hora, IP y motivo obligatorio en la bitácora de auditoría.
* **RN-03: Jerarquía de Tarifarios y Cálculo de Copago por Cobertura:** Toda atención médica debe valorizarse automáticamente al momento de la liquidación en caja según el convenio vigente del paciente:  
  1. *Particular:* Cobertura = 0 %, Copago = 100 % del valor de lista.
  2. *EPS (1 a 5):* Cobertura = porcentaje pactado en convenio (ej. 70 % a 85 %), Copago = deducible fijo + coaseguro resultante.
  3. *SOAT:* Cobertura = 100 % de gastos ambulatorios hasta el límite de cobertura legalmente vigente.
* **RN-04: Compromiso Temporal de Entrega de Resultados Diagnósticos:** Todo examen auxiliar generado desde una consulta médica debe procesarse, adjuntarse y ponerse a disposición en el expediente electrónico en un tiempo máximo de 4 horas contadas desde la toma de muestra o ejecución del estudio.
* **RN-05: Delimitación de Ámbito, Huso Horario y Moneda:** El sistema opera exclusivamente para la sede San Borja, bajo idioma español (Perú), huso horario oficial `America/Lima` (UTC-5) y moneda en soles peruanos (PEN). No se contemplan esquemas multi-sede ni transacciones en moneda extranjera.
* **RN-06: Condicionalidad del Módulo M6:** El desarrollo del Portal del Paciente (M6) únicamente dará inicio si los módulos imprescindibles (M1 a M5) han completado satisfactoriamente sus pruebas de aceptación y se encuentran estables dentro del cronograma del Sprint 2.