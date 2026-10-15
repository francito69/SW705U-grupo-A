# 7. Prototipos UX/UI y Diseño de Interfaz de Usuario — Sistema SIRA

--------------------------------------------------------------------------------

### Contexto y Principios de Diseño Centrado en el Usuario (Semana 6)

El presente documento constituye la especificación formal del **Prototipo UX/UI y Diseño de Interfaz** para el **Sistema de Información Clínico-Administrativo (SIRA)** de la **Clínica San Rafael S.A.C. (Sede San Borja)**, desarrollado en el marco del curso Taller de Ingeniería de Software I (SW705).

El diseño de las interfaces de usuario traduce directamente los requerimientos funcionales y no funcionales de los documentos precedentes (`01-acta-constitucion.md`, `02-documento-vision.md`, `03-especificacion-requerimientos-ERS.md`, `04-modelosUML.md`, `05-arquitectura-SAD.md` y `06-modelo-base-datos.md`) en experiencias operativas tangibles, enfocadas en erradicar los cinco perjuicios históricos de la clínica:
1. **Seguridad clínica y visibilidad médica unificada:** Acceso inmediato a la Historia Clínica Electrónica con alertas destacadas de alergias para evitar errores de medicación (RF-001, RNF-001).
2. **Eficiencia en admisión y erradicación del no-show:** Flujo de agendamiento sin solapamientos en un máximo de 3 pasos (RF-002, RNF-005) con despacho automatizado de recordatorios 24 h (RF-003).
3. **Usabilidad inclusiva para personal con distinta alfabetización digital:** Interfaces limpias, con terminología médica estándar (CIE-10), componentes de alto contraste y baja carga cognitiva para evitar la resistencia al cambio (Riesgo R-02 del Acta).

#### Sistema de Diseño y Pautas Visuales (Design System SIRA)
* **Paleta de Colores Institucional:**
  * **Azul Clínico Principal (`#0A4D68` / `#088395`):** Denota sobriedad, confianza médica y autoridad en barras de navegación, botones primarios y títulos.
  * **Cyan / Teal de Acento (`#05BFDB` / `#EBF7F9`):** Fondos de selección, chips de estado activo y resaltado de consultorios disponibles.
  * **Rojo Carmesí Alerta Médica (`#DC2626` / `#FEE2E2`):** Exclusivo para alergias del paciente, contraindicaciones farmacológicas y cancelaciones críticas.
  * **Ámbar Preventivo (`#F59E0B` / `#FEF3C7`):** Observaciones de glosas, horarios próximos a vencer y citas en espera de confirmación.
  * **Verde Esmeralda Éxito (`#10B981` / `#D1FAE5`):** Citas confirmadas, resultados de laboratorio completados y copagos cancelados.
  * **Gris Neutro y Superficies (`#F8FAFC` fondo base, `#FFFFFF` tarjetas, `#64748B` textos secundarios, `#1E293B` textos principales).
* **Tipografía:** Familia `Inter` / `Roboto` (sin serifa, escala tipográfica jerárquica de 12px a 24px) para máxima legibilidad en monitores médicos de consultorio y terminales de recepción.
* **Componentes Base:** Tarjetas elevadas con sombra sutil (`box-shadow`), badges con bordes redondeados (`rounded-full`), inputs con validación en línea y botones con estados claros (Normal, Hover, Active, Disabled).

--------------------------------------------------------------------------------

## 7.1. Pantalla 1 — Registro de Atención y Consulta de HCE Unificada (Médico Tratante — M1)

