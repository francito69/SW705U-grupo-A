### 📜 Acta de Constitución del Proyecto

---

#### 1.1\. Datos generales

| Campo                                 | Detalle                                                                                                                                                        |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del proyecto**         | Sistema de Información Clínico-Administrativo para la Clínica San Rafael S.A.C. (SIRA)                                                                      |
| **Patrocinador**                | Gerencia General, Clínica San Rafael S.A.C.                                                                                                                   |
| **Equipo de Desarrollo**        | Grupo A:<br />• Albino Soto, Christopher Henrry (20231158C)<br />• Inga Champi, Franz Joe (20231302G)<br />• Rashuaman Sapallanay, Ricco Didier (20231242D) |
| **Fecha del acta**              | 10 de septiembre de 2026                                                                                                                                       |
| **Product Owner de referencia** | Docente del curso SW705 (Mg. Ing. Jose Carlos Garcia La Riva)                                                                                                  |

---

#### 1.2\. Justificación del proyecto

La **Clínica San Rafael S.A.C.** (sede San Borja) experimentó un crecimiento acelerado desde una consulta externa básica hacia una oferta multiespecialidad con 12 consultorios, tópico de emergencia, laboratorio clínico, diagnóstico por imágenes y farmacia propios. No obstante, mantuvo una gestión operativa manual y fragmentada que genera cinco perjuicios críticos comprobables:

1. **Riesgo clínico y de seguridad del paciente:** Historias clínicas dispersas en papel y hojas de cálculo por consultorio, sin vista médica unificada, lo que ya derivó en eventos adversos reportados por duplicación diagnóstica y errores de medicación al desconocer antecedentes o alergias.
2. **Saturación operativa y pérdida de ingresos:** Canal de agendamiento telefónico con esperas de hasta 20 minutos, citas duplicadas o solapadas y una tasa de inasistencia (*no-show*) del 18 % debida a la ausencia total de recordatorios estructurados.
3. **Demora diagnóstica:** Circuito de resultados de laboratorio e imágenes en soporte físico con retrasos de hasta 48 horas y extravíos ocasionales, retrasando decisiones terapéuticas urgentes.
4. **Deterioro del flujo de caja:** Facturación y conciliación manual con 5 EPS y SOAT, provocando continuas observaciones, rechazos de pago y glosas no recuperadas por discrepancias en copagos y tarifarios.
5. **Ceguera en la toma de decisiones:** Falta de reportes e indicadores en tiempo real respecto a ocupación de consultorios, tiempos de espera e ingresos por convenio o especialidad.

El proyecto **SIRA** se justifica plenamente porque integra y automatiza los flujos clínico-administrativos en una sola plataforma web segura, garantizando la continuidad asistencial, eliminando solapamientos, reduciendo el ausentismo de pacientes y agilizando la liquidez de la clínica bajo estricto cumplimiento normativo.

---

#### 1.3\. Objetivos SMART

