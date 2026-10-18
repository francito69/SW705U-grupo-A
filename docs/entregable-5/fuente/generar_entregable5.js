const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign, PageNumber,
  PageBreak, TableOfContents, LevelFormat, PositionalTab, PositionalTabAlignment,
  PositionalTabRelativeTo, PositionalTabLeader, TableLayoutType, ExternalHyperlink,
} = require("docx");

const OUT_DIR = process.argv[2];
const WORK = __dirname;

const GUINDA = "7A0C0C";
const BORDE = "BFBFBF";
const FONDO_ETIQUETA = "F3F0EB";
const FONDO_SUAVE = "FBF8F3";
const ANCHO = 9638;

const logo = fs.readFileSync(path.join(WORK, "logo.png"));
const planRelease = fs.readFileSync(path.join(OUT_DIR, "diagramas", "plan-release.png"));
const tablero = fs.readFileSync(path.join(OUT_DIR, "diagramas", "tablero-sprint1.png"));
const URL_TABLERO = "https://github.com/users/ricco-drs/projects/1";

// Texto con fragmentos en negrita o código: "texto **negrita** `codigo`"
function runs(texto, base = {}) {
  const partes = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let ultimo = 0;
  let m;
  while ((m = re.exec(texto)) !== null) {
    if (m.index > ultimo) partes.push(new TextRun({ text: texto.slice(ultimo, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) partes.push(new TextRun({ text: t.slice(2, -2), ...base, bold: true }));
    else partes.push(new TextRun({ text: t.slice(1, -1), ...base, font: "Consolas", size: (base.size || 21) - 2 }));
    ultimo = m.index + t.length;
  }
  if (ultimo < texto.length) partes.push(new TextRun({ text: texto.slice(ultimo), ...base }));
  return partes;
}

function p(texto, opts = {}) {
  return new Paragraph({
    spacing: { after: 120, line: 276 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    keepNext: opts.keepNext,
    children: runs(texto, opts.run || {}),
  });
}

function h1(texto, pageBreak = true) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: pageBreak, children: [new TextRun(texto)] });
}

function h2(texto) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, children: [new TextRun(texto)] });
}

let nTabla = 0;
function caption(texto) {
  nTabla += 1;
  return new Paragraph({
    keepNext: true,
    spacing: { before: 120, after: 80 },
    children: [
      new TextRun({ text: `Tabla ${nTabla}. `, bold: true, color: GUINDA, size: 18 }),
      new TextRun({ text: texto, color: GUINDA, size: 18 }),
    ],
  });
}

const borde = { style: BorderStyle.SINGLE, size: 4, color: BORDE };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };

function celda(contenido, ancho, opts = {}) {
  const lineas = Array.isArray(contenido) ? contenido : [contenido];
  return new TableCell({
    width: { size: ancho, type: WidthType.DXA },
    borders: bordes,
    rowSpan: opts.rowSpan,
    verticalAlign: opts.vAlign || VerticalAlign.CENTER,
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: opts.compacto ? { top: 25, bottom: 25, left: 90, right: 90 } : { top: 60, bottom: 60, left: 100, right: 100 },
    children: lineas.map((l) => new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      keepNext: opts.keepNext,
      spacing: { after: 20 },
      children: runs(String(l), { size: opts.size || 18, bold: opts.bold, color: opts.color, italics: opts.italics }),
    })),
  });
}

function tabla(anchos, encabezados, filas, opts = {}) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const cab = new TableRow({
    tableHeader: true,
    cantSplit: true,
    children: encabezados.map((e, i) => celda(e, anchos[i], { fill: GUINDA, bold: true, color: "FFFFFF", size: 19 })),
  });
  const cuerpo = filas.map((f) => new TableRow({
    cantSplit: true,
    children: f.map((c, i) => {
      if (c && c.celda) return c.celda;
      const opc = { align: (opts.centrar || []).includes(i) ? AlignmentType.CENTER : AlignmentType.LEFT };
      if ((opts.negrita || []).includes(i)) opc.bold = true;
      if (f.fondo) opc.fill = f.fondo;
      return celda(c, anchos[i], opc);
    }),
  }));
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: anchos,
    layout: TableLayoutType.FIXED,
    alignment: opts.alignment || AlignmentType.LEFT,
    rows: [cab, ...cuerpo],
  });
}

function espacio(after = 120) {
  return new Paragraph({ spacing: { after }, children: [] });
}

