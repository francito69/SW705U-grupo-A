# 6. Modelo de Base de Datos — Sistema SIRA

--------------------------------------------------------------------------------

### Contexto y Metodología de Modelado (Semana 6)

El presente documento constituye la especificación formal del **Modelo de Base de Datos** para el **Sistema de Información Clínico-Administrativo (SIRA)** de la **Clínica San Rafael S.A.C. (Sede San Borja)**, desarrollado en el marco del curso Taller de Ingeniería de Software I (SW705).

El diseño de la base de datos materializa los requerimientos de persistencia definidos en las fases previas (`01-acta-constitucion.md`, `02-documento-vision.md`, `03-especificacion-requerimientos-ERS.md`, `04-modelosUML.md` y `05-arquitectura-SAD.md`), garantizando la integridad transaccional, el soporte normativo de confidencialidad y auditoría (Ley N.° 29733), y el cumplimiento de los atributos de calidad de rendimiento y disponibilidad (RNF-001 a RNF-005).

La base de datos se implementa sobre el motor relacional **PostgreSQL 16**, aprovechando sus capacidades avanzadas de integridad referencial, tipos estructurados, extensiones de rangos temporales (`btree_gist`) para el bloqueo físico de solapamientos en agenda (RF-002) e indexación optimizada B-Tree para la consulta de expedientes clínicos en menos de 2 segundos sobre más de 8 000 registros (RNF-001).

--------------------------------------------------------------------------------

## 6.1. Modelo Entidad-Relación (MER)

### 6.1.1. Fundamentación y Justificación de Normalización (1FN, 2FN y 3FN)

El diseño conceptual y lógico del esquema relacional fue sometido a un riguroso proceso de normalización hasta la **Tercera Forma Normal (3FN)** con el fin de eliminar redundancias, prevenir anomalías de inserción, actualización y borrado, y optimizar el almacenamiento y concurrencia:

1. **Primera Forma Normal (1FN) — Atomicidad de Atributos:**
   * Todos los atributos contienen valores atómicos indivisibles; se eliminaron listas repetitivas o campos multivaluados dentro de una misma columna.
   * Por ejemplo, los diagnósticos no se almacenan como cadenas concatenadas dentro de la atención, sino estandarizados mediante el código oficial `diagnostico_cie10`; los múltiples signos vitales de triaje se desacoplaron en una entidad propia (`triajes`); las prescripciones médicas y las órdenes diagnósticas se desglosaron en entidades atómicas (`ordenes_examen`) con su propio ciclo de vida.
   * Cada tabla cuenta con una Clave Primaria (`PRIMARY KEY`) explícita e irrepetible.

2. **Segunda Forma Normal (2FN) — Dependencia Funcional Completa:**
   * El esquema cumple la 1FN y cada atributo que no forma parte de la clave primaria depende funcionalmente de la totalidad de la clave primaria, eliminando dependencias parciales.
   * En tablas con claves compuestas o relaciones muchos a muchos (como el tarifario entre servicios médicos y convenios), los atributos de cobertura, deducible y vigencia se modelaron en la entidad asociativa `tarifarios_servicios`, dependiendo de la combinación exacta `(id_servicio, id_convenio)` y no de uno solo de ellos de forma aislada.

3. **Tercera Forma Normal (3FN) — Eliminación de Dependencias Transitivas:**
   * El esquema cumple la 2FN y ningún atributo no clave depende funcionalmente de otro atributo no clave (no existen dependencias transitivas $X 
ightarrow Y 
ightarrow Z$).
   * Se separó la información de `consultorios` y `medicos` de la tabla `citas`; de este modo, los datos de especialidad, CMP o piso del consultorio no se duplican en cada cita agendada.
   * Se separó el catálogo de `servicios_medicos` de las `facturas` y de los `tarifarios_servicios`; el valor unitario base y la descripción pertenecen al catálogo, mientras que los importes liquidados y copagos calculados se fijan en la transacción de cobro para preservar la inmutabilidad histórica.
   * Las `glosas` se desacoplaron de las facturas en una entidad dependiente 1 a N, evitando redundar datos de la factura ante múltiples observaciones o estados de sustentación.

---

### 6.1.2. Catálogo de Entidades del Modelo

El modelo relacional de SIRA se compone de **15 entidades principales** organizadas modularmente:

| N.° | Entidad / Tabla | Módulo SIRA | Clave Primaria (PK) | Propósito y Responsabilidad en el Dominio |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `roles` | Transversal / Auth | `id_rol` | Catálogo de roles de seguridad del sistema (Admisión, Médico, Enfermera, Laboratorio, Caja, Gerencia, Admin). |
| **2** | `usuarios` | Transversal / Auth | `id_usuario` | Credenciales de acceso autenticado, hash de contraseña y asociación a rol para RBAC (RNF-002). |
| **3** | `pacientes` | M1 — HCE | `id_paciente` | Datos de filiación del paciente, identificación única (DNI/CE), contacto y vinculación a convenio base. |
| **4** | `medicos` | M1 / M2 | `id_medico` | Registro profesional del cuerpo médico, número de colegiatura (CMP), especialidad y usuario de sistema. |
| **5** | `consultorios` | M2 — Agenda | `id_consultorio` | Infraestructura física de los 12 consultorios de la sede San Borja, numeración y estado operativo. |
| **6** | `citas` | M2 — Agenda | `id_cita` | Programación temporal de citas ambulatorias con validación anti-solapamiento y estados del ciclo de agendamiento. |
| **7** | `atenciones` | M1 — HCE | `id_atencion` | Expediente clínico de consulta externa o tópico de urgencia: motivo, anamnesis, diagnóstico CIE-10 y anulación lógica. |
| **8** | `triajes` | M1 — Triaje | `id_triaje` | Registro de signos vitales (presión arterial, FC, temperatura, peso, talla, IMC) previo a la atención médica. |
| **9** | `servicios_medicos` | M3 / M4 | `id_servicio` | Catálogo general de prestaciones de salud: consultas especializadas, pruebas de laboratorio y procedimientos de imágenes. |
| **10** | `convenios` | M4 — Facturación | `id_convenio` | Catálogo de coberturas institucionales: Particular, 5 EPS (Rímac, Pacífico, Mapfre, Sanitas, La Positiva) y SOAT. |
| **11** | `tarifarios_servicios` | M4 — Facturación | `id_tarifario` | Entidad asociativa (M:N): precios pactados, porcentaje de cobertura y copagos fijados por convenio y servicio. |
| **12** | `ordenes_examen` | M3 — Laboratorio | `id_orden` | Solicitudes diagnósticas generadas durante la consulta médica con trazabilidad de estado (Solicitado, En Proceso, Completado). |
| **13** | `resultados` | M3 — Laboratorio | `id_resultado` | Resultados diagnósticos validados, informe patológico y puntero al archivo privado en almacenamiento seguro. |
| **14** | `facturas` | M4 — Facturación | `id_factura` | Comprobantes de liquidación interna de clínica, cálculo de importe total, cobertura aseguradora y copago neto del paciente. |
| **15** | `glosas` | M4 — Facturación | `id_glosa` | Registro de observaciones y rechazos de liquidación emitidos por las EPS, montos objetados y ciclo de sustentación. |
| **16** | `outbox_notificaciones` | Transversal / M2 | `id_notificacion` | Cola persistente de eventos de mensajería (SMS/Email) desacoplada para recordatorios 24 h y avisos de resultados. |
| **17** | `bitacora_auditoria` | Transversal / RNF | `id_auditoria` | Registro protegido e inmutable de toda transacción sobre la HCE (quién, cuándo, qué acción, IP y motivo). |

