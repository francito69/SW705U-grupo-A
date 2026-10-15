# 5. Documento de Arquitectura de Software (SAD) — Sistema SIRA

--------------------------------------------------------------------------------

### Contexto y Metodología de Diseño Arquitectónico (Semanas 5 y 6)

El presente documento constituye la especificación formal del **Documento de Arquitectura de Software (Software Architecture Document - SAD)** para el **Sistema de Información Clínico-Administrativo (SIRA)** de la **Clínica San Rafael S.A.C. (Sede San Borja)**, desarrollado en el marco del curso Taller de Ingeniería de Software I (SW705) de la Universidad Nacional de Ingeniería (UNI).

La arquitectura define la estructura fundamental del sistema, sus componentes de software, interfaces externas e internas, patrones de diseño y decisiones técnicas de diseño (ADRs). Su objetivo central es garantizar de manera verificable el cumplimiento estricto de los **Requerimientos Funcionales (RF-001 a RF-008)** y los **Atributos de Calidad / Requerimientos No Funcionales (RNF-001 a RNF-005)** establecidos en la Especificación de Requerimientos (`03-especificacion-requerimientos-ERS.md`), integrando lo entregado y sustentado en el avance calificado de la Semana 6 (`semana6.entregable-4-taller.pdf`).

--------------------------------------------------------------------------------

## 5.1. Estilo Arquitectónico y Diseño de Componentes

### 5.1.1. Justificación del Estilo Seleccionado
Se selecciona y justifica formalmente una **arquitectura web cliente-servidor basada en un Monolito Modular en Capas con API REST desacoplada**:
* **Frontend Web:** Aplicación de Página Única (SPA) adaptativa y reactiva desarrollada con **React 18 + TypeScript + Vite**, optimizada para terminales de admisión y consultorios médicos.
* **Backend Monolítico Modular:** Servidor único en **Python 3.12+ con FastAPI**, estructurado internamente en paquetes desacoplados por módulo de dominio (`app/modules/`), con capa de aplicación compartida (`app/api/v1/`) y componentes transversales de infraestructura.
* **Persistencia Relacional Centralizada:** Base de datos **PostgreSQL 16** con integridad referencial nativa, restricciones de exclusión temporal (`btree_gist`) y almacenamiento seguro de objetos para resultados digitalizados (PDF/JPG).
* **Comunicación Asíncrona:** Patrón transaccional **Outbox** con planificador y trabajador en segundo plano (*Background Worker*) para el despacho desacoplado de recordatorios (24 h antes) y notificaciones de exámenes sin penalizar el rendimiento de la API.

#### Evaluación Comparativa de Alternativas Arquitectónicas:
| Alternativa Arquitectónica | Ventajas Identificadas para SIRA | Desventajas, Riesgos y Sobrecostos | Decisión y Dictamen Técnico |
| :--- | :--- | :--- | :--- |
| **Monolito Modular en Capas (Seleccionada — ADR-01)** | • Un solo despliegue y una base relacional compartida minimizan el costo operativo para un equipo de 3 integrantes.<br>• Transacciones ACID locales entre Cita, Atención y Facturación sin consistencia eventual.<br>• Límites modulares estrictos permiten evolución futura hacia microservicios si la demanda multi-sede lo justifica. | • Un fallo crítico en el proceso central puede comprometer varios módulos.<br>• Exige estricta disciplina en el código para no saltarse los límites de dominio directamente en la base de datos. | **SELECCIONADA:** Óptima para el alcance de una sola sede (San Borja), 8 000 pacientes y el tiempo del semestre académico. |
| **Arquitectura de Microservicios Distribuidos** | • Escalabilidad independiente por módulo.<br>• Aislamiento físico de fallas y despliegues autónomos por servicio. | • Sobrecarga operativa severa: orquestación de contenedores, consistencia distribuida (patrón Saga), latencia de red y monitoreo complejo.<br>• Complejidad injustificada para un volumen acotado y un equipo de tres desarrolladores. | **DESCARTADA:** Inviable para el horizonte temporal y recursos del taller. |
| **Monolito Tradicional Espagueti (Sin módulos)** | • Curva de aprendizaje inmediata y rapidez de prototipado inicial. | • Alto acoplamiento; cambios en facturación rompen la HCE; pruebas unitarias difíciles y control de acceso RBAC frágil. | **DESCARTADA:** Viola la mantenibilidad y la seguridad exigidas por la Ley N.° 29733. |

---

### 5.1.2. Catálogo Oficial de Componentes y Responsabilidades (Entregable Semana 6)
El sistema se organiza en **6 módulos de dominio** y **3 componentes transversales**:

| Componente / Módulo | Responsabilidad Única en el Sistema | Interfaz Pública que Expone | Historias de Usuario Cubiertas |
| :--- | :--- | :--- | :--- |
| **M1 — Historia Clínica Electrónica y Triaje** | Mantener el expediente clínico único e integral del paciente: filiación, antecedentes, alergias, triaje de enfermería, atenciones médicas con diagnóstico CIE-10, prescripción de recetas y anulación lógica con trazabilidad. | `GET /pacientes`<br>`POST /pacientes`<br>`GET /pacientes/{id}/hce`<br>`POST /triajes`<br>`POST /atenciones`<br>`GET /atenciones/{id}`<br>`POST /atenciones/{id}/anular`<br>`GET /diagnosticos-cie10` | HU01, HU03, HU04, HU05, HU08 |
| **M2 — Agenda y Citas Médicas** | Administrar la disponibilidad médica y de los 12 consultorios físicos, gestionando el ciclo de vida de la cita (programación, confirmación, llegada, reprogramación y cancelación) con bloqueo estricto de solapamientos. | `GET /medicos`<br>`GET /citas/disponibilidad`<br>`GET /citas`<br>`POST /citas`<br>`POST /citas/{id}/reprogramar`<br>`POST /citas/{id}/cancelar`<br>`POST /citas/{id}/check-in` | HU02, HU06, HU07 |
| **M3 — Laboratorio e Imágenes** | Gestionar el circuito de órdenes médicas diagnósticas, seguimiento de estados operativos y custodia de resultados digitales con enlace seguro. | `POST /ordenes`<br>`GET /ordenes`<br>`PATCH /ordenes/{id}/estado`<br>`POST /ordenes/{id}/resultado`<br>`GET /resultados/{id}/archivo` | HU09, HU10 |
| **M4 — Facturación y Convenios** | Administrar tarifarios institucionales (Particular, EPS 1–5 y SOAT), cálculo paramétrico de copagos/deducibles, emisión de comprobantes internos y ciclo de vida de glosas. | `GET /convenios`<br>`GET /servicios`<br>`GET /tarifas/copago`<br>`POST /facturas`<br>`POST /facturas/{id}/glosas`<br>`PATCH /glosas/{id}/estado` | HU11, HU12 |
| **M5 — Reportes Gerenciales** | Consolidar indicadores de gestión operativa (ocupación de consultorios, tiempo de espera, inasistencia/no-show e ingresos) en solo lectura, sin exponer datos clínicos identificables. | `GET /reportes/indicadores`<br>`GET /reportes/ocupacion`<br>`GET /reportes/ingresos` | HU13 |
| **M6 — Portal del Paciente (Condicional)** | Permitir el autoservicio de agendamiento y consulta de citas propias por el paciente bajo las mismas validaciones de disponibilidad de M2. | `GET /portal/disponibilidad`<br>`POST /portal/citas`<br>`GET /portal/mis-citas` | HU14 |
| **T1 — Seguridad y RBAC (Transversal)** | Autenticar usuarios con contraseñas en hash seguro (bcrypt), emitir tokens JWT y autorizar operaciones según el rol asistencial o administrativo. | `POST /auth/login`<br>`GET /auth/me`<br>*(Middleware interno en cada endpoint)* | Transversal a todas las HUs; RNF-002 |
| **T2 — Auditoría (Transversal)** | Registrar de forma protegida e inmutable quién accedió o modificó datos de salud, cuándo, desde qué IP y con qué motivo. | Interfaz interna: `AuditService.registrar()` | Transversal (RNF-002, RNF-004); HU01, HU08 |
| **T3 — Notificaciones (Transversal)** | Encolar y despachar en segundo plano los recordatorios automáticos 24 h y avisos de resultados mediante el patrón Outbox. | Interfaz interna: `NotificationService.encolar()`<br>*(Worker en segundo plano cada 60 s)* | HU07, HU10 (RF-003, RF-005) |

---

### 5.1.3. Reglas de Propiedad de Datos y Comunicación entre Módulos
Para garantizar que el monolito modular preserve fronteras limpias y no degenere en una base de datos acoplada, se implementan **cuatro reglas arquitectónicas estrictas**:
1. **Propiedad Unívoca de Tablas:** Cada tabla de la base de datos pertenece a un único módulo de dominio (su *owner*). Solo dicho módulo tiene permiso en el código backend para ejecutar sentencias `INSERT`, `UPDATE` o consultas directas sobre sus tablas.
2. **Integridad Referencial en Motor vs. Aislamiento en Código:** Las claves foráneas (`FOREIGN KEYS`) se mantienen en PostgreSQL para garantizar consistencia transaccional y rendimiento relacional (ADR-02); no obstante, el código de un módulo tiene prohibido hacer *JOINs* arbitrarios sobre tablas de otros módulos: debe consumir los servicios públicos del módulo dueño.
3. **Dependencias Unidireccionales sin Ciclos:** El grafo de dependencias entre módulos fluye estrictamente en una dirección jerárquica:
   $$	\text{M6 (Portal)} \longrightarrow 	\text{M2 (Agenda)} \longrightarrow 	\text{M1 (HCE)} \longleftarrow \text{M3 (Laboratorio)} \longleftarrow \text{M4 (Facturación)} $$
   * $\text{M5 (Reportes)}$ opera como consumidor de solo lectura sobre vistas optimizadas.
   * Todos los módulos invocan a los servicios transversales $	\text{T1} $, $	\text{T2}$ y $	\text{T3}$.
