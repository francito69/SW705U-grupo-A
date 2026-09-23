# 📜 Acta de Constitución del Proyecto

---

## 1.1. Datos generales

| Campo                                 | Detalle                                                                                                                                  |
| :------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre del proyecto**         | Sistema de Información Clínico-Administrativo para la Clínica San Rafael S.A.C. (SIRA)                                                |
| **Patrocinador**                | Gerencia General, Clínica San Rafael S.A.C.                                                                                             |
| **Equipo**                      | Grupo A: Albino Soto, Christopher Henrry (20231158C); Inga Champi, Franz Joe (20231302G); Rashuaman Sapallanay, Ricco Didier (20231242D) |
| **Fecha del acta**              | 10 de septiembre de 2026                                                                                                                 |
| **Product Owner de referencia** | Jose Carlos Garcia La Riva                                                                                                               |

---

## 1.2. Justificación del proyecto

La **Clínica San Rafael S.A.C.** pasó de una consulta externa básica a una oferta multiespecialidad con laboratorio, imágenes, farmacia y emergencia propios, pero conservó una gestión de información manual y fragmentada. Ello produce cinco perjuicios verificables: riesgo clínico por historias dispersas en papel y Excel, sin vista única del paciente y con errores de medicación ya reportados; pérdida de demanda e ingresos por una agenda telefónica con hasta 20 minutos de espera, citas duplicadas y 18 % de inasistencia; demora diagnóstica por resultados en papel con hasta 48 horas de retraso y extravío ocasional; deterioro del flujo de caja por la facturación y conciliación manual con 5 EPS y SOAT, que genera glosas; y ceguera gerencial por la ausencia de indicadores de ocupación, tiempos de espera e ingresos por especialidad o convenio.

El proyecto se justifica porque integra y automatiza la gestión clínico-administrativa para garantizar la continuidad de la atención, reducir el ausentismo y agilizar la liquidez de la clínica.

---

## 1.3. Objetivos SMART

|     Código     | Objetivo SMART                                                                                                                                                                                                                                                                                                                                                                                                                          | Indicador de Logro / Verificación |
| :--------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------- |
| **OBJ-01** | Implementar una historia clínica electrónica unificada (M1) que permita consultar el expediente completo de cualquier paciente en menos de 2 segundos sobre una base de 8 000 pacientes de prueba, con acceso restringido por rol y registro de todo acceso en bitácora de auditoría, conforme a la Ley N.° 29733.                                                                                                                 |                                    |
| **OBJ-02** | Poner en operación una agenda digital consolidada (M2) que bloquee el 100 % de los solapamientos de médico y consultorio, reduzca el tiempo de agendamiento de 20 a menos de 3 minutos por cita y notifique el 100 % de las citas con al menos 24 horas de anticipación, para reducir la inasistencia desde la línea base del 18 %.                                                                                                 |                                    |
| **OBJ-03** | Digitalizar el circuito de órdenes y resultados de laboratorio e imágenes (M3) para que el resultado quede disponible en el expediente del paciente en menos de 4 horas desde su carga, frente a las 48 horas actuales, y con trazabilidad de estado que elimine el extravío de resultados.                                                                                                                                          |                                    |
| **OBJ-04** | Automatizar la facturación por convenio (M4) aplicando el tarifario correcto al 100 % de las atenciones registradas en los tres tipos de cobertura (particular, EPS y SOAT), con registro y seguimiento de glosas, y entregar un dashboard gerencial (M5) con los indicadores de ocupación de consultorios, tiempos de espera, ingresos por especialidad y convenio e inasistencia calculados sobre los datos operativos del sistema. |                                    |

---

## 1.4. Alcance Resumido

El proyecto comprende el desarrollo e implantación del sistema web **SIRA** para la sede San Borja de la Clínica San Rafael S.A.C., integrando en una sola plataforma los procesos actualmente dispersos.

### Módulos Imprescindibles (Sprints 1 y 2):

* **M1 — Historia Clínica Electrónica:** Registro y búsqueda de pacientes, expediente único con antecedentes, atenciones multiespecialidad, diagnósticos CIE-10, indicaciones y recetas con acceso restringido por rol.
* **M2 — Agenda y Citas Médicas:** Disponibilidad consolidada de consultorios, programación con bloqueo de solapamientos, confirmación, recordatorios, reprogramación y cancelación con motivo.
* **M3 — Laboratorio e Imágenes:** Generación de órdenes desde la consulta, seguimiento de estados, carga de resultados digitales y notificación automática al médico y paciente.
* **M4 — Facturación y Convenios:** Tarifarios diferenciados (Particular, EPS, SOAT), cálculo de copagos, emisión de comprobantes internos y módulo de gestión de glosas.
* **M5 — Reportes Gerenciales:** Dashboard interactivo con métricas de ocupación, tiempos de espera, ingresos e inasistencia.

### Módulos Transversales:

* Autenticación de usuarios, control de acceso basado en roles (RBAC), bitácora de auditoría clínica no modificable y carga inicial de datos sintéticos de prueba.

