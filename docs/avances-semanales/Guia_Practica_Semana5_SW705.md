![ref1]	**SW705 · Taller de Ingeniería de Software I — Escuela de Ingeniería de Software**

**UNIVERSIDAD NACIONAL DE INGENIERÍA**

*Facultad de Ingeniería Industrial y de Sistemas · Escuela de Ingeniería de Software*

**GUÍA PRÁCTICA — SEMANA 5**

**Arquitectura de software**

SW705 — Taller de Ingeniería de Software I

*Docente: Mg. Ing. José Carlos, García La Riva*

*Caso aplicado: Clínica San Rafael S.A.C.*

|**Integrantes del equipo**||
| :- | :- |
|**Código(s)**||
|**Sección**||
|**Fecha**||

# **Instrucciones generales**
Esta guía acompaña la Semana 5 del curso y los conduce, paso a paso, a diseñar la arquitectura inicial del sistema de información de su proyecto integrador. Cada paso incluye un recuadro de orientación (🧭), un ejemplo resuelto sobre el caso Clínica San Rafael S.A.C. (✅) y un espacio en blanco para que ustedes lo completen con su propio proyecto.

Este producto es un avance formativo hacia el Avance 3 del curso (arquitectura de software, modelo de base de datos y prototipo UX/UI), que se cierra en la Semana 6. Al final de esta guía encontrarán la rúbrica de revisión formativa de esta sesión.

|<p>**🧭 Antes de empezar**</p><p>Tengan a la mano el backlog priorizado y los diagramas UML (casos de uso, clases, actividades) elaborados en la Semana 4: la arquitectura debe ser coherente con ellos.</p><p>Trabajen en equipo: la arquitectura es una decisión colectiva, no de una sola persona.</p><p>El caso Clínica San Rafael S.A.C. se usa solo como ejemplo guía — desarrollen la arquitectura de SU propio proyecto.</p>|
| :- |
# **Paso 1 — Selección del estilo arquitectónico**
**Objetivo**

Elegir y justificar el estilo o patrón arquitectónico más adecuado para su proyecto, comparando al menos dos alternativas.

|<p>**🧭 Cómo hacerlo**</p><p>Listen los estilos candidatos (capas, cliente-servidor, MVC, microservicios, etc.).</p><p>Para cada uno, evalúen: complejidad de implementación, tamaño del equipo, tiempo disponible (un semestre) y necesidad real de escalar por módulos.</p><p>Elijan uno y expliquen por qué es mejor que la alternativa descartada para SU proyecto — no existe una respuesta única válida para todos los equipos.</p>|
| :- |
|<p>**✅ Ejemplo — Clínica San Rafael S.A.C.**</p><p>Alternativa A: Arquitectura en capas con API REST monolítica.</p><p>Alternativa B: Microservicios (uno por módulo: HCE, Agenda, Facturación...).</p><p>Decisión: se elige la Alternativa A, porque el equipo es pequeño (4 integrantes), el proyecto dura un semestre y aún no existe necesidad de escalar u operar los módulos de forma independiente. Los microservicios se dejan como evolución futura, no como requisito del prototipo académico.</p>|

**Complete con su proyecto**

|**Alternativa evaluada**|**Ventajas**|**Desventajas / riesgos**|**¿Se elige? (Sí/No)**|
| :- | :- | :- | :- |
|||||
|||||
|||||
**Decisión final y justificación:**

|<p>*Escriban aquí la decisión final y su justificación (3–5 líneas)*</p><p></p><p></p><p></p><p></p>|
| :-: |

# **Paso 2 — Atributos de calidad**
**Objetivo**

Definir, con métricas concretas, los atributos de calidad que la arquitectura debe garantizar.

|<p>**🧭 Cómo hacerlo**</p><p>No basta con decir "debe ser rápido" o "debe ser seguro": cada atributo necesita una métrica medible.</p><p>Prioricen 3 a 5 atributos que sean realmente críticos para su proyecto — no todos los atributos posibles aplican con la misma fuerza.</p><p>Relacionen cada atributo con un riesgo concreto de no cumplirlo.</p>|
| :- |
|<p>**✅ Ejemplo — Clínica San Rafael S.A.C.**</p><p>Rendimiento: la agenda de citas debe responder en menos de 2 segundos con 500 pacientes activos.</p><p>Seguridad: acceso por roles (recepción, médico, administración) y cifrado de contraseñas.</p><p>Disponibilidad: el sistema debe operar durante el horario de atención (7:00 a. m. – 9:00 p. m.), con respaldo diario de la base de datos.</p><p>Modificabilidad: debe ser posible agregar el módulo de Facturación sin modificar el código de HCE ni de Agenda.</p>|

**Complete con su proyecto**

|**Atributo de calidad**|**Métrica / criterio medible**|**Riesgo si no se cumple**|
| :- | :- | :- |
||||
||||
||||
||||

# **Paso 3 — Decisiones de arquitectura (ADR)**
**Objetivo**

Redactar al menos 3 registros de decisión de arquitectura (Architecture Decision Records) para las decisiones más relevantes del proyecto.

|<p>**🧭 Estructura de un ADR**</p><p>Contexto: ¿qué problema u opción se está evaluando?</p><p>Alternativas consideradas.</p><p>Decisión tomada.</p><p>Consecuencias: ¿qué se gana y qué se sacrifica con esta decisión?</p>|
| :- |
|<p>**✅ Ejemplo — Clínica San Rafael S.A.C. (ADR-01)**</p><p>Contexto: se necesita elegir el estilo arquitectónico general del sistema.</p><p>Alternativas: arquitectura en capas vs. microservicios.</p><p>Decisión: arquitectura en capas con API REST.</p><p>Consecuencias: despliegue más simple y menor curva de aprendizaje para el equipo; en el futuro, separar módulos en microservicios implicará un esfuerzo de refactorización.</p>|

