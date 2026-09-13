# 🏥 Sistema de Información Clínico-Administrativo (SIRA) — Clínica San Rafael S.A.C.

![Universidad Nacional de Ingeniería](https://img.shields.io/badge/Universidad-UNI%20--%20FIIS-blue?style=for-the-badge)
![Curso](https://img.shields.io/badge/Curso-SW705U%20Taller%20de%20Ingenier%C3%ADa%20de%20Software%20I-green?style=for-the-badge)
![Grupo](https://img.shields.io/badge/Grupo-Grupo%20A-orange?style=for-the-badge)
![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow?style=for-the-badge)

Repositorio oficial del **Sistema de Información Clínico-Administrativo (SIRA)** para la sede San Borja de la **Clínica San Rafael S.A.C.**, desarrollado en la **Universidad Nacional de Ingeniería (UNI)** para la asignatura **SW705U - Taller de Ingeniería de Software I**.

---

## 📋 Información Académica

* **Universidad:** Universidad Nacional de Ingeniería (UNI)
* **Facultad:** Facultad de Ingeniería Industrial y de Sistemas (FIIS)
* **Escuela Profesional:** Ingeniería de Software
* **Curso:** SW705U – Taller de Ingeniería de Software I
* **Docente / Product Owner (Ref.):** Prof. José Carlos García La Riva
* **Grupo:** Grupo A

---

## 👥 Equipo de Desarrollo

| N.° | Apellidos y Nombres | Correo Electrónico | Rol Asignado |
| :---: | :--- | :--- | :--- |
| 1 | **Albino Soto, Christopher Henrry** | `christopher.albino.s@uni.pe` | Desarrollador Fullstack / BD |
| 2 | **Inga Champi, Franz Joe** | `franz.inga.c@uni.pe` | Arquitecto / Desarrollador Backend |
| 3 | **Rashuaman Sapallanay, Ricco Didier** | `ricco.rashuaman.s@uni.pe` | Analista QA / UI-UX / Frontend |

---

## 🎯 Descripción y Caso Empresarial

La **Clínica San Rafael S.A.C.** (sede San Borja) afronta ineficiencias operativas y financieras por el uso de historias clínicas fragmentadas en papel/Excel, demoras de hasta 48 horas en entrega de resultados, una tasa de inasistencia a citas del 18% y conciliaciones manuales con 5 EPS/SOAT que generan glosas.

### Objetivo General
Desarrollar e implementar la plataforma web **SIRA** para centralizar la gestión clínico-administrativa de la clínica, garantizando el acceso seguro a historias clínicas en menos de 2 segundos, optimizando la agenda de citas y automatizando la facturación por convenios, bajo estricto cumplimiento de la **Ley N.° 29733 de Protección de Datos Personales**.

---

## 🧩 Módulos del Sistema y Planificación

| Módulo | Descripción Resumida | Prioridad / Fase |
| :--- | :--- | :---: |
| **M1. Historia Clínica Electrónica (HCE)** | Expediente único, antecedentes, diagnósticos CIE-10, recetas e indicaciones con RBAC. | Imprescindible *(Sprint 1)* |
| **M2. Agenda y Citas Médicas** | Disponibilidad consolidada de 12 consultorios, bloqueo de solapamientos y recordatorios. | Imprescindible *(Sprint 1)* |
| **M3. Laboratorio e Imágenes** | Circuito de órdenes digitales, carga de resultados e integración inmediata al expediente. | Imprescindible *(Sprint 2)* |
| **M4. Facturación y Convenios** | Aplicación de tarifarios por convenio (Particular, 5 EPS, SOAT) y control de glosas. | Imprescindible *(Sprint 2)* |
| **M5. Reportes Gerenciales** | Dashboard con métricas de ocupación, tiempos de espera, ingresos e inasistencia. | Imprescindible *(Sprint 2)* |
| **M6. Portal del Paciente / Telemedicina** | Agendamiento en línea y consultas virtuales básicas. | Deseable *(Sprint 2)* |

---

## 📁 Estructura del Repositorio

```text
.
├── .github/                  # Workflows de CI/CD
├── docs/                     # Documentación de Ingeniería
│   ├── entregable-1/         # Documentación de Ingeniería (Semanas 2 a 8)
│   │   ├── 01-acta-constitucion.md
│   │   ├── 02-documento-vision.md
│   │   ├── 03-especificacion-requerimientos-ERS.md
│   │   ├── 04-modelos-uml/
│   │   ├── 05-arquitectura-SAD.md
│   │   ├── 06-modelo-base-datos/
│   │   ├── 07-prototipo-ux-ui/
│   │   └── 08-plan-release-sprint-backlog.md
│   ├── entregable-2/         # Producto y Cierre (Semanas 9 a 16)
│   │   ├── 01-estandares-codigo-git.md
│   │   ├── 02-pruebas-cobertura/
│   │   ├── 03-metricas-dora.md
│   │   ├── 04-manual-usuario.md
│   │   └── 05-informe-final-cierre.md
│   └── avances-semanales/    # Evidencias y reportes semanales
├── src/                      # Código Fuente del Sistema SIRA
│   ├── backend/              # API REST y Lógica de Negocio
│   └── frontend/             # Interfaz Web Adaptativa
├── tests/                    # Pruebas Unitarias e Integración
└── README.md                 # Vista General del Proyecto