// ------------------------------------------------------------------ Encabezado y pie
const encabezado = new Header({
  children: [new Paragraph({
    spacing: { after: 120 },
    children: [
      new ImageRun({ type: "png", data: logo, transformation: { width: 38, height: 48 } }),
      new TextRun({ text: "  SW705 · Taller de Ingeniería de Software I — Escuela de Ingeniería de Software", bold: true, color: GUINDA, size: 16 }),
    ],
  })],
});

const pie = new Footer({
  children: [new Paragraph({
    children: [
      new TextRun({ text: "Grupo A · Entregable 5 · Guía práctica — Semana 7", color: "808080", size: 16 }),
      new TextRun({ children: [new PositionalTab({ alignment: PositionalTabAlignment.RIGHT, relativeTo: PositionalTabRelativeTo.MARGIN, leader: PositionalTabLeader.NONE })] }),
      new TextRun({ children: ["Página ", PageNumber.CURRENT, " de ", PageNumber.TOTAL_PAGES], color: "808080", size: 16 }),
    ],
  })],
});

// ------------------------------------------------------------------ Carátula
function centrado(texto, run, after = 60) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after }, children: [new TextRun({ text: texto, ...run })] });
}

const filaCaratula = (etiqueta, valor) => new TableRow({
  children: [
    celda(etiqueta, 2900, { fill: FONDO_ETIQUETA, bold: true, size: 20 }),
    celda(valor, 5800, { size: 20 }),
  ],
});

const caratula = [
  espacio(600),
  centrado("UNIVERSIDAD NACIONAL DE INGENIERÍA", { bold: true, color: GUINDA, size: 30 }),
  centrado("Facultad de Ingeniería Industrial y de Sistemas · Escuela de Ingeniería de Software", { italics: true, size: 21 }, 360),
  centrado("GUÍA PRÁCTICA — SEMANA 7", { bold: true, color: GUINDA, size: 44 }),
  centrado("Planificación ágil del desarrollo (Scrum)", { bold: true, size: 28 }, 360),
  centrado("SW705 — Taller de Ingeniería de Software I", { size: 22 }),
  centrado("Docente: Mg. Ing. José Carlos, García La Riva", { italics: true, size: 21 }),
  centrado("Caso aplicado: Clínica San Rafael S.A.C.", { italics: true, color: GUINDA, size: 21 }, 360),
  centrado("Entregable 5 — Avance 4 del proyecto integrador", { bold: true, size: 22 }),
  centrado("Sistema de Información Clínico-Administrativo (SIRA)", { size: 22 }, 480),
  new Table({
    width: { size: 8700, type: WidthType.DXA },
    columnWidths: [2900, 5800],
    alignment: AlignmentType.CENTER,
    layout: TableLayoutType.FIXED,
    rows: [
      filaCaratula("Integrantes del equipo", ["Albino Soto, Christopher Henrry", "Inga Champi, Franz Joe", "Rashuaman Sapallanay, Ricco Didier"]),
      filaCaratula("Código(s)", ["20231158C", "20231302G", "20231242D"]),
      filaCaratula("Sección", "U"),
      filaCaratula("Fecha", "15/10/2026"),
      filaCaratula("Grupo", "Grupo A"),
      filaCaratula("Repositorio", "https://github.com/francito69/SW705U-grupo-A"),
    ],
  }),
  espacio(1400),
  centrado("Lima, Perú — Ciclo 2026-2", { size: 18, color: "595959" }),
];

// ------------------------------------------------------------------ Índice
const indice = [
  new Paragraph({ pageBreakBefore: true, spacing: { after: 200 }, children: [new TextRun({ text: "Contenido", bold: true, color: GUINDA, size: 30 })] }),
  new TableOfContents("Contenido", { hyperlink: true, headingStyleRange: "1-2" }),
];

// ------------------------------------------------------------------ Insumos
const insumos = [
  new Paragraph({ spacing: { before: 360 }, children: [] }),
  h1("Insumos de partida", false),
  p("El plan de trabajo parte del backlog priorizado y del prototipo de los avances anteriores. Las historias, los puntos y las tareas de este documento usan la numeración del ERS (HU01 a HU14)."),
  caption("Insumos utilizados en la planificación"),
  tabla([2400, 1000, 3238, 3000], ["Insumo", "Semana", "Ubicación", "Uso en este entregable"], [
    ["Product backlog priorizado (HU01–HU14)", "3", "`docs/entregable-1/03-especificacion-requerimientos-ERS.md` (secciones 3.7 y 3.8)", "Historias, prioridades y criterios de aceptación de los pasos 2 y 4"],
    ["Documento de arquitectura (SAD)", "5", "`docs/entregable-1/05-arquitectura-SAD/`", "Stack (FastAPI, React, PostgreSQL), pruebas con pytest y CI con GitHub Actions que exige la Definición de Hecho"],
    ["Diseño de componentes e interfaces", "6", "Entregable 4, paso 1", "Endpoints que construye cada tarea de backend"],
    ["Script de base de datos (22 tablas)", "6", "`database/01-esquema.sql`", "Tablas, restricciones y triggers que ya existen y no se vuelven a modelar en el Sprint 1"],
    ["Prototipo navegable (P1 a P4)", "6", "https://zaffre-ajar-01499329.figma.site", "Pantallas que construye cada tarea de frontend"],
  ], { centrar: [1] }),
];

