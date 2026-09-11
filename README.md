# 🏥 Sistema de Información Clínico-Administrativo — Clínica San Rafael S.A.C.

![Universidad Nacional de Ingeniería](https://img.shields.io/badge/Universidad-UNI%20--%20FIIS-blue?style=for-the-badge)
![Curso](https://img.shields.io/badge/Curso-SW705U%20Taller%20de%20Ingenier%C3%ADa%20de%20Software%20I-green?style=for-the-badge)
![Grupo](https://img.shields.io/badge/Grupo-Grupo%20A-orange?style=for-the-badge)
![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow?style=for-the-badge)

Repositorio oficial del proyecto integrador para la **Clínica San Rafael S.A.C.**, desarrollado en la **Universidad Nacional de Ingeniería (UNI)** como parte de la asignatura **SW705U - Taller de Ingeniería de Software I**.

---

## 📋 Información Académica

* **Universidad:** Universidad Nacional de Ingeniería (UNI)
* **Facultad:** Facultad de Ingeniería Industrial y de Sistemas (FIIS)
* **Escuela:** Escuela Profesional de Ingeniería de Software
* **Curso:** SW705U – Taller de Ingeniería de Software I
* **Docente:** José Carlos García La Riva
* **Grupo:** Grupo A

---

## 👥 Integrantes y Roles

| N.° | Apellidos y Nombres | Código / Rol | Correo Electrónico |
| :---: | :--- | :--- | :--- |
| 1 | **Albino Soto, Christopher Henrry** | Por ver | `christopher.albino.s@uni.pe` |
| 2 | **Inga Champi, Franz Joe** | Por ver | `franz.inga.c@uni.pe` |
| 3 | **Rashuaman Sapallanay, Ricco Didier** | Por ver | `ricco.rashuaman.s@uni.pe` |

---

## 🎯 Descripción y Caso Empresarial

La **Clínica San Rafael S.A.C.** (ubicada en San Borja, Lima) es una entidad privada de salud que ofrece atención en consulta ambulatoria, laboratorio, imágenes, farmacia, hospitalización, emergencia y cirugía ambulatoria. Actualmente afronta serias ineficiencias debido a la fragmentación de registros clínicos en papel o Excel, agendas saturales con alta inasistencia (18%) y facturación manual con aseguradoras/EPS[cite: 1, 3].

### Objetivo del Proyecto
Desarrollar un **sistema de información clínico-administrativo unificado** que integre la historia clínica electrónica (HCE), la agenda de citas multiespecialidad, la gestión de órdenes de laboratorio e imágenes, la facturación con aseguradoras y reportes gerenciales en tiempo real[cite: 1, 3]. Todo bajo estricto cumplimiento de la **Ley N.º 29733 de Protección de Datos Personales**[cite: 1, 3].

---

## 🧩 Alcance Funcional por Módulos

* **M1. Historia Clínica Electrónica (HCE):** Registro unificado de consultas, diagnósticos (CIE-10), tratamientos y recetas[cite: 1, 3]. *(Sprint 1)*[cite: 1, 3]
* **M2. Agenda y Citas Médicas:** Programación por médico/especialidad, recordatorios automáticos (SMS/WhatsApp/Correo) y reprogramaciones[cite: 1, 3]. *(Sprint 1)*[cite: 1, 3]
* **M3. Laboratorio e Imágenes:** Registro de órdenes médicas, carga y entrega de resultados en formato digital[cite: 1, 3]. *(Sprint 2)*[cite: 1, 3]
* **M4. Facturación y Convenios:** Emisión de comprobantes, tarifarios diferenciados (Particular, EPS, SOAT) y gestión de glosas[cite: 1, 3]. *(Sprint 2)*[cite: 1, 3]
* **M5. Reportes Gerenciales:** Dashboards de ocupación, tiempos de espera, ingresos e inasistencias[cite: 1, 3]. *(Sprint 2)*[cite: 1, 3]
* **M6. Portal del Paciente / Telemedicina (Deseable):** Agendamiento online y consultas virtuales[cite: 1, 3]. *(Sprint 2)*[cite: 1, 3]

---

## 📁 Estructura del Repositorio

El repositorio está organizado jerárquicamente para separar la documentación de ingeniería, el código fuente y las evidencias/capturas semanales:

```text
.
├── .github/                   # Workflows de GitHub Actions (CI/CD)
├── docs/                      # Documentación del Proyecto
│   ├── entregable-1/          # Documentación de Ingeniería (Semanas 2 a 8)
│   │   ├── 01-acta-constitucion.md
│   │   ├── 02-documento-vision.md
│   │   ├── 03-especificacion-requerimientos-ERS.md
│   │   ├── 04-modelos-uml/         # Diagramas Casos de Uso, Clases, Actividades
│   │   ├── 05-arquitectura-SAD.md  # Vistas 4+1, Decisiones ADR
│   │   ├── 06-modelo-base-datos/   # ERD, Diccionario de Datos, Script DDL
│   │   ├── 07-prototipo-ux-ui/     # Enlaces a Figma / Wireframes
│   │   └── 08-plan-release-sprint-backlog.md
│   ├── entregable-2/          # Producto y Cierre (Semanas 9 a 16)
│   │   ├── 01-estandares-codigo-git.md
│   │   ├── 02-pruebas-cobertura/   # Casos de prueba, Reportes de Cobertura
│   │   ├── 03-metricas-dora.md
│   │   ├── 04-manual-usuario.md
│   │   └── 05-informe-final-cierre.md
│   └── avances-semanales/      # Evidencias presentadas por semana
│       ├── semana-02/
│       │   ├── capturas/
│       │   └── reporte.md
│       ├── semana-03/
│       ├── ...
│       └── semana-16/
├── src/                       # Código Fuente del Sistema
│   ├── backend/               # API / Lógica de Negocio
│   └── frontend/              # Interfaz de Usuario
├── tests/                     # Suite de Pruebas Unitarias e Integración
└── README.md                  # Vista General del Repositorio