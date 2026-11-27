# Informe de mitad del Sprint 2 — Sistema SIRA (Clínica San Rafael S.A.C.)

**Fecha de corte:** 2026-11-26 (día 6 de 10)  
**Equipo:** Grupo A (`SW705U`) — Albino Soto, Christopher Henrry · Inga Champi, Franz Joe · Rashuaman Sapallanay, Ricco Didier  
**Repositorio:** https://github.com/francito69/SW705U-grupo-A  

---

## 1. Estado del sprint

- **Puntos comprometidos:** 19 pts
- **Puntos hechos al corte:** 14 pts (`HU-03a`, `HU-03b`, `HU-02`, `T-01`)
- **Puntos restantes al corte:** 5 pts (`HU-07` en curso al momento del corte; completada e integrada durante la sesión en el PR #14)

| Historia | Título | Puntos | Estado al corte | Fecha de fin | Pull request |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `HU-03a` | Validación del DNI del paciente (D1) | 3 | hecha | 2026-11-26 | #8 |
| `HU-03b` | Edad cumplida del paciente (D3) | 3 | hecha | 2026-11-26 | #9 |
| `HU-02` | Flujo integrado cita–triaje–atención y plazo de 90 días (D2) | 5 | hecha | 2026-11-26 | #10 |
| `T-01` | Cobertura mínima de 90 % con ramas en CI y plantilla de SC | 3 | hecha | 2026-11-26 | #11 y #12 |
| `HU-07` | Recordatorio de cita 24 horas antes (integración) | 5 | en_curso | — | #14 |

---

## 2. Métricas de proceso

- **Burndown (real vs. ideal al día 6):** 5 pts restantes reales frente a 7.6 pts ideales (`-2.6 pts` → **adelantado**). Los 14 pts hechos se registran el 26/11, día en que se fusionaron los PR #8 a #12.
- **Ritmo del equipo:** 2.33 pts/día.
- **Proyección al cierre (día 10):** 23.3 pts de 19 pts comprometidos.
- **Tiempo de ciclo (`metricas/prs.csv`, hora de Lima):**
  - Pull requests fusionados: 6 (`#8`, `#9`, `#10`, `#11`, `#12`, `#14`)
  - Mediana: **4.0 días** | Máximo: **4.0 días**
  - Pull requests más lentos: `#8`, `#9`, `#10`, `#11` y `#12` (4.0 días cada uno, abiertos el 22/11 y fusionados en lote el 26/11).
  - `#14` (`HU-07`) se abrió y fusionó en la misma sesión (0.0 días).
  - **Acción de mejora:** ventana diaria de revisión de PRs (SLA < 24 h) inmediatamente después de la Daily para evitar acumulación de lotes.

---

## 3. Métricas de producto

| Métrica | Umbral del equipo | Resultado | ¿Cumple? |
| :--- | :--- | :--- | :---: |
| Pruebas automatizadas (`pytest`) | Todas en verde | 169 passed, 0 failed | Sí |
| Cobertura con ramas: módulos nuevos (`citas.py`, `notificaciones.py`, `recordatorios.py`) | ≥ 90 % | 100 % (0 líneas/ramas sin cubrir) | Sí |
| Cobertura con ramas: total del repositorio | ≥ 90 % | 95 % (2214 stmts, 66 miss, 372 branches, 52 partial) | Sí |
| Complejidad ciclomática máxima (`radon cc`) | ≤ 10 por función | Módulos nuevos en grado A (máximo 3). Promedio general A (2.42); 6 funciones previas superan 10, la mayor `disponibilidad` = E 31 | Parcial (módulos nuevos sí; 6 funciones previas no) |
| Defectos abiertos al cierre | 0 | 0 | Sí |

Funciones sobre el umbral (`radon cc -s -n C`):

| Función | Módulo | Complejidad |
| :--- | :--- | :---: |
| `disponibilidad` | `modulos/agenda/service.py` | E (31) |
| `sembrar_catalogos` | `seed.py` | C (17) |
| `coincidencias_alergia` | `modulos/hce/service.py` | C (15) |
| `finalizar_atencion` | `modulos/hce/service.py` | C (12) |
| `citas_salida` | `api/v1/composicion.py` | C (11) |
| `listar_citas` | `modulos/agenda/service.py` | C (11) |

- **Mutaciones manuales verificadas en `app/recordatorios.py`:**
  1. `<=` cambiado por `<` en la ventana de 24 h → detectada por `test_ventana_de_24_horas_para_recordar[CP-01-1440-reservada-False-True]`.
  2. Eliminación de `not cita.recordada` → detectada por `test_ventana_de_24_horas_para_recordar[CP-07-300-reservada-True-False]` y `test_no_repeticion_en_segundo_ciclo`.

---

## 4. Riesgos y decisiones

- **Riesgo:** `HU-07` y `SC-02` (canal de envío por defecto) modificaban las mismas líneas de `app/citas.py`, generando conflicto de fusión.  
  **Decisión:** Se actualizó `feature/hu-07-recordatorio` con `origin/main`, se resolvió el conflicto conservando `HORAS_ANTES_RECORDATORIO = 24`, `recordada`, `CANAL_DEFECTO = "SMS"` y `canal`, se verificó ausencia de marcadores y se ejecutó `pytest` antes de fusionar el PR #14. **Responsable:** Inga Champi, Franz Joe.
- **Riesgo:** Seis funciones previas superan el umbral de complejidad de 10; la mayor es `disponibilidad` (E 31) en la agenda, que concentra la lógica de turnos libres.  
  **Decisión:** Refactorizar `disponibilidad` en funciones auxiliares (bloques del turno, citas activas y plazo de 90 días) durante los días 7–8, manteniendo la cobertura ≥ 95 %; las otras cinco pasan al backlog técnico. **Responsable:** Rashuaman Sapallanay, Ricco Didier.
- **Riesgo:** Cuello de botella en revisión de PRs (mediana 4.0 días).  
  **Decisión:** Revisar y aprobar PRs en bloques diarios de 15 minutos tras la Daily. **Responsable:** Albino Soto, Christopher Henrry.

---

## 5. Plan hasta el cierre del sprint

- **Día 6 (26/11, tras el corte):** reestructuración del repositorio: `app/` y `tests/` pasan a `sira/backend/` y `sira/tests/` (PR #13).
- **Días 7–8 (27/11 y 30/11):** refactorizar `disponibilidad` hasta grado B (≤ 10) con sus pruebas en verde y validar casos de borde adicionales del recordatorio.
- **Días 9–10 (01/12 y 02/12):** ejecutar la regresión completa en CI, actualizar las evidencias del incremento para el Avance 6 y preparar la demo de cierre.
- **Solicitud al Product Owner:** confirmar los criterios de aceptación finales del módulo de recordatorios (plantilla del mensaje SMS) y validar la prioridad de las historias restantes del Sprint 2 para la revisión de cierre.