4. **Orquestación en Capa de Aplicación:** Cuando una pantalla requiere datos cruzados (por ejemplo, el historial médico de la HCE junto a los nombres de médicos de M2 y resultados de M3), la composición la realiza la **Capa de Aplicación** (`app/api/v1/`), coordinando llamadas a los servicios internos sin generar dependencias cruzadas entre los modelos de dominio.

#### Matriz de Propiedad de Datos y Consumo entre Módulos:
| Módulo | Tablas Propias que Administra (Owner) | Datos que Consume de Otros Módulos e Interfaz de Acceso |
| :--- | :--- | :--- |
| **M1 — HCE y Triaje** | `pacientes`, `atenciones`, `triajes`, `diagnosticos_cie10`, `atencion_diagnosticos`, `prescripciones` | Registra auditoría en $\text{T2}$. Los datos agregados de médicos y resultados son orquestados en la capa de aplicación. |
| **M2 — Agenda y Citas** | `citas`, `medicos`, `especialidades`, `consultorios` | Consulta paciente en M1 (`GET /pacientes`); encola recordatorios en $	\text{T3}$; audita en $	\text{T2}$; consulta copago estimado en M4 (`GET /tarifas/copago`). |
| **M3 — Laboratorio** | `ordenes_examen`, `resultados` | Valida atención de origen en M1 (`GET /atenciones/{id}`); encola avisos de resultados en $	\text{T3}$; audita en $	\text{T2}$; catálogo de pruebas en M4 (`GET /servicios`). |
| **M4 — Facturación** | `convenios`, `servicios_medicos`, `tarifarios_servicios`, `facturas`, `factura_detalle`, `glosas` | Obtiene atención a liquidar en M1 (`GET /atenciones/{id}`); órdenes realizadas en M3 (`GET /ordenes`); audita en $	\text{T2}$. |
| **M5 — Reportes** | Ninguna tabla propia (vistas agregadas de solo lectura) | Consulta métricas consolidadas de citas (M2), atenciones (M1) y facturación/glosas (M4). |
| **M6 — Portal Paciente**| Ninguna tabla propia | Consume disponibilidad y agendamiento de M2 (`GET /citas/disponibilidad`, `POST /citas`) y autenticación de $	\text{T1}$. |
| **T1 — Seguridad** | `usuarios`, `roles` | Ninguno. Provee contexto de identidad a todos los módulos. |
| **T2 — Auditoría** | `bitacora_auditoria` | Recibe eventos de inserción, consulta y anulación de M1, M2, M3 y M4. |
| **T3 — Notificaciones**| `outbox_notificaciones` | Recibe eventos para despacho externo hacia pasarelas SMS/Email por HTTPS. |

---

### 5.1.4. Diagrama de Arquitectura (Vista de Componentes)
A continuación se presenta el diagrama de componentes oficial de SIRA conforme al entregable de la Semana 6:

![image1](Diagrama_Componentes_SIRA.png)

#### Especificación Técnica para Diagramación en Lucidchart:
1. **Lienzo y Notación:** Crear diagrama UML de componentes. 
2. **Capa Superior (Cliente Web):** Componente `«component» Interfaz Web Adaptativa (React 18 + TypeScript)`. Conexión hacia el backend mediante `HTTPS / JSON / JWT`.
3. **Capa Backend (FastAPI / Python 3.12):**
   * Contenedor de Capa de Aplicación: `Routers REST y Handlers (/api/v1/)`.
   * Módulo transversal de seguridad: `T1 Seguridad y Control de Acceso (JWT / RBAC)`.
   * Contenedor de Dominio: Paquetes modulares independientes `M1 HCE y Triaje`, `M2 Agenda y Citas`, `M3 Laboratorio`, `M4 Facturación y Convenios`, `M5 Reportes Gerenciales` y `M6 Portal del Paciente (borde discontinuo)`.
   * Contenedor de Servicios Transversales: `T2 Auditoría (AuditService)` y `T3 Notificaciones (NotificationService + Worker Outbox)`.
