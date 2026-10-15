# 8. Plan de Release, Sprint Backlog 1 y Guion de Sustentación — Sistema SIRA

--------------------------------------------------------------------------------

### Contexto y Metodología de Planificación Ágil (Semana 7)

El presente documento constituye la especificación formal del **Plan de Release**, el **Sprint Backlog 1**, la **Definición de Hecho (Definition of Done - DoD)** y el **Guion de Sustentación del Entregable 1 (Examen Parcial)** para el **Sistema de Información Clínico-Administrativo (SIRA)** de la **Clínica San Rafael S.A.C. (Sede San Borja)**, desarrollado en el marco del curso Taller de Ingeniería de Software I (SW705).

La planificación ágil consolida y materializa el trabajo de ingeniería desarrollado en las fases previas (`01-acta-constitucion.md`, `02-documento-vision.md`, `03-especificacion-requerimientos-ERS.md`, `04-modelosUML.md`, `05-arquitectura-SAD.md`, `06-modelo-base-datos.md` y `07-prototipos-ux-ui.md`). Se fundamenta en el marco de trabajo **Scrum**, adaptado a la capacidad operativa de un equipo de tres integrantes de ingeniería de software (Grupo A), distribuyendo los 70 puntos de historia del Product Backlog en dos ciclos iterativos e incrementales de tres semanas cada uno.

```
+----------------------------------------------------------------------------------------------------+
|                                CRONOGRAMA MAESTRO DEL PROYECTO SIRA                               |
+------------------------------------+----------------------------------+----------------------------+
| FASE 1: INGENIERÍA Y DISEÑO        | FASE 2: SPRINT 1 (M1 + M2)       | FASE 3: SPRINT 2 (M3-M5)   |
| Semanas 2 a 8                      | Semanas 9 a 11                   | Semanas 12 a 14            |
| Entregable 1 (Examen Parcial)      | MVP Clínico-Administrativo       | Producto Integral Operativo|
| • Acta, Visión, ERS, UML           | • HCE Unificada y Triaje         | • Laboratorio e Imágenes   |
| • SAD 4+1, BD en 3FN, Wireframes   | • Agenda en 3 Pasos y Outbox     | • Facturación y Glosas     |
| • Plan de Release y DoD            | • 35 Story Points (8 HUs)        | • Tablero Gerencial (BI)   |
| • Repositorio y CI inicial         | • Pruebas unitarias e integradas | • Despliegue Cloud Demo    |
+------------------------------------+----------------------------------+----------------------------+
```

---

## 8. Plan de Release (Release Planning)

### 8.1. Estrategia y Objetivos de los Releases

El desarrollo del sistema SIRA se estructura en **dos releases funcionales mayores**, orientados a mitigar de forma temprana los riesgos de mayor impacto identificados en el Acta de Constitución (Riesgo R-01: confidencialidad clínica y Riesgo R-02: resistencia al cambio operativo):

1. **Release 1.0.0-alpha — MVP Clínico-Administrativo (Cierre del Sprint 1, Semana 11):**
   * **Propósito:** Poner en operación el núcleo asistencial y de coordinación de citas de la sede San Borja, resolviendo los dos dolores más críticos: el expediente médico disperso en papel y la agenda telefónica saturada con solapamientos y ausentismo.
   * **Módulos Incluidos:** **M1 (Historia Clínica Electrónica y Triaje)** y **M2 (Agenda y Citas Médicas)**, integrados sobre los componentes transversales **T1 (Seguridad RBAC)**, **T2 (Auditoría inmutable)** y **T3 (Worker de notificaciones asíncronas Outbox)**.
   * **Valor Entregado:** Vista unificada del paciente en menos de 2 segundos (RNF-001), agendamiento sin cruces en un máximo de 3 pasos (RNF-005), despacho automatizado de recordatorios a 24 h (RF-003) y registro auditado de atenciones con diagnósticos CIE-10.

2. **Release 2.0.0-final — Sistema Integral Operativo (Cierre del Sprint 2, Semana 14):**
   * **Propósito:** Completar el circuito diagnóstico auxiliar, la liquidación financiera con aseguradoras y la inteligencia operativa para la dirección médica, entregando la plataforma lista para la marcha blanca asistida.
   * **Módulos Incluidos:** **M3 (Laboratorio e Imágenes)**, **M4 (Facturación y Convenios)** y **M5 (Reportes Gerenciales)**. El módulo **M6 (Portal del Paciente / Telemedicina básica)** se mantiene como alcance deseable condicionado a la estabilización de M1-M5.
   * **Valor Entregado:** Carga de resultados digitales vinculados al expediente en menos de 4 h (RF-005), cálculo automatizado de copagos y seguimiento de glosas ante 5 EPS y SOAT (RF-006, RF-007), y tablero ejecutivo con métricas de ocupación, tiempos de espera e ingresos en tiempo real (RF-008).

---

### 8.2. Cronograma de Sprints y Alcance Funcional

Conforme a la estructura requerida en la plantilla oficial del Entregable 1, se formaliza el alcance de cada sprint de desarrollo:

