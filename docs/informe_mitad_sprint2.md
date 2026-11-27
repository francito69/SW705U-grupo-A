# Informe de mitad del Sprint 2 — Sistema SIRA (Clínica San Rafael S.A.C.)

**Fecha de corte:** 2026-11-26 (día 6 de 10)  
**Equipo:** Grupo A (`SW705U`) — Albino Soto, Christopher Henrry · Inga Champi, Franz Joe · Rashuaman Sapallanay, Ricco Didier  
**Repositorio:** https://github.com/francito69/SW705U-grupo-A  

---

## 1. Estado del sprint

- **Puntos comprometidos:** 19 pts
- **Puntos hechos al corte:** 14 pts (`HU-03`, `HU-05`, `HU-08`, `SC-02`)
- **Puntos restantes al corte:** 5 pts (`HU-07` en curso al momento del corte; completada e integrada durante la sesión en el PR #14)

| Historia | Título | Puntos | Estado al corte | Fecha de fin |
| :--- | :--- | :---: | :---: | :---: |
| `HU-03` | Registro y validación de DNI del paciente | 3 | hecha | 2026-11-22 |
| `HU-05` | Triaje y alertas de signos vitales | 3 | hecha | 2026-11-23 |
| `HU-08` | Copago con tarifario vigente y flujo integrado | 5 | hecha | 2026-11-25 |
| `SC-02` | Cobertura mínima 90 % con ramas en CI y plantilla SC | 3 | hecha | 2026-11-26 |
| `HU-07` | Recordatorio de cita 24 horas antes (integración) | 5 | en_curso | — |

---

## 2. Métricas de proceso

- **Burndown (real vs. ideal al día 6):** 5 pts restantes reales frente a 7.6 pts ideales (`-2.6 pts` → **adelantado**).
- **Ritmo del equipo:** 2.33 pts/día.
- **Proyección al cierre (día 10):** 23.3 pts de 19 pts comprometidos.
- **Tiempo de ciclo (`metricas/prs.csv`):**
  - Pull requests fusionados: 6 (`#8`, `#9`, `#10`, `#11`, `#12`, `#14`)
  - Mediana: **4.0 días** | Máximo: **4.0 días**
  - Pull requests más lentos: `#8`, `#9`, `#10`, `#11` y `#12` (4.0 días cada uno, abiertos el 22/11 y fusionados en lote el 26/11).
  - **Acción de mejora:** Instituir una ventana diaria de revisión de PRs (SLA < 24 h) inmediatamente después de la Daily para evitar acumulación de lotes.

---

## 3. Métricas de producto

| Métrica | Umbral del equipo | Resultado | ¿Cumple? |
| :--- | :--- | :--- | :---: |
| Pruebas automatizadas (`pytest`) | Todas en verde | 169 passed, 0 failed | Sí |
| Cobertura con ramas: módulos nuevos (`citas.py`, `notificaciones.py`, `recordatorios.py`) | ≥ 90 % | 100 % (0 líneas/ramas sin cubrir) | Sí |
| Cobertura con ramas: total del repositorio | ≥ 90 % | 95 % (2214 stmts, 66 miss, 372 branches, 52 partial) | Sí |
| Complejidad ciclomática máxima (`radon cc`) | ≤ 10 por función | Promedio A (2.42); módulos nuevos en grado A. Dos funciones previas en `hce/service.py` (`coincidencias_alergia` = C 15, `finalizar_atencion` = C 12) | Parcial (módulos nuevos sí; deuda puntual en `hce/service.py`) |
| Defectos abiertos al cierre | 0 | 0 | Sí |

- **Mutaciones manuales verificadas en `app/recordatorios.py`:**
  1. `<=` cambiado por `<` en la ventana de 24 h → detectada por `test_ventana_de_24_horas_para_recordar[CP-01-1440-reservada-False-True]`.
  2. Eliminación de `not cita.recordada` → detectada por `test_ventana_de_24_horas_para_recordar[CP-07-300-reservada-True-False]` y `test_no_repeticion_en_segundo_ciclo`.

---

## 4. Riesgos y decisiones

- **Riesgo:** `HU-07` y `SC-02` modificaban simultáneamente `app/citas.py`, generando conflicto de fusión.  
  **Decisión:** Se actualizó `feature/hu-07-recordatorio` con `origin/main`, se resolvió el conflicto conservando `HORAS_ANTES_RECORDATORIO = 24`, `recordada`, `CANAL_DEFECTO = "SMS"` y `canal`, se verificó ausencia de marcadores y se ejecutó `pytest` antes de fusionar el PR #14. **Responsable:** Inga Champi, Franz Joe.
- **Riesgo:** Dos funciones heredadas en `app/modulos/hce/service.py` (`coincidencias_alergia` con CC=15 y `finalizar_atencion` con CC=12) superan el umbral de complejidad de 10.  
  **Decisión:** Programar su refactorización en funciones auxiliares más pequeñas durante los días 7–8 del sprint manteniendo la cobertura ≥ 95 %. **Responsable:** Rashuaman Sapallanay, Ricco Didier.
- **Riesgo:** Cuello de botella en revisión de PRs (mediana 4.0 días).  
  **Decisión:** Revisar y aprobar PRs en bloques diarios de 15 minutos tras la Daily. **Responsable:** Albino Soto, Christopher Henrry.

---

## 5. Plan hasta el cierre del sprint

- **Días 7–8 (27–28 nov):** Cerrar la integración final de `HU-07` en producción/demo, refactorizar `coincidencias_alergia` y `finalizar_atencion` para bajar su complejidad a grado A/B (≤ 10), y validar casos de borde adicionales.
- **Días 9–10 (30 nov – 02 dic):** Ejecutar pruebas de regresión completas, actualizar evidencias del incremento para el Avance 6 y preparar la demo de cierre.
- **Solicitud al Product Owner:** Confirmar los criterios de aceptación finales del módulo de recordatorios (plantilla de mensaje SMS) y validar la prioridad de las historias restantes del Sprint 2 para la revisión de cierre.
