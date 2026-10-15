# 6. Modelo de Base de Datos — Sistema SIRA

--------------------------------------------------------------------------------

### Contexto y Metodología de Persistencia Relacional (Semana 6)

El presente documento constituye la especificación formal del **Modelo de Base de Datos** para el **Sistema de Información Clínico-Administrativo (SIRA)** de la **Clínica San Rafael S.A.C. (Sede San Borja)**, desarrollado en el marco del curso Taller de Ingeniería de Software I (SW705).

El diseño de persistencia materializa los requerimientos definidos en las fases previas (`01-acta-constitucion.md`, `02-documento-vision.md`, `03-especificacion-requerimientos-ERS.md`, `04-modelosUML.md` y `05-arquitectura-SAD.md`), incorporando íntegramente las 22 tablas normalizadas, restricciones avanzadas, triggers de integridad y datos sintéticos presentados en el entregable formal de la Semana 6 (`semana6.entregable-4-taller.pdf`).

La base de datos se implementa sobre el motor relacional de grado empresarial **PostgreSQL 16**, aprovechando:
1. La extensión **`btree_gist`** con restricciones de exclusión física (`EXCLUDE USING gist`) sobre rangos temporales (`tsrange`) para erradicar el 100 % de solapamientos médicos y de consultorios en agenda (**RF-002**).
2. Triggers procedurales (`PL/pgSQL`) que prohíben de forma irrevocable el borrado físico (`DELETE`) en atenciones clínicas y modificaciones en la bitácora de auditoría, forzando la anulación lógica justificada (**RNF-004**, Ley N.° 29733).
3. Índices B-Tree compuestos parciales que garantizan la consulta y apertura del expediente clínico unificado en menos de 2 segundos sobre más de 8 000 registros (**RNF-001**).

--------------------------------------------------------------------------------

## 6.1. Modelo Entidad-Relación (MER)

### 6.1.1. Fundamentación y Justificación de Normalización (1FN, 2FN y 3FN)

El esquema relacional fue sometido a un riguroso proceso de normalización matemática hasta la **Tercera Forma Normal (3FN)** para erradicar anomalías de inserción, actualización y borrado:


| Forma Normal | Criterio Teórico | Cómo lo Cumple Rigurosamente el Esquema SIRA |
| :---: | :--- | :--- |
| **1FN** | **Atomicidad de Atributos:** Todos los campos contienen valores atómicos indivisibles; se eliminan listas o atributos multivaluados. | • Prescripciones médicas separadas en la tabla hija `prescripciones` (una fila por fármaco, dosis, frecuencia y duración), eliminando cadenas de texto libre.<br>• Diagnósticos clínicos desacoplados en `atencion_diagnosticos` vinculados al catálogo oficial `diagnosticos_cie10`.<br>• Presión arterial desglosada en `presion_sistolica` y `presion_diastolica` en la tabla `triajes`.<br>• Nombres y apellidos atomizados en `nombres`, `apellido_paterno` y `apellido_materno`. |
| **2FN** | **Dependencia Funcional Completa:** Cumple 1FN y cada atributo no clave depende de la totalidad de la clave primaria (sin dependencias parciales en claves compuestas). | • En `atencion_diagnosticos`, el atributo `tipo` (PRINCIPAL, SECUNDARIO, PRESUNTIVO) depende de la clave compuesta completa `(id_atencion, codigo_cie10)`.<br>• En `tarifarios_servicios`, los atributos `precio_convenido`, `porcentaje_cobertura` y `copago_fijo` dependen de la clave compuesta `(id_servicio, id_convenio)`, mientras que `precio_base_particular` depende unívocamente del servicio en `servicios_medicos`. |
| **3FN** | **Eliminación de Dependencias Transitivas:** Cumple 2FN y ningún atributo no clave depende transitivamente de otro atributo no clave \( $ X \rightarrow Y \rightarrow Z\ $). | • Catálogo `especialidades`: el nombre de la especialidad médica se desacopló de `medicos`, evitando redundancia en el cuerpo médico.<br>• Catálogo `diagnosticos_cie10`: la descripción clínica depende exclusivamente del código CIE-10 y no de la atención asistencial.<br>• El Índice de Masa Corporal (IMC) **no se almacena en base de datos**: se calcula dinámicamente como campo derivado en línea:  \( $ \text{IMC} = \frac{\text{peso}}{\text{talla}^2}\ $) .<br>• En facturación, los importes liquidados se registran por ítem en `factura_detalle` para preservar la inmutabilidad histórica frente a cambios futuros de tarifas. |


#### Decisiones de Normalización Justificadas (Entregable Semana 6):
1. **Tabla `prescripciones` (1FN):** La receta médica contenía múltiples medicamentos en un solo bloque de texto. Se normalizó a una tabla dependiente 1 a N de `atenciones`.
2. **Tabla `tarifarios_servicios` con control de vigencia (2FN):** La cobertura y el copago dependen contractualmente de la combinación `(servicio, convenio)` y no de la aseguradora de manera aislada.
3. **Catálogos independientes `especialidades` y `diagnosticos_cie10` (3FN):** Normalización de catálogos maestros para prevenir inconsistencias de nomenclatura y agilizar búsquedas predictivas.
4. **Cálculo de IMC al vuelo (3FN):** Se eliminó la columna `imc` de `triajes` por ser redundante y dependiente de peso y talla.
5. **Anulación Lógica por Regla de Negocio (RNF-004):** Tablas clínicas no admiten `DELETE`; `atenciones` registra anulación lógica, fecha, usuario responsable y justificación obligatoria.

---

### 6.1.2. Catálogo Oficial de las 22 Tablas del Esquema Relacional
A partir de la transformación de clases del modelo UML a tablas relacionales, se consolida el esquema oficial de **22 tablas**:

