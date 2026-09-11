# 📜 Acta de Constitución del Proyecto

---

## 1.1. Datos Generales

| Campo | Detalle |
| :--- | :--- |
| **Nombre del Proyecto** | Sistema de Información Clínico-Administrativo para la Clínica San Rafael S.A.C. |
| **Patrocinador** | Gerencia General, Clínica San Rafael S.A.C. |
| **Equipo de Desarrollo** | **Grupo A:**<br>• Albino Soto, Christopher Henrry<br>• Inga Champi, Franz Joe<br>• Rashuaman Sapallanay, Ricco Didier |
| **Fecha del Acta** | Inicio del Ciclo Académico |
| **Product Owner (Ref.)** | Prof. José Carlos García La Riva |

---

## 1.2. Justificación del Proyecto

La **Clínica San Rafael S.A.C.** evolucionó de una atención de consulta externa básica hacia una oferta multiespecialidad con laboratorio, imágenes, farmacia, hospitalización y emergencia. Sin embargo, conservó una gestión de información manual y fragmentada que produce cinco perjuicios operativos y financieros verificables:

* 🚨 **Riesgo clínico:** Historias clínicas dispersas en papel y hojas de cálculo Excel por especialidad, sin una vista única del paciente. Se han reportado errores de medicación por desconocimiento del historial clínico completo.
* 📉 **Pérdida de demanda e ingresos:** Agenda de citas gestionada por vía telefónica con tiempos de espera de hasta 20 minutos, citas duplicadas o mal asignadas, y una tasa de inasistencia (*no-show*) del 18% por falta de recordatorios.
* ⏱️ **Demora diagnóstica:** Entrega de resultados de laboratorio e imágenes en formato físico en papel, con retrasos de hasta 48 horas y extravío ocasional de los exámenes.
* 💸 **Deterioro del flujo de caja:** Procesos de facturación y conciliación manual con 5 EPS y aseguradoras (incluyendo SOAT), lo que genera glosas (rechazos de pago) y demoras sustanciales en la cobranza.
* 🙈 **Ceguera gerencial:** La dirección carece de indicadores oportunos en tiempo real sobre la tasa de ocupación de consultorios, tiempos de espera e ingresos por especialidad o convenio.

En consecuencia, el proyecto automatizará e integrará la gestión clínico-administrativa para garantizar la continuidad de la atención médica, reducir el ausentismo y agilizar la liquidez financiera de la empresa.

---

## 1.3. Objetivos SMART del Proyecto

| Código | Objetivo SMART | Indicador de Logro / Verificación |
| :---: | :--- | :--- |
| **OBJ-01** | Implementar una Historia Clínica Electrónica (HCE) unificada (**M1**). | Consultar el expediente completo de cualquier paciente en **menos de 2 segundos**, demostrable en la semana 16 sobre datos de prueba. |
| **OBJ-02** | Poner en operación una agenda digital consolidada (**M2**). | Visualizar disponibilidad de médicos y consultorios bloqueando solapamientos, reduciendo el tiempo de agendamiento a **menos de 3 minutos por cita**. |
| **OBJ-03** | Digitalizar el circuito de órdenes y resultados de laboratorio e imágenes (**M3**). | Publicar el resultado digital en el expediente el **mismo día de su carga**, eliminando al 100% el extravío de resultados en papel. |
| **OBJ-04** | Automatizar la facturación por convenios de salud (**M4**). | Aplicar el tarifario correcto según tipo de cobertura (Particular, EPS, SOAT) permitiendo el registro y seguimiento de glosas. |
| **OBJ-05** | Entregar un dashboard gerencial ejecutivo (**M5**). | Visualizar indicadores en tiempo real de ocupación, tiempos de espera, ingresos e inasistencia consultables sobre datos operativos. |

---

## 1.4. Alcance Resumido

El proyecto comprende el desarrollo e implantación de un sistema de información clínico-administrativo web para la sede de San Borja de la Clínica San Rafael S.A.C., integrando en una sola plataforma los procesos actualmente dispersos.

### Módulos Imprescindibles (Sprints 1 y 2):
* **M1 — Historia Clínica Electrónica:** Registro y búsqueda de pacientes, expediente único con antecedentes, atenciones multiespecialidad, diagnósticos CIE-10, indicaciones y recetas con acceso restringido por rol.
* **M2 — Agenda y Citas Médicas:** Disponibilidad consolidada, programación con bloqueo de solapamientos, confirmación, recordatorios, reprogramación y cancelación con motivo.
* **M3 — Laboratorio e Imágenes:** Generación de órdenes desde la consulta, seguimiento de estados, carga de resultados digitales y notificación automática al médico y paciente.
* **M4 — Facturación y Convenios:** Tarifarios diferenciados (Particular, EPS, SOAT), cálculo de copagos, emisión de comprobantes internos y módulo de gestión de glosas.
* **M5 — Reportes Gerenciales:** Dashboard interactivo con métricas de ocupación, tiempos de espera, ingresos e inasistencia.

### Módulos Transversales:
* Autenticación de usuarios, control de acceso basado en roles (RBAC), bitácora de auditoría clínica no modificable y carga inicial de datos sintéticos de prueba.

### Alcance Deseable:
* **M6 — Portal del Paciente y Telemedicina Básica:** Agendamiento en línea y atención virtual básica de seguimiento (sujeto al avance de los módulos M1-M5).

---

## 1.5. Exclusiones del Proyecto

