# Prototipo de baja fidelidad — SIRA

Prototipo navegable **solo frontend** (HTML + CSS + JS, sin dependencias ni backend). Usa datos ficticios guardados en memoria, que se reinician al recargar la página.

## Cómo abrirlo

- Doble clic en `index.html`, o
- `python -m http.server 8765` dentro de esta carpeta, y luego abrir <http://127.0.0.1:8765>

## Recorrido sugerido

Ingresa con el rol **Recorrido completo** para ver todos los módulos y sigue este orden:

1. **Agendar cita (M2):** busca el DNI `45871236`, elige un turno libre y confirma (3 pasos).
2. **Triaje (M1):** marca "Llegó", registra los signos vitales y guarda.
3. **Agenda médica (M1):** pulsa "Atender", ingresa el diagnóstico CIE-10, la receta y las órdenes, y firma.
4. **Laboratorio (M3):** carga el resultado de la orden y publícalo en la HCE.
5. **Facturación (M4):** revisa la liquidación por convenio y luego envía o registra la glosa.
6. **Dashboard (M5):** los indicadores y la bitácora se recalculan con lo que hiciste.
7. **Portal paciente (M6):** solo un esbozo (Sprint 2).

Las notas amarillas explican la regla o el requisito (RF/RNF) detrás de cada pantalla. Se pueden ocultar con la casilla "notas" de la barra superior.