4. **Capa de Persistencia y Externos:**
   * `PostgreSQL 16 Engine` (TCP 5432 SSL) conteniendo las 22 tablas del esquema.
   * `Almacenamiento Privado de Archivos (PDF/JPG)` para resultados médicos.
   * `Proveedor Externo de Mensajería SMS / Correo` conectado mediante HTTPS desde el Worker Outbox.

--------------------------------------------------------------------------------

## 5.2. Vistas Arquitectónicas 4+1 (Kruchten)

### 5.2.1. Vista Lógica
* **Propósito:** Describir la descomposición funcional del sistema en capas y módulos, sus responsabilidades e interconexiones lógicas, independiente del hardware de ejecución.
* **Estructura en Cuatro Capas:**
  1. **Capa de Presentación:** Componentes web estructurados por funcionalidad (`features/patients`, `features/appointments`, `features/triage`, `features/laboratory`, `features/billing`, `features/reports`). Consume la API REST mediante clientes tipados en Axios con interceptores JWT.
  2. **Capa de Aplicación y API REST:** Endpoints versionados (`/api/v1/`), esquemas Pydantic de entrada/salida, validación estricta de tipos y despacho a servicios de aplicación.
  3. **Capa de Dominio:** Entidades de negocio, lógica transaccional de bloqueo de agenda, fórmulas de copago según tarifario y reglas clínicas (diagnóstico CIE-10 obligatorio, prohibición de borrado físico).
  4. **Capa de Persistencia e Infraestructura:** Modelos ORM SQLAlchemy 2, repositorios especializados, adaptadores de almacenamiento de archivos y driver `asyncpg/psycopg2` hacia PostgreSQL.

* **Marcador de Imagen:**
![image2](Vista_Logica_SIRA.png)

---

### 5.2.2. Vista de Procesos
* **Propósito:** Mostrar los hilos de ejecución, procesos concurrentes, sincronización transaccional y flujo asíncrono para satisfacer los requerimientos de tiempo real y seguridad.
* **Flujos Principales:**
  1. **Proceso Crítico de Agendamiento Concurrente (HU02, RF-002):**
     * Solicitud de reserva `POST /api/v1/citas` \(
ightarrow\) Verificación de convenio en M4 \(
ightarrow\) Apertura de transacción en PostgreSQL \(
ightarrow\) Validación de exclusión temporal física (`EXCLUDE USING gist`) para médico y consultorio \(
ightarrow\) Inserción simultánea de la cita y del evento en `outbox_notificaciones` \(
ightarrow\) Commit transaccional \(
ightarrow\) Respuesta HTTP 201 en \(< 1.5\) segundos.
     * En caso de conflicto de horario simultáneo: el motor PostgreSQL detecta violación de exclusión y retorna excepción inmediata; el backend captura el error y responde HTTP 409 (*Conflict*), solicitando al usuario elegir un nuevo horario sin persistir datos corruptos.
  2. **Proceso Asíncrono de Recordatorios 24 h (HU07, RF-003):**
     * Proceso de fondo (*Worker Daemon*) despierta cada 60 segundos \(
ightarrow\) Consulta en `outbox_notificaciones` eventos con `estado = 'PENDIENTE'` y `programado_para <= NOW()` \(
ightarrow\) Invoca adaptador SMS/Email \(
ightarrow\) En caso exitoso: marca `estado = 'ENVIADO'` y `procesado_en = NOW()`. En caso de fallo: incrementa contador de `intentos`, registra `error_detalle` y reprograma reintento exponencial (máximo 3 intentos).
  3. **Proceso de Atención y Registro en HCE (HU01, HU04, HU08):**
     * Consulta cronológica en \(\le 2\) segundos \(
ightarrow\) Captura de atención con diagnóstico CIE-10 y prescripción \(
ightarrow\) Interceptor `AuditService` genera registro inmutable en `bitacora_auditoria` con usuario, IP y fecha.

* **Marcador de Imagen:**
![image3](Vista_Procesos_SIRA.png)

---