### 7.1.1. Arquitectura de Información y Mapeo Funcional
* **Módulo Relacionado:** M1 — Historia Clínica Electrónica (HCE).
* **Usuario Objetivo:** Médico Tratante (Cardiología, Pediatría, Medicina General, etc.).
* **Trazabilidad:** RF-001 (HCE unificada), RF-004 (Órdenes digitales), RNF-001 (Apertura en $\le 2$ s con 8 000 registros), RNF-002 (RBAC y Ley N.° 29733), RNF-004 (Baja lógica sin borrado físico); Historias de Usuario HU01, HU04, HU08.
* **Estructura de la Pantalla:**
  1. **Barra Superior de Contexto del Paciente (Patient Banner):** Barra fija en la parte superior que muestra de forma perenne la fotografía/avatar del paciente, apellidos y nombres completos, tipo y número de documento (DNI), edad calculada, sexo biológico, tipo de sangre, aseguradora activa (ej. *Pacífico EPS - Plan Red Preferente*) y código de historia clínica.
  2. **Banner de Alerta Crítica (Alergias y Advertencias):** Franja roja destacada con icono de advertencia (`AlertTriangle`) inmediatamente debajo de los datos del paciente: *"ALERGIAS: PENICILINA / SULFAS — ASMA BRONQUIAL LEVE"*. Este componente mitiga directamente el riesgo de eventos adversos reportado en el caso.
  3. **Panel Lateral Izquierdo (35 % ancho) — Línea de Tiempo del Expediente Unificado:**
     * Buscador y filtro por especialidad o rango de fechas.
     * Lista cronológica paginada de atenciones históricas (Cardiología 15/08/2026, Dermatología 02/06/2026, Consulta Externa 10/01/2026).
     * Cada tarjeta de atención histórica muestra fecha, médico tratante, diagnóstico CIE-10 principal y un botón *"Ver detalle / Receta"*.
     * Sección de *"Resultados de Laboratorio e Imágenes vinculados"* con badges de estado y enlace de descarga de PDF digital.
  4. **Panel Central / Derecho (65 % ancho) — Acto Médico Actual:**
     * **Widget de Triaje (Solo Lectura):** Tarjeta horizontal con los signos vitales tomados previamente por enfermería (PA: 120/80 mmHg, FC: 78 lpm, Temp: 36.8 °C, Peso: 72.5 kg, Talla: 1.70 m, IMC: 25.1 Normal).
     * **Motivo de Consulta y Anamnesis:** Áreas de texto expandibles para el relato del paciente y examen físico.
     * **Diagnóstico CIE-10 (Buscador Predictivo):** Input con autocompletado en tiempo real que busca por código o descripción médica (ej. escribe *"J00"* y sugiere *"J00 - Rinofaringitis aguda [resfriado común]"*).
     * **Prescripción Médica (Receta Digital):** Tabla dinámica para agregar medicamentos (Medicamento, Concentración, Posología/Vía, Frecuencia y Duración).
     * **Barra de Acciones Inferior:**
       * Botón secundario *"Emitir Orden de Laboratorio / Imágenes"* (despliega modal).
       * Botón de anulación lógica *"Anular Registro"* (requiere confirmación y motivo).
       * Botón primario prominente *"Firmar y Finalizar Atención"*.

---

### 7.1.2. Marcador de Imagen para el Documento
![image1](Mockup_Pantalla1_HCE.png)

---

### 7.1.3. Prompt Detallado para Generar la Pantalla en Stitch IA

> **INSTRUCCIONES PARA EL ESTUDIANTE:**  
> Copia el siguiente texto íntegro en la caja de prompt de **Stitch IA** (o herramienta de generación de interfaces IA) para generar el mockup de alta fidelidad de la Pantalla 1.

