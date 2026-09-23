# 3. Especificacion de Requerimientos de Software (ERS)

## 3.1. Proposito y alcance

Este documento especifica los requerimientos del **Sistema de Informacion Clinico-Administrativo (SIRA)** para la sede San Borja de la Clinica San Rafael S.A.C. Su objetivo es convertir la vision del proyecto en funcionalidades verificables, requerimientos no funcionales, historias de usuario y un backlog inicial priorizado.

El alcance se organiza en los siguientes modulos:

| Modulo | Nombre | Sprint | Prioridad |
| --- | --- | --- | --- |
| M1 | Historia Clinica Electronica (HCE) | Sprint 1 | Imprescindible |
| M2 | Agenda y Citas | Sprint 1 | Imprescindible |
| M3 | Laboratorio e Imagenes | Sprint 2 | Imprescindible |
| M4 | Facturacion y Convenios | Sprint 2 | Imprescindible |
| M5 | Reportes Gerenciales | Sprint 2 | Imprescindible |
| M6 | Portal del Paciente y Telemedicina basica | Sprint 2 | Deseable |

Los requerimientos se basan en el Acta de Constitucion, el Documento de Vision y el avance de la Semana 3. Las pruebas y demostraciones utilizaran datos ficticios o anonimizados.

## 3.2. Actores y necesidades

| Actor | Necesidad principal | Modulo relacionado |
| --- | --- | --- |
| Admision / Recepcion | Registrar y localizar pacientes, validar su convenio y gestionar citas sin cruces de horario. | M1, M2 |
| Medico tratante | Consultar el expediente completo, registrar la atencion y emitir ordenes de laboratorio o imagenes. | M1, M2, M3 |
| Enfermera | Registrar triaje y signos vitales, y consultar la informacion clinica autorizada. | M1 |
| Personal de laboratorio | Recibir ordenes, registrar su ejecucion y cargar resultados digitales. | M3 |
| Cajero / Facturacion | Emitir comprobantes, calcular copagos y dar seguimiento a glosas. | M4 |
| Gerencia medica | Consultar indicadores para decidir sobre horarios, personal y convenios. | M5 |
| Paciente | Recibir confirmaciones y recordatorios, consultar resultados y, si se habilita M6, agendar en linea. | M2, M3, M6 |

## 3.3. Requerimientos funcionales

| ID | Descripcion | Modulo | Prioridad |
| --- | --- | --- | --- |
| RF01 | El sistema debe registrar, buscar y desplegar la Historia Clinica Electronica unificada del paciente, integrando antecedentes, atenciones de distintas especialidades, diagnosticos CIE-10 y prescripciones. | M1 - HCE | Must |
| RF02 | El sistema debe gestionar la disponibilidad de agenda para los 12 consultorios y validar en tiempo real el bloqueo de solapamientos entre medicos, horarios y consultorios. | M2 - Agenda y Citas | Must |
| RF03 | El sistema debe emitir y enviar notificaciones o recordatorios de citas al paciente por correo electronico o SMS con un minimo de 24 horas de anticipacion. | M2 - Agenda y Citas | Must |
| RF04 | El sistema debe permitir al medico tratante emitir ordenes digitales de laboratorio e imagenes asociadas a la consulta actual e integradas a la HCE. | M3 - Laboratorio e Imagenes | Must |
| RF05 | El sistema debe permitir al personal de laboratorio cargar y adjuntar resultados digitales a la orden del paciente, notificando automaticamente al medico tratante y al expediente del paciente. | M3 - Laboratorio e Imagenes | Must |
| RF06 | El sistema debe calcular y emitir comprobantes de cobro aplicando automaticamente el tarifario vigente segun el convenio del paciente (Particular, EPS 1-5 o SOAT) y determinando el valor de copago. | M4 - Facturacion y Convenios | Must |
| RF07 | El sistema debe registrar las glosas emitidas por las EPS o aseguradoras y permitir el seguimiento de su estado de sustentacion y conciliacion. | M4 - Facturacion y Convenios | Must |
| RF08 | El sistema debe presentar un dashboard gerencial con indicadores interactivos de ocupacion de consultorios, tiempo promedio de espera, porcentaje de inasistencia e ingresos por especialidad o convenio. | M5 - Reportes Gerenciales | Must |

## 3.4. Requerimientos no funcionales