### 5.2.3. Vista de Desarrollo
* **Propósito:** Especificar la arquitectura del código fuente, estándares de empaquetamiento y gestión de dependencias en el repositorio GitHub (`https://github.com/francito69/SW705U-grupo-A`).
* **Estructura Oficial del Repositorio:**
```text
sw705u-grupo-a/
├── docs/                               # Documentación de ingeniería del proyecto
│   └── entregable-1/
│       ├── 01-acta-constitucion.md
│       ├── 02-documento-vision.md
│       ├── 03-especificacion-requerimientos-ERS.md
│       ├── 04-modelos-uml/
│       ├── 05-arquitectura-SAD.md
│       ├── 06-modelo-base-datos.md
│       └── 07-prototipos-ux-ui.md
├── database/                           # Scripts SQL de base de datos
│   ├── 01-esquema.sql                  # 22 tablas, restricciones btree_gist, triggers
│   ├── 02-datos-prueba.sql             # Dataset sintético institucional
│   └── 03-verificacion.sql             # 10 pruebas automatizadas de restricciones
├── src/
│   ├── frontend/                       # SPA React 18 + TypeScript + Vite
│   │   ├── src/
│   │   │   ├── app/                    # Rutas, layouts y estado global
│   │   │   ├── components/             # UI Components (Design System, badges, tablas)
│   │   │   ├── features/               # Módulos desacoplados de pantallas
│   │   │   │   ├── patients/           # M1: HCE y filiación
│   │   │   │   ├── appointments/       # M2: Agenda y citas en 3 pasos
│   │   │   │   ├── triage/             # M1: Triaje de enfermería
│   │   │   │   ├── laboratory/         # M3: Órdenes y resultados
│   │   │   │   ├── billing/            # M4: Facturación, convenios y glosas
│   │   │   │   └── reports/            # M5: Dashboard gerencial de indicadores
│   │   │   └── services/               # Clientes Axios tipados con interceptor JWT
│   └── backend/                        # API REST en Python 3.12 con FastAPI
│       ├── app/
│       │   ├── api/v1/                 # Routers HTTP y controladores REST
│       │   ├── core/                   # Seguridad, configuración, hashing bcrypt, JWT
│       │   ├── modules/                # Paquetes de dominio con reglas de negocio
│       │   │   ├── patients/           # Dominio M1 (HCE y Triaje)
│       │   │   ├── appointments/       # Dominio M2 (Agenda y disponibilidad)
│       │   │   ├── laboratory/         # Dominio M3 (Laboratorio e imágenes)
│       │   │   ├── billing/            # Dominio M4 (Tarifarios y copagos)
│       │   │   └── reports/            # Dominio M5 (Consultas analíticas)
│       │   ├── shared/                 # Componentes transversales
│       │   │   ├── audit/              # T2: AuditService e interceptores
│       │   │   └── notifications/      # T3: Worker Outbox y adaptadores SMS/Email
│       │   └── infrastructure/         # Repositorios SQLAlchemy, sesión BD, S3/Files
└── tests/                              # Suite de pruebas automatizadas
    ├── unit/                           # Pruebas unitarias de dominio y copagos
    └── integration/                    # Pruebas de integración de endpoints con pytest
```

* **Marcador de Imagen:**
![image4](Vista_Desarrollo_SIRA.png)

---

### 5.2.4. Vista Física (Despliegue)
* **Propósito:** Mapear los componentes de software sobre la infraestructura de hardware, redes y límites de confianza en la nube, garantizando bajo costo y alta disponibilidad (RNF-003).
* **Nodos de Despliegue y Canales:**
  1. **Nodos de Usuario (Clientes):** Navegadores web estándar en PCs de escritorio de consultorios/recepción y dispositivos móviles del paciente. Tráfico 100 % forzado sobre **HTTPS / TLS 1.3** (puerto 443).
  2. **Nodo de Entrada y CDN:** Servicio de proxy inverso / balanceador con terminación TLS y enrutamiento hacia el frontend estático y hacia el contenedor backend.
  3. **Nodo de Servidor de Aplicación (Compute):** Contenedor Docker ejecutando el servidor ASGI `Uvicorn` con la aplicación FastAPI (Python 3.12), junto con el proceso en segundo plano del Worker Outbox.
  4. **Nodo de Base de Datos Privada:** Instancia administrada de **PostgreSQL 16**, alojada en una red privada virtual (VPC/Subnet privada) sin exposición a Internet pública. Acceso restringido exclusivamente a la IP/Security Group del servidor backend mediante credenciales seguras.
  5. **Nodo de Almacenamiento Seguro de Objetos:** Repositorio privado en la nube para documentos digitales (PDF de resultados e imágenes escaneadas), accesible mediante URLs prefirmadas de vigencia temporal (15 minutos).
  6. **Servicios Externos:** Gateway de mensajería SMS/Email conectado mediante API REST segura sobre HTTPS para despacho asíncrono.
  7. **Plano de Integración Continua (CI/CD):** Pipeline en **GitHub Actions** que ejecuta automáticamente análisis estático de código (`flake8`, `mypy`), suite de pruebas unitarias (`pytest`) y verificación de migraciones de base de datos (`alembic`) ante cada *push* o *pull request*.

* **Marcador de Imagen:**
![image5](Vista_Fisica_SIRA.png)

---

