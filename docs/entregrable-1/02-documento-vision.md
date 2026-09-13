# 👁️ Documento de Visión — Sistema SIRA

---

## 2.1. Declaración de Visión

> **Para** el personal clínico y administrativo de la Clínica San Rafael S.A.C.  
> **Que** necesita una vista única, oportuna y segura de la información del paciente y de la operación diaria,  
> **El** **Sistema de Información Clínico-Administrativo (SIRA)**  
> **Es una** plataforma web integrada  
> **Que** consolida la historia clínica electrónica, la agenda multiespecialidad, el circuito de laboratorio e imágenes, la facturación por convenios y los reportes gerenciales, con acceso restringido por rol y trazabilidad completa;  
> **A diferencia de** las historias clínicas en papel y Excel, la agenda telefónica y la conciliación manual con aseguradoras, que fragmentan el expediente del paciente, saturan la atención telefónica, demoran los resultados hasta 48 horas y dejan a la dirección sin indicadores.

---

## 2.2. Perfiles de Usuario (Stakeholders)

| Perfil | Necesidad Principal | Módulo Relacionado |
| :--- | :--- | :--- |
| **Admisión / Recepción** | Registrar y localizar al paciente sin duplicar expedientes, verificar su convenio vigente y programar, reprogramar o cancelar citas sobre la disponibilidad consolidada de médicos y consultorios. | **M2** (principal), **M1** |
| **Médico tratante** | Abrir el expediente completo del paciente antes de la consulta, registrar la atención con diagnóstico CIE-10, indicaciones y receta, y generar órdenes de laboratorio o imágenes. | **M1** (principal), **M3**, **M2** |
| **Enfermera** | Registrar el triaje y los signos vitales al inicio de la atención y consultar alergias, medicación vigente e indicaciones, sin acceso al expediente clínico completo. | **M1** (acceso restringido por rol) |
| **Personal de laboratorio** | Recibir la orden médica digital, registrar su ejecución, cargar el resultado y que el sistema notifique automáticamente al médico tratante y al paciente. | **M3** (principal) |
| **Cajero / Facturación** | Emitir el comprobante aplicando el tarifario del convenio correspondiente, calcular el copago del paciente y registrar y dar seguimiento a las glosas de las EPS. | **M4** (principal) |
| **Gerencia médica** | Disponer de indicadores de ocupación de consultorios, tiempos de espera, ingresos por especialidad y convenio, e inasistencia, para decidir sobre horarios, personal y convenios. | **M5** (principal) |
| **Paciente** | Agendar sin esperar en la línea telefónica, recibir confirmación y recordatorio de su cita y consultar sus resultados sin acudir presencialmente. | **M6** (deseable); receptor de notificaciones de **M2** y **M3** |

---

## 2.3. Análisis de Factibilidad

### 🛠️ Factibilidad Técnica
**El proyecto es factible.**
* **Volumen de datos:** El volumen del caso (8,000 pacientes registrados en una sede) es manejable por una base de datos relacional sobre infraestructura modesta, alcanzando el tiempo de apertura del expediente en menos de 2 segundos mediante indexación y paginación estándar (`OBJ-01`).
* **Tratamiento de puntos críticos:**
  * **Motor de disponibilidad de la agenda:** Se resuelve con validación de solapamiento a nivel de base de datos (`OBJ-02`).
  * **Tarifario por convenio:** Se estructura mediante un modelo de relación *Servicio–Convenio–Vigencia* (`OBJ-04`).
  * **Confidencialidad:** Se garantiza con control de acceso basado en roles (RBAC) y bitácora de auditoría no modificable (`R-01`).
* **Competencias:** El equipo cuenta con la formación previa en modelado de datos, desarrollo web y control de versiones adquirida en los cursos prerrequisito.

### ⚙️ Factibilidad Operativa
**El proyecto es factible con condiciones.**
* **Factores a favor:** La propia dirección médica reconoce y reporta los problemas actuales (errores de medicación, demoras de cobranza). El sistema no elimina puestos de trabajo, sino que redistribuye tareas manuales ineficientes.
* **Factores en contra:** El personal presenta distintos niveles de alfabetización digital y la transición desde el papel es el punto de mayor fricción (`R-02`).
* **Estrategia de mitigación:** La usabilidad se aborda como un requisito esencial: flujos de pocos pasos, terminología clínica en lugar de técnica y validaciones que previenen el error. Se contempla la entrega de un manual de usuario por rol y una etapa de marcha blanca antes de retirar los registros en papel.

### 💰 Factibilidad Económica
**El proyecto es factible.**
* **Costos:** La infraestructura se limita a servicios en la nube de nivel gratuito o de costo moderado, sin inversión en servidores propios (`EXC-01`, `SR-01`).
* **Beneficios cuantificables:**
  * Reducir la inasistencia del 18% recupera capacidad de consulta hoy desperdiciada en 12 consultorios.
  * Acortar el agendamiento de 20 a menos de 3 minutos libera horas operativas del personal de admisión (`OBJ-02`).
  * El seguimiento sistemático de glosas reduce la facturación a EPS que hoy se pierde o se cobra con retraso (`OBJ-04`).
* **Beneficios no cuantificables:** Prevención de errores de medicación y cumplimiento demostrable de la Ley N.° 29733 de Protección de Datos Personales (`SR-02`).