```text
Create a modern, clean, high-fidelity medical desktop web application screen for the Electronic Health Record (EHR) and Medical Consultation module of "Clínica San Rafael S.A.C.". 

Layout & Dimensions: Desktop widescreen (1440x900px), professional clinical SaaS interface. Light mode with white (#FFFFFF) and soft light slate (#F8FAFC) background, primary deep clinical teal/blue (#0A4D68 and #088395), dark navy text (#1E293B), subtle borders (#E2E8F0), and Inter/Roboto typography.

1. TOP NAVIGATION & HEADER:
- Deep teal header bar with "Clínica San Rafael" logo, "SIRA" title, breadcrumb "Consulta Externa > Cardiología > Atención en Curso".
- Right side: Doctor profile "Dr. Carlos Mendoza (CMP: 48921)", active badge "Consultorio 04", and notification bell.

2. PERSISTENT PATIENT SUMMARY BANNER (Top full-width card):
- Patient avatar placeholder, patient name in bold 18px: "QUISPE ROJAS, MARÍA ELENA", "DNI: 45892014 | Femenino | 42 años | Tipo: O+".
- Insurance Badge: Green pill badge "Pacífico Seguros (EPS Copago 15%)".
- CRITICAL MEDICAL ALERT BANNER: Red highlight badge (#DC2626) with warning icon: "ALERGIAS: PENICILINA - SULFAS | HIPERTENSIÓN ARTERIAL CONTROLADA".

3. MAIN CONTENT - TWO-COLUMN CLINICAL DASHBOARD:
LEFT COLUMN (35% width, Timeline Feed):
- Section title: "Expediente Clínico Unificado (Historial Multiespecialidad)" with search bar and date filter.
- Chronological timeline cards:
  * Card 1 (Active/Recent): "12/09/2026 - Medicina General (Dr. Ramos) - Diagnóstico: J00 Rinofaringitis aguda".
  * Card 2: "15/05/2026 - Dermatología (Dra. Soto) - Diagnóstico: L20 Dermatitis atópica".
  * Card 3: "04/02/2026 - Laboratorio Clínico: Perfil Lipídico Completo [PDF badge]".
- Small button at bottom: "Ver historial completo (8 atenciones)".

RIGHT COLUMN (65% width, Active Medical Encounter):
- Card 1: "Signos Vitales y Triaje (Tomado por Enf. Rocío Paz a las 09:15 AM)":
  * 4 quick stat pill boxes: "PA: 125/80 mmHg" (Normal), "FC: 76 bpm", "Temp: 36.7 °C", "IMC: 24.8 (Normal - 68 kg / 1.65 m)".
- Card 2: "Motivo de Consulta y Examen Clínico":
  * Multiline text input with placeholder text: "Paciente refiere cefalea matutina recurrente y mareos leves desde hace 3 días...".
- Card 3: "Diagnóstico CIE-10":
  * Search bar with active dropdown showing: "I10 - Hipertensión esencial (primaria)" selected with a checkmark badge.
- Card 4: "Prescripción Médica y Receta Digital":
  * Clean table with columns: "Medicamento", "Presentación / Dosis", "Frecuencia", "Duración", "Acciones".
  * Row 1: "Losartán Potásico | 50 mg tableta | Cada 24 horas (Mañanas) | 30 días".
  * Button: "+ Agregar Medicamento".
- Card 5: "Indicaciones y Órdenes Auxiliares":
  * Text area for patient dietary care, plus an outline button: "[+] Solicitar Orden de Laboratorio / Imágenes".

4. BOTTOM ACTION TOOLBAR (Sticky footer):
- Left: Red danger outline button "Anular Atención Médica (Con motivo)".
- Right: Gray outline button "Guardar Borrador", and large primary teal filled button "Firmar y Concluir Consulta Médica (Firma Digital)".
```

--------------------------------------------------------------------------------

## 7.2. Pantalla 2 — Agendamiento de Citas Médicas en 3 Pasos con Bloqueo de Solapamientos (Admisión — M2)

### 7.2.1. Arquitectura de Información y Mapeo Funcional
* **Módulo Relacionado:** M2 — Agenda y Citas Médicas.
* **Usuario Objetivo:** Personal de Admisión y Recepción (Ventanilla / Central telefónica).
* **Trazabilidad:** RF-002 (Bloqueo en tiempo real de solapamientos en 12 consultorios), RF-003 (Recordatorio automatizado con 24 h de anticipación), RNF-003 (Disponibilidad 99.5 %), RNF-005 (Agendamiento en un máximo de 3 pasos desde pantalla principal); Historias de Usuario HU02, HU03, HU06, HU07.
* **Estructura de la Pantalla en 3 Pasos (Cumplimiento Estricto de RNF-005):**
  1. **Indicador de Progreso Visual (Stepper Superior en 3 Pasos):**
     * *Paso 1:* Identificación y Validación del Paciente (Completado / Activo).
     * *Paso 2:* Especialidad, Médico y Horario Disponible (Activo).
     * *Paso 3:* Verificación de Cobertura y Confirmación (Pendiente).
  2. **Área de Contenido Dinámico:**
     * **Paso 1 (Búsqueda Predictiva de Paciente):**
       * Input destacado con selector de tipo de documento (DNI, Carné de Extranjería) y campo numérico con búsqueda reactiva en menos de 0.5 s.
       * Si el paciente existe: tarjeta con nombres, teléfono de contacto para recordatorios, correo electrónico y aseguradora vigente detectada automáticamente (*Rímac EPS / Copago S/ 25.00*).
       * Si el paciente no existe: botón rápido *"Registrar nuevo paciente en 30 segundos"* sin abandonar el flujo.
     * **Paso 2 (Matriz Consolidada de Disponibilidad y Consultorios):**
       * Filtros superiores inmediatos: Selector de Especialidad (*Medicina General, Pediatría, Traumatología, etc.*), Selector de Médico Tratante y selector de fecha/semana.
       * **Cuadrícula de Horarios (Grid Visual de Disponibilidad):**
         * Matriz interactiva de bloques horarios de 20 minutos (08:00 AM a 01:00 PM / 03:00 PM a 08:00 PM).
         * Bloques libres representados en **Verde Menta (`#D1FAE5`)** con borde teal: interactivos y clickeables.
         * Bloques ocupados representados en **Gris Deshabilitado (`#F1F5F9`)** con etiqueta *"Ocupado"* y candado de bloqueo para evitar solapamientos médicos y de consultorio físico.
         * Consultorio físico asignado (del 1 al 12) desplegado en cada tarjeta.
     * **Paso 3 (Panel Lateral de Resumen y Liquidación de Copago):**
       * Tarjeta flotante a la derecha con resumen de la cita: Médico seleccionado, consultorio físico (ej. *Consultorio 06 - Piso 2*), fecha y hora exacta.
       * Desglose del tarifario institucional: Tarifa base consulta (S/ 120.00), Cobertura EPS 80 % (-S/ 96.00), **Copago neto a cobrar al paciente: S/ 24.00**.
       * Interruptor de notificación: *"Enviar recordatorio por SMS y Correo Electrónico (24 horas antes)"* activado por defecto con el número móvil visible para edición.
       * Botón de confirmación primario *"Confirmar Cita y Emitir Ticket"*.