| Sprint | Semanas | Alcance Funcional y Módulos | Historias de Usuario | Puntos de Historia | Entregable Verificable / Incremento de Software |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **Sprint 1** | **9 – 11** | **M1: Historia Clínica Electrónica y Triaje**<br>• Registro y búsqueda de filiación única.<br>• Consulta de HCE cronológica multiespecialidad.<br>• Registro de triaje y signos vitales.<br>• Acto médico con diagnóstico CIE-10 y prescripción.<br>• Anulación lógica justificada.<br><br>**M2: Agenda y Citas Médicas**<br>• Matriz de disponibilidad para 12 consultorios.<br>• Agendamiento en 3 pasos con bloqueo anti-solapamiento.<br>• Reprogramación y cancelación justificada.<br>• Notificación asíncrona de recordatorio a 24 h.<br><br>**Servicios Transversales (T1, T2, T3)**<br>• Autenticación JWT y RBAC en backend.<br>• Bitácora inmutable de auditoría (Ley N.° 29733).<br>• Cola transaccional Outbox y worker de despacho. | HU01, HU02, HU03, HU04, HU05, HU06, HU07, HU08 | **35 pts** | **Release 1.0.0-alpha:**<br>API REST FastAPI operativa con 15 endpoints core, base de datos PostgreSQL 16 con restricciones físicas, interfaz web React responsiva (P1, P2 y P3) desplegada en entorno local/staging, suite de pruebas automatizadas con cobertura >= 80 % y pipeline de GitHub Actions en verde. |
| **Sprint 2** | **12 – 14** | **M3: Laboratorio e Imágenes**<br>• Emisión de órdenes médicas diagnósticas.<br>• Carga de informes y custodia de archivos PDF/JPG.<br>• Aviso de disponibilidad de resultados a médico y paciente.<br><br>**M4: Facturación y Convenios**<br>• Tarifarios vigentes (Particular, EPS 1–5, SOAT).<br>• Cálculo de coberturas, deducibles y copago en ventanilla.<br>• Emisión de comprobantes internos de liquidación.<br>• Registro, sustentación y conciliación de glosas.<br><br>**M5: Reportes Gerenciales (BI)**<br>• Dashboard ejecutivo con KPIs consolidados.<br>• Ocupación de los 12 consultorios y tiempos de espera.<br>• Ingresos por convenio y tasa de no-show.<br><br>**M6: Portal del Paciente (Condicional)**<br>• Autoservicio de citas y consulta de órdenes propias. | HU09, HU10, HU11, HU12, HU13, HU14 | **35 pts** | **Release 2.0.0-final:**<br>Sistema web SIRA completamente integrado de extremo a extremo (M1 a M5), almacenamiento seguro de archivos en la nube, módulo de liquidación y glosas probado con casos representativos de aseguradoras, dashboard reactivo (P4), despliegue público en plataforma cloud y manuales de usuario por rol. |
| **Total** | **S9 – S14** | **6 Módulos de Dominio + 3 Componentes Transversales** | **14 HUs** | **70 pts** | **Producto de Software Funcional y Acreditado** |

---

### 8.3. Capacidad del Equipo y Velocidad Estimada

La estimación del esfuerzo y la cadencia de entrega se calibran en función de la capacidad real del **Grupo A**, compuesto por 3 estudiantes de ingeniería de software con dedicación a tiempo parcial en el taller:

* **Parámetros de Capacidad Nominal por Integrante:**
  * Dedicación semanal al proyecto: **15 horas de ingeniería** (distribuidas en 6 h de desarrollo presencial/taller y 9 h de trabajo autónomo en repositorio).
  * Horas de trabajo semanal del equipo: $3 \text{ integrantes} \times 15 \text{ horas/semana} = \mathbf{45 \text{ horas/semana}}$.
  * Duración de cada Sprint: **3 semanas calendario**.
  * **Capacidad total por Sprint:** $45 \text{ horas/semana} \times 3 \text{ semanas} = \mathbf{135 \text{ horas-hombre}}$.

* **Factor de Enfoque y Velocidad Estimada:**
  * Aplicando un factor de productividad técnica del **75 %** (para absorber reuniones de coordinación, revisiones de código, resolución de bloqueos y preparación de evidencias):
    $$\text{Horas efectivas de desarrollo} = 135 \text{ h} \times 0.75 = 101.25 \text{ horas netas por Sprint.}$$
  * Con una estimación promedio de **3.8 horas por punto de historia**, la capacidad proyectada es:
    $$\text{Velocidad del Sprint (Story Points)} = \frac{101.25 \text{ horas}}{3.8 \text{ h/punto}} \approx \mathbf{27 \text{ a } 35 \text{ Story Points por Sprint.}}$$
  * Se fijan **35 puntos de historia para el Sprint 1**, coincidiendo con la descomposición granular de las 8 historias de usuario prioritarias de M1 y M2.

```
+----------------------------------------------------------------------------------------------------+
|                             BALANCE DE CARGA DE TRABAJO — SPRINT 1                                 |
+------------------------------------+--------------------------+---------------------+--------------+
| Integrante (Grupo A)               | Rol Principal de Trabajo | Historias Asignadas | Horas Est.   |
+------------------------------------+--------------------------+---------------------+--------------+
| Inga Champi, Franz Joe             | Backend & Architecture   | HU01, HU04, HU08    | 46 horas     |
| Rashuaman Sapallanay, Ricco Didier | Data & Engine Specialist | HU02, HU06, HU07    | 45 horas     |
| Albino Soto, Christopher Henrry    | Frontend & UX/UI Lead    | HU03, HU05, Soporte | 44 horas     |
+------------------------------------+--------------------------+---------------------+--------------+
| TOTAL EQUIPO GRUPO A               | 3 Desarrolladores        | 8 HUs (35 Puntos)   | 135 horas    |
+------------------------------------+--------------------------+---------------------+--------------+
```

--------------------------------------------------------------------------------

## 9. Sprint Backlog 1 (Semanas 9 a 11)

### 9.1. Tabla Oficial del Sprint Backlog 1

Conforme a la estructura establecida en la sección 9 de la plantilla oficial del Entregable 1, a continuación se detallan las historias de usuario asignadas al Sprint 1 con sus responsables, estimación y estado inicial:

| Historia | Descripción Funcional Resumida | Responsable Principal | Puntos | Prioridad | Estado Inicial |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **HU01** | **Consulta de la HCE unificada:** El médico tratante consulta el expediente cronológico del paciente con atenciones previas, diagnósticos CIE-10, triajes y alergias destacadas en menos de 2 segundos sobre 8 000 registros sintéticos. | Inga Champi, Franz Joe | **8 pts** | Must | Por Iniciar |
| **HU02** | **Agendamiento de citas sin solapamientos:** El personal de admisión agenda una cita médica validando disponibilidad consolidada de médico y consultorio en tiempo real, bloqueando el 100 % de cruces de horarios concurrentes. | Rashuaman Sapallanay, Ricco Didier | **5 pts** | Must | Por Iniciar |
| **HU03** | **Registro y búsqueda del paciente:** Admisión busca al paciente por DNI/CE con autocompletado en < 0.5 s; si no existe, permite su registro inmediato en menos de 30 segundos verificando su convenio asegurador. | Albino Soto, Christopher Henrry | **3 pts** | Must | Por Iniciar |
| **HU04** | **Atención médica con diagnóstico CIE-10 y receta:** El médico tratante registra el acto asistencial con diagnóstico CIE-10 asistido por autocompletado, indicaciones y prescripción farmacológica atómica. | Inga Champi, Franz Joe | **5 pts** | Must | Por Iniciar |
| **HU05** | **Registro de triaje y signos vitales:** La enfermera registra presión arterial, frecuencia cardíaca, temperatura, peso y talla desde la cola de espera, calculando automáticamente el IMC y alertando valores fuera de rango. | Albino Soto, Christopher Henrry | **3 pts** | Must | Por Iniciar |
| **HU06** | **Reprogramación y cancelación de citas:** Admisión reprograma o cancela turnos médicos previa justificación obligatoria del motivo, liberando automáticamente el consultorio y bloque horario. | Rashuaman Sapallanay, Ricco Didier | **3 pts** | Must | Por Iniciar |
| **HU07** | **Recordatorio automático de citas con 24 h de anticipación:** El sistema despacha notificaciones asíncronas vía SMS/correo 24 horas antes de la cita mediante el patrón Outbox para reducir el no-show del 18 %. | Rashuaman Sapallanay, Ricco Didier | **5 pts** | Must | Por Iniciar |
| **HU08** | **Anulación lógica de registro clínico con auditoría:** El médico o auditor anula una atención previa registrando motivo obligatorio (>= 20 caracteres), preservando el registro original e inscribiendo la traza en bitácora. | Inga Champi, Franz Joe | **3 pts** | Must | Por Iniciar |
| **TOTAL** | **Alcance Completo de M1 y M2 (Sprint 1)** | **Grupo A (3 Integrantes)** | **35 pts** | — | **0 / 35 pts** |