| ID | Descripcion | Categoria | Verificacion |
| --- | --- | --- | --- |
| RNF01 | La historia clinica de un paciente debe abrirse en menos de 2 segundos, incluso con una base de 8 000 pacientes registrados. | Rendimiento | Ejecutar pruebas de carga con JMeter y verificar los indices necesarios en la base de datos. |
| RNF02 | El sistema debe controlar el acceso por rol (RBAC) y cifrar las comunicaciones con HTTPS, cumpliendo la Ley N.° 29733 de Proteccion de Datos Personales. | Seguridad | Revisar la matriz de accesos y comprobar mediante inspeccion de red que el trafico viaje cifrado. |
| RNF03 | La plataforma debe estar disponible al menos el 99.5 % del horario de atencion de la clinica, de lunes a sabado, de 7:00 a. m. a 9:00 p. m. | Disponibilidad | Monitorear el uptime del servidor y revisar los registros de disponibilidad. |
| RNF04 | Ningun registro clinico se puede borrar fisicamente de la base de datos; toda anulacion debe conservar el usuario, la fecha, la hora y el motivo. | Trazabilidad | Probar el borrado logico y revisar el registro correspondiente en la bitacora de auditoria. |
| RNF05 | La interfaz debe adaptarse a distintos tamanos de pantalla y permitir registrar una cita en un maximo de 3 pasos desde la pantalla principal de admision. | Usabilidad | Ejecutar una prueba con un usuario simulado, contando pasos y tiempo de agendamiento. |

## 3.5. Historias de usuario y criterios de aceptacion

### HU01 - Consulta de HCE unificada (8 puntos)

**Como** medico tratante, **quiero** consultar la historia clinica unificada de un paciente con el historial completo de todas las especialidades, **para** conocer sus antecedentes y atenciones previas sin cometer errores de medicacion o diagnosticos duplicados.

**Criterio de aceptacion:** Dado un paciente con consultas registradas en mas de una especialidad, cuando el medico busca y abre su expediente, entonces el sistema muestra todas las entradas ordenadas cronologicamente en menos de 2 segundos, incluyendo antecedentes, diagnosticos CIE-10, alergias y prescripciones.

### HU02 - Agendamiento con bloqueo de solapamientos (5 puntos)

**Como** personal de admision, **quiero** agendar una cita verificando la disponibilidad consolidada de medicos y consultorios, **para** reducir el tiempo de atencion telefonica y evitar cruces de horarios.

**Criterio de aceptacion:** Dado un paciente que solicita una cita para una especialidad y fecha, cuando el operador selecciona medico, consultorio y horario, entonces el sistema valida que no exista solapamiento, registra la cita en menos de 3 minutos y emite una confirmacion.

### HU03 - Carga de resultados de laboratorio e imagenes (5 puntos)

**Como** personal de laboratorio, **quiero** adjuntar resultados digitales asociados a una orden medica, **para** que esten disponibles de inmediato en la historia clinica del paciente.

**Criterio de aceptacion:** Dado un examen procesado correspondiente a una orden activa, cuando el analista sube el documento y marca la orden como "Completada", entonces el resultado se adjunta a la HCE en menos de 4 horas desde la toma de muestra y se notifica al medico tratante.

### HU04 - Facturacion por convenio y copago (8 puntos)

**Como** cajero o facturador, **quiero** emitir el comprobante aplicando automaticamente el tarifario del convenio del paciente, **para** cobrar el copago correcto y evitar glosas posteriores.

**Criterio de aceptacion:** Dado un paciente con convenio activo de EPS o SOAT, cuando el cajero selecciona el servicio y genera el comprobante, entonces el sistema calcula la cobertura, determina el copago exacto y registra la liquidacion para la aseguradora.

### HU05 - Dashboard gerencial (5 puntos)

**Como** gerencia medica, **quiero** consultar un dashboard interactivo con indicadores de ocupacion de consultorios e inasistencia, **para** tomar decisiones sobre turnos y convenios.

**Criterio de aceptacion:** Dado un usuario autenticado con rol de Gerencia Medica, cuando accede a reportes y selecciona un rango de fechas, entonces el sistema muestra graficos interactivos de ocupacion por consultorio, tiempos promedio de espera y porcentaje de inasistencia.

### HU06 - Registro de triaje y signos vitales (3 puntos)

**Como** enfermera, **quiero** registrar el triaje del paciente antes de la consulta, **para** que el medico tenga esos datos al momento de atenderlo.

**Criterio de aceptacion:** Dado un paciente que hizo check-in y espera su turno, cuando la enfermera registra presion, temperatura, frecuencia cardiaca y peso, entonces los datos quedan guardados en la atencion del dia y son visibles para el medico al abrir el expediente.

### HU07 - Recordatorio de cita (5 puntos)