// ------------------------------------------------------------------ Paso 1
const paso1 = [
  h1("Paso 1 — Roles y acuerdos de trabajo"),
  caption("Roles de Scrum del equipo"),
  tabla([2400, 2000, 5238], ["Integrante", "Rol Scrum", "Responsabilidades principales"], [
    ["Inga Champi, Franz Joe", "Product Owner · Developer", [
      "Mantiene y ordena el product backlog y representa a la Clínica San Rafael ante el equipo.",
      "Aclara los criterios de aceptación durante el Sprint y acepta o rechaza cada historia en la Sprint Review.",
      "Como developer: backend del módulo M1 (HCE, triaje y atención) y autenticación.",
    ]],
    ["Albino Soto, Christopher Henrry", "Scrum Master del Sprint 1 · Developer", [
      "Facilita la Sprint Planning, el Daily Scrum, la Sprint Review y la Retrospectiva.",
      "Mantiene el tablero al día, registra los impedimentos y verifica la Definición de Hecho antes de mover una historia a Hecho.",
      "Como developer: interfaz web en React (pantallas P1, P2 y P3).",
    ]],
    ["Rashuaman Sapallanay, Ricco Didier", "Developer (Scrum Master del Sprint 2)", [
      "Backend del módulo M2 (agenda y citas) y acceso a datos en PostgreSQL.",
      "Pruebas unitarias y de integración, y pipeline de integración continua en GitHub Actions.",
      "Revisa los pull requests del resto del equipo.",
    ]],
    ["Mg. Ing. José Carlos García La Riva (docente)", "Stakeholder · cliente de referencia", [
      "Revisa el incremento al cierre de cada Sprint y da retroalimentación sobre el plan y el backlog.",
      "El Product Owner traslada sus observaciones al product backlog.",
    ]],
  ], { negrita: [0] }),
  h2("Acuerdos del equipo"),
  caption("Acuerdos de trabajo"),
  tabla([2600, 7038], ["Acuerdo", "Detalle"], [
    ["Daily Scrum", "Lunes, miércoles y viernes a las 9:00 p. m., 15 minutos, por Google Meet. Cada integrante dice qué hizo, qué hará y qué lo bloquea. Lo facilita el Scrum Master."],
    ["Ausencia al Daily", "Quien no pueda conectarse deja su avance y sus bloqueos por escrito en el grupo del equipo antes de las 9:00 p. m."],
    ["Canal de comunicación", "Grupo de WhatsApp «SW705 – Grupo A» para la coordinación diaria; GitHub (issues, pull requests y tablero) para todo lo técnico; Google Meet para los eventos de Scrum."],
    ["Rotación del Scrum Master", "Sprint 1 (semanas 9–11): Albino Soto, Christopher Henrry. Sprint 2 (semanas 13–14): Rashuaman Sapallanay, Ricco Didier. El Product Owner no rota, para mantener la continuidad del backlog."],
    ["Eventos del Sprint", "Sprint Planning: semana 7 (Sprint 1) y semana 12 (Sprint 2), 2 horas. Sprint Review y Retrospectiva: semana 12 (Sprint 1) y cierre de la semana 14 (Sprint 2), 1 hora cada una."],
    ["Dedicación", "12 horas semanales por integrante durante los Sprints."],
    ["Flujo de trabajo en Git", "Una rama por historia (`feature/HUxx-descripcion`). Integración a `main` solo por pull request revisado por otro integrante en menos de 24 horas."],
    ["Uso del tablero", "Cada integrante mueve sus propias tarjetas el mismo día en que cambia su estado."],
  ], { negrita: [0] }),
];