### 5.2.5. Vista de Escenarios (+1)
* **Propósito:** Validar la coherencia integral entre las vistas lógica, de procesos, de desarrollo y física mediante la ejecución de los casos de uso más representativos del sistema.

| Código Escenario | Escenario de Validación Arquitectónica | Trazabilidad ERS | Secuencia Operativa y Comportamiento Esperado | Componentes de Software Involucrados |
| :---: | :--- | :---: | :--- | :--- |
| **S-01** | **Consulta Ultrarrápida de HCE Unificada** | RF-001, RNF-001, RNF-002, RNF-004; HU01 | Médico autenticado abre expediente del paciente. El backend valida rol en `T1`, consulta PostgreSQL mediante índice compuesto `idx_atenciones_paciente_fecha` y retorna historial cronológico completo en $\le 2$ s sobre 8 000 registros. `T2` registra acceso exitoso en bitácora. | `Frontend (P1)`, `FastAPI Router`, `M1 Domain`, `PostgreSQL 16`, `T1 RBAC`, `T2 Audit`. |
| **S-02** | **Reserva de Cita con Bloqueo de Solapamiento y Outbox** | RF-002, RF-003, RNF-003, RNF-005; HU02, HU07 | Admisión selecciona médico y consultorio. Backend valida en tiempo real con restricción `EXCLUDE USING gist`. Si hay colisión simultánea, retorna HTTP 409 y revierte transacción. Si está libre, inserta cita y evento Outbox en el mismo commit. Worker despacha recordatorio 24 h antes. | `Frontend (P2)`, `M2 Agenda`, `M4 Tarifas`, `PostgreSQL (btree_gist)`, `T3 Outbox Worker`. |
| **S-03** | **Custodia de Resultado Digital y Trazabilidad** | RF-004, RF-005; HU09, HU10 | Personal de laboratorio carga informe PDF. Backend calcula hash SHA-256, sube archivo a almacenamiento privado, actualiza orden a `COMPLETADO` en $\le 4$ h desde muestra y encola notificación al médico tratante y paciente. | `Frontend Lab`, `M3 Laboratorio`, `Almacenamiento Privado`, `T3 Notificaciones`. |
| **S-04** | **Liquidación con Copago Diferenciado y Control de Glosa** | RF-006, RF-007; HU11, HU12 | Cajero liquida consulta. Backend calcula porcentaje y deducible exacto según convenio (Particular, EPS 1–5, SOAT). Al recibir reparo de EPS, registra glosa y audita trazabilidad de sustentación. | `Frontend Caja`, `M4 Facturación`, `PostgreSQL`, `T2 Audit`. |

* **Marcador de Imagen:**
![image6](Diagrama_Secuencia_S2_Agendamiento.png)

--------------------------------------------------------------------------------

## 5.3. Registro de Decisiones de Arquitectura (ADR)

### ADR-01: Adopción del Estilo Monolito Modular en Capas
* **Estado:** Aprobado e implementado (Semana 5).
* **Contexto:** El sistema SIRA integra 6 módulos clínico-administrativos para una sede única de salud, desarrollado por un equipo de 3 estudiantes bajo un cronograma académico semestral acotado. Se requiere consistencia transaccional estricta en agenda y facturación sin sobrecostos de infraestructura.
* **Alternativas Evaluadas:** Microservicios independientes; Monolito tradicional sin fronteras modulares.
* **Decisión:** Construir un Monolito Modular estructurado en paquetes independientes por dominio (`app/modules/`), con API REST tipada y base relacional compartida.
* **Consecuencias:** Despliegue único y sencillo; transacciones ACID locales garantizadas; límites claros que evitan código acoplado; facilita pruebas integrales. Requiere disciplina en el equipo para no invocar tablas de otros módulos de forma directa.

---

### ADR-02: PostgreSQL 16 para Persistencia Relacional y Almacenamiento Seguro de Archivos
* **Estado:** Aprobado e implementado (Semana 6).
* **Contexto:** Se requiere gestionar 22 tablas normalizadas en 3FN, garantizar integridad referencial estricta, almacenar diagnósticos, prescripciones, facturas y enlaces a resultados digitalizados de laboratorio (PDF/JPG) sin incurrir en licencias propietarias de servidores PACS.
* **Alternativas Evaluadas:** Bases documentales NoSQL (MongoDB); Archivos guardados como binarios BLOB en columnas de base de datos; Servidor PACS dedicado con protocolo DICOM.
* **Decisión:** Usar **PostgreSQL 16** con la extensión `btree_gist` para datos estructurados e integridad temporal, y un repositorio privado de almacenamiento de objetos para los archivos de resultados, resguardando en base únicamente la URI segura y el hash SHA-256.
* **Consecuencias:** Consistencia relacional nativa; prevención física de citas solapadas por motor; alta velocidad en consultas agregadas del dashboard; cumplimiento de la exclusión formal de PACS/DICOM.