| Código          | Objetivo SMART                                                                                                                                                                                                                                                                                                                                                                         | Indicador de Logro / Verificación                                                                                                                                                                                                                                                    | Plazo / Hito                 |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| **OBJ-01** | Implementar una**Historia Clínica Electrónica unificada (M1)** que permita consultar el expediente completo de cualquier paciente en menos de 2 segundos sobre una base de 8 000 registros sintéticos, con control de acceso basado en roles (RBAC) y auditoría inmutable de accesos según la Ley N.° 29733.                                                               | • Tiempo de apertura y renderizado del expediente$\\le 2$ s (percentil 95 en JMeter).• 100 % de accesos y modificaciones registradas con usuario, fecha, hora y motivo.• 0 accesos no autorizados a información clínica sensible en pruebas de penetración.                   | Fin del Sprint 1 (Semana 11) |
| **OBJ-02** | Poner en operación una**agenda digital consolidada (M2)** para los 12 consultorios que bloquee el 100 % de los solapamientos de médico y consultorio, reduzca el tiempo de agendamiento en admisión de 20 a menos de 3 minutos por cita y procese recordatorios automáticos con al menos 24 horas de anticipación para reducir la tasa de inasistencia (línea base: 18 %). | • 0 % de citas solapadas (validado mediante transacciones y pruebas de concurrencia).• Tiempo de registro$\\le 3$ minutos en un máximo de 3 pasos de pantalla.• 100 % de citas programadas procesadas por el trabajador asíncrono de notificación 24 h antes.                 | Fin del Sprint 1 (Semana 11) |
| **OBJ-03** | Digitalizar el circuito de**órdenes y resultados de laboratorio e imágenes (M3)** para que el resultado digital quede vinculado al expediente del paciente en menos de 4 horas desde la toma de muestra (frente a las 48 h actuales) y con trazabilidad de estados que elimine el extravío de resultados.                                                                     | • Tiempo de ciclo de orden a resultado disponible en HCE$\\le 4$ horas.• Tasa de resultados extraviados = 0 %.• 100 % de resultados adjuntados en almacenamiento digital privado y notificados al médico tratante y paciente.                                                   | Fin del Sprint 2 (Semana 14) |
| **OBJ-04** | Automatizar la**facturación por convenios (M4)** aplicando el tarifario vigente al 100 % de las atenciones registradas en las tres coberturas (Particular, EPS 1–5 y SOAT), incorporando control de copagos y glosas, y desplegar un **dashboard gerencial (M5)** con métricas operativas en tiempo real.                                                               | • 100 % de comprobantes emitidos con cálculo automatizado de cobertura y copago.• 100 % de glosas registradas con motivo, monto objetado y trazabilidad de resolución.• Tiempo de carga del dashboard$\\le 3$ s con datos agregados de ocupación, espera, ingresos y no-show. | Fin del Sprint 2 (Semana 14) |

---

#### 1.4\. Alcance Resumido

El proyecto comprende el desarrollo, verificación e implantación de la plataforma web adaptativa **SIRA** para la sede San Borja de la Clínica San Rafael S.A.C., centralizando los procesos clínicos y administrativos actualmente aislados.

##### Módulos Imprescindibles:

* **Sprint 1 (Semanas 9 a 11):**
  * **M1 — Historia Clínica Electrónica (HCE) y Triaje:** Búsqueda y registro unificado de pacientes, expediente integral por especialidades, antecedentes, alergias, registro de triaje (signos vitales por enfermería), atenciones médicas con diagnósticos estandarizados CIE-10, prescripción de recetas y anulación lógica con trazabilidad.
  * **M2 — Agenda y Citas Médicas:** Calendario consolidado para los 12 consultorios, programación de citas, motor de validación con bloqueo estricto de solapamientos entre médicos y consultorios, reprogramación, cancelación justificada y gestor asíncrono de recordatorios automáticos (SMS/correo) con 24 h de anticipación.
* **Sprint 2 (Semanas 12 a 14):**
  * **M3 — Laboratorio e Imágenes:** Emisión de órdenes de examen desde la consulta médica, seguimiento de estados operativos (solicitado, en proceso, completado), carga y resguardo de resultados digitales en repositorio privado y notificación de disponibilidad al médico y paciente.
  * **M4 — Facturación y Convenios:** Catálogo de tarifarios por modalidad de aseguramiento (Particular, EPS 1 a 5 y SOAT), cálculo paramétrico de copagos y deducibles, emisión de comprobantes de control interno y módulo de registro, sustentación y seguimiento de glosas.
  * **M5 — Reportes Gerenciales:** Cuadro de mando interactivo para la gerencia médica con indicadores dinámicos de porcentaje de ocupación de consultorios, tiempo promedio de espera, ingresos por especialidad/convenio y tasa de inasistencia (*no-show*).

##### Componentes Transversales de Seguridad y Arquitectura:

* Módulo de autenticación centralizada y control de acceso basado en roles (RBAC: Admisión, Médico, Enfermera, Laboratorio, Caja, Gerencia, Administrador).
* Bitácora de auditoría inmutable para operaciones clínicas protegidas (registro de usuario, fecha/hora, acción, IP y motivo).
* Carga y administración de datos sintéticos/anonimizados de prueba (+8 000 registros).

##### Alcance Deseable (Condicional):

