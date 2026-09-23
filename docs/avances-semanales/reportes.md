# Reporte de consistencia de avances

## Revision Semana 2 - Semana 3

Fecha de revision: 23 de septiembre de 2026.

Se compararon el avance de Semana 2, el avance de Semana 3 y la especificacion de requerimientos documentada en `docs/entregable-1/03-especificacion-requerimientos-ERS.md`.

### Consistencias confirmadas

- El producto mantiene el mismo nombre y proposito: Sistema de Informacion Clinico-Administrativo (SIRA) para la Clinica San Rafael S.A.C.
- Se conserva la sede San Borja, el contexto de datos fragmentados, la inasistencia base del 18 %, la demora actual de hasta 48 horas y la operacion con 5 EPS y SOAT.
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