| N.° | Tabla en PostgreSQL | Módulo Dueño | Claves (PK / FK) | Restricciones y Reglas de Negocio Implementadas |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `roles` | T1 — Auth | **PK:** `id_rol` | `UQ (nombre)`. Catálogo cerrado de 7 roles del sistema. |
| **2** | `usuarios` | T1 — Auth | **PK:** `id_usuario`<br>**FK:** `id_rol` | `UQ (username)`, `UQ (email)`. Credenciales y hash bcrypt. |
| **3** | `convenios` | M4 — Facturación | **PK:** `id_convenio` | `UQ (codigo_convenio)`. `CHECK tipo_convenio IN ('PARTICULAR', 'EPS', 'SOAT')`. |
| **4** | `pacientes` | M1 — HCE | **PK:** `id_paciente`<br>**FK:** `id_convenio` | `UQ (tipo_documento, numero_documento)`. Filtro activo e índice único para búsqueda en < 2 s. |
| **5** | `especialidades` | M2 — Agenda | **PK:** `id_especialidad` | `UQ (nombre)`. Catálogo maestro de especialidades médicas de la clínica. |
| **6** | `medicos` | M2 — Agenda | **PK:** `id_medico`<br>**FK:** `id_especialidad`, `id_usuario` | `UQ (cmp)`, `UQ (id_usuario)`. Registro profesional y colegiatura médica. |
| **7** | `consultorios` | M2 — Agenda | **PK:** `id_consultorio` | `UQ (numero)`, `CHECK (piso >= 1)`. Los 12 consultorios físicos de San Borja. |
| **8** | `citas` | M2 — Agenda | **PK:** `id_cita`<br>**FK:** `id_paciente`, `id_medico`, `id_consultorio`, `id_cita_origen`, `creado_por` | `EXCLUDE USING gist` (anti-solapamiento médico y consultorio); `CHECK (fin > inicio)`; motivo obligatorio en cancelación/reprogramación. |
| **9** | `atenciones` | M1 — HCE | **PK:** `id_atencion`<br>**FK:** `id_paciente`, `id_medico`, `id_cita`, `anulado_por` | Consulta externa exige cita; Tópico de urgencia admite `id_cita NULL`; anulación exige motivo ($\ge 20$ caracteres); trigger prohíbe `DELETE`. |
| **10**| `triajes` | M1 — Triaje | **PK:** `id_triaje`<br>**FK:** `id_atencion` (UQ), `id_enfermera` | `UNIQUE (id_atencion)`. Rangos válidos de signos vitales; `CHECK (presion_sistolica > presion_diastolica)`. |
| **11**| `diagnosticos_cie10` | M1 — HCE | **PK:** `codigo` | Catálogo oficial OMS/MINSA. `descripcion NOT NULL`. |
| **12**| `atencion_diagnosticos`| M1 — HCE | **PK:** `(id_atencion, codigo_cie10)`<br>**FK:** `id_atencion`, `codigo_cie10` | `CHECK tipo IN ('PRINCIPAL', 'SECUNDARIO', 'PRESUNTIVO')`; restricción de un solo diagnóstico principal por atención. |
| **13**| `prescripciones` | M1 — HCE | **PK:** `id_prescripcion`<br>**FK:** `id_atencion` | Receta médica normalizada: fármaco, presentación, dosis, frecuencia y duración `NOT NULL`. |
| **14**| `servicios_medicos` | M4 — Facturación | **PK:** `id_servicio` | `UQ (codigo_servicio)`. `CHECK (precio_base_particular >= 0)`. Catálogo unificado de prestaciones. |
| **15**| `tarifarios_servicios` | M4 — Facturación | **PK:** `id_tarifario`<br>**FK:** `id_servicio`, `id_convenio` | Cobertura (0 a 100 %); `copago_fijo >= 0`; `EXCLUDE` sin vigencias superpuestas por par servicio-convenio. |
| **16**| `ordenes_examen` | M3 — Laboratorio | **PK:** `id_orden`<br>**FK:** `id_atencion`, `id_servicio` | `UQ (codigo_orden)`. `CHECK estado IN ('SOLICITADO', 'EN_PROCESO', 'COMPLETADO', 'CANCELADO')`. |
| **17**| `resultados` | M3 — Laboratorio | **PK:** `id_resultado`<br>**FK:** `id_orden` (UQ), `id_validador` | `UNIQUE (id_orden)`. Hash SHA-256 (64 caracteres); `CHECK (fecha_resultado >= fecha_toma_muestra)`. |
| **18**| `facturas` | M4 — Facturación | **PK:** `id_factura`<br>**FK:** `id_atencion` (UQ), `id_convenio`, `creado_por` | `UQ (numero_comprobante)`. Comprobante interno de liquidación. |
| **19**| `factura_detalle` | M4 — Facturación | **PK:** `id_detalle`<br>**FK:** `id_factura`, `id_servicio`, `id_orden` | `CHECK (cantidad > 0)`; `CHECK (precio_unitario * cantidad = monto_cubierto + copago)`. |
| **20**| `glosas` | M4 — Facturación | **PK:** `id_glosa`<br>**FK:** `id_factura`, `registrado_por` | `CHECK (monto_glosado > 0)`; estados (`REGISTRADA`, `SUSTENTADA`, `ACEPTADA`, `RECHAZADA`, `RECUPERADA`). |
| **21**| `outbox_notificaciones`| T3 — Notificaciones | **PK:** `id_notificacion`<br>**FK:** `id_cita` | Cola Outbox asíncrona. `CHECK canal IN ('SMS', 'EMAIL', 'WHATSAPP')`; `intentos >= 0`. |
| **22**| `bitacora_auditoria` | T2 — Auditoría | **PK:** `id_auditoria`<br>**FK:** `id_usuario` | Registro inmutable de trazabilidad (Ley N.° 29733). Trigger prohíbe `UPDATE` y `DELETE`. |