---

### 9.2. Desglose Detallado de Tareas Técnicas por Historia de Usuario

Para asegurar la ejecución metódica y el seguimiento diario en el tablero ágil de GitHub Projects, cada historia de usuario se descompone en tareas de ingeniería de software con estimación en horas:

#### HU01 — Consulta de la HCE Unificada (8 Story Points)
* **Criterios de Aceptación:** Dado un paciente con consultas registradas en más de una especialidad, cuando el médico tratante busca y abre su expediente, el sistema muestra todas las entradas ordenadas cronológicamente en menos de 2 segundos (RNF-001) y registra el acceso en la bitácora de auditoría (RNF-002, Ley N.° 29733). Si un usuario sin rol clínico intenta abrir el expediente, el sistema responde con error 403 Forbidden y registra el intento no autorizado.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU01-01` | Diseñar e implementar el endpoint `GET /api/v1/pacientes/{id}/hce` con paginación de 10 en 10 y filtros por fecha y especialidad. | Backend (M1) | Inga Champi, Franz | 5 h | Pruebas de integración con pytest responden HTTP 200 con payload JSON estructurado. |
| `T-HU01-02` | Crear índice B-Tree compuesto `idx_atenciones_paciente_fecha` en PostgreSQL y optimizar la consulta ORM con SQLAlchemy 2. | Base de Datos | Rashuaman, Ricco | 3 h | Plan de ejecución `EXPLAIN ANALYZE` muestra Index Scan en < 50 ms sobre 8 000 registros. |
| `T-HU01-03` | Implementar middleware de seguridad RBAC que valide rol de 'Médico' o 'Enfermera' y capture IP, usuario y timestamp. | Backend (T1/T2) | Inga Champi, Franz | 4 h | Petición con token de rol 'Caja' o 'Admisión' es rechazada con HTTP 403 y evento en bitácora. |
| `T-HU01-04` | Construir componente frontend de línea de tiempo cronológica (P1) con React, Tailwind y badges de especialidad. | Frontend (M1) | Albino Soto, Christopher | 6 h | La interfaz renderiza tarjetas de atención colapsables y paginación reactiva sin refresco. |
| `T-HU01-05` | Implementar banner de advertencia visual permanente de alergias (`#DC2626`) en la cabecera del expediente clínico. | Frontend (M1) | Albino Soto, Christopher | 3 h | Alergias registradas se muestran en rojo de forma perenne ante cualquier scroll de la pantalla. |
| `T-HU01-06` | Elaborar script de pruebas de carga con JMeter para simular 40 consultas concurrentes sobre 8 000 pacientes. | QA / Pruebas | Inga Champi, Franz | 4 h | Reporte de JMeter confirma tiempo de respuesta en percentil 95 $\le 1.85$ segundos. |
| **Subtotal** | **Tareas de Ingeniería HU01** | — | — | **25 h** | — |

---

#### HU02 — Agendamiento de Citas con Bloqueo de Solapamientos (5 Story Points)
* **Criterios de Aceptación:** Dado un paciente identificado, cuando el operador de admisión selecciona especialidad, médico, consultorio físico y bloque horario, el sistema valida que no exista solapamiento en tiempo real; si está libre, confirma la cita en menos de 45 segundos (RNF-005) y encola el evento outbox; si el bloque fue tomado concurrentemente, responde HTTP 409 Conflicto y solicita elegir otro turno.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU02-01` | Implementar endpoint `GET /api/v1/citas/disponibilidad` que retorne slots de 30 min filtrados por médico, fecha y consultorio. | Backend (M2) | Rashuaman, Ricco | 4 h | Retorna lista de bloques con banderas booleanas `disponible: true/false`. |
| `T-HU02-02` | Implementar endpoint transaccional `POST /api/v1/citas` que inserte la cita y el evento outbox bajo la misma transacción ACID. | Backend (M2) | Rashuaman, Ricco | 5 h | Si falla la inserción de outbox, la cita hace rollback automático sin inconsistencias. |
| `T-HU02-03` | Validar restricción física `btree_gist` en PostgreSQL (`no_solapamiento_medico` y `no_solapamiento_consultorio`). | Base de Datos | Rashuaman, Ricco | 3 h | Script `03-verificacion.sql` arroja violación de exclusión ante inserts superpuestos. |
| `T-HU02-04` | Construir interfaz de cuadrícula horaria en 3 pasos (P2) con selector de médico y botones visuales verde/gris. | Frontend (M2) | Albino Soto, Christopher | 6 h | Stepper funcional: (1) Paciente -> (2) Turno -> (3) Confirmación, cumpliendo RNF-005. |
| `T-HU02-05` | Programar pruebas de concurrencia simulada con scripts en paralelo intentando reservar el mismo cupo médico. | QA / Pruebas | Inga Champi, Franz | 3 h | De dos peticiones simultáneas idénticas, exactamente una responde 201 y la otra 409. |
| **Subtotal** | **Tareas de Ingeniería HU02** | — | — | **21 h** | — |

---

#### HU03 — Registro y Búsqueda del Paciente (3 Story Points)
* **Criterios de Aceptación:** Dado un operador en recepción, cuando ingresa el número de DNI o Carné de Extranjería, el sistema busca en la base de datos indexada en menos de 0.5 s; si no existe, permite registrar los datos mínimos (nombres, apellidos, fecha nacimiento, teléfono, correo y convenio asegurador) validando unicidad de documento.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU03-01` | Desarrollar endpoints `GET /api/v1/pacientes` (búsqueda reactiva) y `POST /api/v1/pacientes` con validadores Pydantic. | Backend (M1) | Inga Champi, Franz | 3 h | Validación de formato de DNI (8 dígitos numéricos) y rechazo de duplicados (HTTP 409). |
| `T-HU03-02` | Construir modal reactivo de captura rápida de paciente en el Paso 1 de agendamiento (P2). | Frontend (M1/M2) | Albino Soto, Christopher | 4 h | Operador registra paciente en < 30 s sin perder el contexto del flujo de cita. |
| `T-HU03-03` | Implementar pruebas unitarias de validación de datos de filiación y unicidad en base de datos. | QA / Pruebas | Albino Soto, Christopher | 2 h | Suite de pruebas pytest cubre inserción correcta y captura de constraint `uq_paciente_documento`. |
| **Subtotal** | **Tareas de Ingeniería HU03** | — | — | **9 h** | — |

