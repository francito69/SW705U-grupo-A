-- SIRA - Clínica San Rafael S.A.C.
-- 01-esquema.sql: creación de tablas, restricciones, índices y triggers
-- Motor: PostgreSQL 16

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- T1 - Seguridad y control de acceso
CREATE TABLE roles (
    id_rol      SERIAL       PRIMARY KEY,
    nombre      VARCHAR(30)  NOT NULL UNIQUE
                CHECK (nombre IN ('ADMISION', 'MEDICO', 'ENFERMERA', 'LABORATORIO',
                                  'CAJA', 'GERENCIA', 'ADMINISTRADOR')),
    descripcion VARCHAR(150)
);

CREATE TABLE usuarios (
    id_usuario    SERIAL       PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    id_rol        INT          NOT NULL REFERENCES roles (id_rol),
    activo        BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- M4 - Convenios (se crea antes porque pacientes la referencia)
CREATE TABLE convenios (
    id_convenio        SERIAL       PRIMARY KEY,
    codigo_convenio    VARCHAR(20)  NOT NULL UNIQUE,
    nombre_institucion VARCHAR(100) NOT NULL,
    tipo_convenio      VARCHAR(12)  NOT NULL
                       CHECK (tipo_convenio IN ('PARTICULAR', 'EPS', 'SOAT')),
    contacto_operativo VARCHAR(150),
    activo             BOOLEAN      NOT NULL DEFAULT TRUE
);

-- M1 - Pacientes
CREATE TABLE pacientes (
    id_paciente          SERIAL       PRIMARY KEY,
    tipo_documento       VARCHAR(10)  NOT NULL
                         CHECK (tipo_documento IN ('DNI', 'CE', 'PASAPORTE')),
    numero_documento     VARCHAR(15)  NOT NULL,
    nombres              VARCHAR(100) NOT NULL,
    apellido_paterno     VARCHAR(60)  NOT NULL,
    apellido_materno     VARCHAR(60)  NOT NULL,
    fecha_nacimiento     DATE         NOT NULL,
    sexo                 CHAR(1)      NOT NULL CHECK (sexo IN ('M', 'F')),
    telefono             VARCHAR(20)  NOT NULL,
    email                VARCHAR(150),
    direccion            VARCHAR(200),
    id_convenio          INT          NOT NULL REFERENCES convenios (id_convenio),
    antecedentes_medicos TEXT,
    alergias             TEXT,
    activo               BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en            TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_paciente_documento UNIQUE (tipo_documento, numero_documento)
);

-- M2 - Agenda y citas
CREATE TABLE especialidades (
    id_especialidad SERIAL      PRIMARY KEY,
    nombre          VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE medicos (
    id_medico       SERIAL       PRIMARY KEY,
    cmp             VARCHAR(10)  NOT NULL UNIQUE,
    nombres         VARCHAR(100) NOT NULL,
    apellidos       VARCHAR(120) NOT NULL,
    id_especialidad INT          NOT NULL REFERENCES especialidades (id_especialidad),
    telefono        VARCHAR(20),
    email           VARCHAR(150),
    id_usuario      INT          UNIQUE REFERENCES usuarios (id_usuario),
    activo          BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE consultorios (
    id_consultorio SERIAL       PRIMARY KEY,
    numero         VARCHAR(10)  NOT NULL UNIQUE,
    piso           SMALLINT     NOT NULL CHECK (piso >= 1),
    descripcion    VARCHAR(100),
    activo         BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE citas (
    id_cita            SERIAL      PRIMARY KEY,
    id_paciente        INT         NOT NULL REFERENCES pacientes (id_paciente),
    id_medico          INT         NOT NULL REFERENCES medicos (id_medico),
    id_consultorio     INT         NOT NULL REFERENCES consultorios (id_consultorio),
    fecha_hora_inicio  TIMESTAMP   NOT NULL,
    fecha_hora_fin     TIMESTAMP   NOT NULL,
    estado             VARCHAR(15) NOT NULL DEFAULT 'CONFIRMADA'
                       CHECK (estado IN ('CONFIRMADA', 'EN_ESPERA', 'ATENDIDA',
                                         'CANCELADA', 'REPROGRAMADA', 'NO_ASISTIO')),
    motivo_cancelacion TEXT,
    hora_llegada       TIMESTAMP,
    id_cita_origen     INT         UNIQUE REFERENCES citas (id_cita),
    canal_agendamiento VARCHAR(12) NOT NULL DEFAULT 'ADMISION'
                       CHECK (canal_agendamiento IN ('ADMISION', 'PORTAL_WEB', 'TELEFONICO')),
    creado_por         INT         NOT NULL REFERENCES usuarios (id_usuario),
    creado_en          TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cita_rango CHECK (fecha_hora_fin > fecha_hora_inicio),
    CONSTRAINT chk_cita_motivo CHECK (
        estado NOT IN ('CANCELADA', 'REPROGRAMADA') OR motivo_cancelacion IS NOT NULL),
    CONSTRAINT chk_cita_llegada CHECK (
        estado NOT IN ('EN_ESPERA', 'ATENDIDA') OR hora_llegada IS NOT NULL),
    CONSTRAINT no_solapamiento_medico EXCLUDE USING gist (
        id_medico WITH =,
        tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&
    ) WHERE (estado IN ('CONFIRMADA', 'EN_ESPERA')),
    CONSTRAINT no_solapamiento_consultorio EXCLUDE USING gist (
        id_consultorio WITH =,
        tsrange(fecha_hora_inicio, fecha_hora_fin) WITH &&
    ) WHERE (estado IN ('CONFIRMADA', 'EN_ESPERA'))
);

-- M1 - Historia clínica electrónica y triaje
CREATE TABLE atenciones (
    id_atencion      SERIAL      PRIMARY KEY,
    id_paciente      INT         NOT NULL REFERENCES pacientes (id_paciente),
    id_medico        INT         NOT NULL REFERENCES medicos (id_medico),
    id_cita          INT         UNIQUE REFERENCES citas (id_cita),
    tipo_atencion    VARCHAR(20) NOT NULL DEFAULT 'CONSULTA_EXTERNA'
                     CHECK (tipo_atencion IN ('CONSULTA_EXTERNA', 'TOPICO_URGENCIA')),
    estado           VARCHAR(12) NOT NULL DEFAULT 'EN_CURSO'
                     CHECK (estado IN ('EN_CURSO', 'FINALIZADA')),
    motivo_consulta  TEXT,
    anamnesis        TEXT,
    indicaciones     TEXT,
    inicio_consulta  TIMESTAMP,
    finalizada_en    TIMESTAMP,
    anulado          BOOLEAN     NOT NULL DEFAULT FALSE,
    motivo_anulacion TEXT,
    anulado_por      INT         REFERENCES usuarios (id_usuario),
    anulado_en       TIMESTAMP,
    creado_en        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_atencion_cita CHECK (
        tipo_atencion = 'TOPICO_URGENCIA' OR id_cita IS NOT NULL),
    CONSTRAINT chk_atencion_finalizada CHECK (
        estado = 'EN_CURSO' OR (motivo_consulta IS NOT NULL AND finalizada_en IS NOT NULL)),
    CONSTRAINT chk_atencion_anulacion CHECK (
        (anulado = FALSE AND motivo_anulacion IS NULL AND anulado_por IS NULL AND anulado_en IS NULL)
        OR
        (anulado = TRUE AND char_length(motivo_anulacion) >= 20
                        AND anulado_por IS NOT NULL AND anulado_en IS NOT NULL))
);

CREATE TABLE triajes (
    id_triaje               SERIAL       PRIMARY KEY,
    id_atencion             INT          NOT NULL UNIQUE REFERENCES atenciones (id_atencion),
    presion_sistolica       SMALLINT     NOT NULL CHECK (presion_sistolica BETWEEN 50 AND 300),
    presion_diastolica      SMALLINT     NOT NULL CHECK (presion_diastolica BETWEEN 30 AND 200),
    temperatura             NUMERIC(4,1) NOT NULL CHECK (temperatura BETWEEN 30.0 AND 45.0),
    frecuencia_cardiaca     SMALLINT     NOT NULL CHECK (frecuencia_cardiaca BETWEEN 30 AND 250),
    frecuencia_respiratoria SMALLINT     CHECK (frecuencia_respiratoria BETWEEN 8 AND 60),
    saturacion_oxigeno      SMALLINT     CHECK (saturacion_oxigeno BETWEEN 50 AND 100),
    peso                    NUMERIC(5,2) NOT NULL CHECK (peso BETWEEN 1 AND 350),
    talla                   NUMERIC(3,2) NOT NULL CHECK (talla BETWEEN 0.30 AND 2.50),
    observaciones           TEXT,
    id_enfermera            INT          NOT NULL REFERENCES usuarios (id_usuario),
    registrado_en           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_triaje_presion CHECK (presion_sistolica > presion_diastolica)
);

CREATE TABLE diagnosticos_cie10 (
    codigo      VARCHAR(10)  PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL
);

CREATE TABLE atencion_diagnosticos (
    id_atencion  INT         NOT NULL REFERENCES atenciones (id_atencion),
    codigo_cie10 VARCHAR(10) NOT NULL REFERENCES diagnosticos_cie10 (codigo),
    tipo         VARCHAR(12) NOT NULL
                 CHECK (tipo IN ('PRINCIPAL', 'SECUNDARIO', 'PRESUNTIVO')),
    PRIMARY KEY (id_atencion, codigo_cie10)
);

CREATE UNIQUE INDEX uq_diagnostico_principal
    ON atencion_diagnosticos (id_atencion) WHERE tipo = 'PRINCIPAL';

CREATE TABLE prescripciones (
    id_prescripcion SERIAL       PRIMARY KEY,
    id_atencion     INT          NOT NULL REFERENCES atenciones (id_atencion),
    medicamento     VARCHAR(120) NOT NULL,
    presentacion    VARCHAR(80)  NOT NULL,
    frecuencia      VARCHAR(80)  NOT NULL,
    duracion        VARCHAR(40)  NOT NULL
);

-- M4 - Catálogo de servicios y tarifarios
CREATE TABLE servicios_medicos (
    id_servicio            SERIAL        PRIMARY KEY,
    codigo_servicio        VARCHAR(20)   NOT NULL UNIQUE,
    nombre_servicio        VARCHAR(150)  NOT NULL,
    tipo_servicio          VARCHAR(15)   NOT NULL
                           CHECK (tipo_servicio IN ('CONSULTA', 'LABORATORIO',
                                                    'IMAGENES', 'PROCEDIMIENTO')),
    precio_base_particular NUMERIC(10,2) NOT NULL CHECK (precio_base_particular >= 0),
    activo                 BOOLEAN       NOT NULL DEFAULT TRUE
);

CREATE TABLE tarifarios_servicios (
    id_tarifario         SERIAL        PRIMARY KEY,
    id_servicio          INT           NOT NULL REFERENCES servicios_medicos (id_servicio),
    id_convenio          INT           NOT NULL REFERENCES convenios (id_convenio),
    precio_convenido     NUMERIC(10,2) NOT NULL CHECK (precio_convenido >= 0),
    porcentaje_cobertura NUMERIC(5,2)  NOT NULL CHECK (porcentaje_cobertura BETWEEN 0 AND 100),
    copago_fijo          NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (copago_fijo >= 0),
    vigente_desde        DATE          NOT NULL,
    vigente_hasta        DATE,
    CONSTRAINT chk_tarifario_vigencia CHECK (vigente_hasta IS NULL OR vigente_hasta > vigente_desde),
    CONSTRAINT no_solapamiento_tarifario EXCLUDE USING gist (
        id_servicio WITH =,
        id_convenio WITH =,
        daterange(vigente_desde, vigente_hasta) WITH &&
    )
);

-- M3 - Laboratorio e imágenes
CREATE TABLE ordenes_examen (
    id_orden              SERIAL      PRIMARY KEY,
    codigo_orden          VARCHAR(20) NOT NULL UNIQUE,
    id_atencion           INT         NOT NULL REFERENCES atenciones (id_atencion),
    id_servicio           INT         NOT NULL REFERENCES servicios_medicos (id_servicio),
    indicaciones_clinicas TEXT,
    estado                VARCHAR(12) NOT NULL DEFAULT 'SOLICITADO'
                          CHECK (estado IN ('SOLICITADO', 'EN_PROCESO', 'COMPLETADO', 'ANULADO')),
    fecha_solicitud       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resultados (
    id_resultado         SERIAL       PRIMARY KEY,
    id_orden             INT          NOT NULL UNIQUE REFERENCES ordenes_examen (id_orden),
    informe_diagnostico  TEXT         NOT NULL,
    ruta_archivo_privado VARCHAR(500) NOT NULL,
    hash_archivo         CHAR(64)     NOT NULL CHECK (hash_archivo ~ '^[0-9a-f]{64}$'),
    fecha_toma_muestra   TIMESTAMP    NOT NULL,
    fecha_resultado      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_validador         INT          NOT NULL REFERENCES usuarios (id_usuario),
    CONSTRAINT chk_resultado_fechas CHECK (fecha_resultado >= fecha_toma_muestra)
);

-- M4 - Facturación y glosas
CREATE TABLE facturas (
    id_factura         SERIAL      PRIMARY KEY,
    numero_comprobante VARCHAR(25) NOT NULL UNIQUE,
    id_atencion        INT         NOT NULL UNIQUE REFERENCES atenciones (id_atencion),
    id_convenio        INT         NOT NULL REFERENCES convenios (id_convenio),
    estado             VARCHAR(10) NOT NULL DEFAULT 'EMITIDA'
                       CHECK (estado IN ('EMITIDA', 'PAGADA', 'OBSERVADA', 'ANULADA')),
    creado_por         INT         NOT NULL REFERENCES usuarios (id_usuario),
    fecha_emision      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE factura_detalle (
    id_detalle      SERIAL        PRIMARY KEY,
    id_factura      INT           NOT NULL REFERENCES facturas (id_factura),
    id_servicio     INT           NOT NULL REFERENCES servicios_medicos (id_servicio),
    id_orden        INT           UNIQUE REFERENCES ordenes_examen (id_orden),
    cantidad        SMALLINT      NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario >= 0),
    monto_cubierto  NUMERIC(10,2) NOT NULL CHECK (monto_cubierto >= 0),
    copago          NUMERIC(10,2) NOT NULL CHECK (copago >= 0),
    CONSTRAINT chk_detalle_montos CHECK (precio_unitario * cantidad = monto_cubierto + copago)
);

CREATE TABLE glosas (
    id_glosa           SERIAL        PRIMARY KEY,
    id_factura         INT           NOT NULL REFERENCES facturas (id_factura),
    codigo_glosa       VARCHAR(30)   NOT NULL,
    monto_glosado      NUMERIC(10,2) NOT NULL CHECK (monto_glosado > 0),
    motivo_observacion TEXT          NOT NULL,
    sustento           TEXT,
    estado             VARCHAR(12)   NOT NULL DEFAULT 'REGISTRADA'
                       CHECK (estado IN ('REGISTRADA', 'SUSTENTADA', 'ACEPTADA',
                                         'RECHAZADA', 'RECUPERADA')),
    fecha_observacion  DATE          NOT NULL DEFAULT CURRENT_DATE,
    fecha_resolucion   DATE,
    registrado_por     INT           NOT NULL REFERENCES usuarios (id_usuario),
    CONSTRAINT chk_glosa_fechas CHECK (
        fecha_resolucion IS NULL OR fecha_resolucion >= fecha_observacion),
    CONSTRAINT chk_glosa_cierre CHECK (
        estado IN ('REGISTRADA', 'SUSTENTADA') OR fecha_resolucion IS NOT NULL)
);

-- T3 - Notificaciones (patrón Outbox)
CREATE TABLE outbox_notificaciones (
    id_notificacion SERIAL       PRIMARY KEY,
    id_cita         INT          REFERENCES citas (id_cita),
    tipo_evento     VARCHAR(20)  NOT NULL
                    CHECK (tipo_evento IN ('RECORDATORIO_24H', 'CONFIRMACION_CITA', 'AVISO_RESULTADO')),
    canal           VARCHAR(10)  NOT NULL CHECK (canal IN ('SMS', 'EMAIL', 'WHATSAPP')),
    destinatario    VARCHAR(150) NOT NULL,
    mensaje         TEXT         NOT NULL,
    programado_para TIMESTAMP    NOT NULL,
    estado          VARCHAR(10)  NOT NULL DEFAULT 'PENDIENTE'
                    CHECK (estado IN ('PENDIENTE', 'ENVIADO', 'FALLIDO')),
    intentos        SMALLINT     NOT NULL DEFAULT 0 CHECK (intentos >= 0),
    error_detalle   TEXT,
    procesado_en    TIMESTAMP,
    creado_en       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- T2 - Bitácora de auditoría
CREATE TABLE bitacora_auditoria (
    id_auditoria         BIGSERIAL   PRIMARY KEY,
    id_usuario           INT         NOT NULL REFERENCES usuarios (id_usuario),
    nombre_tabla         VARCHAR(50) NOT NULL,
    id_registro_afectado INT         NOT NULL,
    accion               VARCHAR(16) NOT NULL
                         CHECK (accion IN ('SELECT', 'INSERT', 'UPDATE', 'ANULAR', 'ACCESO_DENEGADO')),
    direccion_ip         INET        NOT NULL,
    datos_anteriores     JSONB,
    datos_nuevos         JSONB,
    motivo               TEXT,
    fecha_hora           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_auditoria_motivo CHECK (accion <> 'ANULAR' OR motivo IS NOT NULL)
);

-- Índices de rendimiento (RNF-001)
CREATE INDEX idx_atenciones_paciente_fecha
    ON atenciones (id_paciente, creado_en DESC) WHERE anulado = FALSE;
CREATE INDEX idx_citas_medico_inicio      ON citas (id_medico, fecha_hora_inicio);
CREATE INDEX idx_citas_paciente           ON citas (id_paciente);
CREATE INDEX idx_prescripciones_atencion  ON prescripciones (id_atencion);
CREATE INDEX idx_ordenes_atencion         ON ordenes_examen (id_atencion);
CREATE INDEX idx_ordenes_estado           ON ordenes_examen (estado, fecha_solicitud);
CREATE INDEX idx_detalle_factura          ON factura_detalle (id_factura);
CREATE INDEX idx_outbox_pendientes
    ON outbox_notificaciones (programado_para) WHERE estado = 'PENDIENTE';
CREATE INDEX idx_auditoria_usuario_fecha  ON bitacora_auditoria (id_usuario, fecha_hora DESC);

-- Prohibición de borrado físico de información clínica (RNF-004)
CREATE FUNCTION impedir_borrado() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'No se permite eliminar registros de %: use la anulación lógica (RNF-004)',
        TG_TABLE_NAME
        USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pacientes_sin_borrado BEFORE DELETE ON pacientes
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();
CREATE TRIGGER trg_atenciones_sin_borrado BEFORE DELETE ON atenciones
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();
CREATE TRIGGER trg_triajes_sin_borrado BEFORE DELETE ON triajes
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();
CREATE TRIGGER trg_diagnosticos_sin_borrado BEFORE DELETE ON atencion_diagnosticos
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();
CREATE TRIGGER trg_prescripciones_sin_borrado BEFORE DELETE ON prescripciones
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();
CREATE TRIGGER trg_ordenes_sin_borrado BEFORE DELETE ON ordenes_examen
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();
CREATE TRIGGER trg_resultados_sin_borrado BEFORE DELETE ON resultados
    FOR EACH ROW EXECUTE FUNCTION impedir_borrado();

-- La bitácora de auditoría no admite modificaciones ni borrados
CREATE FUNCTION impedir_cambios_bitacora() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'La bitácora de auditoría es inmutable: no admite %', TG_OP
        USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bitacora_inmutable BEFORE UPDATE OR DELETE ON bitacora_auditoria
    FOR EACH ROW EXECUTE FUNCTION impedir_cambios_bitacora();

-- Vista de totales por comprobante (los montos se guardan por línea)
CREATE VIEW v_facturas_totales AS
SELECT f.id_factura,
       f.numero_comprobante,
       f.estado,
       SUM(d.precio_unitario * d.cantidad) AS monto_total,
       SUM(d.monto_cubierto)               AS monto_cubierto_seguro,
       SUM(d.copago)                       AS copago_paciente
FROM facturas f
JOIN factura_detalle d ON d.id_factura = f.id_factura
GROUP BY f.id_factura, f.numero_comprobante, f.estado;