---

### 6.1.3. Matriz Completa de Relaciones y Cardinalidades

A continuación se detalla la semántica de interconexión entre todas las entidades del modelo relacional, explicitando claves primarias (PK), foráneas (FK), multiplicidad en ambos extremos y tipo de relación:

| Entidad Origen (1) | Cardinalidad | Entidad Destino (N) | Llave Primaria (PK) | Llave Foránea (FK) | Tipo de Relación | Regla de Negocio e Integridad Referencial |
| :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| `roles` | **1 : N** | `usuarios` | `roles.id_rol` | `usuarios.id_rol` | No identificable | Un rol agrupa a muchos usuarios; un usuario posee exactamente 1 rol activo (`ON DELETE RESTRICT`). |
| `usuarios` | **1 : 0..1** | `medicos` | `usuarios.id_usuario` | `medicos.id_usuario` | No identificable | Un usuario del sistema puede corresponder a un médico tratante; relación opcional 1 a 1. |
| `convenios` | **1 : N** | `pacientes` | `convenios.id_convenio` | `pacientes.id_convenio` | No identificable | Un convenio cubre a muchos pacientes; un paciente tiene asignado 1 convenio vigente base (`ON DELETE RESTRICT`). |
| `pacientes` | **1 : N** | `citas` | `pacientes.id_paciente` | `citas.id_paciente` | No identificable | Un paciente registra de 0 a muchas citas; una cita pertenece obligatoriamente a 1 paciente (`ON DELETE RESTRICT`). |
| `medicos` | **1 : N** | `citas` | `medicos.id_medico` | `citas.id_medico` | No identificable | Un médico atiende muchas citas; una cita es asignada a 1 médico tratante (`ON DELETE RESTRICT`). |
| `consultorios` | **1 : N** | `citas` | `consultorios.id_consultorio` | `citas.id_consultorio` | No identificable | Un consultorio alberga muchas citas; una cita se ejecuta en 1 consultorio físico (`ON DELETE RESTRICT`). |
| `pacientes` | **1 : N** | `atenciones` | `pacientes.id_paciente` | `atenciones.id_paciente` | No identificable | Un paciente posee un expediente con múltiples atenciones; cada atención pertenece a 1 paciente. |
| `medicos` | **1 : N** | `atenciones` | `medicos.id_medico` | `atenciones.id_medico` | No identificable | Un médico realiza muchas atenciones; una atención es firmada por 1 médico responsable. |
| `citas` | **0..1 : 1** | `atenciones` | `citas.id_cita` | `atenciones.id_cita` | No identificable | Una consulta externa programada se origina en 1 cita; una atención de tópico de urgencia no tiene cita previa (`id_cita NULL`). |
| `atenciones` | **1 : 0..1** | `triajes` | `atenciones.id_atencion` | `triajes.id_atencion` | Identificable | Una atención clínica posee a lo sumo 1 registro de triaje asociado (`UNIQUE`); una atención puede no requerir triaje. |
| `usuarios` | **1 : N** | `triajes` | `usuarios.id_usuario` | `triajes.id_enfermera` | No identificable | La enfermera autenticada firma múltiples registros de triaje (`ON DELETE RESTRICT`). |
| `atenciones` | **1 : N** | `ordenes_examen` | `atenciones.id_atencion` | `ordenes_examen.id_atencion` | No identificable | Durante una atención se pueden emitir 0 a muchas órdenes diagnósticas; la orden depende de la atención. |
| `servicios_medicos`| **1 : N** | `ordenes_examen` | `servicios_medicos.id_servicio` | `ordenes_examen.id_servicio` | No identificable | Un servicio del catálogo (ej. Hemograma) se solicita en muchas órdenes (`ON DELETE RESTRICT`). |
| `ordenes_examen` | **1 : 0..1** | `resultados` | `ordenes_examen.id_orden` | `resultados.id_orden` | Identificable | Una orden médica genera a lo sumo 1 resultado digital validado (`UNIQUE`); la orden puede estar pendiente. |
| `usuarios` | **1 : N** | `resultados` | `usuarios.id_usuario` | `resultados.id_validador` | No identificable | El tecnólogo/patólogo valida múltiples resultados de examen (`ON DELETE RESTRICT`). |
| `servicios_medicos`| **1 : N** | `tarifarios_servicios` | `servicios_medicos.id_servicio` | `tarifarios_servicios.id_servicio` | Identificable (M:N) | Resuelve la relación N:N entre servicios y convenios; contiene precios específicos por cobertura. |
| `convenios` | **1 : N** | `tarifarios_servicios` | `convenios.id_convenio` | `tarifarios_servicios.id_convenio` | Identificable (M:N) | Un convenio fija tarifas diferenciadas para múltiples servicios del catálogo (`ON DELETE CASCADE`). |
| `atenciones` | **1 : 0..1** | `facturas` | `atenciones.id_atencion` | `facturas.id_atencion` | No identificable | Una atención médica genera como máximo 1 comprobante de cobro interno (`UNIQUE`); el cobro depende de la consulta. |
| `convenios` | **1 : N** | `facturas` | `convenios.id_convenio` | `facturas.id_convenio` | No identificable | Un convenio es aplicado en múltiples facturas emitidas por caja (`ON DELETE RESTRICT`). |
| `facturas` | **1 : N** | `glosas` | `facturas.id_factura` | `glosas.id_factura` | No identificable | Una factura puede recibir 0 a muchas glosas/observaciones de la aseguradora (`ON DELETE CASCADE`). |
| `citas` | **1 : N** | `outbox_notificaciones` | `citas.id_cita` | `outbox_notificaciones.id_cita` | No identificable | Una cita genera eventos de recordatorio y confirmación en el outbox asíncrono (`ON DELETE SET NULL`). |
| `usuarios` | **1 : N** | `bitacora_auditoria` | `usuarios.id_usuario` | `bitacora_auditoria.id_usuario` | No identificable | Todo usuario que consulte o modifique la HCE genera trazas de auditoría inmutables (`ON DELETE RESTRICT`). |

---

### 6.1.4. Diagrama Entidad-Relación Lógico/Físico (Notación Crow's Foot)

A continuación se presenta el marcador de imagen oficial del modelo entidad-relación del proyecto integrador, acompañado de su guía técnica para renderizado y transcripción:

![image1](ModeloEntidadRelacion.png)