---

### 7.2.2. Marcador de Imagen para el Documento
![image2](Mockup_Pantalla2_Agendamiento.png)

---

### 7.2.3. Prompt Detallado para Generar la Pantalla en Stitch IA

> **INSTRUCCIONES PARA EL ESTUDIANTE:**  
> Copia el siguiente texto íntegro en la caja de prompt de **Stitch IA** para generar el mockup de alta fidelidad de la Pantalla 2.

```text
Create a modern, ultra-clean desktop SaaS web interface for the Medical Appointment Scheduling Module of "Clínica San Rafael S.A.C." (SIRA System) designed for Reception and Admissions staff.

Layout & Canvas: Desktop widescreen 1440x900px, 12-column grid layout, white and slate palette (#F8FAFC, #FFFFFF), primary deep medical teal (#0A4D68, #088395), emerald green for open slots (#10B981), disabled gray (#E2E8F0), crisp Inter typography.

1. TOP HEADER & NAVIGATION:
- Top bar with Clinic brand "Clínica San Rafael SIRA - Sede San Borja".
- Operator indicator: "Admisión: Franz Inga (Caja/Ventanilla 2)" with status badge "En línea".
- Navigation tabs: "Pacientes", "Agenda y Citas (Active)", "Caja y Copagos", "Reportes".

2. THREE-STEP WIZARD PROGRESS BAR (Steering UI compliant with RNF-005: 3-step maximum booking):
- Centered step indicator:
  * Step 1 (Finished/Check icon): "1. Identificar Paciente"
  * Step 2 (Active/Highlighted with blue ring): "2. Especialidad, Médico y Turno"
  * Step 3 (Next): "3. Cobertura y Confirmación"

3. SPLIT WORKSPACE (2/3 Grid Area + 1/3 Floating Confirmation Summary):

LEFT/CENTER AREA (Filters & Availability Grid):
- Top Filter Row:
  * Dropdown 1: "Especialidad: Pediatría (12 consultorios)"
  * Dropdown 2: "Médico: Dr. Jorge Valdivia (CMP: 39412)"
  * Date Picker: "Miércoles, 14 de Octubre de 2026" with "< Hoy >" navigation buttons.
- APPOINTMENT AVAILABILITY MATRIX (Time Slot Grid for Consultorio 02):
  * Grid of modern interactive pill buttons grouped by Turno Mañana (08:00 - 13:00) and Turno Tarde (14:00 - 19:00).
  * 08:00 AM: Disabled light gray with lock icon "Ocupado (Cita #849)"
  * 08:30 AM: Disabled light gray "Ocupado"
  * 09:00 AM: ACTIVE SELECTED (Deep teal filled with white text, checkmark): "09:00 AM - 09:30 AM (Seleccionado)"
  * 09:30 AM: Light green background with green text and border: "09:30 AM (Libre)"
  * 10:00 AM: Light green background "10:00 AM (Libre)"
  * 10:30 AM: Light green background "10:30 AM (Libre)"
  * 11:00 AM: Disabled light gray "Ocupado"
  * Visual banner note below grid: "Sistema con bloqueo transaccional anti-solapamiento activado para 12 consultorios".

RIGHT SIDEBAR (Floating Appointment Summary Card - Step 3 Review):
- Card header: "Resumen de la Cita Médica"
- Patient info snippet: "Paciente: BUSTAMANTE VEGA, LUCAS (DNI: 78945612)"
- Doctor & Location: "Dr. Jorge Valdivia | Consultorio 02 - Piso 1"
- Date & Time: "Miércoles 14 Oct 2026, 09:00 - 09:30 AM"
- Insurance & Copay Calculation Breakdown:
  * Modalidad: "EPS Pacífico - Plan Salud Total"
  * Tarifa Base Servicio: "S/ 140.00"
  * Cobertura Aseguradora (85%): "- S/ 119.00"
  * Total Copago a Pagar por Paciente: "S/ 21.00" (Bold 20px teal text)
- Notification Toggle Switch:
  * Switch ON (Green): "Enviar recordatorio automático SMS / Correo 24h antes (+51 987 654 321)"
- Action Buttons:
  * Primary large button: "Confirmar Agendamiento y Emitir Comprobante (Enter)"
  * Secondary button: "Cancelar / Limpiar Selección"
```

