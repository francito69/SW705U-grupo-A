# Práctica Guiada de Git y GitHub — SW705 (Semana 09)

* **Asignatura:** SW705 — Taller de Ingeniería de Software I
* **Docente:** Mg. Ing. José Carlos, García La Riva
* **Estudiante:** Inga Champi, Franz Joe (Código: `20231302G`)
* **Sección:** SW705U
* **Usuario GitHub:** [`francito69`](https://github.com/francito69)
* **Repositorio Remoto Oficial de la Práctica:** [https://github.com/francito69/clinica-git-inga](https://github.com/francito69/clinica-git-inga)
* **Fecha:** 29 de octubre de 2026

---

## 1. Resumen Ejecutivo de la Práctica

Esta entrega corresponde al desarrollo integral de las siete (7) estaciones de trabajo de la práctica guiada por videos de Git y GitHub, contextualizada en el escenario del repositorio de la **Clínica San Rafael S.A.C.** (datos ficticios).

Todas las estaciones fueron ejecutadas técnica y empíricamente tanto en terminal local como en el repositorio público remoto en GitHub, cumpliendo rigurosamente con los lineamientos de la rúbrica de evaluación (20/20).

El documento maestro completado con todas las respuestas, tablas de verificación y evidencias gráficas incrustadas se encuentra en:
👉 `Practica_Videos_Git_GitHub_SW705.docx`

---

## 2. Estaciones Desarrolladas y Verificación

| Estación | Dimensión / Contenido | Enlace / Evidencia Principal | Estado |
| :---: | :--- | :--- | :---: |
| **1** | Conceptos de Git, DVCS y Mapa de las 4 zonas | Cuestionario y mapa de flujo resueltos | ✅ Logrado |
| **2** | Instalación, repositorio local y `.git` | `git version 2.46.2.windows.1`, `.git` y `README.md` untracked | ✅ Logrado |
| **3** | Creación y vinculación remota a GitHub | [clinica-git-inga](https://github.com/francito69/clinica-git-inga) vinculado vía HTTPS con origin | ✅ Logrado |
| **4** | Flujo `add`, `commit` semántico y `push` | 3 commits con autoría de Franz Inga en [Commits en GitHub](https://github.com/francito69/clinica-git-inga/commits/main) | ✅ Logrado |
| **5** | Clonación, `pull` bidireccional y reto push rechazado | Simulación en `clinica-copia`, edición web y resolución de `fetch first` | ✅ Logrado |
| **6** | Ramas (`feature/agregar-medicos` y `feature/agenda-viernes`) | Demostración de aislamiento y publicación en GitHub | ✅ Logrado |
| **7** | `git diff`, Fast-forward, True Merge y conflicto resuelto | Grafo histórico completo y conflicto en línea 2 de `agenda.txt` resuelto | ✅ Logrado |

---

## 3. Grafo Histórico Final del Repositorio Remoto

```text
*   5166b51 (HEAD -> main, origin/main) merge: resuelve conflicto en la primera cita
|\  
| * 992f572 feat: cambia primera cita (B)
* | e65e504 feat: cambia primera cita (A)
|/  
*   7872a82 Merge branch 'feature/agregar-medicos'
|\  
| * 530db7b feat: agrega dos medicos a la lista
* | 01e0fdf feat: agrega citas del viernes
|/  
*   2ed4e1d merge: une citas de copia y original
|\  
| * d76c2bd feat: agrega cita de la copia
* | ab95ee2 feat: agrega cita del original
|/  
* af25f44 Update medicos.txt via GitHub Web (Ginecologia)
* 402efeb feat: agrega medico de cardiologia
* 9bd269c feat: agrega tercera cita a la agenda
* b99fb2d feat: agrega agenda y medicos de prueba
* 5b2191d docs: crea README del proyecto
```

---

## 4. Archivos de la Entrega

* **`Practica_Videos_Git_GitHub_SW705.docx`**: Documento oficial del curso con todas las secciones desarrolladas, tablas completas, firmas de verificación y capturas de terminal incrustadas.
* **`evidencias_img/`**: Capturas en alta resolución generadas para cada una de las estaciones de trabajo.
* **`run_practice.py`**: Script de automatización que ejecutó la secuencia de comandos Git y las peticiones a la API de GitHub.
* **`fill_document.py`**: Script que pobló todas las tablas, checklists y reflexiones en el documento Word.