---

### ADR-03: Control de Acceso Centralizado por Rol (RBAC) y Bitácora de Auditoría Inmutable
* **Estado:** Aprobado e implementado (Semana 6).
* **Contexto:** La Ley N.° 29733 de Protección de Datos Personales y el estándar RNF-002 exigen que la HCE solo sea consultada por personal asistencial autorizado, y que toda modificación o anulación clínica sea auditable de forma estricta, prohibiendo el borrado físico (`RNF-004`).
* **Alternativas Evaluadas:** Filtrado de menús únicamente en la interfaz web; Validación de permisos dispersa en cada controlador.
* **Decisión:** Implementar un middleware centralizado en FastAPI que intercepte cada petición HTTP, verifique la firma del token JWT y contraste el rol contra una matriz de permisos estricta. Todo acceso y anulación clínica invoca al componente `AuditService`, que persiste de forma protegida el usuario, fecha/hora, acción, tabla, registro, IP y motivo. Se prohíbe `DELETE` mediante triggers de base de datos.
* **Consecuencias:** Protección integral de la confidencialidad clínica independiente del cliente web; trazabilidad verificable ante auditorías médicas; cumplimiento del marco legal peruano de salud.

---

### ADR-04: Patrón Transaccional Outbox para Notificaciones y Recordatorios Asíncronos
* **Estado:** Aprobado e implementado (Semana 6).
* **Contexto:** El envío de recordatorios de citas con 24 h de anticipación (RF-003) y avisos de resultados de laboratorio no debe bloquear la respuesta inmediata de la API ni perderse ante caídas de la pasarela externa de correo/SMS.
* **Alternativas Evaluadas:** Envío sincrónico directo al registrar la cita; Cola de mensajes externa pesada (RabbitMQ/Kafka).
* **Decisión:** Implementar el patrón **Transactional Outbox**: la cita y el registro de notificación pendiente se insertan en la misma transacción ACID de PostgreSQL (`outbox_notificaciones`). Un proceso en segundo plano (*Worker*) sondea periódicamente la tabla, despacha los mensajes y registra los reintentos.
* **Consecuencias:** Confirmación de citas inmediata en pantalla (cumpliendo RNF-005); tolerancia a fallos del proveedor externo; reintentos automáticos sin riesgo de duplicar reservas en agenda.

---

### ADR-05: Stack Web Tipado y Despliegue Portable en Contenedores
* **Estado:** Aprobado e implementado (Semana 6).
* **Contexto:** El equipo requiere velocidad de desarrollo, alta calidad de código y despliegue reproducible para la sustentación del Examen Parcial y Final, operando con herramientas modernas de tipado estático.
* **Alternativas Evaluadas:** Django / Flask; Node.js / Express; Frontend con Server-Side Rendering (Next.js).
* **Decisión:** Frontend con **React 18 + TypeScript + Vite + Tailwind CSS**; Backend con **Python 3.12 + FastAPI + SQLAlchemy 2 + Pydantic v2**; Contenedores Docker orquestados con Docker Compose para desarrollo y despliegue cloud.
* **Consecuencias:** Tipado estricto de extremo a extremo que previene errores en tiempo de ejecución; generación automática de documentación interactiva OpenAPI (Swagger); entorno de ejecución idéntico en local y demostración en la nube.

--------------------------------------------------------------------------------

## 5.4. Soporte Arquitectónico de Atributos de Calidad (RNF)