// ------------------------------------------------------------------ Paso 2
const votos = (r1, r2) => (r2 ? [`R1: ${r1}`, `R2: ${r2}`] : [r1]);
const paso2 = [
  h1("Paso 2 — Estimación del backlog"),
  p("**Historia de referencia:** HU03 Registro y búsqueda de paciente, 3 puntos: un formulario, una búsqueda por documento y una restricción de unicidad que ya existe en la base de datos. **Serie de votación:** 1, 2, 3, 5, 8, 13. Los votos se muestran en el orden Inga · Albino · Rashuaman; cuando hubo segunda ronda se muestran ambas (R1 y R2)."),
  caption("Estimación del product backlog con planning poker"),
  tabla([4338, 1300, 2400, 1600], ["Historia de usuario", "Prioridad", "Votos del equipo", "Puntos acordados"], [
    ["HU01 Consulta de la HCE unificada", "1", ["R1: 8 · 13 · 13"], "Se divide (> 8)"],
    ["   HU01a Consulta cronológica de la HCE", "1", votos("5 · 5 · 3", "5 · 5 · 5"), "**5**"],
    ["   HU01b Acceso por rol y registro en bitácora de la HCE", "1", votos("3 · 3 · 3"), "**3**"],
    ["HU02 Agendamiento de citas sin solapamientos", "2", votos("5 · 5 · 8", "5 · 5 · 5"), "**5**"],
    ["HU03 Registro y búsqueda de paciente", "3", ["Referencia"], "**3**"],
    ["HU04 Atención médica con diagnóstico CIE-10 y receta", "4", votos("3 · 5 · 5", "5 · 5 · 5"), "**5**"],
    ["HU05 Registro de triaje y signos vitales", "5", votos("3 · 3 · 3"), "**3**"],
    ["HU06 Reprogramación y cancelación de citas", "6", votos("3 · 2 · 3", "3 · 3 · 3"), "**3**"],
    ["HU07 Recordatorio automático de citas a 24 h", "7", votos("5 · 8 · 5", "5 · 5 · 5"), "**5**"],
    ["HU08 Anulación lógica de atenciones con bitácora", "8", votos("3 · 3 · 2", "3 · 3 · 3"), "**3**"],
    ["HU09 Emisión de órdenes de laboratorio e imágenes", "9", votos("5 · 5 · 5"), "**5**"],
    ["HU10 Carga y vinculación de resultados digitales", "10", votos("5 · 3 · 5", "5 · 5 · 5"), "**5**"],
    ["HU11 Facturación por convenio y cálculo de copagos", "11", votos("8 · 13 · 8", "8 · 8 · 8"), "**8**"],
    ["HU12 Registro y seguimiento de glosas", "12", votos("5 · 5 · 5"), "**5**"],
    ["HU13 Tablero de control gerencial", "13", votos("5 · 8 · 5", "5 · 5 · 5"), "**5**"],
    ["HU14 Agendamiento en el portal del paciente (condicional)", "14", votos("8 · 8 · 8"), "**8**"],
    Object.assign(["**Total del product backlog**", "", "", "**71**"], { fondo: FONDO_SUAVE }),
  ], { centrar: [1, 2, 3] }),
  h2("Discusiones que definieron los puntos"),
  caption("Razonamiento de los votos extremos"),
  tabla([1300, 6138, 2200], ["Historia", "Razonamiento de quienes votaron más alto y más bajo", "Resultado"], [
    ["HU01", "Albino y Rashuaman (13): la historia junta dos trabajos distintos, mostrar el expediente en menos de 2 s con 8 000 pacientes (RNF-001) y protegerlo con control por rol y bitácora (RNF-002). Inga (8): los índices y los triggers de auditoría ya existen en la base de datos.", "Se divide en HU01a y HU01b; cada parte se votó por separado (5 y 3)."],
    ["HU02", "Rashuaman (8): hay que probar dos reservas simultáneas sobre el mismo bloque. Inga (5): la restricción de exclusión de citas ya está en la base de datos; solo falta responder 409.", "5 en la segunda ronda."],
    ["HU04", "Inga (3): es un formulario. Albino y Rashuaman (5): suma el autocompletado CIE-10 y la regla de un solo diagnóstico principal.", "5 en la segunda ronda."],
    ["HU07", "Albino (8): el envío real de SMS es incierto. Inga (5): la cola Outbox ya existe y el envío se valida por correo con un proveedor de prueba.", "5 en la segunda ronda."],
    ["HU11", "Albino (13): 5 EPS, SOAT y tarifarios con vigencia. Inga (8): el cálculo sigue una sola regla (RN-03) parametrizada por convenio.", "8 en la segunda ronda; no requiere división."],
  ], { negrita: [0], centrar: [0] }),
];