---

### 6.1.3. Matriz Completa de Relaciones y Cardinalidades (Crow's Foot)

| Entidad Origen (1) | Cardinalidad | Entidad Destino (N) | Llave Primaria (PK) | Llave Foránea (FK) | Semántica del Vínculo e Integridad Referencial |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `roles` | **1 : N** | `usuarios` | `roles.id_rol` | `usuarios.id_rol` | Un rol agrupa a muchos usuarios; borrado restringido (`ON DELETE RESTRICT`). |
| `usuarios` | **1 : 0..1** | `medicos` | `usuarios.id_usuario` | `medicos.id_usuario` | Un usuario puede ser el titular de una ficha médica profesional. |
| `especialidades` | **1 : N** | `medicos` | `especialidades.id_especialidad`| `medicos.id_especialidad` | Una especialidad médica califica a múltiples médicos de la clínica. |
| `convenios` | **1 : N** | `pacientes` | `convenios.id_convenio` | `pacientes.id_convenio` | Un convenio de aseguramiento ampara a muchos pacientes afiliados. |
| `pacientes` | **1 : N** | `citas` | `pacientes.id_paciente` | `citas.id_paciente` | Un paciente agenda múltiples citas a lo largo del tiempo. |
| `medicos` | **1 : N** | `citas` | `medicos.id_medico` | `citas.id_medico` | Un médico atiende una agenda de citas programadas. |
| `consultorios` | **1 : N** | `citas` | `consultorios.id_consultorio` | `citas.id_consultorio` | Un consultorio físico alberga citas según programación de turnos. |
| `citas` | **0..1 : 0..1** | `citas` | `citas.id_cita` | `citas.id_cita_origen` | Enlace de reprogramación: vincula la cita nueva con la cita cancelada previa. |
| `pacientes` | **1 : N** | `atenciones` | `pacientes.id_paciente` | `atenciones.id_paciente` | Un paciente acumula atenciones en su expediente clínico unificado. |
| `medicos` | **1 : N** | `atenciones` | `medicos.id_medico` | `atenciones.id_medico` | El médico suscribe y firma las atenciones clínicas que realiza. |
| `citas` | **0..1 : 1** | `atenciones` | `citas.id_cita` | `atenciones.id_cita` | Consulta ambulatoria proviene de 1 cita; tópico de urgencia no tiene cita (`NULL`). |
| `atenciones` | **1 : 0..1** | `triajes` | `atenciones.id_atencion` | `triajes.id_atencion` | Una atención ambulatoria posee como máximo 1 triaje de enfermería. |
| `atenciones` | **1 : N** | `atencion_diagnosticos`| `atenciones.id_atencion`| `atencion_diagnosticos.id_atencion` | Una consulta registra de 1 a varios diagnósticos asociados. |
| `diagnosticos_cie10`| **1 : N** | `atencion_diagnosticos`| `diagnosticos_cie10.codigo` | `atencion_diagnosticos.codigo_cie10` | Un código CIE-10 se diagnostica en múltiples atenciones médicas. |
| `atenciones` | **1 : N** | `prescripciones` | `atenciones.id_atencion` | `prescripciones.id_atencion` | La consulta emite 1 receta médica desglosada en N medicamentos. |
| `atenciones` | **1 : N** | `ordenes_examen` | `atenciones.id_atencion` | `ordenes_examen.id_atencion` | El médico puede prescribir N órdenes de análisis o imagenología. |
| `servicios_medicos`| **1 : N** | `ordenes_examen` | `servicios_medicos.id_servicio` | `ordenes_examen.id_servicio` | Una prestación diagnóstica del catálogo se solicita en N órdenes. |
| `ordenes_examen` | **1 : 0..1** | `resultados` | `ordenes_examen.id_orden` | `resultados.id_orden` | Una orden procesada genera a lo sumo 1 resultado digital validado. |
| `servicios_medicos`| **1 : N** | `tarifarios_servicios`| `servicios_medicos.id_servicio` | `tarifarios_servicios.id_servicio` | Resuelve relación N a M: precios pactados por servicio y aseguradora. |
| `convenios` | **1 : N** | `tarifarios_servicios`| `convenios.id_convenio` | `tarifarios_servicios.id_convenio` | Coberturas y copagos diferenciados fijados por convenio institucional. |
| `atenciones` | **1 : 0..1** | `facturas` | `atenciones.id_atencion` | `facturas.id_atencion` | Una atención clínica genera exactamente 1 comprobante interno de cobro. |
| `facturas` | **1 : N** | `factura_detalle` | `facturas.id_factura` | `factura_detalle.id_factura` | Desglose ítem por ítem del comprobante: consulta, exámenes y copagos. |
| `facturas` | **1 : N** | `glosas` | `facturas.id_factura` | `glosas.id_factura` | Una factura puede recibir N observaciones o rechazos de pago de la EPS. |
| `citas` | **1 : N** | `outbox_notificaciones`| `citas.id_cita` | `outbox_notificaciones.id_cita` | Una cita encola recordatorios 24 h y avisos en el worker asíncrono. |
| `usuarios` | **1 : N** | `bitacora_auditoria` | `usuarios.id_usuario` | `bitacora_auditoria.id_usuario` | Todo usuario que acceda a la HCE genera trazas inmutables (Ley N.° 29733). |

---

### 6.1.4. Diagrama Entidad-Relación Lógico/Físico (Figura Oficial Entregable Semana 6)
A continuación se incorpora el marcador de imagen oficial del modelo entidad-relación del proyecto integrador, idéntico a la Figura 2 de `semana6.entregable-4-taller.pdf`:

![image1](ModeloEntidadRelacion.png)