**Complete con su proyecto — ADR 1**

|**Contexto**|**Alternativas consideradas**|**Decisión**|**Consecuencias**|
| :- | :- | :- | :- |
|||||
**Complete con su proyecto — ADR 2**

|**Contexto**|**Alternativas consideradas**|**Decisión**|**Consecuencias**|
| :- | :- | :- | :- |
|||||
**Complete con su proyecto — ADR 3**

|**Contexto**|**Alternativas consideradas**|**Decisión**|**Consecuencias**|
| :- | :- | :- | :- |
|||||

# **Paso 4 — Vistas del Documento de Arquitectura (SAD)**
**Objetivo**

Elaborar, al menos, la vista lógica y la vista física (despliegue) de la arquitectura del sistema.

|<p>**🧭 Cómo hacerlo**</p><p>Vista lógica: dibujen las capas o módulos del sistema y cómo se conectan entre sí.</p><p>Vista física: dibujen en qué equipos/servidores correrá cada componente y cómo se comunican (protocolo).</p><p>Usen una herramienta de diagramación (draw.io, Lucidchart, o incluso a mano de forma ordenada) y péguenla en el espacio indicado.</p>|
| :- |
|**✅ Ejemplo — Vista lógica en capas (Clínica San Rafael S.A.C.)**|

![](Aspose.Words.e2e30a17-65fc-4b5a-a9a1-fc7711aa7401.002.png)

**Complete con su proyecto — Vista lógica**

|<p>*Pegue aquí el diagrama de la vista lógica de su proyecto*</p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p>|
| :-: |
**Complete con su proyecto — Vista física (despliegue)**

|<p>*Pegue aquí el diagrama de la vista física de su proyecto*</p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p>|
| :-: |

# **Paso 5 — Stack tecnológico**
**Objetivo**

Seleccionar y justificar el stack tecnológico (lenguaje, framework, base de datos, hosting) que usará el equipo para construir el proyecto.

|<p>**🧭 Cómo hacerlo**</p><p>Consideren la experiencia previa del equipo: un stack conocido reduce el riesgo del proyecto.</p><p>Verifiquen que el stack elegido soporte los atributos de calidad definidos en el Paso 2.</p><p>Prefieran herramientas gratuitas o de nivel académico (planes free/estudiante) para el despliegue.</p>|
| :- |
|<p>**✅ Ejemplo — Clínica San Rafael S.A.C.**</p><p>Lenguaje/backend: Python con FastAPI (rapidez de desarrollo, buena documentación automática).</p><p>Base de datos: SQLite en desarrollo, con posibilidad de migrar a PostgreSQL en producción sin cambiar el código del modelo.</p><p>Frontend: por definir en la Semana 6, junto con el prototipo UX/UI.</p><p>Control de versiones y CI: GitHub + GitHub Actions para pruebas automáticas.</p>|

**Complete con su proyecto**

|**Componente**|**Tecnología elegida**|**Justificación**|
| :- | :- | :- |
||||
||||
||||
||||

![ref1]	**SW705 · Taller de Ingeniería de Software I — Escuela de Ingeniería de Software**

# **Rúbrica de evaluación — Revisión formativa, Semana 5**
Carácter: FORMATIVO. Esta revisión no otorga una nota que se promedie directamente en la Promedio de Prácticas (PP); su propósito es retroalimentar el avance del equipo antes del cierre del Avance 3 (arquitectura, modelo de base de datos y prototipo UX/UI) en la Semana 6, donde sí se evaluará con una rúbrica sumativa.

|**Criterio**|**Logrado (18–20)**|**Satisfactorio (14–17)**|**En proceso (11–13)**|**Inicial (0–10)**|
| :- | :- | :- | :- | :- |
|<p>**Selección y justificación**</p><p>**del estilo arquitectónico**</p><p>**(25%)**</p>|Compara alternativas reales y justifica la decisión con criterios técnicos sólidos y propios del proyecto.|Compara alternativas y justifica la decisión, con criterios generales.|Elige un estilo sin comparar alternativas o con justificación superficial.|No presenta estilo arquitectónico definido.|
|<p>**Atributos de calidad**</p><p>**medibles**</p><p>**(25%)**</p>|Define 3 a 5 atributos con métricas claras y su riesgo asociado, pertinentes al proyecto.|Define atributos con métricas, aunque alguna es poco medible.|Menciona atributos de forma genérica, sin métricas.|No define atributos de calidad.|
|<p>**Calidad de los ADR**</p><p>**(25%)**</p>|Presenta 3 ADR completos y coherentes (contexto, alternativas, decisión, consecuencias) para decisiones realmente relevantes.|Presenta 3 ADR completos, aunque alguna decisión es de bajo impacto.|Presenta menos de 3 ADR o con estructura incompleta.|No presenta ADR.|
|<p>**Coherencia de las vistas**</p><p>**del SAD (lógica y física)**</p><p>**(25%)**</p>|Ambas vistas son coherentes entre sí, con el backlog/UML de la Semana 4 y con el estilo elegido.|Ambas vistas están presentes, con alguna inconsistencia menor.|Presenta solo una vista o con inconsistencias relevantes.|No presenta vistas de arquitectura.|

Escala vigesimal (0–20). El docente registrará el nivel alcanzado por criterio y brindará retroalimentación oral o escrita para que el equipo ajuste su arquitectura antes de la sustentación del Avance 3.

[ref1]: Aspose.Words.e2e30a17-65fc-4b5a-a9a1-fc7711aa7401.001.png