--------------------------------------------------------------------------------

## 7.3. Pantalla 3 (Complementaria) — Registro de Triaje y Signos Vitales (Enfermería — M1)

### 7.3.1. Arquitectura de Información y Mapeo Funcional
* **Módulo Relacionado:** M1 — Historia Clínica Electrónica (Triaje).
* **Usuario Objetivo:** Personal de Enfermería / Tópico de Urgencias.
* **Trazabilidad:** RF-001 (Captura de signos vitales asociada a la atención), RNF-003 (Disponibilidad en tópico continuo de urgencias), RNF-005 (Captura ágil en menos de 2 minutos); Historias de Usuario HU05, HU06.
* **Estructura de la Pantalla:**
  1. **Lista de Espera en Vivo (Cola de Pacientes en Tópico/Consulta):** Tabla izquierda con pacientes que hicieron *check-in* en admisión, tiempo de espera transcurrido, consultorio de destino y estado de triaje (*Pendiente* en amarillo / *Completado* en verde).
  2. **Formulario Ergonómico de Medición Asistencial:**
     * Panel numérico de gran tamaño para ingreso rápido de Presión Arterial (Sistólica/Diastólica), Frecuencia Cardíaca, Temperatura axilar, Frecuencia Respiratoria y Saturación de Oxígeno ($SpO_2$).
     * Calculador automático integrado de Índice de Masa Corporal (IMC) a partir de los campos Peso (kg) y Talla (m), categorizando visualmente el resultado (Bajo peso, Normal, Sobrepeso, Obesidad).
     * Checkbox de confirmación de alergias y observaciones rápidas.
     * Botón de guardado *"Registrar Triaje y Transferir a Consultorio"*.

---

### 7.3.2. Marcador de Imagen para el Documento
![image3](Mockup_Pantalla3_Triaje.png)

---

### 7.3.3. Prompt Detallado para Generar la Pantalla en Stitch IA

> **INSTRUCCIONES PARA EL ESTUDIANTE:**  
> Copia el siguiente texto íntegro en la caja de prompt de **Stitch IA** para generar el mockup de la Pantalla 3.