| N.° | Exclusión |
| :---: | :--- |
| **EXC-01** | Compra, adquisición o mantenimiento de infraestructura física de servidores (se usará entorno nube/hosting). |
| **EXC-02** | Desarrollo de sistemas de contabilidad general, finanzas profundas, nómina o RRHH internos. |
| **EXC-03** | Integración por API/Web Services con sistemas externos fuera de las 5 EPS/aseguradoras definidas en el caso. |
| **EXC-04** | Gestión de hospitalización y cirugía ambulatoria (censo de camas, programación de SOP o protocolos quirúrgicos). |
| **EXC-05** | Control de inventario físico y dispensación de farmacia (stock, lotes, vencimientos); el alcance concluye en la receta digital. |
| **EXC-06** | Emisión de comprobantes electrónicos con firma digital/CDR ante la SUNAT (el sistema genera comprobantes de control interno). |
| **EXC-07** | Almacenamiento/visualización de imágenes médicas en formato DICOM o servidores PACS (los resultados se gestionan como documentos digitales PDF/imagen). |
| **EXC-08** | Migración masiva de registros históricos físicos en papel o Excel; únicamente se cargará el conjunto de datos de prueba. |
| **EXC-09** | Desarrollo de aplicaciones móviles nativas para Android o iOS (la solución será exclusivamente una aplicación web adaptativa/*responsive*). |

---

## 1.6. Supuestos y Restricciones Adicionales

| N.° | Tipo | Descripción |
| :---: | :---: | :--- |
| **SR-01** | **Restricción** | Presupuesto de infraestructura acotado a servicios en la nube de costo moderado o capas de evaluación. |
| **SR-02** | **Restricción** | Cumplimiento estricto de la Ley N.° 29733 de Protección de Datos Personales y normas del MINSA. |
| **SR-03** | **Restricción** | La solución se desplegará para una sola sede (San Borja); no contempla arquitectura multi-sede. |
| **SR-04** | **Restricción** | El sistema operará en idioma español (Perú), zona horaria `America/Lima` y moneda en Soles (`PEN`). |
| **SR-05** | **Restricción** | Prohibido el borrado físico de información clínica; toda supresión será anulación lógica con registro de usuario, fecha y motivo. |
| **SR-06** | **Supuesto** | Se utilizará única y exclusivamente información sintética/anonimizada para pruebas y demostraciones. |
| **SR-07** | **Supuesto** | La clínica designará responsables por área (Admisión, Médicos, Laboratorio, Caja) para validar requerimientos y pruebas. |
| **SR-08** | **Supuesto** | La administración proporcionará los tarifarios vigentes por convenio y catálogos de exámenes para la base de datos de prueba. |
| **SR-09** | **Supuesto** | El personal cuenta con estaciones de trabajo con navegadores web actualizados y conectividad estable a internet. |

---

## 1.7. Matriz de Riesgos Iniciales

| Código | Riesgo Identificado | Impacto | Estrategia de Mitigación |
| :---: | :--- | :---: | :--- |
| **R-01** | **Vulneración de confidencialidad en datos clínicos:** Acceso no autorizado a expedientes de salud. | **Alto** | Implementación estricta de RBAC (control por roles), encriptación y bitácoras de auditoría no modificables. |
| **R-02** | **Resistencia al cambio y baja adopción operativa:** Rechazo del personal al pasar del registro manual/papel al sistema digital. | **Alto** | Involucrar a jefes de área desde la ERS, diseñar interfaces minimalistas en lenguaje clínico, entregar manuales por rol y realizar marcha blanca antes del retiro del papel. |
| **R-03** | **Subestimación de la complejidad en facturación:** Errores en tarifarios por convenio, copagos o ciclo de glosas. | **Medio** | Modelar la relación *Servicio-Convenio-Vigencia* en la BD desde la fase de diseño y validar copagos con casos de prueba previos a la codificación. |
| **R-04** | **Falla del entorno de demostración durante la sustentación:** Indisponibilidad de la nube durante el examen final. | **Medio** | Mantener un despliegue en la nube y una copia local ejecutable con contenedores (Docker) con el juego de datos de prueba versionado. |
| **R-05** | **Lentitud en la apertura del expediente clínico:** Tiempos de respuesta superiores a 2 segundos al aumentar los datos. | **Medio** | Definir índices SQL y paginación desde el diseño, probar con la base poblada desde el inicio y automatizar métricas de respuesta. |
| **R-06** | **Concentración del conocimiento técnico:** Dependencia de un solo integrante ante ausencias o bajas temporales. | **Medio** | Propiedad colectiva del código, revisiones cruzadas obligatorias (*Pull Requests*) y registro documentado de decisiones técnicas en el repositorio. |

> 📌 **Nota de Criterio Técnico (Riesgo R-02):**  
> El riesgo de resistencia al cambio se clasifica con **Impacto Alto** debido a que es la causa principal de fallo en proyectos de Historia Clínica Electrónica en el sector salud. Sin una adecuada estrategia de adopción, el personal tiende a mantener registros paralelos en papel, duplicando la carga laboral y anulando la confiabilidad del software.

---

## 1.8. Hitos Principales del Proyecto

| Semana | Hito Principal | Entregables Asociados |
| :---: | :--- | :--- |
| **Semana 2** | Concepción del Proyecto | Acta de Constitución y Documento de Visión |
| **Semana 4** | Requerimientos y Backlog | Especificación ERS, Product Backlog e Historias de Usuario |
| **Semana 6** | Diseño y Arquitectura | Documento SAD, Modelo E-R / DDL y Prototipo UX/UI |
| **Semana 7** | Planificación del Desarrollo | Plan de Release y Sprint Backlog 1 |
| **Semana 8** | **Examen Parcial (EP)** | **Sustentación del Entregable 1 (Documentación de Ingeniería)** |
| **Semana 16** | **Examen Final (EF)** | **Sustentación del Entregable 2 (Producto Funcional + Demo en Vivo)** |