---

#### HU04 — Atención Médica con Diagnóstico CIE-10 y Prescripción (5 Story Points)
* **Criterios de Aceptación:** Dado un paciente en consultorio con triaje realizado, cuando el médico tratante ingresa motivo, examen clínico, selecciona diagnósticos CIE-10 y redacta medicamentos en la receta digital, el sistema persiste la atención en estado 'FINALIZADA', asociando las prescripciones de forma atómica y registrando la firma en bitácora.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU04-01` | Desarrollar endpoints `GET /api/v1/diagnosticos-cie10` (autocompletado predictivo) y `POST /api/v1/atenciones`. | Backend (M1) | Inga Champi, Franz | 5 h | Búsqueda por subcadena retorna códigos oficiales CIE-10 en < 100 ms. |
| `T-HU04-02` | Implementar lógica de persistencia relacional en tablas `atenciones`, `atencion_diagnosticos` y `prescripciones`. | Backend (M1) | Inga Champi, Franz | 4 h | Inserción en cascada transaccional garantiza que no existan recetas huérfanas. |
| `T-HU04-03` | Construir formulario médico ergonómico en React (P1): buscador CIE-10 con chips y tabla dinámica de recetas. | Frontend (M1) | Albino Soto, Christopher | 6 h | Médico agrega fármacos dinámicamente especificando dosis, vía, frecuencia y días. |
| `T-HU04-04` | Pruebas automatizadas de regla de negocio: exactamente un diagnóstico marcado como 'PRINCIPAL'. | QA / Pruebas | Inga Champi, Franz | 3 h | Base de datos y API rechazan atenciones con 0 o más de 1 diagnóstico principal. |
| **Subtotal** | **Tareas de Ingeniería HU04** | — | — | **18 h** | — |

---

#### HU05 — Registro de Triaje y Signos Vitales (3 Story Points)
* **Criterios de Aceptación:** Dado un paciente en sala de espera con ticket emitido, cuando la enfermera captura presión arterial, frecuencia cardíaca, temperatura, frecuencia respiratoria, saturación, peso y talla, el sistema calcula automáticamente el IMC, valida rangos biológicos coherentes (sistólica > diastólica) y habilita los datos en la HCE del médico.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU05-01` | Desarrollar endpoints `POST /api/v1/triajes` y `POST /api/v1/citas/{id}/check-in` con validaciones de rango. | Backend (M1/M2) | Inga Champi, Franz | 3 h | Rechazo con HTTP 422 si sistólica <= diastólica o temperatura < 30 °C. |
| `T-HU05-02` | Construir pantalla de toma de triaje ergonómica (P3) con calculadora automática de IMC en tiempo real. | Frontend (M1) | Albino Soto, Christopher | 5 h | Al ingresar peso (75 kg) y talla (1.70 m), muestra badge amarillo: "IMC: 25.95 (Sobrepeso leve)". |
| `T-HU05-03` | Pruebas de integración: vinculación 1 a 1 entre registro de triaje y atención médica del día. | QA / Pruebas | Albino Soto, Christopher | 2 h | El médico visualiza el widget de triaje en modo solo lectura al abrir la consulta médica. |
| **Subtotal** | **Tareas de Ingeniería HU05** | — | — | **10 h** | — |

---

#### HU06 — Reprogramación y Cancelación de Citas Médicas (3 Story Points)
* **Criterios de Aceptación:** Dado una cita médica confirmada o programada, cuando admisión solicita reprogramar o cancelar, el sistema exige un motivo de texto obligatorio (>= 10 caracteres), actualiza el estado, libera de inmediato el bloque de horario y consultorio, y encola la notificación correspondiente en el outbox.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU06-01` | Desarrollar endpoints `POST /api/v1/citas/{id}/reprogramar` y `POST /api/v1/citas/{id}/cancelar`. | Backend (M2) | Rashuaman, Ricco | 4 h | La reprogramación enlaza `id_cita_origen` y libera el slot anterior en una sola transacción. |
| `T-HU06-02` | Implementar modal de confirmación con campo obligatorio de motivo y alerta de liberación de consultorio. | Frontend (M2) | Albino Soto, Christopher | 4 h | Botón confirmar deshabilitado si el motivo tiene menos de 10 caracteres. |
| `T-HU06-03` | Pruebas unitarias de liberación de restricciones temporales en la agenda tras cancelación. | QA / Pruebas | Rashuaman, Ricco | 2 h | Slot horario cancelado vuelve a figurar como libre en `GET /citas/disponibilidad`. |
| **Subtotal** | **Tareas de Ingeniería HU06** | — | — | **10 h** | — |

---

#### HU07 — Recordatorio Automático de Citas con 24 h de Anticipación (5 Story Points)
* **Criterios de Aceptación:** Dado un lote de citas programadas para el día siguiente, cuando el worker asíncrono ejecuta su ciclo periódico, identifica los eventos pendientes en `outbox_notificaciones` cuya fecha programada sea menor o igual a la hora actual, despacha el mensaje mediante el adaptador de correo/SMS simulado, actualiza el estado a 'ENVIADO' con timestamp o registra reintentos ante fallos.
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU07-01` | Diseñar e implementar el componente `NotificationService` con método `encolar()` bajo patrón Outbox. | Backend (T3) | Rashuaman, Ricco | 4 h | Inserción en `outbox_notificaciones` comparte la sesión transaccional de la cita. |
| `T-HU07-02` | Construir el proceso en segundo plano (Worker/Scheduler con APScheduler/Asyncio) con ciclo de 60 s. | Backend (T3) | Rashuaman, Ricco | 6 h | Worker consulta registros `PENDIENTE`, ejecuta despacho y actualiza estados de forma aislada. |
| `T-HU07-03` | Implementar adaptador desacoplado de mensajería (Email / SMS Mock) con registro de logs y reintentos (max 3). | Integración (T3) | Rashuaman, Ricco | 4 h | Si el gateway simula timeout, incrementa contador `intentos` y pasa a estado `REINTENTO`. |
| `T-HU07-04` | Pruebas de integración del ciclo de vida de notificación desde la reserva hasta el envío confirmado. | QA / Pruebas | Rashuaman, Ricco | 4 h | Verificación en PostgreSQL: registro cambia a 'ENVIADO' con `procesado_en` no nulo. |
| **Subtotal** | **Tareas de Ingeniería HU07** | — | — | **18 h** | — |