```text
Create a modern, clean, high-efficiency desktop medical UI screen for the Nurse Triage and Vitals Intake Module of "Clínica San Rafael S.A.C.".

Theme: Healthcare SaaS dashboard, desktop 1440x900px, white and clean slate background (#F8FAFC, #FFFFFF), vibrant clinical teal (#088395), status badges, readable bold numbers, Inter font.

1. TOP BAR:
- "Clínica San Rafael - Módulo de Triaje y Enfermería (Sede San Borja)".
- User: "Lic. Enf. Rocío Paz", "Tópico de Triaje A", Clock: "09:42 AM".

2. TWO-PANEL SPLIT SCREEN:
LEFT PANEL (40% width): "Pacientes en Sala de Espera para Triaje (8 en cola)"
- Search bar for patient name or ticket number.
- Patient queue list cards:
  * Card 1 (Selected): "Ticket T-04 | HERRERA DÍAZ, JOSÉ (DNI: 41258963) | Destino: Consultorio 05 (Cardiología) | Espera: 8 min | Estado: [En Atención - Azul]".
  * Card 2: "Ticket T-05 | LÓPEZ VEGA, ANA | Destino: Consultorio 02 (Pediatría) | Espera: 14 min | Estado: [Pendiente - Amarillo]".
  * Card 3: "Ticket T-06 | CASTILLO M., RAÚL | Destino: Tópico de Urgencias | Espera: 2 min | Estado: [Prioridad Urgente - Rojo]".

RIGHT PANEL (60% width): "Formulario Rápido de Signos Vitales - Paciente: HERRERA DÍAZ, JOSÉ"
- Grid of 6 high-visibility measurement input cards with big bold numbers and units:
  * Box 1: "Presión Arterial": Two inputs "120" / "80" mmHg (Status pill: "Normal").
  * Box 2: "Frecuencia Cardíaca": Input "74" lpm with heart icon.
  * Box 3: "Temperatura Corporal": Input "36.8" °C with thermometer icon.
  * Box 4: "Saturación de Oxígeno (SpO2)": Input "98" % with pulse icon.
  * Box 5: "Frecuencia Respiratoria": Input "18" rpm.
  * Box 6: "Antropometría": Weight "75.0" kg, Height "1.72" m -> Auto-calculated chip: "IMC: 25.35 (Sobrepeso leve - Amarillo)".
- Text area: "Observaciones de Enfermería: Paciente acude consciente y orientado, sin signos de dificultad respiratoria aguda".
- Bottom action button: Full-width teal button "Guardar Triaje y Habilitar en Historia Clínica del Médico".
```

--------------------------------------------------------------------------------

## 7.4. Pantalla 4 (Complementaria) — Dashboard Gerencial de Indicadores Operativos (Gerencia Médica — M5)

### 7.4.1. Arquitectura de Información y Mapeo Funcional
* **Módulo Relacionado:** M5 — Reportes Gerenciales y BI.
* **Usuario Objetivo:** Dirección Médica y Gerencia General de la Clínica.
* **Trazabilidad:** RF-008 (Dashboard con ocupación, espera, ingresos y no-show), RNF-002 (Acceso restringido por rol de gerencia sin datos clínicos confidenciales expuestos), RNF-003 (Métricas operativas consolidadas); Historias de Usuario HU12.
* **Estructura de la Pantalla:**
  1. **Barra Superior de Filtros Analíticos:** Selector de rango de fechas (*Hoy, Esta Semana, Septiembre 2026, Personalizado*), filtro por especialidad médica y filtro por tipo de convenio asegurador.
  2. **Tarjetas de KPIs Principales (Top Stat Cards):**
     * **Tasa de Ocupación de Consultorios:** *86.4 %* (con indicador de variación $+8.2\,\%$ vs. mes previo, base de 12 consultorios).
     * **Tasa de Inasistencia (No-Show):** *7.8 %* (mostrando reducción de 10.2 puntos porcentuales respecto a la línea base histórica del 18 % gracias a los recordatorios 24 h).
     * **Tiempo Promedio de Espera en Sala:** *14.2 min* (reducción drástica frente a las demoras históricas).
     * **Ingresos Operativos Totales:** *S/ 248,500.00* (Particular 35 %, EPS 55 %, SOAT 10 %).
  3. **Gráficos Analíticos Centrales:**
     * Gráfico de barras de ocupación y atenciones por cada uno de los 12 consultorios físicos.
     * Gráfico de pastel/anillo de distribución de facturación por aseguradora (Particular, Pacífico, Rímac, Mapfre, Sanitas, La Positiva, SOAT).
     * Tabla inferior con balance de glosas registradas, sustentadas y recuperadas ante las EPS.

---

### 7.4.2. Marcador de Imagen para el Documento
![image4](Mockup_Pantalla4_Dashboard.png)

---

### 7.4.3. Prompt Detallado para Generar la Pantalla en Stitch IA

> **INSTRUCCIONES PARA EL ESTUDIANTE:**  
> Copia el siguiente texto íntegro en la caja de prompt de **Stitch IA** para generar el mockup de la Pantalla 4.