* **M6 — Portal del Paciente y Telemedicina Básica:** Autoconsulta de citas en línea, acceso a resultados propios y sala virtual básica de teleconsulta para casos de seguimiento no urgentes. Queda sujeto estrictamente a la culminación exitosa de los módulos M1 al M5.

---

#### 1.5\. Exclusiones

| N.°        | Exclusión                                                                                                        | Justificación Técnica y Operativa                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Gestión de hospitalización, cirugía ambulatoria mayor y dispensación física de farmacia.**           | El proyecto se enfoca en el circuito ambulatorio, diagnóstico y administrativo de la sede. Se excluyen el censo de camas de internamiento prolongado, la programación de quirófanos centrales y el control de inventario/kardex físico de farmacia (el alcance clínico culmina formalmente en la emisión de la receta médica).*Nota de cobertura operativa:* La atención de urgencias ambulatorias en el **tópico de emergencia** se cubre mediante M1 (triaje obligatorio y consulta) y M2 (admisión directa sin cita previa). |
| **2** | **Interoperabilidad e integración externa formal con SUNAT, pasarelas EPS/TEDEF y servidores PACS/DICOM.** | No se contempla conexión directa por API/EDI con SUNAT (los comprobantes emitidos son de control y liquidación interna de clínica), intercambio electrónico automatizado de expedientes con aseguradoras, ni servidores PACS especializados para visor nativo DICOM. Los resultados de imagenología se gestionan como documentos digitales adjuntos (PDF/JPG) en almacenamiento seguro.                                                                                                                                                      |
| **3** | **Infraestructura física dedicada, sistemas ERP contables/nómina y aplicaciones móviles nativas.**       | No incluye compra ni mantenimiento de servidores locales (*on-premise*), módulos de nómina, contabilidad financiera general, tesorería, aplicaciones móviles compiladas para iOS/Android (se desarrolla una aplicación web adaptativa *responsive*) ni migración manual masiva del archivo físico histórico (se trabaja sobre el dataset sintético).                                                                                                                                                                                 |

---

#### 1.6\. Supuestos y restricciones adicionales

| N.°        | Tipo                   | Descripción                                                                                                                                                                                                                                                                                                                                                         |
| ----------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Restricción** | **Ámbito y localización:** La solución se diseña y despliega exclusivamente para una sola sede física (San Borja), operando en español (Perú), huso horario `America/Lima` (UTC-5) y moneda en soles peruanos (PEN). No incluye arquitectura multi-sede ni multi-moneda.                                                                              |
| **2** | **Restricción** | **Normativa de protección de datos (Ley N.° 29733):** Se prohíbe de manera absoluta el borrado físico (`DELETE`) de registros clínicos en la base de datos. Cualquier corrección o anulación se implementa como baja lógica (`anulado = TRUE`) registrando usuario responsable, marca temporal y motivo justificado en la bitácora de auditoría. |
| **3** | **Restricción** | **Disponibilidad operativa continua:** Los módulos de agenda y tópico de emergencia/triaje deben garantizar una disponibilidad mínima del 99.5 % durante el horario de atención de la clínica (lunes a sábado de 7:00 a. m. a 9:00 p. m., incluyendo turnos de guardia).                                                                                 |
| **4** | **Restricción** | **Presupuesto y confidencialidad académica:** Infraestructura en la nube de costo moderado/gratuito sin datos reales de pacientes. Todas las pruebas, migraciones iniciales y demostraciones se ejecutan con datos sintéticos provistos por el taller.                                                                                                       |
| **5** | **Supuesto**     | **Compromiso de interlocutores clave:** La dirección médica de la clínica designará a un responsable operativo por cada área funcional (Admisión, Cuerpo Médico, Enfermería, Laboratorio y Facturación) para validar requerimientos, reglas de tarifarios por EPS y participar en las pruebas de aceptación.                                         |

---

#### 1.7\. Riesgos iniciales