// ------------------------------------------------------------------ Paso 3
const metaSprint = "Que admisión registre pacientes y agende, reprograme o cancele citas sin cruces de horario, que enfermería registre el triaje y que el médico registre la atención y consulte la historia clínica completa con acceso controlado por rol.";
const paso3 = [
  new Paragraph({ spacing: { before: 240 }, children: [] }),
  h1("Paso 3 — Definición de Hecho y Meta del Sprint", false),
  caption("Definición de Hecho (común a todas las historias)"),
  tabla([700, 5838, 3100], ["N.º", "Criterio verificable de la Definición de Hecho", "Evidencia"], [
    ["1", "El código está integrado en la rama `main` mediante un pull request aprobado por un integrante distinto del autor.", "Pull request aprobado en GitHub"],
    ["2", "Las pruebas unitarias de la historia pasan y la cobertura de la lógica del módulo es de 80 % o más.", "Reporte de `pytest --cov` (backend) y Vitest (frontend)"],
    ["3", "Los escenarios Dado/Cuando/Entonces de los criterios de aceptación de la historia están verificados.", "Pruebas automatizadas o demostración al Product Owner"],
    ["4", "El pipeline de GitHub Actions termina en verde: análisis estático (flake8 y ESLint), pruebas y build.", "Check del pull request"],
    ["5", "Cada endpoint nuevo está documentado en la documentación automática de la API con sus códigos de respuesta.", "Swagger de FastAPI (`/docs`)"],
    ["6", "Las operaciones sobre datos clínicos validan el rol del usuario (403 si no corresponde), quedan registradas en `bitacora_auditoria` y no usan borrado físico.", "Prueba con un rol no autorizado"],
    ["7", "No hay errores abiertos de prioridad alta asociados a la historia.", "Tablero sin tarjetas de error de prioridad alta abiertas"],
    ["8", "El Product Owner aceptó la historia en la Sprint Review.", "Tarjeta en la columna Hecho con su aprobación"],
  ], { centrar: [0] }),
  new Paragraph({ keepNext: true, spacing: { before: 240, after: 100 }, children: [new TextRun({ text: "Meta del Sprint 1:", bold: true, size: 21 })] }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160, line: 300 },
    shading: { fill: FONDO_SUAVE, type: ShadingType.CLEAR, color: "auto" },
    border: {
      top: { style: BorderStyle.DASHED, size: 6, color: "999999", space: 10 },
      bottom: { style: BorderStyle.DASHED, size: 6, color: "999999", space: 10 },
      left: { style: BorderStyle.DASHED, size: 6, color: "999999", space: 10 },
      right: { style: BorderStyle.DASHED, size: 6, color: "999999", space: 10 },
    },
    indent: { left: 200, right: 200 },
    children: [new TextRun({ text: `"${metaSprint}"`, italics: true, size: 22 })],
  }),
];

// ------------------------------------------------------------------ Paso 4
const INGA = "Inga Champi, Franz Joe";
const ALBINO = "Albino Soto, Christopher Henrry";
const RASHU = "Rashuaman Sapallanay, Ricco Didier";
const CORTO = { [INGA]: "Franz Inga", [ALBINO]: "Christopher Albino", [RASHU]: "Ricco Rashuaman" };