```text
Create a modern executive analytics dashboard web application screen for the Medical Management and Operations Dashboard (M5 Module) of "Clínica San Rafael S.A.C.".

Layout: Desktop widescreen 1440x900px, modern BI layout like Tableau/Metabase with healthcare aesthetic. Background #F8FAFC, white cards #FFFFFF with clean borders, deep navy/teal branding (#0A4D68), vibrant data viz colors (Emerald green #10B981, Amber #F59E0B, Crimson #EF4444, Indigo #6366F1), Inter font.

1. HEADER & GLOBAL CONTROLS:
- Title: "Dashboard Gerencial de Operaciones Clínicas - Sede San Borja".
- Subtitle: "Métricas consolidadas de ocupación, tiempos de espera, inasistencia e ingresos".
- Date Filter Pills: "Hoy | Últimos 7 días | Este Mes (Septiembre 2026 - Selected) | Rango Personalizado".
- Secondary Filter: Dropdown "Todos los convenios (Particular, 5 EPS, SOAT)".

2. ROW OF 4 EXECUTIVE KPI CARDS:
- Card 1: "Ocupación de Consultorios (12 activos)": Big number "86.4%", subtitle badge "+8.2% vs. mes anterior (Verde)", progress bar showing capacity.
- Card 2: "Tasa de Inasistencia (No-Show)": Big number "7.8%", green highlight text "-10.2% reducción desde línea base del 18% (Impacto recordatorios 24h)".
- Card 3: "Tiempo Medio de Espera en Sala": Big number "14.2 min", trend indicator "-6 min de mejora".
- Card 4: "Facturación Bruta Acumulada": Big number "S/ 248,520.00", subtitle "Recaudado en ventanilla y liquidaciones EPS".

3. CHARTS GRID (2-Column Middle Row):
- Left Chart Card (60% width): "Ocupación y Rendimiento por Consultorio (Consultorios 01 al 12)"
  * Modern vertical bar chart showing percentage utilization of each of the 12 medical offices. Consultorios 01 to 04 (Cardiology/Peds) at >90%, others at 80%.
- Right Chart Card (40% width): "Distribución de Ingresos por Modalidad de Cobertura"
  * Modern donut chart: Particular (32% - Teal), Rímac EPS (28% - Blue), Pacífico EPS (22% - Indigo), Otras EPS (12% - Amber), SOAT (6% - Violet).

4. BOTTOM TABLE: "Seguimiento de Glosas y Liquidaciones con Aseguradoras"
- Table with columns: "Aseguradora / EPS", "Comprobantes Emitidos", "Monto Facturado", "Monto Glosado / Observado", "Glosas Recuperadas", "Estado".
- Row 1: "Rímac EPS | 420 | S/ 68,400.00 | S/ 2,100.00 | S/ 1,850.00 (88%) | [En conciliación - Verde]".
- Row 2: "Pacífico Seguros | 380 | S/ 54,200.00 | S/ 1,400.00 | S/ 1,200.00 (85%) | [Al día - Verde]".
- Row 3: "SOAT La Positiva | 95 | S/ 24,100.00 | S/ 850.00 | S/ 850.00 (100%) | [Recuperado - Azul]".
```

--------------------------------------------------------------------------------

## 7.5. Flujo de Navegación del Prototipo (User Flow)

La siguiente tabla describe formalmente la secuencia operativa mediante la cual los usuarios del sistema transitan a través de las pantallas principales del prototipo, validando el cumplimiento estricto de la regla de usabilidad en **máximo 3 pasos (RNF-005)** y la segregación de accesos por rol (RBAC):