### Alcance Deseable:

* **M6 — Portal del Paciente y Telemedicina Básica:** Agendamiento en línea y atención virtual básica de seguimiento (sujeto al avance de los módulos M1-M5).

---

## 1.5. Exclusiones

|    N.°    | Exclusión                                                                                                                                                                                                                                                                                                                                                                                             |
| :---------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | Gestión de hospitalización y cirugía ambulatoria (censo de camas, programación de sala de operaciones y protocolos quirúrgicos), así como control de inventario y dispensación de farmacia; el alcance clínico concluye en la emisión de la receta.                                                                                                                                           |
| **2** | Integración con sistemas externos: emisión de comprobantes electrónicos con firma digital ante SUNAT, intercambio electrónico de expedientes de cobranza con las EPS y aseguradoras, y almacenamiento o visualización de imágenes en formato DICOM o servidores PACS. Los comprobantes y las glosas son de control interno y los resultados de imágenes se gestionan como documentos digitales. |
| **3** | Compra o mantenimiento de infraestructura física de servidores, desarrollo de sistemas de contabilidad, tesorería, nómina o RRHH, aplicaciones móviles nativas para Android o iOS, y migración masiva de los registros históricos en papel y Excel; la solución es una aplicación web adaptativa y solo se carga el conjunto de datos de prueba.                                               |

---

## 1.6. Supuestos y restricciones adicionales

|    N.°    |          Tipo          | Descripción                                                                                                                                                                                                                                                                                      |
| :---------: | :--------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1** | **Restricción** | La solución se despliega para una sola sede (San Borja) y no contempla arquitectura multi-sede; opera en español (Perú), zona horaria`America/Lima` y moneda en soles (PEN).                                                                                                                 |
| **2** | **Restricción** | Se prohíbe el borrado físico de información clínica. Toda supresión se registra como anulación lógica con usuario, fecha y motivo, y todo acceso a la historia clínica queda auditado, conforme a la Ley N.° 29733 de Protección de Datos Personales.                                   |
| **3** |   **Supuesto**   | La clínica designará un responsable por área (admisión, médicos, laboratorio y caja) para validar los requerimientos y participar en las pruebas de aceptación, y entregará los tarifarios vigentes por convenio y los catálogos de servicios necesarios para poblar los datos de prueba. |

---

## 1.7. Riesgos iniciales

| Riesgo                                                                                                                                                                    |     Impacto     | Mitigación                                                                                                                                                                                                                                                                               |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Vulneración de la confidencialidad de los datos clínicos: acceso no autorizado a los expedientes de salud.                                                              | **Alto** | Control de acceso basado en roles (RBAC) verificado en la capa de servicios, cifrado del tráfico y bitácora de auditoría no modificable sobre toda operación en la historia clínica.                                                                                                 |
| Resistencia del personal al cambio y baja adopción del sistema al pasar del registro en papel al digital, agravada por los distintos niveles de alfabetización digital. | **Alto** | Involucrar a los responsables de cada área desde la especificación de requerimientos, diseñar interfaces de pocos pasos y en lenguaje del dominio clínico, entregar manual de usuario por rol y realizar una marcha blanca con acompañamiento antes de retirar el registro en papel. |
| Capacidad del equipo: tres integrantes frente a los cuatro o cinco previstos, con riesgo de no completar los módulos imprescindibles.                                    | **Alto** | Priorización estricta del alcance con M6 como módulo condicional, definición de hecho clara para evitar retrabajo, propiedad colectiva del código con revisión cruzada y control del avance en cada sesión de taller.                                                               |
| Subestimación de la complejidad del módulo de facturación: errores en el tarifario por convenio, el cálculo de copagos o el ciclo de vida de las glosas.              | **Medio** | Modelar la relación servicio–convenio–vigencia desde el diseño de la base de datos y validar el cálculo de copago con casos de prueba de los tres tipos de cobertura antes de codificar.                                                                                             |

> 📌 **Nota de Criterio Técnico (Riesgo R-02):**
> El riesgo de resistencia al cambio se clasifica con **Impacto Alto** debido a que es la causa principal de fallo en proyectos de Historia Clínica Electrónica en el sector salud. Sin una adecuada estrategia de adopción, el personal tiende a mantener registros paralelos en papel, duplicando la carga laboral y anulando la confiabilidad del software.

---

## 1.8. Hitos principales (dado por el cronograma del curso)

|    Semana    | Hito                                                                  |
| :----------: | :-------------------------------------------------------------------- |
| **2** | Acta de constitución y documento de visión                          |
| **4** | Especificación de requerimientos, backlog y modelos UML              |
| **6** | Arquitectura, modelo de base de datos y prototipo UX/UI               |
| **7** | Plan de release y sprint backlog 1                                    |
| **8** | Examen Parcial — sustentación del Entregable 1                      |
| **16** | Examen Final — sustentación del Entregable 2 (producto funcionando) |