const sprintBacklog = [
  { hu: "HU01a Consulta cronológica de la HCE", pts: 5, tareas: [
    ["Endpoint `GET /pacientes/{id}/hce` con el expediente paginado de 10 en 10", INGA],
    ["Endpoint `GET /atenciones/{id}` con el detalle de la atención y su receta", INGA],
    ["Índice por paciente y fecha; prueba de respuesta < 2 s con 8 000 pacientes", RASHU],
    ["Pantalla P1: línea de tiempo de la HCE con banner de alergias", ALBINO],
    ["Pantalla P1: detalle de la atención y paginación", INGA],
  ] },
  { hu: "HU01b Acceso por rol y registro en bitácora de la HCE", pts: 3, tareas: [
    ["Inicio de sesión con JWT y verificación de rol", INGA],
    ["Registro de cada apertura de la HCE en `bitacora_auditoria` y prueba del rechazo 403", RASHU],
    ["Pantalla de inicio de sesión y menú según el rol", ALBINO],
  ] },
  { hu: "HU02 Agendamiento de citas sin solapamientos", pts: 5, tareas: [
    ["Endpoints `GET /medicos` y `GET /citas/disponibilidad`", RASHU],
    ["Endpoint `POST /citas` con respuesta 409 ante un cruce de médico o consultorio", RASHU],
    ["Prueba de dos reservas simultáneas del mismo bloque", RASHU],
    ["Pantalla P2, pasos 1 y 2: paciente, especialidad, médico y bloque libre", ALBINO],
    ["Pantalla P2, paso 3: confirmación y aviso de conflicto", ALBINO],
  ] },
  { hu: "HU03 Registro y búsqueda de paciente", pts: 3, tareas: [
    ["Estructura base del backend y endpoints `GET` y `POST /pacientes`", INGA],
    ["Pantalla de búsqueda por documento y registro con convenio", ALBINO],
    ["Pipeline de GitHub Actions y pruebas del documento duplicado (409)", RASHU],
  ] },
  { hu: "HU04 Atención médica con diagnóstico CIE-10 y receta", pts: 5, tareas: [
    ["Endpoint `GET /diagnosticos-cie10` (búsqueda por código o texto)", INGA],
    ["Endpoint `POST /atenciones` con diagnóstico principal, indicaciones y prescripciones", INGA],
    ["Pruebas de la atención: diagnóstico obligatorio y un solo diagnóstico principal", INGA],
    ["Pantalla P1: formulario de atención con buscador CIE-10", ALBINO],
    ["Pantalla P1: receta e indicaciones", ALBINO],
  ] },
  { hu: "HU05 Registro de triaje y signos vitales", pts: 3, tareas: [
    ["Endpoints `POST /citas/{id}/check-in` y `GET /citas` (lista de espera)", RASHU],
    ["Endpoint `POST /triajes` con alerta de valores fuera de rango", INGA],
    ["Pantalla P3: lista de espera y registro de signos vitales con IMC calculado", ALBINO],
  ] },
  { hu: "HU06 Reprogramación y cancelación de citas", pts: 3, tareas: [
    ["Endpoint `POST /citas/{id}/reprogramar` que libera el bloque anterior", RASHU],
    ["Endpoint `POST /citas/{id}/cancelar` con motivo obligatorio", RASHU],
    ["Acciones de reprogramar y cancelar en la agenda (P2)", ALBINO],
  ] },
];

const AN = [1900, 900, 4288, 1850, 700];
const filasSB = [];
for (const h of sprintBacklog) {
  h.tareas.forEach(([tarea, resp], i) => {
    const kn = i < h.tareas.length - 1;
    const celdas = [];
    if (i === 0) {
      celdas.push({ celda: celda(h.hu, AN[0], { rowSpan: h.tareas.length, bold: true, keepNext: true, compacto: true }) });
      celdas.push({ celda: celda(String(h.pts), AN[1], { rowSpan: h.tareas.length, align: AlignmentType.CENTER, bold: true, keepNext: true, compacto: true }) });
    }
    celdas.push({ celda: celda(tarea, AN[2], { keepNext: kn, compacto: true }) });
    celdas.push({ celda: celda(CORTO[resp], AN[3], { keepNext: kn, compacto: true }) });
    celdas.push({ celda: celda("1", AN[4], { align: AlignmentType.CENTER, keepNext: kn, compacto: true }) });
    filasSB.push(celdas);
  });
}
const totalPts = sprintBacklog.reduce((a, h) => a + h.pts, 0);
const totalDias = sprintBacklog.reduce((a, h) => a + h.tareas.length, 0);
filasSB.push([
  { celda: celda("**Total**", AN[0], { fill: FONDO_SUAVE }) },
  { celda: celda(`**${totalPts}**`, AN[1], { fill: FONDO_SUAVE, align: AlignmentType.CENTER }) },
  { celda: celda(`${totalDias} tareas de un día`, AN[2], { fill: FONDO_SUAVE }) },
  { celda: celda("", AN[3], { fill: FONDO_SUAVE }) },
  { celda: celda(`**${totalDias}**`, AN[4], { fill: FONDO_SUAVE, align: AlignmentType.CENTER }) },
]);

function carga(nombre) {
  let n = 0;
  const hus = [];
  for (const h of sprintBacklog) {
    const k = h.tareas.filter((t) => t[1] === nombre).length;
    if (k) { n += k; hus.push(h.hu.split(" ")[0]); }
  }
  return [nombre, String(n), String(n), hus.join(", ")];
}

