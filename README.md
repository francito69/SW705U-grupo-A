# Sistema de Información Clínico-Administrativo (SIRA) — Clínica San Rafael S.A.C.

![Universidad Nacional de Ingeniería](<https://img.shields.io/badge/Universidad-UNI%20--%20FIIS-blue?style=for-the-badge>)
![Curso](<https://img.shields.io/badge/Curso-SW705U%20Taller%20de%20Ingenier%C3%ADa%20de%20Software%20I-green?style=for-the-badge>)
![Grupo](<https://img.shields.io/badge/Grupo-Grupo%20A-orange?style=for-the-badge>)
![Estado](<https://img.shields.io/badge/Estado-En%20Desarrollo-yellow?style=for-the-badge>)
[![CI](https://github.com/francito69/SW705U-grupo-A/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/francito69/SW705U-grupo-A/actions/workflows/ci.yml)

Repositorio oficial del **Sistema de Información Clínico-Administrativo (SIRA)** para la sede San Borja de la **Clínica San Rafael S.A.C.**, desarrollado en la **Universidad Nacional de Ingeniería (UNI)** para la asignatura **SW705U - Taller de Ingeniería de Software I**.

---

## Información Académica

* **Universidad:** Universidad Nacional de Ingeniería (UNI)
* **Facultad:** Facultad de Ingeniería Industrial y de Sistemas (FIIS)
* **Escuela Profesional:** Ingeniería de Software
* **Curso:** SW705U – Taller de Ingeniería de Software I
* **Docente / Product Owner (Ref.):** Prof. José Carlos García La Riva
* **Grupo:** Grupo A

---

## Equipo de Desarrollo

| N.° | Apellidos y Nombres                          | Correo Electrónico             | Rol Asignado                       |
| :--: | :------------------------------------------- | :------------------------------ | :--------------------------------- |
|  1  | **Albino Soto, Christopher Henrry**    | `christopher.albino.s@uni.pe` | Desarrollador Fullstack / BD       |
|  2  | **Inga Champi, Franz Joe**             | `franz.inga.c@uni.pe`         | Arquitecto / Desarrollador Backend |
|  3  | **Rashuaman Sapallanay, Ricco Didier** | `ricco.rashuaman.s@uni.pe`    | Analista QA / UI-UX / Frontend     |

---

## Descripción y Caso Empresarial

La **Clínica San Rafael S.A.C.** (sede San Borja) afronta ineficiencias operativas y financieras por el uso de historias clínicas fragmentadas en papel/Excel, demoras de hasta 48 horas en entrega de resultados, una tasa de inasistencia a citas del 18% y conciliaciones manuales con 5 EPS/SOAT que generan glosas.

### Objetivo General

Desarrollar e implementar la plataforma web **SIRA** para centralizar la gestión clínico-administrativa de la clínica, garantizando el acceso seguro a historias clínicas en menos de 2 segundos, optimizando la agenda de citas y automatizando la facturación por convenios, bajo estricto cumplimiento de la **Ley N.° 29733 de Protección de Datos Personales**.

---

## Módulos del Sistema y Planificación

| Módulo                                            | Descripción Resumida                                                                       |      Prioridad / Fase      |
| :------------------------------------------------- | :------------------------------------------------------------------------------------------ | :------------------------: |
| **M1. Historia Clínica Electrónica (HCE)** | Expediente único, antecedentes, diagnósticos CIE-10, recetas e indicaciones con RBAC.     | Imprescindible*(Sprint 1)* |
| **M2. Agenda y Citas Médicas**              | Disponibilidad consolidada de 12 consultorios, bloqueo de solapamientos y recordatorios.    | Imprescindible*(Sprint 1)* |
| **M3. Laboratorio e Imágenes**              | Circuito de órdenes digitales, carga de resultados e integración inmediata al expediente. | Imprescindible*(Sprint 2)* |
| **M4. Facturación y Convenios**             | Aplicación de tarifarios por convenio (Particular, 5 EPS, SOAT) y control de glosas.       | Imprescindible*(Sprint 2)* |
| **M5. Reportes Gerenciales**                 | Dashboard con métricas de ocupación, tiempos de espera, ingresos e inasistencia.          | Imprescindible*(Sprint 2)* |
| **M6. Portal del Paciente / Telemedicina**   | Agendamiento en línea y consultas virtuales básicas.                                      |    Deseable*(Sprint 2)*    |

---

## Estructura del Repositorio

```text
.
├── .github/workflows/ci.yml   # ruff + pytest con cobertura en cada pull request
├── sira/
│   ├── backend/               # API REST FastAPI (seguridad, auditoria, hce, agenda, convenios, notificaciones)
│   ├── frontend/              # aplicación web React + TypeScript + Vite
│   ├── database/              # scripts SQL (01-esquema, 02-datos-prueba, 03-verificacion)
│   ├── tests/                 # pruebas con pytest
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── docs/
│   ├── entregable-1/
│   ├── entregable-2/
│   ├── entregable-4/
│   ├── entregable-5/
│   ├── entregable-7/
│   └── prototipo/             # prototipo navegable inicial en HTML
├── .gitignore
└── README.md
```

## Ejecución local

### Backend y pruebas

```bash
cd sira
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m backend.seed --reiniciar  # crea la base SQLite con datos ficticios
uvicorn backend.main:app --reload   # API en http://127.0.0.1:8000/docs
pytest -q                           # suite de pruebas
```

### Frontend

```bash
cd sira/frontend
npm install
npm run dev
```

Las cuentas de demostración se listan en `GET /api/v1/auth/demo`. Todos los datos son ficticios.
