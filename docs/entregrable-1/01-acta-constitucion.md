#  Acta de Constitución del Proyecto

## 1.1. Datos Generales
| Campo | Detalle |
| :--- | :--- |
| **Nombre del Proyecto** | Sistema de Información Clínico-Administrativo para la Clínica San Rafael S.A.C. |
| **Patrocinador** | Gerencia General, Clínica San Rafael S.A.C. |
| **Equipo de Desarrollo** | Grupo A: Albino Soto, Inga Champi, Rashuaman Sapallanay |
| **Fecha del Acta** | [Fecha de inicio del ciclo] |
| **Product Owner (Ref.)** | Prof. José Carlos García La Riva |

## 1.2. Justificación del Proyecto
La Clínica San Rafael S.A.C. presenta ineficiencias operativas por el uso de historias clínicas fragmentadas en papel/Excel, alta tasa de inasistencia a citas (18%) y procesos manuales de facturación con aseguradoras. El proyecto automatizará e integrará la gestión clínico-administrativa para mejorar la atención y liquidez financiera.

## 1.3. Objetivos SMART
1. Reducir la tasa de inasistencia a citas del 18% a menos del 8% mediante recordatorios automáticos.
2. Reducir el tiempo de apertura e ingreso a la historia clínica a menos de 2 segundos.
3. Digitalizar el 100% de las órdenes y resultados de laboratorio e imágenes.
4. Automatizar la facturación y conciliación con las 5 EPS/aseguradoras del convenio.

## 1.4. Alcance Resumido
Desarrollo de los módulos: Historia Clínica Electrónica (M1), Agenda y Citas (M2), Laboratorio e Imágenes (M3), Facturación y Convenios (M4), Reportes Gerenciales (M5) y Portal del Paciente (M6 - deseable).

## 1.5. Exclusiones
* Compra o mantenimiento de infraestructura física de servidores (se usará nube/hosting).
* Desarrollo de sistemas contables o de nómina/RRHH internos.
* Integración con sistemas externos fuera de las 5 EPS/aseguradoras definidas.

## 1.6. Supuestos y Restricciones Adicionales
* **Restricción:** Presupuesto de infraestructura acotado (nube de costo moderado).
* **Restricción:** Cumplimiento de la Ley N.° 29733 de Protección de Datos Personales.
* **Supuesto:** Se usará únicamente información sintética/anonimizada para pruebas.

## 1.7. Riesgos Iniciales
| Riesgo | Impacto | Mitigación |
| :--- | :--- | :--- |
| Incumplimiento de confidencialidad en datos de salud | Alto | Implementación de RBAC (control por roles) y auditoría. |
| Resistencia del personal médico al nuevo software | Medio | Diseño UX/UI intuitivo y capacitaciones interactivas. |
| Retrasos en la integración con tarifarios de EPS | Medio | Uso de simuladores de API/archivos de prueba en Sprints. |

## 1.8. Hitos Principales
| Semana | Hito |
| :---: | :--- |
| **Semana 2** | Acta de Constitución y Documento de Visión |
| **Semana 4** | ERS, Product Backlog e Historias de Usuario |
| **Semana 6** | Arquitectura (SAD), Base de Datos y Prototipos UX/UI |
| **Semana 7** | Plan de Release y Sprint Backlog 1 |
| **Semana 8** | Examen Parcial – Sustentación Entregable 1 |