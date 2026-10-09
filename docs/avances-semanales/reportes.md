# Reporte de consistencia de avances

## Revision Semana 2 - Semana 3

Fecha de revision: 23 de septiembre de 2026.

Se compararon el avance de Semana 2, el avance de Semana 3 y la especificacion de requerimientos documentada en `docs/entregable-1/03-especificacion-requerimientos-ERS.md`.

### Consistencias confirmadas

- El producto mantiene el mismo nombre y proposito: Sistema de Informacion Clinico-Administrativo (SIRA) para la Clinica San Rafael S.A.C.
- Se conserva la sede San Borja, el contexto de datos fragmentados, la inasistencia base del 18 %, la demora actual de hasta 48 horas y la operacion con 5 EPS(Entidades Prestadoras de Salud) y SOAT.
- Los modulos M1 a M5, sus prioridades y la condicion deseable de M6 coinciden con el acta, la vision y el PDF de Semana 3.
- Los actores de negocio son consistentes: admision, medico, enfermera, laboratorio, caja, gerencia medica y paciente.
- Los objetivos de rendimiento, seguridad, trazabilidad y usabilidad del ERS se relacionan con los objetivos SMART y con los riesgos identificados en Semana 2.

### Observaciones y posibles cambios

1. **Cobertura del Sprint 1:** el PDF incluye 9 historias, pero solo HU01, HU02, HU06 y HU07 pertenecen al Sprint 1. La plantilla solicita al menos 8 historias para el Sprint 1 de M1 y M2. Debe confirmarse si se agregaran cuatro historias de M1/M2 o si la consigna se interpretara como ocho historias totales del avance.
2. **Trazabilidad de HU06:** la historia de registro de triaje y signos vitales no tiene un requerimiento funcional propio entre RF01-RF08. Se recomienda crear un RF adicional para el registro y consulta de signos vitales, o indicar formalmente que forma parte de RF01.
3. **Notificacion al paciente por resultados:** el acta y la vision indican que M3 notifica al medico y al paciente, pero RF05 y HU03 solo mencionan al medico. Debe confirmarse si la notificacion al paciente es obligatoria, opcional o se elimina del alcance.
4. **Disponibilidad:** Semana 3 fija 99.5 % de disponibilidad de toda la plataforma en horario de atencion, mientras que la informacion dada por la plantilla menciona especificamente disponibilidad de emergencia y agenda. Conviene validar si el 99.5 % aplica a todos los modulos o solo a esos servicios criticos.
5. **Canal de telemedicina:** HU09 incorpora videollamada. El alcance de Semana 2 solo define una consulta virtual basica, por lo que debe definirse si se implementara videollamada real o un acceso simulado/enlace externo.
6. **Terminologia de facturacion:** el caso base habla de 5 EPS y aseguradoras, mientras que RF06 detalla EPS 1-5 y SOAT. Conviene cerrar el catalogo de convenios y confirmar si SOAT cuenta dentro o fuera de las cinco EPS.

Estas observaciones no cambian automaticamente el alcance aprobado; quedan registradas para validacion del equipo y del Product Owner antes de cerrar la linea base del ERS y del backlog.

---

## Revision Semana 5 - Consistencia de arquitectura

Fecha de revision: 1 de octubre de 2026.

Se contrasto la propuesta del SAD (secciones 5.1-5.5) con el Acta de Constitucion, el Documento de Vision, la ERS, los modelos UML de Semana 4, la guia de Semana 5 y el README del repositorio.

### Consistencias confirmadas

- La arquitectura propuesta es web, para una sola sede (San Borja), y mantiene M1-M5 como imprescindibles y M6 como deseable y condicionado a los modulos anteriores.
- El monolito modular en capas con API REST responde al tamano actual del equipo (tres integrantes), al horizonte academico y a la ausencia de una necesidad demostrada de despliegue independiente por modulo. Microservicios quedan como alternativa futura, no como alcance actual.
- Los modulos y los escenarios del SAD corresponden a los actores, casos de uso, clases e historias HU01-HU08. M6 se conserva como extension opcional de HU09.
- El almacenamiento de metadatos en PostgreSQL y de archivos de resultados en almacenamiento privado es coherente con la clase Resultado y con la exclusion de PACS/DICOM. No se incorporan integraciones con SUNAT ni con sistemas de EPS.
- Los atributos de calidad del SAD conservan los criterios medibles RNF01-RNF05, incluida la apertura de HCE en menos de 2 segundos con 8 000 pacientes y la disponibilidad de 99.5 % en el horario definido.
- El stack se documenta como propuesta, no como tecnologia ya adoptada o desplegada; el proveedor cloud y el servicio de correo/SMS quedan pendientes de seleccion.

### Observaciones que requieren decision o cierre