---

#### HU08 — Anulación Lógica de Registro Clínico con Auditoría (3 Story Points)
* **Criterios de Aceptación:** Dado una atención médica registrada erróneamente, cuando un usuario con rol de Médico Auditor solicita la anulación, el sistema exige un motivo de al menos 20 caracteres, actualiza `anulado = TRUE` sin ejecutar borrado físico (`DELETE`), persiste el motivo y usuario responsable, y genera una entrada obligatoria en `bitacora_auditoria` (RNF-002, RNF-004).
* **Desglose de Tareas de Ingeniería:**

| Código Tarea | Descripción Técnica de la Tarea | Capa / Módulo | Responsable | Estimación | Criterio de Verificación |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `T-HU08-01` | Desarrollar endpoint `POST /api/v1/atenciones/{id}/anular` con validación de rol 'Médico Auditor' o 'Gerencia'. | Backend (M1) | Inga Champi, Franz | 3 h | Petición de usuario asistencial estándar es rechazada con HTTP 403 Forbidden. |
| `T-HU08-02` | Implementar trigger PostgreSQL `trg_impedir_borrado_atencion` que arroje excepción ante sentencias `DELETE`. | Base de Datos | Rashuaman, Ricco | 2 h | Ejecución de `DELETE FROM atenciones` es abortada con error SQL: "Prohibido el borrado físico". |
| `T-HU08-03` | Construir modal de anulación en UI médica (P1) con conteo de caracteres en tiempo real (mínimo 20). | Frontend (M1) | Albino Soto, Christopher | 3 h | Botón de anulación bloqueado hasta alcanzar los 20 caracteres requeridos por rúbrica. |
| `T-HU08-04` | Pruebas de integración de auditoría: verificar creación de registro en tabla `bitacora_auditoria`. | QA / Pruebas | Inga Champi, Franz | 2 h | Verificación de inserción con `accion = 'ANULAR'`, snapshot JSON anterior y motivo registrado. |
| **Subtotal** | **Tareas de Ingeniería HU08** | — | — | **10 h** | — |

---

### 9.3. Consolidado de Esfuerzo del Sprint 1

$$\text{Total Horas Planificadas del Sprint 1} = 25 + 21 + 9 + 18 + 10 + 10 + 18 + 10 = \mathbf{121 \text{ horas de ingeniería.}}$$

* **Margen de Contingencia Operativa:** $135 \text{ h (Capacidad)} - 121 \text{ h (Estimadas)} = \mathbf{14 \text{ horas (10.4 \%)}}$ reservadas para resolución de bugs, preparación de la suite de pruebas del Avance 5 y ajustes post-revisión docente.

--------------------------------------------------------------------------------

## 9.1. Definición de Hecho (Definition of Done — DoD)

Para asegurar que cada historia de usuario completada constituya un incremento de software con calidad de producción, el **Grupo A** establece formalmente los siguientes **ocho (08) criterios obligatorios de la Definición de Hecho (DoD)**, los cuales deben cumplirse en su totalidad antes de considerar una historia como `DONE`:

```
+----------------------------------------------------------------------------------------------------+
|                         CHECKLIST DE LA DEFINICIÓN DE HECHO (DoD) — SIRA                           |
+----+------------------------------------+----------------------------------------------------------+
| N° | Criterio de Calidad de Ingeniería  | Mecanismo de Verificación y Evidencia Objetiva           |
+----+------------------------------------+----------------------------------------------------------+
| 01 | Criterios de Aceptación Gherkin    | 100 % de escenarios Dado/Cuando/Entonces aprobados.      |
| 02 | Estándares de Código y Linters     | Flake8 (Python) y ESLint (React) con 0 errores.          |
| 03 | Cobertura de Pruebas Unitarias     | Cobertura >= 80 % en lógica de dominio con pytest.       |
| 04 | Integridad de Base de Datos        | Migración Alembic ejecutada y constraints verificadas.   |
| 05 | Seguridad y Ley N.° 29733          | Middleware RBAC activo y auditoría registrada.           |
| 06 | Usabilidad y Accesibilidad         | Tareas operativas en <= 3 pasos y responsive.            |
| 07 | Revisión por Pares (Code Review)   | Pull Request aprobado por al menos 1 compañero de equipo.|
| 08 | Integración Continua (CI Pipeline) | Workflow de GitHub Actions ejecutado en verde.           |
+----+------------------------------------+----------------------------------------------------------+
```

### Detalle de los Criterios de la Definición de Hecho (DoD):

1. **Criterios de Aceptación Funcionales Cumplidos al 100 %:**
   * Todos los escenarios de prueba formulados bajo sintaxis Gherkin (`Dado / Cuando / Entonces`) en la especificación de requerimientos (ERS) fueron ejecutados y validados satisfactoriamente con datos de prueba sintéticos del caso.