| Atributo de Calidad / RNF | Criterio de Aceptación Verificable (ERS) | Táctica y Soporte Arquitectónico Implementado | Mecanismo de Verificación en Pruebas |
| :--- | :--- | :--- | :--- |
| **Rendimiento de Consulta (RNF-001)** | Apertura de la HCE completa de cualquier paciente en $\le 2$ segundos con base de 8 000 pacientes. | • Índice B-Tree compuesto parcial en PostgreSQL: `CREATE INDEX idx_atenciones_paciente_fecha ON atenciones (id_paciente, creado_en DESC) WHERE anulado = FALSE;`.<br>• Paginación en servidor (lotes de 10 atenciones).<br>• Carga asíncrona de resultados de exámenes. | Prueba de carga automatizada con JMeter / Locust sobre dataset sintético de 8 000 registros, midiendo percentil 95 ($P95 \le 2$ s). |
| **Seguridad y Privacidad (RNF-002)** | RBAC estricto, cifrado en tránsito HTTPS/TLS 1.3 y auditoría inmutable bajo la Ley N.° 29733. | • Middleware RBAC en FastAPI que valida claims JWT en cada solicitud.<br>• Hashing de contraseñas con bcrypt (cost factor 12).<br>• Encriptación SSL en conexiones a PostgreSQL y HTTPS forzado en frontend.<br>• Bitácora protegida sin endpoints de edición. | Inspección de paquetes con Wireshark/ZAP; suite de pruebas de seguridad intentando acceder a la HCE con rol de cajero/paciente (retorno 403 Forbidden). |
| **Disponibilidad Continua (RNF-003)** | Disponibilidad $\ge 99.5\,\%$ durante horario de atención (Lunes a Sábado de 7:00 a 21:00). | • Monitoreo de salud mediante endpoint `/healthz`.<br>• Contenedores Docker con reinicio automático (`restart: always`).<br>• Pool de conexiones administrado por SQLAlchemy para prevenir saturación.<br>• Respaldo automatizado diario de base de datos. | Cálculo mensual de uptime mediante monitor externo: $$\frac{\text{minutos operativos}}{\text{minutos programados}} \times 100 \ge 99.5\,\%$$|
| **Trazabilidad e Integridad (RNF-004)** | Prohibición absoluta de borrado físico en datos clínicos; bajas solo por anulación lógica justificada. | • Trigger de base de datos `trg_atenciones_sin_borrado` que intercepta sentencias `DELETE` y lanza excepción `restrict_violation`.<br>• Campo `anulado BOOLEAN DEFAULT FALSE` y constraint `chk_atencion_anulacion` que exige motivo de $\ge 20$ caracteres.<br>• Registro automático en `bitacora_auditoria`. | Ejecución de script `03-verificacion.sql` (Prueba 3 y 4 en pgAdmin): intento de `DELETE` es rechazado por el motor relacional. |
| **Usabilidad y Eficiencia (RNF-005)** | Agendamiento de citas en admisión completable en un máximo de 3 pasos y $\le 3$ minutos. | • Interfaz web en React diseñada en un wizard / stepper guiado de 3 pasos: (1) Identificar paciente, (2) Elegir turno y consultorio, (3) Confirmar con copago.<br>• Búsqueda reactiva por DNI indexada en $< 0.5$ s.<br>• Matriz de turnos visual en verde/gris. | Medición empírica registrada en entregable Semana 6: tarea completada en **40.6 segundos** (participante Ricco Rashuaman), superando la meta. |

--------------------------------------------------------------------------------

## 5.5. Stack Tecnológico Oficial y Justificación de Herramientas

| Capa / Responsabilidad | Tecnología y Versión | Justificación Técnica de Elección |
| :--- | :--- | :--- |
| **Frontend Web** | **React 18.3 + TypeScript 5.5 + Vite** | Ecosistema estándar de la industria, tipado estático riguroso para interfaces médicas complejas y compilación ultrarrápida. |
| **Diseño y Estilos UI** | **Tailwind CSS + Lucide React** | Sistema de diseño modular, alta fidelidad visual en escala médica y consistencia con los mockups de Google Stitch. |
| **Backend Framework** | **Python 3.12 + FastAPI 0.111** | Rendimiento asíncrono superior en I/O sobre ASGI, validación nativa con Pydantic v2 y generación automática de contratos OpenAPI (Swagger). |
| **Motor de Base de Datos** | **PostgreSQL 16 + Extensión btree_gist** | Base de datos relacional de grado empresarial; soporte de rangos temporales para erradicar solapamientos físicos en agenda (RF-002). |
| **ORM y Migraciones** | **SQLAlchemy 2.0 + Alembic** | Mapeo objeto-relacional tipado, control de versiones del esquema de base de datos reproducible e inyección segura de parámetros anti SQL Injection. |
| **Seguridad y Criptografía** | **PyJWT + Passlib (bcrypt)** | Estándar de la industria para tokens de sesión stateless firmados con HMAC-SHA256 y hashing seguro de contraseñas. |
| **Almacenamiento de Archivos**| **MinIO / AWS S3 API Compatible** | Almacenamiento seguro de resultados de laboratorio e imágenes en buckets privados con generación de URLs prefirmadas de corta duración. |
| **Testing y Calidad** | **pytest, pytest-cov, httpx, JMeter** | Batería automatizada de pruebas unitarias, cobertura de código y pruebas de carga concurrente sobre la HCE. |
| **Control de Versiones y CI** | **Git, GitHub y GitHub Actions** | Repositorio centralizado con ramas de trabajo, revisión por pares (*Pull Requests*) y pipeline automatizado de pruebas antes de desplegar. |
| **Entorno de Despliegue** | **Docker & Docker Compose en Linux Cloud** | Empaquetamiento portátil de contenedores que garantiza ejecución determinística entre desarrollo local y el entorno de demostración académica. |