1. **Triaje en la ERS:** HU06 y el modelo de clases incluyen el registro de signos vitales, pero RF01-RF08 no lo identifica expresamente. La arquitectura lo ubica en M1 como parte del alcance de HU06, sin crear un RF nuevo. Confirmar si se amplia RF01 o se agrega un requerimiento funcional.
2. **Notificacion del resultado al paciente:** la vision y el diagrama de casos de uso sugieren notificacion al paciente, mientras que RF05 y HU03 requieren notificar al medico y vincular el resultado a la HCE. Definir si el aviso al paciente es obligatorio, opcional y/o dependiente de M6, y actualizar la ERS antes de implementarlo.
3. **Disponibilidad:** RNF03 indica 99.5 % para la plataforma durante todo el horario de atencion. Confirmar que el criterio aplica a todos los modulos, no solo agenda y emergencia, y definir como se medira en la demostracion academica.
4. **Multiplicidades UML:** la guia de Semana 4 declara que las relaciones deben mostrar cardinalidades, pero en la imagen compartida del diagrama de clases no se distinguen multiplicidades en los extremos. Revisar el archivo fuente y hacerlas visibles en la version final.
5. **Stack y entorno productivo:** FastAPI, React/TypeScript, PostgreSQL y los servicios auxiliares son una propuesta del SAD, pues no se encontro una decision tecnologica adoptada en los documentos revisados. El equipo debe ratificar el stack y seleccionar hosting/notificaciones antes de fijar dependencias o tratar datos reales.
6. **M6 y consulta virtual:** HU09 menciona videollamada, pero la arquitectura no introduce un proveedor de videoconferencia ni lo da por incluido. Aclarar si la demostracion usara enlace externo, simulacion o si esa funcionalidad queda fuera del alcance del semestre.

Estas observaciones no modifican por si mismas el alcance aprobado. Se recomienda cerrarlas con el Product Owner/equipo y actualizar la ERS o los modelos UML cuando corresponda, preservando la trazabilidad entre documentos.

---

## Revision Semana 5 - Trazabilidad de requisitos a arquitectura

Fecha de revision: 1 de octubre de 2026.

Esta revision verifica que los requisitos y actores clave tengan un punto de realizacion identificable en el SAD. No constituye una prueba de implementacion: la arquitectura esta en estado de propuesta.

| Elemento de origen | Soporte descrito en el SAD | Estado de trazabilidad |
| --- | --- | --- |
| RF01 / HU01 - HCE unificada | M1, consultas PostgreSQL, autorizacion RBAC, auditoria y escenario S1 | Cubierto en el diseno; RNF01 requiere medicion con carga de prueba. |
| RF02 / HU02 - agenda sin solapamientos | M2, confirmacion en servidor, transaccion y flujo de conflicto del escenario S2 | Cubierto en el diseno; probar solicitudes concurrentes. |
| RF03 / HU07 - recordatorio con 24 horas | Planificador, trabajador y adaptador correo/SMS; escenario S2 | Cubierto en el diseno; proveedor y reintentos pendientes. |
| RF04-RF05 / HU03 - orden y resultado digital | M3, PostgreSQL para metadatos, almacenamiento privado y escenario S3 | Cubierto para medico y HCE; notificacion al paciente pendiente de aclaracion. |
| RF06-RF07 / HU04 y HU08 - cobertura, copago y glosa | M4, datos relacionales y escenario S4 | Cubierto en el diseno; tarifarios vigentes y casos de prueba dependen de datos del negocio. |
| RF08 / HU05 - dashboard | M5, consultas agregadas, rango de fechas y autorizacion para Gerencia medica | Cubierto en el diseno; definicion exacta de formulas debe validarse con el Product Owner. |
| HU06 - triaje y signos vitales | M1, flujo de atencion clinica y modelo de dominio | Trazabilidad existente a historia/modelo, pero falta un RF explicito en la ERS. |
| RNF01 - rendimiento de HCE | Indices/paginacion propuestos y prueba JMeter con 8 000 pacientes | Criterio y metodo identificados; resultado aun no verificado. |
| RNF02 - RBAC y HTTPS | API, autorizacion de servidor, TLS y verificacion de matriz de roles | Mecanismos especificados; prueba de red y de permisos pendiente. |
| RNF03 - disponibilidad | Medicion de uptime en horario de atencion y formula de calculo | Criterio documentado; proveedor, monitoreo y alcance del entorno por confirmar. |
| RNF04 - trazabilidad clinica | Anulacion logica y bitacora protegida con actor, fecha/hora y motivo | Mecanismo especificado; pruebas de no-borrado pendientes. |
| RNF05 - usabilidad | Interfaz adaptativa y flujo de admision de hasta tres pasos | Criterio documentado; requiere validacion con usuario simulado. |

### Acciones recomendadas antes de cerrar la linea base

1. Resolver la cobertura de HU06 en los requerimientos funcionales y hacer visibles las multiplicidades del diagrama de clases.
2. Resolver el alcance de la notificacion al paciente por resultados y actualizar RF05/HU03 y los casos de uso si procede.
3. Ratificar el stack y seleccionar entornos/proveedores con las restricciones de datos ficticios para la demostracion.
4. Convertir los criterios RNF01-RNF05 en pruebas de aceptacion ejecutables y guardar sus resultados como evidencia del siguiente avance.

El reporte separa decisiones de arquitectura de verificaciones futuras: que un mecanismo este descrito en el SAD no significa que su requisito ya haya sido implementado o aprobado operacionalmente.