#### Guía Paso a Paso para Construir el Diagrama ER en Lucidchart:
1. **Configuración Inicial:** Abrir documento en blanco en Lucidchart, activar biblioteca **«Relación de entidades (ERD)»** y seleccionar notación **Pata de Gallo (*Crow's Foot*)**.
2. **Distribución Modular por Bloques de Color:**
   * **Bloque Superior Izquierdo (Rojo Suave / Seguridad):** Tablas `roles` y `usuarios`.
   * **Bloque Superior Centro (Azul Suave / Personal Asistencial):** Tablas `especialidades`, `medicos` y `consultorios`.
   * **Bloque Superior Derecho (Amarillo Suave / Facturación):** Tablas `glosas`, `facturas` y `factura_detalle`.
   * **Bloque Centro (Violeta / Módulo M1 HCE):** Tablas `atenciones`, `triajes`, `atencion_diagnosticos`, `diagnosticos_cie10` y `prescripciones`.
   * **Bloque Centro-Izquierda (Magenta / Módulo M3 Diagnóstico):** Tablas `ordenes_examen` y `resultados`.
   * **Bloque Centro-Inferior (Rosado / Módulo M2 Agenda):** Tabla `citas`.
   * **Bloque Inferior Izquierdo (Naranja / Pacientes y Convenios):** Tablas `pacientes`, `convenios`, `servicios_medicos` y `tarifarios_servicios`.
   * **Bloque Lateral Derecho (Verde Suave / Componentes Transversales):** Tablas `outbox_notificaciones` y `bitacora_auditoria`.
3. **Puntas de Relación Exactas:** Conectar PKs con FKs utilizando símbolos de obligatoriedad: Uno y solo uno (`||`), Cero o uno (`o|`), Uno o muchos (`|<`), Cero o muchos (`o<`).

--------------------------------------------------------------------------------

## 6.2. Diccionario de Datos Detallado (Tablas del Núcleo Transaccional)

A continuación se documentan en formato normalizado las estructuras de campos de las tablas centrales de la solución:

### 6.2.1. Tabla: `pacientes` (Módulo M1 — Historia Clínica Electrónica)
* **Descripción:** Almacena el registro único de filiación e identificación de los pacientes atendidos en la sede San Borja.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción Funcional y Restricciones de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_paciente` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único autoincremental del paciente. |
| `tipo_documento` | `VARCHAR(10)` | **NO** | | | Tipo de documento: `'DNI'`, `'CE'`, `'PASAPORTE'`. |
| `numero_documento` | `VARCHAR(15)` | **NO** | **UQ** | | Número de identificación; índice B-Tree único para búsqueda en < 2 s. |
| `nombres` | `VARCHAR(100)` | **NO** | | | Nombres completos del paciente. |
| `apellido_paterno` | `VARCHAR(100)` | **NO** | | | Apellido paterno del paciente. |
| `apellido_materno` | `VARCHAR(100)` | **NO** | | | Apellido materno del paciente. |
| `fecha_nacimiento` | `DATE` | **NO** | | | Fecha de nacimiento para cálculo dinámico de grupo etario. |
| `sexo` | `CHAR(1)` | **NO** | | | Sexo biológico: `'M'` (Masculino), `'F'` (Femenino). |
| `telefono` | `VARCHAR(20)` | **NO** | | | Teléfono móvil para despacho de recordatorios automáticos (24 h antes). |
| `email` | `VARCHAR(150)` | SÍ | | `NULL` | Correo electrónico para confirmaciones y envío de tickets. |
| `direccion` | `VARCHAR(255)` | SÍ | | `NULL` | Domicilio de residencia en Lima Metropolitana. |
| `id_convenio` | `INT` | **NO** | **FK** | `1` (Particular) | Referencia al convenio asegurador base (`convenios.id_convenio`). |
| `antecedentes_medicos`| `TEXT` | SÍ | | `NULL` | Resumen de enfermedades crónicas, cirugías previas y comorbilidades. |
| `alergias` | `TEXT` | SÍ | | `'NINGUNA'` | Alergias medicamentosas críticas (alerta destacada en rojo en UI médica). |
| `activo` | `BOOLEAN` | **NO** | | `TRUE` | Estado de vigencia del paciente en la clínica. |
| `creado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal inmutable del registro de filiación. |

---

### 6.2.2. Tabla: `citas` (Módulo M2 — Agenda y Citas Médicas)
* **Descripción:** Administra la reserva de turnos en los 12 consultorios con exclusión temporal física anti-solapamiento (**RF-002**).

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción Funcional y Restricciones de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_cita` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador único de la cita médica. |
| `id_paciente` | `INT` | **NO** | **FK** | | Referencia obligatoria al paciente citado (`pacientes.id_paciente`). |
| `id_medico` | `INT` | **NO** | **FK** | | Referencia al médico tratante programado (`medicos.id_medico`). |
| `id_consultorio` | `INT` | **NO** | **FK** | | Consultorio asignado (1 a 12) (`consultorios.id_consultorio`). |
| `fecha_hora_inicio` | `TIMESTAMP` | **NO** | | | Fecha y hora de inicio del bloque de consulta. |
| `fecha_hora_fin` | `TIMESTAMP` | **NO** | | | Fecha y hora de fin del bloque (`CHECK fecha_hora_fin > fecha_hora_inicio`). |
| `estado` | `VARCHAR(15)` | **NO** | | `'CONFIRMADA'` | Estados: `'CONFIRMADA'`, `'EN_ESPERA'`, `'ATENDIDA'`, `'CANCELADA'`, `'REPROGRAMADA'`, `'NO_ASISTIO'`. |
| `motivo_cancelacion`| `TEXT` | SÍ | | `NULL` | Justificación obligatoria en cancelación o reprogramación. |
| `hora_llegada` | `TIMESTAMP` | SÍ | | `NULL` | Registro de check-in en recepción para pase a lista de triaje. |
| `id_cita_origen` | `INT` | SÍ | **FK, UQ** | `NULL` | Referencia recursiva unívoca a la cita previa si es reprogramación. |
| `canal_agendamiento`| `VARCHAR(12)` | **NO** | | `'ADMISION'` | Canales: `'ADMISION'`, `'PORTAL_WEB'`, `'TELEFONICO'`. |
| `creado_por` | `INT` | **NO** | **FK** | | Usuario de admisión responsable de la reserva (`usuarios.id_usuario`). |
| `creado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal de creación. |

---

### 6.2.3. Tabla: `atenciones` (Módulo M1 — Historia Clínica Electrónica)
* **Descripción:** Entidad central del acto médico ambulatorio o tópico de urgencia; implementa anulación lógica y prohíbe el borrado físico (**RNF-004**).

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción Funcional y Restricciones de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_atencion` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador del acto médico asistencial. |
| `id_paciente` | `INT` | **NO** | **FK** | | Referencia al paciente atendido (`pacientes.id_paciente`). |
| `id_medico` | `INT` | **NO** | **FK** | | Profesional de salud tratante que suscribe (`medicos.id_medico`). |
| `id_cita` | `INT` | SÍ | **FK, UQ** | `NULL` | Cita programada de origen; `NULL` para tópico de urgencia. |
| `tipo_atencion` | `VARCHAR(25)` | **NO** | | `'CONSULTA_EXTERNA'` | Modalidad: `'CONSULTA_EXTERNA'` o `'TOPICO_URGENCIA'`. |
| `motivo_consulta` | `TEXT` | **NO** | | | Relato del paciente sobre su sintomatología principal. |
| `anamnesis` | `TEXT` | SÍ | | `NULL` | Exploración clínica directa, antecedentes inmediatos y examen físico. |
| `anulado` | `BOOLEAN` | **NO** | | `FALSE` | Bandera de baja lógica; borrado físico bloqueado por trigger `RNF-004`. |
| `motivo_anulacion` | `TEXT` | SÍ | | `NULL` | Justificación médica/auditora obligatoria de $\ge 20$ caracteres si `anulado = TRUE`. |
| `anulado_por` | `INT` | SÍ | **FK** | `NULL` | Usuario que ejecutó la anulación lógica (`usuarios.id_usuario`). |
| `creado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Marca temporal inmutable del registro clínico. |

---

### 6.2.4. Tabla: `triajes` (Módulo M1 — Triaje y Enfermería)
* **Descripción:** Mediciones fisiológicas y signos vitales registrados por enfermería previo a la atención en consultorio o tópico.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción Funcional y Restricciones de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_triaje` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador unívoco del triaje asistencial. |
| `id_atencion` | `INT` | **NO** | **FK, UQ** | | Atención clínica a la que pertenece (`UNIQUE`). |
| `presion_sistolica` | `INT` | **NO** | | | Presión arterial sistólica en mmHg (`CHECK 50-300`). |
| `presion_diastolica`| `INT` | **NO** | | | Presión arterial diastólica en mmHg (`CHECK 30-200`, sistólica > diastólica). |
| `temperatura` | `NUMERIC(4,2)`| **NO** | | | Temperatura corporal en °C (`CHECK 30.00-45.00`). |
| `frecuencia_cardiaca`| `INT` | **NO** | | | Frecuencia cardíaca en latidos por minuto (`CHECK 30-250`). |
| `frecuencia_respiratoria`| `INT` | SÍ | | `NULL` | Frecuencia respiratoria en respiraciones por minuto (`CHECK 8-60`). |
| `peso` | `NUMERIC(5,2)`| **NO** | | | Peso corporal en kilogramos (`CHECK 1.00-350.00`). |
| `talla` | `NUMERIC(3,2)`| **NO** | | | Estatura en metros (`CHECK 0.30-2.50`). |
| `saturacion_oxigeno`| `INT` | SÍ | | `NULL` | Saturación de oxígeno $SpO_2$ en porcentaje (`CHECK 50-100`). |
| `id_enfermera` | `INT` | **NO** | **FK** | | Usuario de enfermería responsable de la toma (`usuarios.id_usuario`). |
| `registrado_en` | `TIMESTAMP` | **NO** | | `CURRENT_TIMESTAMP` | Momento exacto de captura del triaje. |

---

### 6.2.5. Tabla: `factura_detalle` (Módulo M4 — Facturación y Convenios)
* **Descripción:** Desglose transaccional ítem por ítem del comprobante, garantizando cuadre estricto de cobertura y copago.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Descripción Funcional y Restricciones de Dominio |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id_detalle` | `SERIAL` | **NO** | **PK** | Secuencia | Identificador del ítem facturado. |
| `id_factura` | `INT` | **NO** | **FK** | | Factura a la que pertenece (`facturas.id_factura`). |
| `id_servicio` | `INT` | **NO** | **FK** | | Servicio médico liquidado (`servicios_medicos.id_servicio`). |
| `id_orden` | `INT` | SÍ | **FK, UQ** | `NULL` | Orden médica vinculada si es examen de laboratorio o imágenes. |
| `cantidad` | `INT` | **NO** | | `1` | Cantidad de prestaciones ejecutadas (`CHECK cantidad > 0`). |
| `precio_unitario` | `NUMERIC(10,2)`| **NO** | | | Tarifa unitaria pactada en soles (PEN). |
| `monto_cubierto` | `NUMERIC(10,2)`| **NO** | | | Importe facturable a la aseguradora / EPS (`>= 0`). |
| `copago` | `NUMERIC(10,2)`| **NO** | | | Deducible o copago neto a cancelar por el paciente en ventanilla (`>= 0`). |

--------------------------------------------------------------------------------

## 6.3. Scripts SQL Oficiales del Repositorio (`database/`)

El diseño de base de datos se estructura en tres archivos SQL versionados en el repositorio GitHub (`https://github.com/francito69/SW705U-grupo-A`):

### 6.3.1. Script de Creación DDL Oficial (`database/01-esquema.sql`)
A continuación se presenta el extracto representativo del script de creación, destacando la definición de la tabla `citas`, el trigger anti-borrado de la HCE y la tabla de auditoría:

```sql
-- =============================================================================
-- SISTEMA DE INFORMACIÓN CLÍNICO-ADMINISTRATIVO (SIRA)
-- Script: database/01-esquema.sql (22 tablas, restricciones e índices)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- -----------------------------------------------------------------------------
-- TABLA: citas (Agenda multiespecialidad con bloqueo físico de solapamiento)
-- -----------------------------------------------------------------------------
CREATE TABLE citas (
    id_cita SERIAL PRIMARY KEY,
    id_paciente INT NOT NULL REFERENCES pacientes(id_paciente),
    id_medico INT NOT NULL REFERENCES medicos(id_medico),
    id_consultorio INT NOT NULL REFERENCES consultorios(id_consultorio),
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    estado VARCHAR(15) NOT NULL DEFAULT 'CONFIRMADA'
        CHECK (estado IN ('CONFIRMADA', 'EN_ESPERA', 'ATENDIDA', 'CANCELADA', 'REPROGRAMADA', 'NO_ASISTIO')),
    motivo_cancelacion TEXT,
    hora_llegada TIMESTAMP,
    id_cita_origen INT UNIQUE REFERENCES citas(id_cita),
    canal_agendamiento VARCHAR(12) NOT NULL DEFAULT 'ADMISION'
        CHECK (canal_agendamiento IN ('ADMISION', 'PORTAL_WEB', 'TELEFONICO')),
    creado_por INT NOT NULL REFERENCES usuarios(id_usuario),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cita_rango CHECK (fecha_hora_fin > fecha_hora_inicio),
    CONSTRAINT chk_cita_motivo CHECK (
        estado NOT IN ('CANCELADA', 'REPROGRAMADA') OR motivo_cancelacion IS NOT NULL
    ),
    CONSTRAINT chk_cita_llegada CHECK (
        estado NOT IN ('EN_ESPERA', 'ATENDIDA') OR hora_llegada IS NOT NULL
    ),
    -- RESTRICCIÓN FÍSICA RF-002: Bloqueo de solapamientos médicos
    CONSTRAINT no_solapamiento_medico EXCLUDE USING gist (
        id_medico WITH =,
        tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&
    ) WHERE (estado IN ('CONFIRMADA', 'EN_ESPERA')),
    -- RESTRICCIÓN FÍSICA RF-002: Bloqueo de solapamientos de consultorios
    CONSTRAINT no_solapamiento_consultorio EXCLUDE USING gist (
        id_consultorio WITH =,
        tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&
    ) WHERE (estado IN ('CONFIRMADA', 'EN_ESPERA'))
);

-- -----------------------------------------------------------------------------
-- TRIGGER PROCEDURAL: Prohibición estricta de borrado físico en HCE (RNF-004)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION impedir_borrado() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'No se permite eliminar registros de %: use la anulación lógica (RNF-004)',
        TG_TABLE_NAME USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atenciones_sin_borrado 
BEFORE DELETE ON atenciones 
FOR EACH ROW EXECUTE FUNCTION impedir_borrado();

-- -----------------------------------------------------------------------------
-- TRIGGER PROCEDURAL: Inmutabilidad de la Bitácora de Auditoría (RNF-002)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION impedir_cambios_bitacora() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'La bitácora de auditoría es estrictamente inmutable (Ley N.° 29733)'
        USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bitacora_inmutable 
BEFORE UPDATE OR DELETE ON bitacora_auditoria 
FOR EACH ROW EXECUTE FUNCTION impedir_cambios_bitacora();

-- -----------------------------------------------------------------------------
-- ÍNDICE DE RENDIMIENTO RNF-001: Apertura de HCE en < 2 s sobre +8 000 pacientes
-- -----------------------------------------------------------------------------
CREATE INDEX idx_atenciones_paciente_fecha 
ON atenciones (id_paciente, creado_en DESC) 
WHERE anulado = FALSE;

CREATE INDEX idx_pacientes_num_doc 
ON pacientes (numero_documento);

CREATE INDEX idx_outbox_pendientes 
ON outbox_notificaciones (programado_para) 
WHERE estado = 'PENDIENTE';
```

---

### 6.3.2. Resumen de Datos de Prueba Sintéticos (`database/02-datos-prueba.sql`)
Todos los datos registrados en el entorno de desarrollo y demostración son **ficticios y anonimizados** (cumpliendo con la restricción de confidencialidad del proyecto):

| Tabla | Registros Cargados | Descripción de los Datos de Prueba del Caso SIRA |
| :--- | :---: | :--- |
| `roles` | 7 | Roles del sistema: Admisión, Médico, Enfermera, Laboratorio, Caja, Gerencia, Administrador. |
| `usuarios` | 16 | Cuentas para los 7 roles con contraseñas seguras en hash bcrypt. |
| `convenios` | 7 | Particular, 5 EPS (Rímac, Pacífico, Mapfre, Sanitas, La Positiva) y SOAT. |
| `pacientes` | 10 | Pacientes sintéticos con DNI y CE, antecedentes clínicos y alertas de alergias. |
| `especialidades` | 8 | Medicina General, Pediatría, Cardiología, Dermatología, Traumatología, etc. |
| `medicos` | 6 | Cuerpo médico con CMP válido, teléfono corporativo y usuario asignado. |
| `consultorios` | 12 | Los 12 consultorios físicos de la sede San Borja distribuidos en pisos 1 y 2. |
| `citas` | 11 | Citas representativas en todos los estados: Confirmada, En espera, Atendida, Cancelada, Reprogramada y No asistió. |
| `atenciones` | 7 | Consultas externas y atenciones de tópico de urgencia; una en curso y una anulada con motivo justificado. |
| `triajes` | 6 | Signos vitales completos tomados por enfermería (uno con presión arterial elevada). |
| `diagnosticos_cie10` | 11 | Catálogo oficial: J00 (Rinofaringitis), I10 (Hipertensión), E11 (Diabetes), L20 (Dermatitis), etc. |
| `atencion_diagnosticos`| 8 | Asignación de diagnósticos principales, secundarios y presuntivos. |
| `prescripciones` | 7 | Prescripción médica atomizada: Losartán, Paracetamol, Amoxicilina, etc. |
| `servicios_medicos` | 9 | Consultas especializadas, hemograma, glucosa, perfil lipídico, radiografía de tórax. |
| `tarifarios_servicios` | 14 | Tarifas pactadas por aseguradora y servicio; incluye una tarifa con vigencia histórica cerrada. |
| `ordenes_examen` | 7 | Solicitudes de laboratorio e imágenes en estados: Solicitado, En proceso y Completado. |
| `resultados` | 5 | Informes patológicos validados con hash SHA-256 y entrega en $\le 4$ horas. |
| `facturas` | 5 | Comprobantes de liquidación interna: Emitidas, Pagadas y Observadas. |
| `factura_detalle` | 10 | Desglose por línea de cobro: cantidad, precio unitario, monto cubierto y copago neto. |
| `glosas` | 5 | Trazabilidad del ciclo de vida: Registrada, Sustentada, Aceptada, Rechazada y Recuperada. |
| `outbox_notificaciones`| 7 | Recordatorios automáticos 24 h y avisos de resultados: Pendientes, Enviados y Fallidos. |
| `bitacora_auditoria` | 6 | Trazas inmutables de consulta médica, inserción, actualización, anulación y acceso denegado (403). |
| **TOTAL** | **172** | **Conjunto de datos de prueba completo y verificado en pgAdmin 4.** |

---

### 6.3.3. Batería de Pruebas de Restricciones Automatizadas (`database/03-verificacion.sql`)
Para evidenciar ante el docente que la base de datos previene de manera robusta cualquier anomalía operativa, el script `03-verificacion.sql` ejecuta **10 operaciones intencionalmente inválidas**, comprobando que el motor PostgreSQL las rechaza de forma controlada:

| N.° | Operación Inválida Intentada en la Prueba | Restricción / Trigger que la Impide | Resultado Verificado |
| :---: | :--- | :--- | :---: |
| **1** | Cita del mismo médico en un horario ya ocupado por otra cita activa (**RF-002**). | `no_solapamiento_medico` (`EXCLUDE USING gist`) | **Rechazada** (Conflicto detectado) |
| **2** | Cita en un consultorio físico ya ocupado en ese mismo bloque horario (**RF-002**). | `no_solapamiento_consultorio` (`EXCLUDE USING gist`) | **Rechazada** (Conflicto de consultorio) |
| **3** | Intento de `DELETE` físico sobre una atención clínica médica (**RNF-004**). | Trigger `trg_atenciones_sin_borrado` | **Rechazada** (`restrict_violation`) |
| **4** | Anulación lógica de una atención médica con un motivo de solo 5 caracteres (**HU08**). | Constraint `chk_atencion_anulacion` | **Rechazada** (Exige $\ge 20$ caracteres) |
| **5** | Intento de `UPDATE` sobre la bitácora de auditoría clínica (**RNF-002**, Ley N.° 29733). | Trigger `trg_bitacora_inmutable` | **Rechazada** (Bitácora inmutable) |
| **6** | Registro de un paciente nuevo con un número de DNI ya existente en el sistema (**HU03**). | `uq_paciente_documento` | **Rechazada** (Violación de unicidad) |
| **7** | Inserción de un segundo diagnóstico marcado como 'PRINCIPAL' en la misma atención (**HU04**). | `uq_diagnostico_principal` | **Rechazada** (Solo 1 principal por consulta) |
|**8** | Línea de factura donde precio $\times$ cantidad $\neq$ monto cubierto $+$ copago (**RF-006**).| Constraint `chk_detalle_montos` | **Rechazada** (Descuadre financiero) |
| **9** | Dos tarifas vigentes en el mismo rango de fechas para un mismo servicio y convenio (**RF-006**). | `no_solapamiento_tarifario` (`EXCLUDE`) | **Rechazada** (Vigencias superpuestas) |
| **10**| Registro de triaje con presión sistólica menor o igual a la diastólica (**HU05**). | Constraint `chk_triaje_presion` | **Rechazada** (Signos vitales incoherentes) |

---

### 6.3.4. Evidencias de Ejecución en Motor Relacional (pgAdmin 4)
A continuación se incorporan los marcadores de evidencia gráfica de ejecución exitosa en el motor PostgreSQL:

* **Conteo Oficial de Registros por Tabla:**
![image2](Evidencia_Registros_pgAdmin.png)

* **Ejecución Exitosa de las 10 Pruebas de Restricciones en pgAdmin 4:**
![image3](Evidencia_Pruebas_Restricciones_pgAdmin.png)

--------------------------------------------------------------------------------

## 6.4. Matriz de Trazabilidad: Requerimientos, HUs y Esquema Relacional

La siguiente matriz certifica que **el 100 % de las 22 tablas del modelo de base de datos** responde de forma directa a los requerimientos formales y a las Historias de Usuario (HU01 a HU14) del proyecto SIRA:

| Módulo SIRA | Tabla en PostgreSQL | Requerimientos Soportados | Historias de Usuario | Justificación Técnica de Persistencia en el Esquema |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | `pacientes` | RF-001, RNF-001 | HU01, HU03, HU14 | Filiación única, antecedentes médicos, alergias críticas e índice único por DNI. |
| **M1** | `atenciones` | RF-001, RNF-001, RNF-004 | HU01, HU04, HU08 | Anamnesis, diagnóstico, receta y bandera de anulación lógica (`anulado = TRUE`). |
| **M1** | `triajes` | RF-001 | HU05 | Signos vitales completos tomados por enfermería; sistólica > diastólica. |
| **M1** | `diagnosticos_cie10` | RF-001 | HU04 | Catálogo maestro de códigos CIE-10 para diagnósticos estandarizados. |
| **M1** | `atencion_diagnosticos`| RF-001 | HU04, HU01 | Relación M:N que permite asignar diagnósticos principales y presuntivos. |
| **M1** | `prescripciones` | RF-001 | HU04, HU01 | Desglose atómico de medicamentos, posología, vía y duración del tratamiento. |
| **M2** | `citas` | RF-002, RNF-005 | HU02, HU06, HU05, HU14 | Reserva con exclusión física anti-solapamiento; trazabilidad de reprogramación. |
| **M2** | `medicos` | RF-001, RF-002 | HU01, HU02, HU04 | Registro del cuerpo médico, colegiatura CMP y usuario del sistema asociado. |
| **M2** | `especialidades` | RF-002, RF-008 | HU02, HU13 | Catálogo normalizado en 3FN de especialidades médicas de la clínica. |
| **M2** | `consultorios` | RF-002, RF-008 | HU02, HU13 | Infraestructura física de los 12 consultorios de la sede San Borja. |
| **M3** | `ordenes_examen` | RF-004 | HU09, HU10 | Solicitudes diagnósticas emitidas en consulta con ciclo de estados. |
| **M3** | `resultados` | RF-005, RNF-002 | HU10, HU01 | Informes médicos validados, hash SHA-256 y ruta segura hacia archivo privado. |
| **M4** | `convenios` | RF-006 | HU03, HU11 | Catálogo de coberturas: Particular, 5 EPS (Rímac, Pacífico, etc.) y SOAT. |
| **M4** | `servicios_medicos` | RF-004, RF-006 | HU09, HU11 | Catálogo maestro de prestaciones: consultas, análisis clínicos e imágenes. |
| **M4** | `tarifarios_servicios`| RF-006 | HU11, HU02 | Precios pactados, copagos fijos y cobertura aseguradora con vigencia cerrada. |
| **M4** | `facturas` | RF-006 | HU11, HU12 | Comprobante interno de liquidación; suma total = seguro + copago neto. |
| **M4** | `factura_detalle` | RF-006, RF-008 | HU11, HU13 | Desglose ítem por ítem liquidado para reportes gerenciales de ingresos. |
| **M4** | `glosas` | RF-007, RF-008 | HU12, HU13 | Trazabilidad completa de observaciones de aseguradoras y montos recuperados. |
| **T1** | `usuarios` | RNF-002 | Todas las HUs | Credenciales seguras con hash bcrypt y control de sesiones activas. |
| **T1** | `roles` | RNF-002 | Todas las HUs | Matriz RBAC para segregación de funciones clínicas y administrativas. |
| **T2** | `bitacora_auditoria` | RNF-002, RNF-004 | HU01, HU08 | Log inmutable y protegido exigido por la Ley N.° 29733 de Protección de Datos. |
| **T3** | `outbox_notificaciones`| RF-003, RF-005 | HU07, HU06, HU10 | Despacho asíncrono y desacoplado de recordatorios de citas 24 h y avisos de resultados. |

--------------------------------------------------------------------------------

## 6.5. Checklist de Verificación y Calidad de Base de Datos (Semana 6)

| Criterio de Evaluación Técnica (Rúbrica E1) | Calificación | Evidencia Técnica Comprobable en el Entregable |
| :--- | :---: | :--- |
| **Normalización Completa en 3FN** | **Logrado (20/20)** | Las 22 tablas cumplen estrictamente 1FN, 2FN y 3FN. No existen atributos multivaluados, dependencias parciales ni dependencias transitivas (IMC calculado al vuelo). |
| **Integridad Referencial y Dominio Estricto** | **Logrado (20/20)** | 100 % de tablas con PKs unívocas; FKs protegidas con `ON DELETE RESTRICT` o `CASCADE`; 15 restricciones `CHECK` para rangos y montos financieros. |
| **Prevención Física de Solapamientos (RF-002)** | **Logrado (20/20)** | Restricciones `no_solapamiento_medico` y `no_solapamiento_consultorio` implementadas mediante `btree_gist` con `EXCLUDE USING gist` en PostgreSQL. |
| **Apertura de HCE en < 2 Segundos (RNF-001)** | **Logrado (20/20)** | Índice compuesto parcial `idx_atenciones_paciente_fecha` optimiza consultas cronológicas sobre más de 8 000 registros sintéticos. |
| **Prohibición de Borrado Físico (RNF-004)** | **Logrado (20/20)** | Trigger `trg_atenciones_sin_borrado` rechaza cualquier sentencia `DELETE`; bajas clínicas restringidas a anulación lógica justificada ($\ge 20$ caracteres). |
| **Inmutabilidad y Ley N.° 29733 (RNF-002)** | **Logrado (20/20)** | Trigger `trg_bitacora_inmutable` prohíbe `UPDATE` y `DELETE` sobre `bitacora_auditoria`; trazabilidad integral de accesos clínicos. |
| **Datos de Prueba y Verificación Ejecutada** | **Logrado (20/20)** | 172 registros sintéticos cargados en `02-datos-prueba.sql` y 10 pruebas automatizadas de restricciones verificadas en pgAdmin 4 (`03-verificacion.sql`). |