| Riesgo                                                                                                                                                                                              | Impacto         | Mitigación                                                                                                                                                                                                                                                                                               |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **R-01\. Vulneración de la confidencialidad de datos de salud:** Acceso indebido a diagnósticos o recetas por actores internos o externos no autorizados.                                   | **Alto**  | Implementar autorización RBAC estricta validada en la capa de servicios backend, cifrado de datos en tránsito con HTTPS/TLS 1.3, almacenamiento privado de resultados y bitácora de auditoría no modificable sobre el 100 % de consultas a la HCE.                                                    |
| **R-02\. Resistencia al cambio y brecha de alfabetización digital:** Rechazo del personal clínico o administrativo al migrar del papel/Excel al sistema web, generando registros paralelos. | **Alto**  | Diseñar interfaces adaptativas de alta usabilidad con flujos guiados en$\\le 3$ pasos, emplear terminología médica nativa (CIE-10), involucrar a médicos líderes en la validación del prototipo, elaborar manuales de usuario por rol y programar una marcha blanca con acompañamiento continuo. |
| **R-03\. Capacidad acotada del equipo de desarrollo:** Equipo conformado por 3 integrantes para cubrir 5 módulos imprescindibles dentro del calendario académico del semestre.              | **Alto**  | Priorización rigurosa del Product Backlog mediante MoSCoW, manteniendo el módulo M6 (portal del paciente) como alcance estrictamente condicional; aplicar revisión por pares (*code review*), integración continua y reutilización de componentes estandarizados.                                  |
| **R-04\. Inconsistencias en el motor de facturación y convenios:** Complejidad en el cálculo de coberturas, deducibles, copagos diferenciados por EPS/SOAT y manejo del ciclo de glosas.    | **Medio** | Modelar una estructura de datos relacional normalizada`Servicio–Convenio–Tarifa–Vigencia` desde la fase de diseño y construir una batería de pruebas automatizadas con casos representativos de las 5 EPS y SOAT antes de iniciar la integración con caja.                                        |

📌 **Nota de Criterio Técnico (Riesgo R-02):** El riesgo de resistencia al cambio se clasifica con **Impacto Alto** dado que la literatura especializada y los antecedentes del sector salud identifican la baja adopción del usuario asistencial como el principal factor de fracaso en la implementación de Historias Clínicas Electrónicas. Si la interfaz entorpece el tiempo de consulta médica, los profesionales retornan a apuntes físicos informales, anulando la confiabilidad global del sistema.

---

#### 1.8\. Hitos principales del proyecto

| Semana              | Hito / Entregable                                                  | Alcance Clave y Evidencia Verificable                                                                                         |
| ------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **Semana 2**  | **Avance 1: Acta de Constitución y Documento de Visión**   | Formalización del alcance, objetivos SMART, análisis de factibilidad y matriz de stakeholders.                              |
| **Semana 4**  | **Avance 2: ERS, Backlog y Modelos UML**                     | Catálogo formal de RF/RNF (IEEE 29148), backlog priorizado con HUs INVEST y diagramas de Casos de Uso, Clases y Actividades. |
| **Semana 6**  | **Avance 3: Arquitectura (SAD), Base de Datos y Prototipos** | Documento SAD (Vistas 4+1, ADRs), modelo entidad-relación en 3FN, script DDL y wireframes de alta fidelidad (HCE y Citas).   |
| **Semana 7**  | **Avance 4: Plan de Release y Sprint Backlog 1**             | Planificación temporal de entregas, definición de hecho (DoD) y asignación de historias del Sprint 1.                      |
| **Semana 8**  | **Examen Parcial: Sustentación del Entregable 1**           | Sustentación técnica grupal e individual (15 min) defendiendo la documentación de ingeniería completa.                    |
| **Semana 11** | **Avance 5: Incremento Funcional Sprint 1**                  | Despliegue operativo de M1 (HCE y Triaje) y M2 (Agenda y Citas) con pruebas unitarias automatizadas y pipeline CI activo.     |
| **Semana 14** | **Avance 6: Incremento Funcional Sprint 2**                  | Integración de M3 (Laboratorio), M4 (Facturación) y M5 (Reportes), validado con suite de pruebas y despliegue en la nube.   |
| **Semana 15** | **Avance 7: Informe Final y Manuales**                       | Entrega de memoria del proyecto, manuales de usuario por rol y pre-sustentación formativa.                                   |
| **Semana 16** | **Examen Final: Sustentación del Entregable 2**             | Demostración en vivo (20 min) del sistema web SIRA completamente funcional con datos de prueba realistas.                    |