**Como** paciente, **quiero** recibir un recordatorio de mi cita un dia antes, **para** no olvidarla y poder avisar si no puedo asistir.

**Criterio de aceptacion:** Dado que el paciente tiene una cita para el dia siguiente, cuando faltan 24 horas para la cita, entonces recibe un correo electronico o SMS con la fecha, hora y medico.

### HU08 - Registro y seguimiento de glosas (5 puntos)

**Como** cajero, **quiero** registrar cuando una EPS observa un pago y actualizar su estado, **para** no perder de vista los cobros pendientes.

**Criterio de aceptacion:** Dado un comprobante observado por una EPS, cuando el cajero registra el motivo y monto observado, entonces la glosa queda en estado "registrada" y puede avanzar a sustentada, aceptada, rechazada o recuperada.

### HU09 - Portal de paciente y consulta virtual (8 puntos)

**Como** paciente, **quiero** agendar mi cita desde un portal y contar con una opcion de consulta virtual para casos no urgentes, **para** evitar llamadas y acceder a la atencion desde el portal.

**Criterio de aceptacion:** Dado un paciente autenticado, cuando elige especialidad, medico y horario libre, entonces la cita queda agendada como en admision y, si es virtual, puede ingresar a la videollamada desde el portal.

### Validacion INVEST

Las historias se consideran **valiosas**, **estimables** y **testeables** porque describen un usuario, un beneficio, un alcance acotado, puntos de historia y un criterio Dado/Cuando/Entonces. Son negociables porque el detalle de canales, estados y pantallas puede ajustarse durante la planificacion. La independencia entre historias debe revisarse al descomponer la implementacion: HU03 depende tecnicamente de una orden medica y HU07 de una cita registrada, aunque ambas conservan valor funcional propio.

## 3.6. Product backlog priorizado

| Orden | ID | Historia (resumen) | Modulo | MoSCoW | Sprint | Puntos |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | HU01 | Consulta de Historia Clinica Unificada por el medico | M1 - HCE | Must | Sprint 1 | 8 |
| 2 | HU02 | Agendamiento de cita con bloqueo de solapamientos | M2 - Agenda | Must | Sprint 1 | 5 |
| 3 | HU06 | Registro de triaje y signos vitales por enfermeria | M1 - HCE | Must | Sprint 1 | 3 |
| 4 | HU07 | Envio de recordatorios automaticos de citas | M2 - Agenda | Must | Sprint 1 | 5 |
| 5 | HU03 | Carga e integracion de resultados de laboratorio e imagenes | M3 - Laboratorio | Must | Sprint 2 | 5 |
| 6 | HU04 | Facturacion por convenio y calculo de copago | M4 - Facturacion | Must | Sprint 2 | 8 |
| 7 | HU05 | Dashboard gerencial de ocupacion, espera e inasistencia | M5 - Reportes | Must | Sprint 2 | 5 |
| 8 | HU08 | Registro y seguimiento de glosas | M4 - Facturacion | Should | Sprint 2 | 5 |
| 9 | HU09 | Agendamiento en linea y consulta mediante portal paciente | M6 - Telemedicina | Could | Sprint 2 | 8 |

**Totales de referencia:** Sprint 1: 21 puntos. Sprint 2: 31 puntos. Total: 52 puntos.

## 3.7. Trazabilidad resumida

| Hallazgo del problema | Requerimientos / historias relacionadas |
| --- | --- |
| Atencion telefonica saturada e inasistencia del 18 % | RF02, RF03, RF08; HU02, HU07, HU09 |
| Expediente clinico fragmentado y riesgo de medicacion | RF01; HU01, HU06 |
| Retraso o perdida de resultados | RF04, RF05; HU03 |
| Errores de facturacion y glosas | RF06, RF07; HU04, HU08 |
| Falta de metricas gerenciales | RF08; HU05 |

## 3.8. Reglas y restricciones de negocio

- La solucion se desplegara para una sola sede, San Borja, y operara en espanol, zona horaria `America/Lima` y moneda PEN.
- El acceso a la HCE se controla por rol y queda registrado en auditoria; no se permite el borrado fisico de registros clinicos.
- Los comprobantes, tarifarios y glosas son de control interno; no se incluye integracion electronica con SUNAT ni con los sistemas de las EPS.
- No se incluyen hospitalizacion, cirugia ambulatoria, inventario o dispensacion de farmacia, aplicaciones moviles nativas ni migracion masiva de historicos.
- M6 queda condicionado a la finalizacion de los modulos imprescindibles M1-M5.