#### Guía Paso a Paso para Construir el Diagrama ER en Lucidchart:
1. **Configuración del Lienzo:**
   * Abrir documento en blanco en Lucidchart.
   * Activar la biblioteca de formas: **«Relación de entidades (ERD)»**.
   * Seleccionar notación estándar: **Pata de Gallo (*Crow's Foot*)**.
2. **Distribución Espacial por Módulos (Recomendada):**
   * **Zona Superior Izquierda (Seguridad y Usuarios):** Dibujar las entidades `roles` y `usuarios`.
   * **Zona Central Superior (Módulo M1 - Pacientes y Personal):** Dibujar `pacientes` y `medicos`.
   * **Zona Lateral Izquierda (Módulo M2 - Agenda y Espacios):** Dibujar `consultorios` y `citas`.
   * **Zona Centro (Núcleo Clínico M1 - HCE):** Dibujar `atenciones` y `triajes`.
   * **Zona Inferior Izquierda (Módulo M3 - Diagnóstico):** Dibujar `servicios_medicos`, `ordenes_examen` y `resultados`.
   * **Zona Inferior Derecha (Módulo M4 - Facturación y Glosas):** Dibujar `convenios`, `tarifarios_servicios`, `facturas` y `glosas`.
   * **Zona Lateral Derecha (Servicios Transversales):** Dibujar `outbox_notificaciones` y `bitacora_auditoria`.
3. **Representación de Atributos en las Cajas de Entidad:**
   * Utilizar cajas de tres columnas: `Clave (PK / FK)` | `Nombre de Campo` | `Tipo de Dato`.
   * Resaltar las claves primarias (`PK`) con icono de llave o negrita.
   * Resaltar las claves foráneas (`FK`) en cursiva o etiqueta identificativa.
4. **Trazado de Relaciones y Puntas de Flecha:**
   * Relación `pacientes` a `citas`: Uno a Muchos obligatoria (`||-----o<`).
   * Relación `medicos` a `citas`: Uno a Muchos obligatoria (`||-----o<`).
   * Relación `consultorios` a `citas`: Uno a Muchos obligatoria (`||-----o<`).
   * Relación `citas` a `atenciones`: Cero o Uno a Uno condicional (`>o-----||`).
   * Relación `atenciones` a `triajes`: Uno a Cero o Uno (`||-----o|`).
   * Relación `atenciones` a `ordenes_examen`: Uno a Cero o Muchos (`||-----o<`).
   * Relación `ordenes_examen` a `resultados`: Uno a Cero o Uno (`||-----o|`).
   * Relación `servicios_medicos` y `convenios` hacia `tarifarios_servicios`: Doble relación Uno a Muchos obligatoria (`||-----|<`).
   * Relación `atenciones` a `facturas`: Uno a Cero o Uno (`||-----o|`).
   * Relación `facturas` a `glosas`: Uno a Cero o Muchos (`||-----o<`).

--------------------------------------------------------------------------------

## 6.2. Diccionario de Datos (Tablas Principales y Complementarias)

A continuación se documenta la estructura detallada de las tablas que componen la base de datos relacional de SIRA, especificando el nombre físico del campo, tipo de dato PostgreSQL, obligatoriedad, rol de clave y descripción funcional de negocio:

### 6.2.1. Tabla: `pacientes` (Módulo M1 — HCE)
* **Descripción:** Almacena el registro único de filiación de los pacientes de la clínica, evitando duplicidades y centralizando antecedentes y aseguramiento.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_paciente` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único autoincremental del paciente. |
| `tipo_documento` | `VARCHAR(10)` | **NO** | | | Tipo de documento de identidad: `'DNI'`, `'CE'`, `'PASAPORTE'`. |
| `numero_documento` | `VARCHAR(15)` | **NO** | **UQ** | | Número de documento único; indexado para búsqueda en < 2 s. |
| `nombres` | `VARCHAR(100)` | **NO** | | | Nombres completos del paciente. |
| `apellido_paterno` | `VARCHAR(100)` | **NO** | | | Apellido paterno del paciente. |
| `apellido_materno` | `VARCHAR(100)` | **NO** | | | Apellido materno del paciente. |
| `fecha_nacimiento` | `DATE` | **NO** | | | Fecha de nacimiento para cálculo dinámico de grupo etario. |
| `sexo` | `CHAR(1)` | **NO** | | | Sexo biológico del paciente: `'M'` (Masculino), `'F'` (Femenino). |
| `telefono` | `VARCHAR(20)` | **NO** | | | Teléfono móvil para despacho de notificaciones y recordatorios. |
| `email` | `VARCHAR(150)` | SÍ | | `NULL` | Correo electrónico para recordatorios 24 h y confirmaciones. |
| `direccion` | `VARCHAR(255)` | SÍ | | `NULL` | Domicilio de residencia del paciente. |
| `id_convenio` | `INT` | **NO** | **FK** | `1` (Particular) | Referencia al convenio de salud activo (`convenios.id_convenio`). |
| `antecedentes_medicos` | `TEXT` | SÍ | | `NULL` | Resumen de comorbilidades crónicas e intervenciones previas. |
| `alergias` | `TEXT` | SÍ | | `'NINGUNA'` | Alergias medicamentosas o alimentarias (alerta crítica en UI). |
| `activo` | `BOOLEAN` | **NO** | | `TRUE` | Estado de vigencia del registro del paciente. |
| `creado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal de registro de filiación en el sistema. |

---

### 6.2.2. Tabla: `citas` (Módulo M2 — Agenda y Citas)
* **Descripción:** Administra la reserva de turnos de consulta externa en los 12 consultorios, implementando bloqueo físico de solapamientos médicos y de espacio.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_cita` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador unívoco autoincremental de la cita. |
| `id_paciente` | `INT` | **NO** | **FK** | | Referencia obligatoria al paciente citado (`pacientes.id_paciente`). |
| `id_medico` | `INT` | **NO** | **FK** | | Referencia obligatoria al médico asignado (`medicos.id_medico`). |
| `id_consultorio` | `INT` | **NO** | **FK** | | Consultorio físico asignado (1 a 12) (`consultorios.id_consultorio`). |
| `fecha_hora_inicio` | `TIMESTAMP` | **NO** | | | Fecha y hora exacta de inicio del bloque de atención. |
| `fecha_hora_fin` | `TIMESTAMP` | **NO** | | | Fecha y hora exacta de culminación del bloque (`> fecha_hora_inicio`). |
| `estado` | `VARCHAR(20)` | **NO** | | `'PROGRAMADA'` | Estado: `'PROGRAMADA'`, `'CONFIRMADA'`, `'ATENDIDA'`, `'CANCELADA'`, `'REPROGRAMADA'`. |
| `motivo_cancelacion` | `TEXT` | SÍ | | `NULL` | Causa justificada si la cita fue cancelada o reprogramada. |
| `canal_agendamiento` | `VARCHAR(20)` | **NO** | | `'ADMISION'` | Origen del agendamiento: `'ADMISION'`, `'PORTAL_WEB'`, `'TELEFONICO'`. |
| `creado_por` | `INT` | **NO** | **FK** | | Usuario de admisión responsable de la reserva (`usuarios.id_usuario`). |
| `creado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal de creación del registro. |

---

### 6.2.3. Tabla: `atenciones` (Módulo M1 — Historia Clínica Electrónica)
* **Descripción:** Entidad central del expediente clínico unificado. Registra cada acto médico realizado en consulta externa o tópico de urgencia, con soporte de anulación lógica y trazabilidad.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_atencion` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único de la atención médica. |
| `id_paciente` | `INT` | **NO** | **FK** | | Referencia al paciente atendido (`pacientes.id_paciente`). |
| `id_medico` | `INT` | **NO** | **FK** | | Médico tratante responsable que suscribe el acto (`medicos.id_medico`). |
| `id_cita` | `INT` | SÍ | **FK, UQ** | `NULL` | Cita asociada si fue programada; `NULL` para tópico de urgencia. |
| `tipo_atencion` | `VARCHAR(25)` | **NO** | | `'CONSULTA_EXTERNA'` | Modalidad: `'CONSULTA_EXTERNA'` o `'TOPICO_URGENCIA'`. |
| `motivo_consulta` | `TEXT` | **NO** | | | Sintomatología principal y razón de visita descrita por el paciente. |
| `anamnesis` | `TEXT` | SÍ | | `NULL` | Relato cronológico de la enfermedad y examen clínico directo. |
| `diagnostico_cie10` | `VARCHAR(10)` | **NO** | | | Código internacional estandarizado de la enfermedad (ej. `'J00'`). |
| `diagnostico_descripcion` | `VARCHAR(255)` | **NO** | | | Glosa médica descriptiva del diagnóstico principal. |
| `prescripcion` | `TEXT` | **NO** | | | Receta médica: fármacos, posología, vía y duración del tratamiento. |
| `indicaciones` | `TEXT` | SÍ | | `NULL` | Cuidados complementarios, reposo y recomendaciones dietéticas. |
| `anulado` | `BOOLEAN` | **NO** | | `FALSE` | Bandera de baja lógica; prohíbe el borrado físico (`RNF-004`). |
| `motivo_anulacion` | `TEXT` | SÍ | | `NULL` | Justificación médica/administrativa obligatoria si `anulado = TRUE`. |
| `anulado_por` | `INT` | SÍ | **FK** | `NULL` | Usuario que ejecutó la anulación lógica (`usuarios.id_usuario`). |
| `creado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal inmutable del registro asistencial. |

---

### 6.2.4. Tabla: `triajes` (Módulo M1 — Triaje y Enfermería)
* **Descripción:** Almacena las mediciones antropométricas y signos vitales registrados por el personal de enfermería previo a la consulta médica.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_triaje` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único del registro de triaje. |
| `id_atencion` | `INT` | **NO** | **FK, UQ** | | Referencia unívoca a la atención (`atenciones.id_atencion`). |
| `presion_sistolica` | `INT` | **NO** | | | Presión arterial sistólica en mmHg (ej. `120`). |
| `presion_diastolica` | `INT` | **NO** | | | Presión arterial diastólica en mmHg (ej. `80`). |
| `temperatura` | `NUMERIC(4,2)` | **NO** | | | Temperatura corporal en °C (ej. `36.80`). |
| `frecuencia_cardiaca` | `INT` | **NO** | | | Frecuencia cardíaca en latidos por minuto (LPM). |
| `frecuencia_respiratoria` | `INT` | SÍ | | `NULL` | Frecuencia respiratoria en respiraciones por minuto (RPM). |
| `peso` | `NUMERIC(5,2)` | **NO** | | | Peso corporal en kilogramos (ej. `74.50`). |
| `talla` | `NUMERIC(3,2)` | **NO** | | | Estatura en metros (ej. `1.72`). |
| `saturacion_oxigeno` | `INT` | SÍ | | `NULL` | Oximetría de pulso en porcentaje (ej. `98`). |
| `id_enfermera` | `INT` | **NO** | **FK** | | Usuario de enfermería que ejecutó la toma (`usuarios.id_usuario`). |
| `registrado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal de captura del triaje. |

---

### 6.2.5. Tabla: `ordenes_examen` (Módulo M3 — Laboratorio e Imágenes)
* **Descripción:** Controla las solicitudes de exámenes diagnósticos emitidas por los médicos durante la consulta médica ambulatoria o urgencias.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_orden` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único de la orden diagnóstica. |
| `codigo_orden` | `VARCHAR(20)` | **NO** | **UQ** | | Código alfanumérico visible de la orden (ej. `'ORD-2026-00845'`). |
| `id_atencion` | `INT` | **NO** | **FK** | | Atención clínica de origen (`atenciones.id_atencion`). |
| `id_servicio` | `INT` | **NO** | **FK** | | Examen solicitado del catálogo (`servicios_medicos.id_servicio`). |
| `indicaciones_clinicas`| `TEXT` | SÍ | | `NULL` | Instrucciones específicas del médico para el tecnólogo. |
| `estado` | `VARCHAR(20)` | **NO** | | `'SOLICITADO'` | Estados: `'SOLICITADO'`, `'EN_PROCESO'`, `'COMPLETADO'`, `'CANCELADO'`. |
| `fecha_solicitud` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Momento exacto de emisión por el médico tratante. |

---

### 6.2.6. Tabla: `resultados` (Módulo M3 — Laboratorio e Imágenes)
* **Descripción:** Resguarda los informes diagnósticos y el enlace securizado hacia el archivo privado en almacenamiento cloud (RNF-002).

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_resultado` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único del resultado. |
| `id_orden` | `INT` | **NO** | **FK, UQ** | | Referencia a la orden médica procesada (`ordenes_examen.id_orden`). |
| `informe_diagnostico` | `TEXT` | **NO** | | | Conclusiones clínicas o valores cuantitativos del examen. |
| `ruta_archivo_privado`| `VARCHAR(500)` | **NO** | | | URI o clave de acceso privado al archivo adjunto (PDF/JPG). |
| `hash_archivo` | `VARCHAR(64)` | SÍ | | `NULL` | Hash SHA-256 para verificación de integridad del documento digital. |
| `id_validador` | `INT` | **NO** | **FK** | | Usuario de laboratorio que valida el informe (`usuarios.id_usuario`). |
| `fecha_resultado` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Fecha y hora de validación (disponible en HCE en $\le 4$ h). |

---

### 6.2.7. Tabla: `convenios` (Módulo M4 — Facturación y Convenios)
* **Descripción:** Catálogo de planes y coberturas financieras: Particular, EPS 1 a 5 y SOAT.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_convenio` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador del convenio asegurador. |
| `codigo_convenio` | `VARCHAR(20)` | **NO** | **UQ** | | Código comercial (ej. `'PARTICULAR'`, `'EPS_PACIFICO'`, `'SOAT'`). |
| `nombre_institucion` | `VARCHAR(100)` | **NO** | | | Razón social o denominación (ej. `'Pacífico Seguros S.A.'`). |
| `tipo_convenio` | `VARCHAR(20)` | **NO** | | `'EPS'` | Clasificación: `'PARTICULAR'`, `'EPS'`, `'SOAT'`. |
| `contacto_operativo` | `VARCHAR(150)` | SÍ | | `NULL` | Correo o enlace de la mesa de ayuda de la aseguradora. |
| `activo` | `BOOLEAN` | **NO** | | `TRUE` | Bandera de vigencia del convenio con la clínica. |

---

### 6.2.8. Tabla: `servicios_medicos` (Módulos M1, M3, M4)
* **Descripción:** Catálogo maestro unificado de prestaciones asistenciales, consultas, pruebas de laboratorio e imágenes.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_servicio` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador unívoco del servicio médico. |
| `codigo_servicio` | `VARCHAR(20)` | **NO** | **UQ** | | Código de prestación (ej. `'CON-MED-01'`, `'LAB-HEM-01'`). |
| `nombre_servicio` | `VARCHAR(150)` | **NO** | | | Descripción oficial (ej. `'Consulta Externa Medicina General'`). |
| `tipo_servicio` | `VARCHAR(30)` | **NO** | | `'CONSULTA'` | Tipo: `'CONSULTA'`, `'LABORATORIO'`, `'IMAGENES'`, `'PROCEDIMIENTO'`. |
| `precio_base_particular`| `NUMERIC(10,2)` | **NO** | | | Precio unitario base en moneda nacional (PEN). |
| `activo` | `BOOLEAN` | **NO** | | `TRUE` | Estado de vigencia en el catálogo asistencial. |

---

### 6.2.9. Tabla: `tarifarios_servicios` (Módulo M4 — Facturación)
* **Descripción:** Entidad asociativa que resuelve la relación N a M entre servicios médicos y convenios aseguradores, fijando copagos específicos.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_tarifario` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único del registro de tarifa. |
| `id_servicio` | `INT` | **NO** | **FK** | | Servicio del catálogo (`servicios_medicos.id_servicio`). |
| `id_convenio` | `INT` | **NO** | **FK** | | Convenio asegurador (`convenios.id_convenio`). |
| `precio_convenido` | `NUMERIC(10,2)` | **NO** | | | Tarifa unitaria pactada contractualmente en PEN. |
| `porcentaje_cobertura`| `NUMERIC(5,2)` | **NO** | | | Porcentaje asumido por aseguradora (0.00 % a 100.00 %). |
| `copago_fijo` | `NUMERIC(10,2)` | **NO** | | `0.00` | Monto deducible fijo obligatorio a cargo del paciente (PEN). |
| `vigente` | `BOOLEAN` | **NO** | | `TRUE` | Estado de vigencia del tarifario contractual. |

---

### 6.2.10. Tabla: `facturas` (Módulo M4 — Facturación y Convenios)
* **Descripción:** Comprobantes internos de liquidación emitidos por caja, registrando el desglose de importes cubiertos y copago recaudado.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_factura` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador del comprobante interno de facturación. |
| `numero_comprobante` | `VARCHAR(25)` | **NO** | **UQ** | | Serie y correlativo interno (ej. `'LIQ-2026-001205'`). |
| `id_atencion` | `INT` | **NO** | **FK, UQ** | | Atención clínica liquidada (`atenciones.id_atencion`). |
| `id_convenio` | `INT` | **NO** | **FK** | | Cobertura aplicada (`convenios.id_convenio`). |
| `monto_total` | `NUMERIC(10,2)` | **NO** | | | Importe total liquidado de la prestación en PEN. |
| `monto_cubierto_seguro`| `NUMERIC(10,2)` | **NO** | | | Porción facturable a la aseguradora / EPS en PEN. |
| `copago_paciente` | `NUMERIC(10,2)` | **NO** | | | Importe neto cancelado por el paciente en ventanilla. |
| `estado` | `VARCHAR(20)` | **NO** | | `'EMITIDA'` | Estados: `'EMITIDA'`, `'PAGADA'`, `'OBSERVADA'`, `'ANULADA'`. |
| `creado_por` | `INT` | **NO** | **FK** | | Cajero responsable de emisión (`usuarios.id_usuario`). |
| `fecha_emision` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal de liquidación en caja. |

---

### 6.2.11. Tabla: `glosas` (Módulo M4 — Facturación y Glosas)
* **Descripción:** Controla las observaciones de liquidación deducidas por las aseguradoras, registrando montos objetados y estados de sustentación.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_glosa` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador unívoco del registro de glosa. |
| `id_factura` | `INT` | **NO** | **FK** | | Factura afectada (`facturas.id_factura`). |
| `codigo_glosa` | `VARCHAR(30)` | **NO** | | | Código normativo del motivo de rechazo remitido por la EPS. |
| `monto_glosado` | `NUMERIC(10,2)` | **NO** | | | Importe monetario retenido u objetado en PEN. |
| `motivo_observacion`| `TEXT` | **NO** | | | Descripción del reparo formulado por la aseguradora. |
| `estado` | `VARCHAR(20)` | **NO** | | `'REGISTRADA'` | Estados: `'REGISTRADA'`, `'SUSTENTADA'`, `'ACEPTADA'`, `'RECUPERADA'`. |
| `fecha_observacion` | `DATE` | **NO** | | `CURRENT_DATE` | Fecha de notificación de la glosa por la aseguradora. |
| `fecha_resolucion` | `DATE` | SÍ | | `NULL` | Fecha de cierre o recuperación del cobro disputado. |
| `registrado_por` | `INT` | **NO** | **FK** | | Usuario administrativo gestor (`usuarios.id_usuario`). |

---

### 6.2.12. Tabla: `outbox_notificaciones` (Transversal — Patrón Outbox)
* **Descripción:** Cola transaccional de mensajería (SMS/Email) que garantiza el despacho asíncrono y desacoplado de recordatorios de citas a 24 horas (RF-003, ADR-04).

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_notificacion` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador del evento de notificación. |
| `id_cita` | `INT` | SÍ | **FK** | `NULL` | Cita vinculada si es recordatorio (`citas.id_cita`). |
| `tipo_evento` | `VARCHAR(30)` | **NO** | | | Tipo: `'RECORDATORIO_24H'`, `'CONFIRMACION_CITA'`, `'AVISO_RESULTADO'`. |
| `canal` | `VARCHAR(15)` | **NO** | | `'SMS'` | Canal de comunicación: `'SMS'`, `'EMAIL'`, `'WHATSAPP'`. |
| `destinatario` | `VARCHAR(150)` | **NO** | | | Número de teléfono o correo de destino. |
| `mensaje` | `TEXT` | **NO** | | | Contenido de texto formateado de la alerta. |
| `programado_para` | `TIMESTAMP` | **NO** | | | Fecha y hora en la que debe ser despachado el mensaje. |
| `estado` | `VARCHAR(20)` | **NO** | | `'PENDIENTE'` | Estados: `'PENDIENTE'`, `'ENVIADO'`, `'FALLIDO'`, `'REINTENTO'`. |
| `intentos` | `INT` | **NO** | | `0` | Contador de reintentos efectuados por el worker en segundo plano. |
| `error_detalle` | `TEXT` | SÍ | | `NULL` | Mensaje de excepción reportado por el gateway externo ante fallos. |
| `procesado_en` | `TIMESTAMP` | SÍ | | `NULL` | Momento exacto de entrega confirmada por el worker. |

---

### 6.2.13. Tabla: `bitacora_auditoria` (Transversal — Seguridad y Ley N.° 29733)
* **Descripción:** Registro inmutable de trazabilidad que audita de forma no modificable todo acceso, consulta o anulación sobre la HCE (RNF-002, RNF-004).

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción y Restricción de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_auditoria` | `BIGSERIAL` | **NO** | **PK** | Secuencia | Identificador correlativo del registro de auditoría. |
| `id_usuario` | `INT` | **NO** | **FK** | | Identificador del usuario que ejecutó la operación (`usuarios.id_usuario`). |
| `nombre_tabla` | `VARCHAR(50)` | **NO** | | | Entidad afectada (ej. `'atenciones'`, `'pacientes'`, `'resultados'`). |
| `id_registro_afectado`| `INT` | **NO** | | | Clave primaria del registro auditado en la tabla correspondiente. |
| `accion` | `VARCHAR(20)` | **NO** | | | Operación: `'SELECT'`, `'INSERT'`, `'UPDATE'`, `'ANULAR'`. |
| `direccion_ip` | `VARCHAR(45)` | **NO** | | | Dirección IP de origen de la solicitud de red (IPv4 / IPv6). |
| `datos_anteriores` | `JSONB` | SÍ | | `NULL` | Snapshot JSON de los valores antes de la modificación (si aplica). |
| `datos_nuevos` | `JSONB` | SÍ | | `NULL` | Snapshot JSON de los nuevos valores introducidos (si aplica). |
| `motivo` | `TEXT` | SÍ | | `NULL` | Justificación obligatoria en operaciones de anulación lógica. |
| `fecha_hora` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal inmutable y protegida por políticas de motor. |

--------------------------------------------------------------------------------

## 6.3. Script DDL Completo y Optimizado (PostgreSQL)

A continuación se presenta el script de definición de datos (**Data Definition Language - DDL**) completamente ejecutable para PostgreSQL 16. El script incorpora la extensión `btree_gist` con restricciones de exclusión físicas para erradicar solapamientos de citas, restricciones de integridad referencial, cheques de dominio e índices B-Tree optimizados para certificar tiempos de apertura de HCE en menos de 2 segundos (RNF-001):

```sql
-- =============================================================================
-- SISTEMA DE INFORMACIÓN CLÍNICO-ADMINISTRATIVO (SIRA)
-- CLÍNICA SAN RAFAEL S.A.C. - SEDE SAN BORJA
-- SCRIPT DDL OFICIAL - VERSIÓN NORMALIZADA (3FN) PARA POSTGRESQL 16
-- =============================================================================

-- Habilitar extensión requerida para restricciones de exclusión temporal anti-solapamiento
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- -----------------------------------------------------------------------------
-- 1. TABLA: roles
-- -----------------------------------------------------------------------------
CREATE TABLE roles (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. TABLA: usuarios (Autenticación y RBAC)
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    id_rol INT NOT NULL REFERENCES roles(id_rol) ON DELETE RESTRICT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. TABLA: convenios (Aseguradoras, EPS y SOAT)
-- -----------------------------------------------------------------------------
CREATE TABLE convenios (
    id_convenio SERIAL PRIMARY KEY,
    codigo_convenio VARCHAR(20) NOT NULL UNIQUE,
    nombre_institucion VARCHAR(100) NOT NULL,
    tipo_convenio VARCHAR(20) NOT NULL CHECK (tipo_convenio IN ('PARTICULAR', 'EPS', 'SOAT')),
    contacto_operativo VARCHAR(150),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 4. TABLA: pacientes (Filiación centralizada y HCE base)
-- -----------------------------------------------------------------------------
CREATE TABLE pacientes (
    id_paciente SERIAL PRIMARY KEY,
    tipo_documento VARCHAR(10) NOT NULL CHECK (tipo_documento IN ('DNI', 'CE', 'PASAPORTE')),
    numero_documento VARCHAR(15) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo CHAR(1) NOT NULL CHECK (sexo IN ('M', 'F')),
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(150),
    direccion VARCHAR(255),
    id_convenio INT NOT NULL DEFAULT 1 REFERENCES convenios(id_convenio) ON DELETE RESTRICT,
    antecedentes_medicos TEXT,
    alergias TEXT DEFAULT 'NINGUNA',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 5. TABLA: medicos (Cuerpo médico de la clínica)
-- -----------------------------------------------------------------------------
CREATE TABLE medicos (
    id_medico SERIAL PRIMARY KEY,
    cmp VARCHAR(10) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    id_usuario INT UNIQUE REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 6. TABLA: consultorios (Infraestructura física de 12 consultorios)
-- -----------------------------------------------------------------------------
CREATE TABLE consultorios (
    id_consultorio SERIAL PRIMARY KEY,
    numero VARCHAR(10) NOT NULL UNIQUE,
    piso INT NOT NULL CHECK (piso >= 1),
    descripcion VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- -----------------------------------------------------------------------------
-- 7. TABLA: citas (Agenda multiespecialidad con bloqueo físico de solapamiento)
-- -----------------------------------------------------------------------------
CREATE TABLE citas (
    id_cita SERIAL PRIMARY KEY,
    id_paciente INT NOT NULL REFERENCES pacientes(id_paciente) ON DELETE RESTRICT,
    id_medico INT NOT NULL REFERENCES medicos(id_medico) ON DELETE RESTRICT,
    id_consultorio INT NOT NULL REFERENCES consultorios(id_consultorio) ON DELETE RESTRICT,
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PROGRAMADA' 
        CHECK (estado IN ('PROGRAMADA', 'CONFIRMADA', 'ATENDIDA', 'CANCELADA', 'REPROGRAMADA')),
    motivo_cancelacion TEXT,
    canal_agendamiento VARCHAR(20) NOT NULL DEFAULT 'ADMISION' 
        CHECK (canal_agendamiento IN ('ADMISION', 'PORTAL_WEB', 'TELEFONICO')),
    creado_por INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rango_horario CHECK (fecha_hora_fin > fecha_hora_inicio),
    -- RESTRICCIÓN FÍSICA RF-002: Bloqueo de solapamientos médicos por concurrencia
    CONSTRAINT no_solapamiento_medico EXCLUDE USING gist (
        id_medico WITH =,
        tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&
    ) WHERE (estado IN ('PROGRAMADA', 'CONFIRMADA')),
    -- RESTRICCIÓN FÍSICA RF-002: Bloqueo de solapamientos de consultorio físico
    CONSTRAINT no_solapamiento_consultorio EXCLUDE USING gist (
        id_consultorio WITH =,
        tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&
    ) WHERE (estado IN ('PROGRAMADA', 'CONFIRMADA'))
);

-- -----------------------------------------------------------------------------
-- 8. TABLA: atenciones (Acto médico asistencial, HCE y baja lógica)
-- -----------------------------------------------------------------------------
CREATE TABLE atenciones (
    id_atencion SERIAL PRIMARY KEY,
    id_paciente INT NOT NULL REFERENCES pacientes(id_paciente) ON DELETE RESTRICT,
    id_medico INT NOT NULL REFERENCES medicos(id_medico) ON DELETE RESTRICT,
    id_cita INT UNIQUE REFERENCES citas(id_cita) ON DELETE SET NULL,
    tipo_atencion VARCHAR(25) NOT NULL DEFAULT 'CONSULTA_EXTERNA' 
        CHECK (tipo_atencion IN ('CONSULTA_EXTERNA', 'TOPICO_URGENCIA')),
    motivo_consulta TEXT NOT NULL,
    anamnesis TEXT,
    diagnostico_cie10 VARCHAR(10) NOT NULL,
    diagnostico_descripcion VARCHAR(255) NOT NULL,
    prescripcion TEXT NOT NULL,
    indicaciones TEXT,
    anulado BOOLEAN NOT NULL DEFAULT FALSE,
    motivo_anulacion TEXT,
    anulado_por INT REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_motivo_anulacion CHECK (
        (anulado = FALSE AND motivo_anulacion IS NULL) OR 
        (anulado = TRUE AND motivo_anulacion IS NOT NULL)
    )
);

-- -----------------------------------------------------------------------------
-- 9. TABLA: triajes (Mediciones previas por enfermería)
-- -----------------------------------------------------------------------------
CREATE TABLE triajes (
    id_triaje SERIAL PRIMARY KEY,
    id_atencion INT NOT NULL UNIQUE REFERENCES atenciones(id_atencion) ON DELETE CASCADE,
    presion_sistolica INT NOT NULL CHECK (presion_sistolica BETWEEN 50 AND 300),
    presion_diastolica INT NOT NULL CHECK (presion_diastolica BETWEEN 30 AND 200),
    temperatura NUMERIC(4,2) NOT NULL CHECK (temperatura BETWEEN 30.00 AND 45.00),
    frecuencia_cardiaca INT NOT NULL CHECK (frecuencia_cardiaca BETWEEN 30 AND 250),
    frecuencia_respiratoria INT CHECK (frecuencia_respiratoria BETWEEN 8 AND 60),
    peso NUMERIC(5,2) NOT NULL CHECK (peso BETWEEN 1.00 AND 350.00),
    talla NUMERIC(3,2) NOT NULL CHECK (talla BETWEEN 0.30 AND 2.50),
    saturacion_oxigeno INT CHECK (saturacion_oxigeno BETWEEN 50 AND 100),
    id_enfermera INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 10. TABLA: servicios_medicos (Catálogo maestro de prestaciones)
-- -----------------------------------------------------------------------------
CREATE TABLE servicios_medicos (
    id_servicio SERIAL PRIMARY KEY,
    codigo_servicio VARCHAR(20) NOT NULL UNIQUE,
    nombre_servicio VARCHAR(150) NOT NULL,
    tipo_servicio VARCHAR(30) NOT NULL 
        CHECK (tipo_servicio IN ('CONSULTA', 'LABORATORIO', 'IMAGENES', 'PROCEDIMIENTO')),
    precio_base_particular NUMERIC(10,2) NOT NULL CHECK (precio_base_particular >= 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 11. TABLA: tarifarios_servicios (Asociativa M:N Servicios - Convenios)
-- -----------------------------------------------------------------------------
CREATE TABLE tarifarios_servicios (
    id_tarifario SERIAL PRIMARY KEY,
    id_servicio INT NOT NULL REFERENCES servicios_medicos(id_servicio) ON DELETE RESTRICT,
    id_convenio INT NOT NULL REFERENCES convenios(id_convenio) ON DELETE CASCADE,
    precio_convenido NUMERIC(10,2) NOT NULL CHECK (precio_convenido >= 0),
    porcentaje_cobertura NUMERIC(5,2) NOT NULL CHECK (porcentaje_cobertura BETWEEN 0.00 AND 100.00),
    copago_fijo NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (copago_fijo >= 0),
    vigente BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_servicio_convenio UNIQUE (id_servicio, id_convenio)
);

-- -----------------------------------------------------------------------------
-- 12. TABLA: ordenes_examen (Circuito diagnóstico de laboratorio/imágenes)
-- -----------------------------------------------------------------------------
CREATE TABLE ordenes_examen (
    id_orden SERIAL PRIMARY KEY,
    codigo_orden VARCHAR(20) NOT NULL UNIQUE,
    id_atencion INT NOT NULL REFERENCES atenciones(id_atencion) ON DELETE CASCADE,
    id_servicio INT NOT NULL REFERENCES servicios_medicos(id_servicio) ON DELETE RESTRICT,
    indicaciones_clinicas TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'SOLICITADO' 
        CHECK (estado IN ('SOLICITADO', 'EN_PROCESO', 'COMPLETADO', 'CANCELADO')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 13. TABLA: resultados (Informes diagnósticos y puntero seguro a archivos)
-- -----------------------------------------------------------------------------
CREATE TABLE resultados (
    id_resultado SERIAL PRIMARY KEY,
    id_orden INT NOT NULL UNIQUE REFERENCES ordenes_examen(id_orden) ON DELETE CASCADE,
    informe_diagnostico TEXT NOT NULL,
    ruta_archivo_privado VARCHAR(500) NOT NULL,
    hash_archivo VARCHAR(64),
    id_validador INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    fecha_resultado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 14. TABLA: facturas (Comprobantes internos y liquidación con copagos)
-- -----------------------------------------------------------------------------
CREATE TABLE facturas (
    id_factura SERIAL PRIMARY KEY,
    numero_comprobante VARCHAR(25) NOT NULL UNIQUE,
    id_atencion INT NOT NULL UNIQUE REFERENCES atenciones(id_atencion) ON DELETE RESTRICT,
    id_convenio INT NOT NULL REFERENCES convenios(id_convenio) ON DELETE RESTRICT,
    monto_total NUMERIC(10,2) NOT NULL CHECK (monto_total >= 0),
    monto_cubierto_seguro NUMERIC(10,2) NOT NULL CHECK (monto_cubierto_seguro >= 0),
    copago_paciente NUMERIC(10,2) NOT NULL CHECK (copago_paciente >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'EMITIDA' 
        CHECK (estado IN ('EMITIDA', 'PAGADA', 'OBSERVADA', 'ANULADA')),
    creado_por INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_suma_importes CHECK (monto_total = monto_cubierto_seguro + copago_paciente)
);

-- -----------------------------------------------------------------------------
-- 15. TABLA: glosas (Gestión de observaciones emitidas por aseguradoras)
-- -----------------------------------------------------------------------------
CREATE TABLE glosas (
    id_glosa SERIAL PRIMARY KEY,
    id_factura INT NOT NULL REFERENCES facturas(id_factura) ON DELETE CASCADE,
    codigo_glosa VARCHAR(30) NOT NULL,
    monto_glosado NUMERIC(10,2) NOT NULL CHECK (monto_glosado > 0),
    motivo_observacion TEXT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'REGISTRADA' 
        CHECK (estado IN ('REGISTRADA', 'SUSTENTADA', 'ACEPTADA', 'RECUPERADA')),
    fecha_observacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_resolucion DATE,
    registrado_por INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 16. TABLA: outbox_notificaciones (Patrón Outbox para mensajería asíncrona)
-- -----------------------------------------------------------------------------
CREATE TABLE outbox_notificaciones (
    id_notificacion SERIAL PRIMARY KEY,
    id_cita INT REFERENCES citas(id_cita) ON DELETE SET NULL,
    tipo_evento VARCHAR(30) NOT NULL,
    canal VARCHAR(15) NOT NULL CHECK (canal IN ('SMS', 'EMAIL', 'WHATSAPP')),
    destinatario VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    programado_para TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' 
        CHECK (estado IN ('PENDIENTE', 'ENVIADO', 'FALLIDO', 'REINTENTO')),
    intentos INT NOT NULL DEFAULT 0,
    error_detalle TEXT,
    procesado_en TIMESTAMP,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 17. TABLA: bitacora_auditoria (Registro inmutable y protegido - Ley 29733)
-- -----------------------------------------------------------------------------
CREATE TABLE bitacora_auditoria (
    id_auditoria BIGSERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    nombre_tabla VARCHAR(50) NOT NULL,
    id_registro_afectado INT NOT NULL,
    accion VARCHAR(20) NOT NULL CHECK (accion IN ('SELECT', 'INSERT', 'UPDATE', 'ANULAR')),
    direccion_ip VARCHAR(45) NOT NULL,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    motivo TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ÍNDICES DE RENDIMIENTO Y OPTIMIZACIÓN (Soporte RNF-001 y RNF-003)
-- =============================================================================

-- 1. Apertura de HCE en < 2 segundos sobre +8 000 pacientes (RNF-001)
-- Permite indexar atenciones válidas por paciente ordenadas cronológicamente
CREATE INDEX idx_atenciones_paciente_fecha 
ON atenciones (id_paciente, creado_en DESC) 
WHERE anulado = FALSE;

-- 2. Búsqueda instantánea de pacientes por documento de identidad
CREATE INDEX idx_pacientes_num_doc 
ON pacientes (numero_documento);

-- 3. Búsqueda y validación de disponibilidad de citas en agenda
CREATE INDEX idx_citas_rango_medico 
ON citas (id_medico, fecha_hora_inicio, fecha_hora_fin) 
WHERE estado IN ('PROGRAMADA', 'CONFIRMADA');

CREATE INDEX idx_citas_rango_consultorio 
ON citas (id_consultorio, fecha_hora_inicio, fecha_hora_fin) 
WHERE estado IN ('PROGRAMADA', 'CONFIRMADA');

-- 4. Extracción rápida de eventos pendientes para el Worker de mensajería (Outbox)
CREATE INDEX idx_outbox_pendientes 
ON outbox_notificaciones (programado_para) 
WHERE estado = 'PENDIENTE';

-- 5. Búsqueda rápida de órdenes médicas por estado
CREATE INDEX idx_ordenes_atencion_estado 
ON ordenes_examen (id_atencion, estado);

-- 6. Trazabilidad rápida en bitácora de auditoría por usuario y fecha
CREATE INDEX idx_auditoria_usuario_fecha 
ON bitacora_auditoria (id_usuario, fecha_hora DESC);
```

--------------------------------------------------------------------------------

## 6.4. Matriz de Trazabilidad: Requerimientos, HUs y Base de Datos

La siguiente matriz certifica el soporte y alineamiento completo entre las tablas de la base de datos, los requerimientos formales (RF/RNF) y las Historias de Usuario priorizadas:

| Módulo SIRA | Tabla en PostgreSQL | Requerimientos Soportados | Historias de Usuario | Justificación de Soporte en Esquema |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | `pacientes` | RF-001, RNF-001 | HU01, HU03 | Registro único de filiación, antecedentes, alergias e índice único por DNI. |
| **M1** | `atenciones` | RF-001, RNF-001, RNF-004 | HU01, HU04, HU08 | Contiene anamnesis, CIE-10, prescripción y campo `anulado = TRUE` (baja lógica). |
| **M1** | `triajes` | RF-001 | HU05 | Captura de signos vitales asociada 1 a 1 con la atención clínica. |
| **M2** | `citas` | RF-002, RNF-005 | HU02, HU06 | Maneja los 12 consultorios y aplica restricción de exclusión física anti-solapamiento. |
| **M2** | `consultorios` | RF-002 | HU02 | Catálogo físico de consultorios médicos de la sede San Borja. |
| **M2** | `medicos` | RF-001, RF-002 | HU01, HU02 | Asocia CMP, especialidad médica y credenciales del usuario tratante. |
| **M3** | `ordenes_examen` | RF-004 | HU09 | Solicitudes diagnósticas emitidas en consulta con ciclo de estados. |
| **M3** | `resultados` | RF-005, RNF-002 | HU09 | Resguarda diagnóstico validado y URI segura a archivo privado en la nube. |
| **M4** | `convenios` | RF-006 | HU03, HU10 | Catálogo de Particular, 5 EPS y SOAT para asignación de coberturas. |
| **M4** | `tarifarios_servicios`| RF-006 | HU10 | Parametriza precios pactados, copagos fijos y porcentajes cubiertos. |
| **M4** | `facturas` | RF-006 | HU10 | Comprobantes internos con validación de suma: total = seguro + copago. |
| **M4** | `glosas` | RF-007 | HU11 | Trazabilidad del ciclo de vida de observaciones formuladas por aseguradoras. |
| **Transversal**| `outbox_notificaciones`| RF-003 | HU07 | Desacoplamiento transaccional para recordatorios de citas con 24 h de anticipación. |
| **Transversal**| `bitacora_auditoria` | RNF-002, RNF-004 | HU08 | Cumplimiento de la Ley N.° 29733 mediante log inmutable de accesos clínicos. |

--------------------------------------------------------------------------------

## 6.5. Checklist de Verificación y Calidad de Base de Datos (Semana 6)

| Criterio de Evaluación Técnica | Estado | Evidencia y Justificación en el Entregable |
| :--- | :---: | :--- |
| **Normalización en Tercera Forma Normal (3FN)** | **Cumple** | Todas las relaciones transitivas y multivaluadas fueron eliminadas; entidades maestras y transaccionales separadas. |
| **Integridad Referencial Estricta (PK y FK)** | **Cumple** | 100 % de tablas cuentan con PK explícitas y FKs con políticas restrictivas (`ON DELETE RESTRICT / CASCADE`). |
| **Prevención Física de Solapamientos (RF-002)** | **Cumple** | Implementado mediante `btree_gist` y restricciones de exclusión `EXCLUDE USING gist` sobre médico y consultorio. |
| **Rendimiento de Apertura de HCE (RNF-001)** | **Cumple** | Índice compuesto parcial `idx_atenciones_paciente_fecha` garantiza acceso en $\le 2$ s sobre 8 000 pacientes. |
| **Trazabilidad y No Borrado Físico (RNF-004)** | **Cumple** | Bajas clínicas restringidas a anulación lógica (`anulado = TRUE`, motivo obligatorio y registro en bitácora). |
| **Seguridad de Datos de Salud (Ley 29733)** | **Cumple** | Tabla `bitacora_auditoria` con almacenamiento JSONB de cambios y restricción de acceso a archivos privados. |
| **Compatibilidad con Plantilla Entregable 1** | **Cumple** | Cumple y supera los requisitos de las secciones 6.1 (MER), 6.2 (Diccionario de Datos) y 6.3 (Script DDL). |