const paso4 = [
  h1("Paso 4 — Sprint Backlog 1"),
  h2("Capacidad del equipo"),
  caption("Cálculo de la capacidad del Sprint 1"),
  tabla([3400, 6238], ["Concepto", "Valor"], [
    ["Integrantes que desarrollan", "3"],
    ["Duración del Sprint 1", "3 semanas (semanas 9 a 11)"],
    ["Dedicación por integrante", "12 h por semana → 36 h en el Sprint"],
    ["Factor de foco", "75 % (eventos de Scrum, revisión de pull requests e imprevistos) → 27 h efectivas por integrante"],
    ["Día de tarea", "3 h de trabajo efectivo → 9 días de tarea por integrante"],
    ["Calibración con la historia de referencia", "HU03 (3 puntos) se descompone en 3 tareas de un día → 1 punto ≈ 1 día de tarea"],
    [{ celda: celda("**Capacidad estimada**", 3400, { fill: FONDO_SUAVE }) }, { celda: celda("**9 puntos por integrante × 3 integrantes = 27 puntos**", 6238, { fill: FONDO_SUAVE }) }],
  ], { negrita: [0] }),
  espacio(60),
  p("Por orden de prioridad entran HU01a, HU01b, HU02, HU03, HU04, HU05 y HU06, que suman 27 puntos. HU07 (5 puntos) ya no cabe en la capacidad y pasa al Sprint 2 junto con HU08 (3 puntos)."),
  new Paragraph({ heading: HeadingLevel.HEADING_2, pageBreakBefore: true, keepNext: true, children: [new TextRun("Sprint Backlog 1")] }),
  caption("Sprint Backlog 1: historias, tareas, responsables y días"),
  tabla(AN, ["Historia", "Puntos", "Tareas", "Responsable", "Días"], filasSB),
  new Paragraph({
    spacing: { before: 160, after: 200 },
    children: [
      new TextRun({ text: "Capacidad estimada del equipo: ", bold: true, size: 21 }),
      new TextRun({ text: `${totalPts} puntos.`, bold: true, size: 21, color: GUINDA }),
      new TextRun({ text: "     Total comprometido: ", bold: true, size: 21 }),
      new TextRun({ text: `${totalPts} puntos.`, bold: true, size: 21, color: GUINDA }),
    ],
  }),
  h2("Carga por integrante"),
  caption("Distribución de las tareas del Sprint 1"),
  tabla([3000, 1000, 1000, 4638], ["Integrante", "Tareas", "Días", "Historias en las que participa"], [
    carga(INGA), carga(ALBINO), carga(RASHU),
    Object.assign(["**Total**", `**${totalDias}**`, `**${totalDias}**`, ""], { fondo: FONDO_SUAVE }),
  ], { centrar: [1, 2] }),
  h2("Orden de trabajo dentro del Sprint"),
  caption("Secuencia semanal de las historias del Sprint 1"),
  tabla([1200, 2200, 1000, 5238], ["Semana", "Historias", "Puntos", "Motivo del orden"], [
    ["9", "HU03, HU01b, HU02", "11", "Base del backend, autenticación y agenda: las demás historias necesitan pacientes, usuarios y citas."],
    ["10", "HU05, HU04", "8", "Flujo de la atención: triaje desde la lista de espera y registro de la atención médica."],
    ["11", "HU06, HU01a", "8", "Cambios de agenda y consulta de la HCE con los datos ya registrados en las semanas anteriores."],
    Object.assign(["**Total**", "", "**27**", ""], { fondo: FONDO_SUAVE }),
  ], { centrar: [0, 2] }),
];