2. **Estándares de Codificación Limpia y Análisis Estático:**
   * El código backend en Python cumple rigurosamente con el estándar **PEP 8**, verificado mediante `flake8` sin advertencias de estilo ni variables no utilizadas.
   * El código frontend en React + TypeScript compila sin errores (`tsc --noEmit`) y pasa el linter `eslint` con cero errores críticos.
   * Los nombres de variables, funciones, clases y esquemas siguen la convención acordada en la arquitectura (`snake_case` para backend/BD y `camelCase` para frontend).

3. **Pruebas Automatizadas y Cobertura de Código:**
   * Cada historia de usuario cuenta con sus respectivas pruebas unitarias y de integración desarrolladas con `pytest` para backend y `vitest` / `react-testing-library` para frontend.
   * La cobertura global de código de las capas de aplicación y dominio alcanza como mínimo el **80 %** de sentencias (`pytest --cov=app --cov-report=term-missing`).
   * No se aceptan pruebas con aserciones triviales o que ignoren excepciones intencionalmente.

4. **Persistencia e Integridad Relacional Verificada:**
   * Toda modificación en el esquema de base de datos se implementa mediante un script de migración versionado con **Alembic** (`alembic upgrade head`), garantizando reproducibilidad en cualquier entorno.
   * Se verifica que ninguna operación asistencial ejecute borrado físico (`DELETE`); las restricciones de exclusión temporal (`btree_gist`) y triggers de auditoría se encuentran activos y probados.

5. **Seguridad, Control de Acceso y Cumplimiento Normativo (Ley N.° 29733):**
   * Cada endpoint expuesto valida obligatoriamente la presencia y vigencia del token JWT y el rol del usuario mediante las dependencias de inyección de FastAPI (`get_current_user`, `require_role`).
   * Toda consulta, modificación o anulación sobre la HCE genera una traza automática e inmutable en `bitacora_auditoria` con usuario, IP, fecha/hora y motivo.
   * Las contraseñas se almacenan exclusivamente como hashes no reversibles mediante algoritmo `bcrypt` con salting aleatorio.

6. **Usabilidad, Diseño Ergonómico y Rendimiento Percibido:**
   * La interfaz implementada respeta estrictamente los wireframes de alta fidelidad y el Design System de SIRA (paleta clínica, fuentes Inter/Roboto y estados de componentes).
   * El flujo de agendamiento de citas en recepción se completa en un máximo de **3 pasos de pantalla** (RNF-005) y en menos de 3 minutos medidos cronométricamente.
   * La consulta y renderizado del expediente clínico se completa en un tiempo inferior a **2 segundos** sobre la base sintética de 8 000 pacientes (RNF-001).

7. **Control de Versiones y Revisión Cruzada por Pares (Pull Request):**
   * El código fue desarrollado en una rama de feature independiente siguiendo la convención: `feature/HUxx-descripcion-corta`.
   * Para fusionar la rama a `develop`, se crea un Pull Request (PR) con descripción de cambios, capturas de pantalla de la funcionalidad y lista de pruebas ejecutadas.
   * El PR requiere la aprobación obligatoria (`Approve`) de al menos un integrante del equipo distinto al autor, tras verificar que cumple los estándares técnicos.

8. **Integración Continua Automatizada (CI en Verde):**
   * El workflow de GitHub Actions (`.github/workflows/ci.yml`) se ejecutó de forma automatizada sobre el Pull Request, completando exitosamente las tres fases de validación:
     1. Fase 1: Linting y verificación de formato (`flake8`, `eslint`).
     2. Fase 2: Ejecución de la suite completa de pruebas unitarias (`pytest`).
     3. Fase 3: Compilación y build exitoso del paquete web (`npm run build`).

--------------------------------------------------------------------------------

## 10. Guion de Sustentación del Entregable 1 (15 Minutos — Examen Parcial)

Conforme a lo estipulado en la sección 10 de la plantilla oficial del Entregable 1 y la Rúbrica de Sustentación de la Semana 8, se establece la distribución formal de tiempos, responsables y contenido técnico para la defensa oral del proyecto:

| Tiempo | Bloque Temático y Secciones de la Plantilla | Quién Expone (Grupo A) | Diapositivas / Artefactos a Proyectar | Mensajes Clave de Ingeniería y Defensa Técnica |
| :---: | :--- | :--- | :--- | :--- |
| **2 min** | **Problema Empresarial y Visión de la Solución**<br>• Secciones 1 y 2 de la plantilla.<br>• Justificación y Objetivos SMART.<br>• Declaración de Visión y Stakeholders. | **Albino Soto, Christopher Henrry** | • Diapositiva de Contexto: Clínica San Rafael.<br>• Matriz de 5 Perjuicios Históricos.<br>• Objetivos SMART cuantitativos (OBJ-01 a OBJ-04). | • Demostrar que el problema no es solo 'falta de software', sino fragmentación clínica y riesgo en vidas humanas (alergias no visibles).<br>• Enfatizar que se atiende la sede San Borja (12 consultorios, 8 000 pacientes de prueba) con un enfoque realista y viable. |
| **4 min** | **Ingeniería de Requisitos, Backlog y Modelos UML**<br>• Secciones 3 y 4 de la plantilla.<br>• Catálogo IEEE 29148 y RNF verificables.<br>• Casos de Uso, Clases y Actividades. | **Inga Champi, Franz Joe** | • Matriz de Requisitos RF/RNF (IEEE 29148).<br>• Product Backlog Priorizado (70 pts).<br>• Diagrama de Casos de Uso del Sistema.<br>• Diagrama de Clases (Dominio en 3FN). | • Sustentar la verificabilidad de RNF-001 (< 2 s en HCE) y RNF-002 (RBAC + Ley 29733 con no borrado físico).<br>• Demostrar cómo el backlog se descompuso en 8 historias INVEST para el Sprint 1.<br>• Explicar la relación `0..1` entre Cita y Atención que soporta el tópico de urgencias sin cita previa. |
| **6 min** | **Arquitectura de Software, Base de Datos y Prototipo UX/UI**<br>• Secciones 5, 6 y 7 de la plantilla.<br>• SAD (Vistas 4+1 y 5 ADRs).<br>• MER en 3FN, DDL y Triggers.<br>• Demostración del Prototipo Navegable. | **Rashuaman Sapallanay, Ricco Didier** | • Diagrama de Componentes (Monolito Modular).<br>• Diagrama de Despliegue Cloud seguro.<br>• Diagrama ER (Notación Crow's Foot en 3FN).<br>• Navegación en vivo en Figma Make (P1 a P4). | • Justificar ADR-01 (Monolito Modular en capas) frente a microservicios: ideal para equipo de 3 y transacciones ACID.<br>• Explicar la restricción física `btree_gist` para erradicar solapamientos (RF-002).<br>• Demostrar en vivo que el agendamiento toma 40.6 segundos en 3 pasos (cumpliendo sobradamente la meta de < 3 min de RNF-005). |
| **3 min** | **Plan de Release, Sprint Backlog 1 y Rueda de Preguntas**<br>• Secciones 8, 9 y 9.1 de la plantilla.<br>• Capacidad del equipo y velocidad.<br>• Definición de Hecho (DoD).<br>• Defensa ante el Jurado / Docente. | **Todo el Equipo**<br>(Modera: Franz Inga;<br>Apoyan: Christopher Albino y Ricco Rashuaman) | • Tabla del Sprint Backlog 1 (35 pts).<br>• Matriz de la Definición de Hecho (DoD).<br>• Repositorio GitHub y Tablero de Proyectos. | • Exponer el balance de carga: 121 h estimadas frente a 135 h de capacidad nominal (10.4 % de reserva técnica).<br>• Demostrar dominio individual cruzado: cualquier integrante está capacitado para defender diseño, datos o frontend ante las preguntas del docente. |

---

### 10.1. Guion Detallado Minuto a Minuto para la Exposición

#### Bloque 1 (Minutos 00:00 a 02:00) — Problema y Visión
* **Expositor:** Albino Soto, Christopher Henrry.
* **Guion Verbal Sugerido:**  
  * *"Buenos días, profesor y compañeros. Como Grupo A, presentamos la documentación de ingeniería del proyecto SIRA para la Clínica San Rafael S.A.C., sede San Borja.*  
  * *La clínica experimentó un crecimiento asistencial acelerado, pasando de una consulta básica a una oferta multiespecialidad con 12 consultorios y tópico de urgencias. Sin embargo, conservó una gestión manual y fragmentada que genera cinco problemas críticos: historias clínicas en papel y Excel que provocaron errores de medicación por desconocer alergias; una agenda telefónica con hasta 20 minutos de espera y 18 % de inasistencia; demoras de hasta 48 horas en entrega de resultados; continuas glosas con 5 EPS por errores de tarifario; y ceguera gerencial por falta de indicadores.*  
  * *Para resolver esto, concebimos SIRA: una plataforma web integrada que unifica el expediente clínico bajo la Ley N.° 29733, automatiza el agendamiento sin solapamientos en 3 pasos y liquida copagos con exactitud. Nuestros cuatro objetivos SMART establecen metas numéricas rigurosas: apertura del expediente en menos de 2 segundos sobre 8 000 pacientes, bloqueo del 100 % de cruces de citas y reducción del ausentismo mediante recordatorios a 24 horas."*

#### Bloque 2 (Minutos 02:00 a 06:00) — Requerimientos, Backlog y Modelos UML
* **Expositor:** Inga Champi, Franz Joe.
* **Guion Verbal Sugerido:**  
  * *"Continuando con la ingeniería de requisitos, bajo el estándar IEEE 29148 especificamos 8 requerimientos funcionales y 5 requerimientos no funcionales de alta exigencia. Resalto el RNF-002, que exige control de acceso por roles y bitácora inmutable; el RNF-004, que prohíbe de forma absoluta el borrado físico de información de salud; y el RNF-005, que limita el agendamiento a un máximo de 3 pasos.*  
  * *Estructuramos un Product Backlog de 70 puntos de historia en 14 historias INVEST. Para el Sprint 1 priorizamos 8 historias imprescindibles de los módulos M1 y M2 que suman exactamente 35 puntos.*  
  * *En el modelado UML, nuestro diagrama de casos de uso refleja 16 casos de uso interactuando con 7 actores del dominio, vinculando auditoría mediante relaciones «include» y el portal condicional M6 mediante «extend». En el diagrama de clases, modelamos 14 entidades normalizadas. Una decisión clave fue la relación entre Cita y Atención con multiplicidad 0..1 a 1: esto permite que una consulta externa provenga de una cita previa, mientras que una urgencia en el tópico se registre de inmediato sin cita, garantizando la continuidad asistencial requerida por la dirección médica."*

#### Bloque 3 (Minutos 06:00 a 12:00) — Arquitectura, Base de Datos y Prototipos UX/UI
* **Expositor:** Rashuaman Sapallanay, Ricco Didier.
* **Guion Verbal Sugerido:**  
  * *"En la arquitectura del sistema, sustentamos mediante el ADR-01 la elección de un Monolito Modular en capas con API REST sobre FastAPI y React. Descartamos microservicios porque para una sola sede y un equipo de tres ingenieros, añadir consistencia distribuida y latencia de red ponía en riesgo la entrega sin aportar valor real. El monolito modular nos permite aislar módulos de dominio en paquetes limpios y garantizar transacciones ACID.*  
  * *En la persistencia, diseñamos un esquema relacional de 22 tablas en Tercera Forma Normal sobre PostgreSQL 16. Implementamos la extensión btree_gist con restricciones de exclusión física: si dos operadores intentan agendar al mismo médico o al mismo consultorio en horarios superpuestos, la propia base de datos rechaza la segunda transacción con error de exclusión, garantizando 0 % de solapamientos a nivel de motor. Para satisfacer el RNF-001 de apertura en menos de 2 segundos, creamos el índice parcial compuesto sobre atenciones válidas.*  
  * *En el prototipo UX/UI, navegable en Figma Make a partir de componentes generados con Google Stitch, diseñamos las cuatro pantallas maestras. En la Pantalla 2 de agendamiento, cumplimos estrictamente el límite de 3 pasos: (1) búsqueda reactiva de paciente, (2) selección en la matriz horaria verde/gris y (3) confirmación con cálculo automático de copago de la aseguradora. En las pruebas de usabilidad cronometradas, un operador completó la reserva en solo 40.6 segundos, superando con creces la meta de 3 minutos. En la Pantalla 1 del médico, el banner de alergias en color rojo carmesí #DC2626 previene activamente errores de medicación al momento de prescribir."*

#### Bloque 4 (Minutos 12:00 a 15:00) — Planificación Ágil y Cierre
* **Expositores:** Todo el Equipo (Grupo A).
* **Guion Verbal Sugerido:**  
  * *(Franz Inga)*: *"Para la fase de construcción, nuestro Plan de Release contempla dos sprints de 3 semanas. El Sprint 1 cuenta con 121 horas de ingeniería estimadas frente a una capacidad nominal de 135 horas, dejándonos un margen de contingencia del 10.4 % para absorber cualquier incidencia técnica.*  
  * *(Christopher Albino)*: *Establecimos una Definición de Hecho (DoD) rigurosa de 8 criterios: ninguna historia pasa a Done sin criterios Gherkin aprobados, linters en cero errores, cobertura de pruebas unitarias mayor al 80 %, revisión por pares obligatoria y pipeline de GitHub Actions en verde.*  
  * *(Ricco Rashuaman)*: *Con esta sólida base de ingeniería documental y técnica, el Grupo A concluye la presentación del Entregable 1 y quedamos a su entera disposición para responder las preguntas del jurado. Muchas gracias."*

---

### 10.2. Banco de Preguntas Técnicas Previstas y Respuestas de Defensa

| N° | Pregunta Probable del Docente / Jurado | Integrante que Responde | Argumentación Técnica Sólida y Evidencia en Documentos |
| :---: | :--- | :---: | :--- |
| **P1** | *¿Por qué eligieron un Monolito Modular en lugar de una arquitectura de Microservicios si la clínica tiene múltiples áreas?* | **Inga Champi, Franz** | *Optamos por el Monolito Modular (ADR-01) evaluando la ley de Conway, la capacidad del equipo (3 integrantes) y el alcance acotado a una sola sede física. Los microservicios introducen sobrecarga de observabilidad, consistencia eventual y orquestación de red que hubieran dilatado el desarrollo de los módulos core. El monolito modular nos brinda límites lógicos estrictos por paquetes, despliegue unificado y transacciones ACID nativas para citas y facturación, con la ventaja de que si a futuro la clínica abre más sedes, los módulos ya están desacoplados para migrar a servicios independientes.* |
| **P2** | *¿Cómo garantizan físicamente que dos recepcionistas no asignen la misma cita al mismo médico en el mismo segundo?* | **Rashuaman, Ricco** | *No confiamos únicamente en la validación del frontend o de la API. En PostgreSQL 16 implementamos la extensión `btree_gist` con la restricción de exclusión física `CONSTRAINT no_solapamiento_medico EXCLUDE USING gist (id_medico WITH =, tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&)`. A nivel de motor relacional es físicamente imposible insertar dos intervalos superpuestos para el mismo médico. En nuestra suite `03-verificacion.sql` ejecutada en pgAdmin 4, la prueba 1 demostró el rechazo automático de la concurrencia.* |
| **P3** | *¿Cómo se garantiza el cumplimiento de la Ley N.° 29733 de Protección de Datos Personales respecto al no borrado físico?* | **Inga Champi, Franz** | *El RNF-004 prohíbe el comando SQL `DELETE`. Implementamos dos salvaguardas: en la capa de datos, creamos el trigger `trg_impedir_borrado_atencion` que aborta cualquier intento de supresión física; en la capa de dominio, expusimos la operación `POST /atenciones/{id}/anular` que exige un motivo formal de al menos 20 caracteres y registra `anulado = TRUE`. Además, el componente transversal T2 inscribe el acceso en `bitacora_auditoria` con usuario, IP, timestamp y snapshot JSON.* |
| **P4** | *¿Cómo lograron que el agendamiento cumpla la regla de los 3 pasos de pantalla (RNF-005)?* | **Albino Soto, Christopher** | *En la Pantalla 2 diseñamos un wizard guiado en 3 etapas visuales: en el Paso 1 se ingresa el DNI y el sistema recupera la filiación y el convenio en < 0.5 s; en el Paso 2 se selecciona la especialidad y el médico sobre la cuadrícula verde/gris de turnos de 30 min; y en el Paso 3, un panel lateral flotante muestra el resumen de cita, el cálculo automático de copago y el switch de recordatorio SMS. En las pruebas empíricas registradas en el informe, un usuario completó el flujo en 40.6 segundos, cumpliendo holgadamente el límite de 3 minutos.* |
| **P5** | *¿Qué pasa si el servicio externo de envío de SMS o correo se cae o tiene latencia? ¿Se traba la reserva de citas?* | **Rashuaman, Ricco** | *No, gracias al patrón Outbox (ADR-04 y componente T3). La creación de la cita guarda el registro en la tabla `citas` y el mensaje pendiente en `outbox_notificaciones` dentro de la misma transacción local de base de datos en milisegundos. Un worker asíncrono desacoplado lee los pendientes cada 60 segundos y despacha los recordatorios a 24 horas. Si el proveedor externo falla, se registran los reintentos sin afectar la experiencia del recepcionista ni bloquear la cita.* |

--------------------------------------------------------------------------------

## 11. Checklist de Calidad del Plan de Release y Sprint Backlog (Rúbrica Semana 7)

| Criterio de Evaluación de la Rúbrica | Estado | Justificación y Evidencia en este Documento |
| :--- | :---: | :--- |
| **Plan de Release Realista y Estructurado** | **Cumple (Logrado)** | Desglose formal de dos sprints alineados a los módulos M1-M2 (Sprint 1) y M3-M5 (Sprint 2), con 35 puntos de historia cada uno. |
| **Capacidad y Velocidad Justificadas** | **Cumple (Logrado)** | Estimación cuantitativa de 135 horas nominales y 121 horas asignadas (10.4 % de contingencia) para 3 desarrolladores. |
| **Sprint Backlog 1 Estimado y Asignado** | **Cumple (Logrado)** | 8 Historias de Usuario con desglose de 27 tareas de ingeniería de software, estimación horaria y responsable asignado. |
| **Definición de Hecho (DoD) Completa y Verificable** | **Cumple (Logrado)** | 8 Criterios rigurosos que abarcan pruebas unitarias (>= 80 %), linters, base de datos en 3FN, seguridad RBAC, CI y Pull Requests. |
| **Guion de Sustentación Calibrado a 15 Minutos** | **Cumple (Logrado)** | Estructura minuto a minuto para el Examen Parcial, distribución equilibrada entre los 3 integrantes y banco de preguntas de defensa. |
| **Alineamiento y Trazabilidad al 100 %** | **Cumple (Logrado)** | Coherencia total con los documentos 01 al 07 y con la plantilla oficial `Entregable1_PLANTILLA_Caso_Clinica_SW705.docx`. |