| Paso | Pantalla Origen | Acción del Usuario / Evento del Sistema | Pantalla Destino | Componente de Validación y Trazabilidad |
| :---: | :--- | :--- | :--- | :--- |
| **Paso 1** | Pantalla de Acceso (Login) | El usuario ingresa sus credenciales corporativas (usuario y contraseña cifrada con bcrypt). El sistema autentica y genera token JWT validando el rol asignado en la base de datos (RNF-002). | Dashboard Principal según Rol (Médico, Admisión, Enfermera o Gerencia) | Middleware RBAC en FastAPI restringe menús y módulos no autorizados. |
| **Paso 2** | Dashboard de Admisión | El operador de recepción busca al paciente por DNI en el buscador rápido. Si existe, selecciona su registro y pulsa *"Nueva Cita"*. (Paso 1 del Agendamiento). | Pantalla 2 — Agendamiento (Paso 2: Matriz de Turnos) | Búsqueda indexada en PostgreSQL resuelve la consulta de filiación en < 0.5 s. |
| **Paso 3** | Pantalla 2 — Matriz de Turnos | El operador filtra la especialidad médica, selecciona el médico tratante y hace clic sobre un bloque horario disponible (en verde). (Paso 2 del Agendamiento). | Pantalla 2 — Panel de Resumen Lateral (Paso 3) | El motor de agenda valida en tiempo real la disponibilidad y previene solapamientos (RF-002). |
| **Paso 4** | Pantalla 2 — Resumen Lateral | El operador verifica la cobertura del convenio (Particular/EPS/SOAT), el monto de copago calculado automáticamente y hace clic en *"Confirmar Cita"*. (Paso 3 del Agendamiento). | Modal de Éxito / Emisión de Ticket de Cita | La cita se guarda en base de datos e inserta el evento en `outbox_notificaciones` para el envío 24 h antes (RF-003, RNF-005). |
| **Paso 5** | Pantalla 3 — Cola de Espera (Enfermería) | Al presentarse el paciente en la clínica, la enfermera selecciona su ticket en espera y registra los signos vitales en el formulario ergonómico de triaje. | Pantalla 3 — Triaje Guardado | Los signos vitales se persisten en la tabla `triajes` y quedan vinculados a la atención del día (RF-001). |
| **Paso 6** | Pantalla 1 — Consulta Médica (Médico) | El médico tratante hace clic sobre el paciente citado en su agenda diaria. El sistema carga el expediente unificado cronológico con alerta destacada de alergias y el triaje tomado por enfermería. | Pantalla 1 — HCE y Consulta Activa | Apertura garantizada en < 2 segundos sobre 8 000 registros (RNF-001, RNF-004). |
| **Paso 7** | Pantalla 1 — Consulta Médica | El médico ingresa el diagnóstico CIE-10 asistido por autocompletado predictivo, formula la receta médica, emite órdenes de laboratorio si lo amerita y pulsa *"Firmar y Concluir Consulta"*. | Modal de Confirmación y Retorno a Agenda Médica | Transacción ACID guarda el acto médico, receta y órdenes, registrando la traza en `bitacora_auditoria` (Ley N.° 29733). |

--------------------------------------------------------------------------------

## 7.6. Checklist de Usabilidad y Calidad UX/UI (Rúbrica E1 - Semana 6)

| Criterio de Calidad UX/UI | Estado | Justificación y Evidencia en el Prototipo |
| :--- | :---: | :--- |
| **Alineamiento con Historias de Usuario (INVEST)** | **Cumple** | Las pantallas reflejan fielmente las historias prioritarias del Sprint 1: HU01 (HCE unificada), HU02 (Agendamiento sin solapamientos), HU04 (Consulta CIE-10), HU05 (Triaje) y HU07 (Recordatorios). |
| **Cumplimiento del Límite de 3 Pasos (RNF-005)** | **Cumple** | La Pantalla 2 implementa un stepper guiado que permite reservar una cita médica en exactamente 3 interacciones: (1) Buscar paciente, (2) Elegir turno libre, (3) Confirmar con copago. |
| **Prevención de Errores Médicos (Seguridad Clínica)** | **Cumple** | La Pantalla 1 sitúa el banner de alergias en color rojo carmesí `#DC2626` en la zona superior de atención inmediata, previniendo prescripciones adversas. |
| **Baja Carga Cognitiva y Brecha Digital (Riesgo R-02)** | **Cumple** | Diseño minimalista con alto contraste, etiquetas en lenguaje clínico natural, buscadores predictivos (CIE-10) y componentes deshabilitados claramente diferenciados. |
| **Percepción de Rendimiento en < 2 s (RNF-001)** | **Cumple** | La división modular de pantallas desacopla la carga pesada mediante carga asíncrona (*lazy loading*) y componentes de esqueleto (*skeleton screens*) mientras consulta PostgreSQL. |
| **Insumos Listos para Generación de Mockups (Stitch IA)** | **Cumple** | Cada una de las 4 pantallas cuenta con su especificación de componentes y su prompt exhaustivo listo para copiar y pegar en herramientas de IA. |