// ------------------------------------------------------------------ Paso 5
const paso5 = [
  h1("Paso 5 — Plan de release y tablero"),
  h2("Plan de release"),
  caption("Plan de release del sistema SIRA"),
  tabla([1700, 2700, 5238], ["Periodo", "Hito o Sprint", "Contenido previsto"], [
    ["Semana 7", "Sprint Planning 1 (Avance 4)", "Roles, estimación del backlog, Definición de Hecho, Sprint Backlog 1 de 27 puntos y tablero configurado."],
    ["Semana 8", "**Examen parcial — Entregable 1**", "Sustentación del acta, la visión, el ERS, los modelos UML, el SAD, el modelo de base de datos, el prototipo y este plan."],
    ["Semanas 9–11", "**Sprint 1** — Release 1: HCE y Agenda", "HU01a, HU01b y HU02 a HU06 (27 puntos): pacientes, citas sin cruces, triaje, atención con CIE-10 e historia clínica; repositorio, CI y pruebas unitarias (Avance 5)."],
    ["Semana 12", "Sprint Review, Retrospectiva y Sprint Planning 2", "Demostración del incremento, velocidad real del Sprint 1 y Sprint Backlog 2 (Avance 6)."],
    ["Semanas 13–14", "**Sprint 2** — Release 2: Laboratorio, Facturación y Reportes", "HU07 y HU08, y los módulos M3, M4 y M5 (HU09 a HU13) ajustados a la velocidad del Sprint 1; despliegue en el entorno de demostración. HU14 (M6) solo si queda capacidad."],
    ["Semana 15", "Cierre (Avance 7)", "Informe final, manual de usuario y pre-sustentación."],
    ["Semana 16", "**Examen final — Entregable 2**", "Sustentación final con demostración en vivo del sistema."],
  ], { negrita: [0] }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: true,
    spacing: { before: 240, after: 80 },
    children: [new ImageRun({ type: "png", data: planRelease, transformation: { width: 620, height: Math.round(620 * 610 / 1881) } })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [
      new TextRun({ text: "Figura 1. ", bold: true, color: GUINDA, size: 18 }),
      new TextRun({ text: "Plan de release del sistema SIRA con los hitos de las semanas 8 y 16", color: GUINDA, size: 18 }),
    ],
  }),
  h2("Tablero del Sprint 1"),
  caption("Configuración del tablero Kanban"),
  tabla([2600, 7038], ["Elemento", "Configuración"], [
    ["Herramienta", "GitHub Projects, proyecto público «SIRA - Sprint 1»"],
    ["Vista", "Tablero «Sprint 1»"],
    ["Columnas", "Por hacer · En progreso · En revisión · Hecho"],
    ["Tarjetas", "Una tarjeta por historia del Sprint Backlog 1 (HU01a, HU01b, HU02 a HU06) con sus puntos; las tareas y sus responsables son los de la tabla 8."],
    ["Estado inicial", "Las 7 historias en Por hacer: el Sprint 1 inicia en la semana 9."],
    ["Paso a Hecho", "Solo cuando la historia cumple los 8 criterios de la Definición de Hecho."],
    [{ celda: celda("Enlace", 2600, { bold: true }) }, { celda: new TableCell({
      width: { size: 7038, type: WidthType.DXA },
      borders: bordes,
      verticalAlign: VerticalAlign.CENTER,
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({ children: [new ExternalHyperlink({
        link: URL_TABLERO,
        children: [new TextRun({ text: URL_TABLERO, style: "Hyperlink", size: 18 })],
      })] })],
    }) }],
  ], { negrita: [0] }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: true,
    spacing: { before: 240, after: 80 },
    children: [new ImageRun({ type: "png", data: tablero, transformation: { width: 620, height: Math.round(620 * 800 / 1334) } })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [
      new TextRun({ text: "Figura 2. ", bold: true, color: GUINDA, size: 18 }),
      new TextRun({ text: "Tablero Kanban del Sprint 1 con el Sprint Backlog 1 cargado", color: GUINDA, size: 18 }),
    ],
  }),
];

// ------------------------------------------------------------------ Anexo A
const anexo = [
  h1("Anexo A. Declaración de uso de herramientas de IA y de terceros"),
  p("Conforme a la disposición de integridad académica del proyecto integrador, el equipo declara las herramientas de inteligencia artificial o de terceros utilizadas en este entregable. Todo el contenido declarado fue revisado por el equipo, que puede explicarlo."),
  caption("Herramientas de IA y de terceros utilizadas"),
  tabla([2000, 3938, 1500, 2200], ["Herramienta", "Uso que se le dio", "Parte del entregable", "Revisado por"], [
    ["Claude (Anthropic)", "Redacción de las decisiones del equipo sobre roles, estimación, Definición de Hecho, Sprint Backlog y plan de release; código del diagrama del plan de release.", "Pasos 1 a 5", [INGA, ALBINO, RASHU]],
    ["Mermaid Live Editor", "Exportación del diagrama del plan de release desde su código fuente.", "Paso 5 (figura 1)", [RASHU]],
  ], { negrita: [0] }),
];

// ------------------------------------------------------------------ Documento
const doc = new Document({
  creator: "Grupo A — SW705U",
  title: "Entregable 5 — Planificación ágil del desarrollo (Scrum)",
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 30, bold: true, color: GUINDA },
        paragraph: { spacing: { before: 120, after: 200 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 22, bold: true, color: "1A1A1A" },
        paragraph: { spacing: { before: 280, after: 100 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1650, bottom: 1100, left: 1134, right: 1134, header: 500, footer: 500 },
      },
      titlePage: false,
    },
    headers: { default: encabezado },
    footers: { default: pie },
    children: [...caratula, ...indice, ...insumos, ...paso1, ...paso2, ...paso3, ...paso4, ...paso5, ...anexo],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const salida = path.join(OUT_DIR, "Entregable5_SW705_GrupoA.docx");
  fs.writeFileSync(salida, buf);
  console.log("OK", salida, `puntos=${totalPts} dias=${totalDias}`);
});
