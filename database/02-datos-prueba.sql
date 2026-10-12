-- SIRA - Clínica San Rafael S.A.C.
-- 02-datos-prueba.sql: datos ficticios para pruebas y demostración
-- Ninguno de estos datos corresponde a personas reales.
-- Se ejecuta sobre una base recién creada con 01-esquema.sql.

BEGIN;

-- T1 - Seguridad
INSERT INTO roles (nombre, descripcion) VALUES
    ('ADMISION',      'Registro de pacientes y agenda de citas'),
    ('MEDICO',        'Atención médica, diagnóstico, receta y órdenes de examen'),
    ('ENFERMERA',     'Triaje y signos vitales'),
    ('LABORATORIO',   'Procesamiento de órdenes y carga de resultados'),
    ('CAJA',          'Liquidación, comprobantes y glosas'),
    ('GERENCIA',      'Indicadores de gestión y anulaciones clínicas'),
    ('ADMINISTRADOR', 'Gestión de usuarios y roles');

INSERT INTO usuarios (username, password_hash, email, id_rol) VALUES
    ('admision.rquispe', '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'rquispe@sanrafael.test',  1),
    ('admision.lflores', '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'lflores@sanrafael.test',  1),
    ('med.jvaldivia',    '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'jvaldivia@sanrafael.test', 2),
    ('med.cmendoza',     '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'cmendoza@sanrafael.test',  2),
    ('med.aramos',       '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'aramos@sanrafael.test',    2),
    ('med.psoto',        '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'psoto@sanrafael.test',     2),
    ('med.mmorales',     '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'mmorales@sanrafael.test',  2),
    ('med.ltorres',      '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'ltorres@sanrafael.test',   2),
    ('enf.rpaz',         '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'rpaz@sanrafael.test',      3),
    ('enf.mcastro',      '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'mcastro@sanrafael.test',   3),
    ('lab.jhuaman',      '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'jhuaman@sanrafael.test',   4),
    ('lab.dchavez',      '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'dchavez@sanrafael.test',   4),
    ('caja.evargas',     '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'evargas@sanrafael.test',   5),
    ('caja.ksilva',      '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'ksilva@sanrafael.test',    5),
    ('ger.rmedina',      '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'rmedina@sanrafael.test',   6),
    ('admin.sira',       '$2b$12$Q7vXk1Lr9pTz3mWc5yHn8eFzJ0aB2cD4eG6hI8jK0lM2nO4pQ6rS', 'admin@sanrafael.test',     7);

-- M4 - Convenios
INSERT INTO convenios (codigo_convenio, nombre_institucion, tipo_convenio, contacto_operativo) VALUES
    ('PARTICULAR',   'Paciente particular', 'PARTICULAR', NULL),
    ('EPS_RIMAC',    'Rímac EPS',           'EPS',        'convenios@rimac-eps.test'),
    ('EPS_PACIFICO', 'Pacífico EPS',        'EPS',        'convenios@pacifico-eps.test'),
    ('EPS_MAPFRE',   'Mapfre Perú EPS',     'EPS',        'convenios@mapfre-eps.test'),
    ('EPS_SANITAS',  'Sanitas Perú EPS',    'EPS',        'convenios@sanitas-eps.test'),
    ('EPS_POSITIVA', 'La Positiva EPS',     'EPS',        'convenios@positiva-eps.test'),
    ('SOAT',         'SOAT',                'SOAT',       'soat@aseguradora.test');

-- M1 - Pacientes
INSERT INTO pacientes (tipo_documento, numero_documento, nombres, apellido_paterno, apellido_materno,
                       fecha_nacimiento, sexo, telefono, email, direccion, id_convenio,
                       antecedentes_medicos, alergias) VALUES
    ('DNI', '45892014',  'María Elena', 'Quispe',    'Rojas',   '1982-04-15', 'F', '987650001', 'maria.quispe@correo.test',     'Av. San Luis 2150, San Borja',        3, 'Hipertensión arterial controlada', 'Penicilina y sulfas'),
    ('DNI', '78945612',  'Lucas',       'Bustamante','Vega',    '2020-05-04', 'M', '987650002', 'elena.vega@correo.test',       'Jr. Las Begonias 340, San Borja',     3, NULL,                               NULL),
    ('DNI', '41258963',  'José',        'Herrera',   'Díaz',    '1972-03-12', 'M', '987650003', 'jose.herrera@correo.test',     'Av. Aviación 3120, San Borja',        3, 'Dislipidemia',                     NULL),
    ('DNI', '77895214',  'Ana',         'López',     'Vega',    '2020-02-10', 'F', '987650004', 'maria.vega@correo.test',       'Calle Los Geranios 115, Surquillo',   1, NULL,                               NULL),
    ('DNI', '10254879',  'Raúl',        'Castillo',  'Medina',  '1958-07-21', 'M', '987650005', 'raul.castillo@correo.test',    'Av. Javier Prado Este 2480, San Borja', 2, 'Diabetes mellitus tipo 2',      'Ácido acetilsalicílico'),
    ('DNI', '08521496',  'Carmen',      'Sandoval',  'Ruiz',    '1988-09-03', 'F', '987650006', 'carmen.sandoval@correo.test',  'Jr. Fray Angélico 560, San Borja',    2, NULL,                               NULL),
    ('DNI', '71452398',  'Felipe',      'Paredes',   'Guzmán',  '1984-01-30', 'M', '987650007', NULL,                           'Av. Primavera 1780, Surco',           1, NULL,                               NULL),
    ('DNI', '72631548',  'Rosa',        'Huamán',    'Díaz',    '1995-11-08', 'F', '987650008', 'rosa.huaman@correo.test',      'Calle Morelli 230, San Borja',        4, 'Gastritis crónica',                NULL),
    ('DNI', '70819324',  'Luis',        'Mendoza',   'Paredes', '1990-06-17', 'M', '987650009', 'luis.mendoza@correo.test',     'Av. Canadá 1450, La Victoria',        7, NULL,                               NULL),
    ('CE',  '001234567', 'Valentina',   'Rossi',     'Bianchi', '1979-12-02', 'F', '987650010', 'valentina.rossi@correo.test',  'Av. Del Parque Norte 480, San Isidro', 5, NULL,                              'Látex');

-- M2 - Especialidades, médicos y consultorios
INSERT INTO especialidades (nombre) VALUES
    ('Medicina General'), ('Pediatría'), ('Cardiología'), ('Ginecología'),
    ('Traumatología'), ('Dermatología'), ('Gastroenterología'), ('Medicina Interna');

INSERT INTO medicos (cmp, nombres, apellidos, id_especialidad, telefono, email, id_usuario) VALUES
    ('39412', 'Jorge',    'Valdivia Ríos',  2, '987600001', 'jvaldivia@sanrafael.test', 3),
    ('48921', 'Carlos',   'Mendoza Salas',  3, '987600002', 'cmendoza@sanrafael.test',  4),
    ('31877', 'Alberto',  'Ramos Peña',     1, '987600003', 'aramos@sanrafael.test',    5),
    ('52310', 'Patricia', 'Soto Lazo',      6, '987600004', 'psoto@sanrafael.test',     6),
    ('44108', 'Mónica',   'Morales Vidal',  4, '987600005', 'mmorales@sanrafael.test',  7),
    ('50733', 'Luis',     'Torres Campos',  5, '987600006', 'ltorres@sanrafael.test',   8);

INSERT INTO consultorios (numero, piso, descripcion) VALUES
    ('C01', 1, 'Medicina general'),
    ('C02', 1, 'Pediatría'),
    ('C03', 1, 'Pediatría'),
    ('C04', 1, 'Medicina interna'),
    ('C05', 1, 'Cardiología'),
    ('C06', 1, 'Dermatología'),
    ('C07', 2, 'Gastroenterología'),
    ('C08', 2, 'Ginecología'),
    ('C09', 2, 'Traumatología'),
    ('C10', 2, 'Otorrinolaringología'),
    ('C11', 2, 'Urología'),
    ('C12', 2, 'Endocrinología');

-- M2 - Citas
INSERT INTO citas (id_paciente, id_medico, id_consultorio, fecha_hora_inicio, fecha_hora_fin,
                   estado, motivo_cancelacion, hora_llegada, id_cita_origen, canal_agendamiento, creado_por) VALUES
    (1,  3, 1, '2026-10-12 09:00', '2026-10-12 09:30', 'ATENDIDA',     NULL, '2026-10-12 08:50', NULL, 'ADMISION',   1),
    (3,  2, 5, '2026-10-14 09:00', '2026-10-14 09:30', 'ATENDIDA',     NULL, '2026-10-14 08:45', NULL, 'ADMISION',   1),
    (2,  1, 2, '2026-10-14 09:00', '2026-10-14 09:30', 'EN_ESPERA',    NULL, '2026-10-14 08:40', NULL, 'TELEFONICO', 2),
    (6,  5, 8, '2026-10-13 10:00', '2026-10-13 10:30', 'ATENDIDA',     NULL, '2026-10-13 09:52', NULL, 'ADMISION',   1),
    (7,  3, 1, '2026-10-13 11:00', '2026-10-13 11:30', 'NO_ASISTIO',   NULL, NULL,               NULL, 'TELEFONICO', 2),
    (8,  4, 6, '2026-10-15 15:00', '2026-10-15 15:30', 'CANCELADA',    'Solicitud de la paciente por viaje', NULL, NULL, 'ADMISION', 2),
    (10, 2, 5, '2026-10-15 10:00', '2026-10-15 10:30', 'REPROGRAMADA', 'La paciente solicitó cambio de horario', NULL, NULL, 'ADMISION', 1),
    (10, 2, 5, '2026-10-16 10:00', '2026-10-16 10:30', 'CONFIRMADA',   NULL, NULL,               7,    'ADMISION',   1),
    (4,  1, 2, '2026-10-15 08:00', '2026-10-15 08:30', 'CONFIRMADA',   NULL, NULL,               NULL, 'TELEFONICO', 2),
    (5,  2, 5, '2026-10-16 11:00', '2026-10-16 11:30', 'CONFIRMADA',   NULL, NULL,               NULL, 'ADMISION',   1),
    (8,  3, 1, '2026-10-12 10:00', '2026-10-12 10:30', 'ATENDIDA',     NULL, '2026-10-12 09:50', NULL, 'ADMISION',   2);

-- M1 - Atenciones, triajes, diagnósticos y prescripciones
INSERT INTO diagnosticos_cie10 (codigo, descripcion) VALUES
    ('J00',   'Rinofaringitis aguda [resfriado común]'),
    ('J06.9', 'Infección aguda de las vías respiratorias superiores, no especificada'),
    ('I10',   'Hipertensión esencial (primaria)'),
    ('R51',   'Cefalea'),
    ('E11.9', 'Diabetes mellitus tipo 2 sin complicaciones'),
    ('K29.7', 'Gastritis, no especificada'),
    ('L20.9', 'Dermatitis atópica, no especificada'),
    ('M54.5', 'Lumbago no especificado'),
    ('S63.5', 'Esguince y torcedura de la muñeca'),
    ('Z01.4', 'Examen ginecológico (general) (de rutina)'),
    ('N39.0', 'Infección de vías urinarias, sitio no especificado');

INSERT INTO atenciones (id_paciente, id_medico, id_cita, tipo_atencion, estado, motivo_consulta, anamnesis,
                        indicaciones, inicio_consulta, finalizada_en, anulado, motivo_anulacion,
                        anulado_por, anulado_en, creado_en) VALUES
    (1, 3, 1,    'CONSULTA_EXTERNA', 'FINALIZADA',
        'Dolor de garganta y congestión nasal desde hace tres días',
        'Afebril. Faringe congestiva sin exudado. Murmullo vesicular conservado.',
        'Reposo relativo por 48 horas e hidratación abundante',
        '2026-10-12 09:05', '2026-10-12 09:25', FALSE, NULL, NULL, NULL, '2026-10-12 08:55'),
    (3, 2, 2,    'CONSULTA_EXTERNA', 'FINALIZADA',
        'Cefalea matutina y mareos leves desde hace tres días',
        'Niega dolor torácico. Ruidos cardiacos rítmicos, sin soplos.',
        'Dieta hiposódica, control de presión arterial en casa y control en 30 días',
        '2026-10-14 09:10', '2026-10-14 09:35', FALSE, NULL, NULL, NULL, '2026-10-14 08:50'),
    (2, 1, 3,    'CONSULTA_EXTERNA', 'EN_CURSO',
        NULL, NULL, NULL, NULL, NULL, FALSE, NULL, NULL, NULL, '2026-10-14 08:45'),
    (6, 5, 4,    'CONSULTA_EXTERNA', 'FINALIZADA',
        'Control ginecológico anual',
        'Asintomática. Examen ginecológico sin hallazgos patológicos.',
        'Control anual y ecografía pélvica de rutina',
        '2026-10-13 10:05', '2026-10-13 10:30', FALSE, NULL, NULL, NULL, '2026-10-13 09:55'),
    (9, 6, NULL, 'TOPICO_URGENCIA',  'FINALIZADA',
        'Dolor en muñeca derecha tras accidente de tránsito',
        'Dolor a la movilización de la muñeca derecha, sin deformidad visible.',
        'Inmovilización con férula, frío local y control en 7 días',
        '2026-10-13 18:20', '2026-10-13 18:50', FALSE, NULL, NULL, NULL, '2026-10-13 18:05'),
    (1, 3, NULL, 'TOPICO_URGENCIA',  'FINALIZADA',
        'Dolor de garganta y congestión nasal',
        NULL, NULL,
        '2026-10-12 10:00', '2026-10-12 10:10', TRUE,
        'Registro duplicado por error de digitación; la atención válida es la del 12/10/2026 a las 09:00',
        15, '2026-10-12 12:00', '2026-10-12 10:00'),
    (8, 3, 11,   'CONSULTA_EXTERNA', 'FINALIZADA',
        'Dolor epigástrico después de las comidas desde hace una semana',
        'Abdomen blando, depresible, doloroso a la palpación en epigastrio.',
        'Dieta blanda fraccionada, evitar irritantes y control en 15 días',
        '2026-10-12 10:05', '2026-10-12 10:25', FALSE, NULL, NULL, NULL, '2026-10-12 09:55');

INSERT INTO triajes (id_atencion, presion_sistolica, presion_diastolica, temperatura, frecuencia_cardiaca,
                     frecuencia_respiratoria, saturacion_oxigeno, peso, talla, observaciones,
                     id_enfermera, registrado_en) VALUES
    (1, 118, 76, 36.9, 82, 16, 98, 62.00, 1.58, 'Odinofagia leve',                         9,  '2026-10-12 08:58'),
    (2, 120, 80, 36.8, 74, 18, 98, 75.00, 1.70, 'Refiere cefalea de intensidad moderada',  9,  '2026-10-14 09:00'),
    (3, 100, 65, 37.2, 96, 22, 99, 21.50, 1.15, 'Acompañado por su madre',                 10, '2026-10-14 08:50'),
    (4, 112, 72, 36.5, 70, 16, 99, 58.30, 1.62, NULL,                                      10, '2026-10-13 09:58'),
    (5, 145, 92, 36.7, 98, 20, 97, 80.20, 1.75, 'Presión elevada; dolor intenso en muñeca', 9, '2026-10-13 18:10'),
    (7, 110, 70, 36.6, 76, 16, 98, 55.00, 1.60, NULL,                                      10, '2026-10-12 09:58');

INSERT INTO atencion_diagnosticos (id_atencion, codigo_cie10, tipo) VALUES
    (1, 'J00',   'PRINCIPAL'),
    (2, 'I10',   'PRINCIPAL'),
    (2, 'R51',   'SECUNDARIO'),
    (3, 'J06.9', 'PRESUNTIVO'),
    (4, 'Z01.4', 'PRINCIPAL'),
    (5, 'S63.5', 'PRINCIPAL'),
    (6, 'J00',   'PRINCIPAL'),
    (7, 'K29.7', 'PRINCIPAL');

INSERT INTO prescripciones (id_atencion, medicamento, presentacion, frecuencia, duracion) VALUES
    (1, 'Paracetamol',       '500 mg tableta',  'Cada 8 horas',                       '3 días'),
    (1, 'Clorfenamina',      '4 mg tableta',    'Cada 12 horas',                      '5 días'),
    (2, 'Losartán potásico', '50 mg tableta',   'Cada 24 horas, con el desayuno',     '30 días'),
    (2, 'Paracetamol',       '500 mg tableta',  'Cada 8 horas si hay dolor de cabeza', '3 días'),
    (5, 'Ibuprofeno',        '400 mg tableta',  'Cada 8 horas, después de comer',     '5 días'),
    (5, 'Diclofenaco',       'Gel al 1 %',      'Cada 12 horas sobre la zona afectada', '7 días'),
    (7, 'Omeprazol',         '20 mg cápsula',   'Cada 24 horas, antes del desayuno',  '14 días');

-- M4 - Servicios y tarifarios
INSERT INTO servicios_medicos (codigo_servicio, nombre_servicio, tipo_servicio, precio_base_particular) VALUES
    ('CON-GEN-01', 'Consulta externa de medicina general', 'CONSULTA',      80.00),
    ('CON-ESP-01', 'Consulta externa de especialidad',     'CONSULTA',     140.00),
    ('LAB-HEM-01', 'Hemograma completo',                   'LABORATORIO',   35.00),
    ('LAB-GLU-01', 'Glucosa en ayunas',                    'LABORATORIO',   15.00),
    ('LAB-LIP-01', 'Perfil lipídico',                      'LABORATORIO',   60.00),
    ('LAB-ORI-01', 'Examen completo de orina',             'LABORATORIO',   20.00),
    ('IMG-RXM-01', 'Radiografía de muñeca (2 incidencias)', 'IMAGENES',     90.00),
    ('IMG-ECO-01', 'Ecografía pélvica',                    'IMAGENES',     120.00),
    ('PRO-TOP-01', 'Atención en tópico de urgencias',      'PROCEDIMIENTO', 100.00);

INSERT INTO tarifarios_servicios (id_servicio, id_convenio, precio_convenido, porcentaje_cobertura,
                                  copago_fijo, vigente_desde, vigente_hasta) VALUES
    (1, 1,  80.00,   0.00,  0.00, '2026-01-01', NULL),
    (2, 1, 140.00,   0.00,  0.00, '2026-01-01', NULL),
    (3, 1,  35.00,   0.00,  0.00, '2026-01-01', NULL),
    (1, 3,  75.00,  80.00, 20.00, '2025-01-01', '2026-01-01'),
    (1, 3,  80.00,  80.00, 20.00, '2026-01-01', NULL),
    (2, 3, 140.00,  85.00, 25.00, '2026-01-01', NULL),
    (4, 3,  15.00,  85.00,  0.00, '2026-01-01', NULL),
    (5, 3,  60.00,  85.00,  0.00, '2026-01-01', NULL),
    (2, 2, 140.00,  80.00, 20.00, '2026-01-01', NULL),
    (8, 2, 120.00,  80.00,  0.00, '2026-01-01', NULL),
    (1, 4,  80.00,  75.00, 15.00, '2026-01-01', NULL),
    (3, 4,  35.00,  75.00,  0.00, '2026-01-01', NULL),
    (9, 7, 100.00, 100.00,  0.00, '2026-01-01', NULL),
    (7, 7,  90.00, 100.00,  0.00, '2026-01-01', NULL);

-- M3 - Órdenes de examen y resultados
INSERT INTO ordenes_examen (codigo_orden, id_atencion, id_servicio, indicaciones_clinicas, estado, fecha_solicitud) VALUES
    ('ORD-2026-00001', 2, 5, 'Ayuno de 12 horas',                    'COMPLETADO', '2026-10-14 09:30'),
    ('ORD-2026-00002', 2, 4, 'Ayuno de 8 horas',                     'COMPLETADO', '2026-10-14 09:30'),
    ('ORD-2026-00003', 4, 8, 'Vejiga llena',                         'COMPLETADO', '2026-10-13 10:25'),
    ('ORD-2026-00004', 5, 7, 'Descartar fractura de radio distal',   'COMPLETADO', '2026-10-13 18:30'),
    ('ORD-2026-00005', 7, 3, NULL,                                   'COMPLETADO', '2026-10-12 10:20'),
    ('ORD-2026-00006', 3, 6, 'Muestra de la primera orina del día',  'SOLICITADO', '2026-10-14 09:20'),
    ('ORD-2026-00007', 7, 4, 'Ayuno de 8 horas',                     'EN_PROCESO', '2026-10-12 10:20');

INSERT INTO resultados (id_orden, informe_diagnostico, ruta_archivo_privado, hash_archivo,
                        fecha_toma_muestra, fecha_resultado, id_validador) VALUES
    (1, 'Colesterol total 218 mg/dL (alto); LDL 142 mg/dL; HDL 41 mg/dL; triglicéridos 175 mg/dL',
        'resultados/2026/10/ORD-2026-00001.pdf',
        '7abc4033a6a7c1fc7b9b2d4ddf3c4669de1cbfeb0de316a43ce392b1a5795fe9',
        '2026-10-14 10:00', '2026-10-14 12:40', 11),
    (2, 'Glucosa en ayunas 98 mg/dL, dentro del rango normal',
        'resultados/2026/10/ORD-2026-00002.pdf',
        '436892b163b7fe5e487095dc2f7b668119eaeed6dfb64637201baf4b6759073a',
        '2026-10-14 10:00', '2026-10-14 11:30', 11),
    (3, 'Útero y anexos de forma y tamaño normales; sin hallazgos patológicos',
        'resultados/2026/10/ORD-2026-00003.pdf',
        '3a58732bb9855b4e8843d3fc0c86747e46a052021f2181e3cdd016a6d067c545',
        '2026-10-13 11:00', '2026-10-13 13:15', 12),
    (4, 'Sin trazos de fractura; aumento de partes blandas en la región radiocarpiana',
        'resultados/2026/10/ORD-2026-00004.pdf',
        'f3e536b3a269beba7a6d5e4b988112f28ee49363cdf2c9a56967a55619c63d63',
        '2026-10-13 18:40', '2026-10-13 19:30', 12),
    (5, 'Hemoglobina 12.8 g/dL; leucocitos 7200/mm3; plaquetas 265000/mm3; valores normales',
        'resultados/2026/10/ORD-2026-00005.pdf',
        'a160f778844f70e8379495b6c23a51087ca883e17f9b09a4cc14a5ce5b10d5e7',
        '2026-10-12 10:40', '2026-10-12 12:10', 11);

-- M4 - Comprobantes, detalle y glosas
INSERT INTO facturas (numero_comprobante, id_atencion, id_convenio, estado, creado_por, fecha_emision) VALUES
    ('LIQ-2026-000101', 1, 3, 'PAGADA',    13, '2026-10-12 09:40'),
    ('LIQ-2026-000102', 7, 4, 'PAGADA',    14, '2026-10-12 10:40'),
    ('LIQ-2026-000103', 4, 2, 'OBSERVADA', 13, '2026-10-13 10:50'),
    ('LIQ-2026-000104', 5, 7, 'EMITIDA',   14, '2026-10-13 19:10'),
    ('LIQ-2026-000105', 2, 3, 'EMITIDA',   13, '2026-10-14 09:50');

INSERT INTO factura_detalle (id_factura, id_servicio, id_orden, cantidad, precio_unitario, monto_cubierto, copago) VALUES
    (1, 1, NULL, 1,  80.00,  48.00, 32.00),
    (2, 1, NULL, 1,  80.00,  48.75, 31.25),
    (2, 3, 5,    1,  35.00,  26.25,  8.75),
    (3, 2, NULL, 1, 140.00,  96.00, 44.00),
    (3, 8, 3,    1, 120.00,  96.00, 24.00),
    (4, 9, NULL, 1, 100.00, 100.00,  0.00),
    (4, 7, 4,    1,  90.00,  90.00,  0.00),
    (5, 2, NULL, 1, 140.00,  97.75, 42.25),
    (5, 5, 1,    1,  60.00,  51.00,  9.00),
    (5, 4, 2,    1,  15.00,  12.75,  2.25);

INSERT INTO glosas (id_factura, codigo_glosa, monto_glosado, motivo_observacion, sustento, estado,
                    fecha_observacion, fecha_resolucion, registrado_por) VALUES
    (3, 'GL-RIM-0412', 24.00, 'Ecografía facturada sin informe firmado adjunto',
        'Se adjunta el informe firmado por el médico radiólogo', 'SUSTENTADA', '2026-10-14', NULL, 13),
    (1, 'GL-PAC-0098', 10.00, 'Diferencia en el copago fijo pactado para consulta general',
        NULL, 'ACEPTADA', '2026-10-13', '2026-10-14', 13),
    (2, 'GL-MAP-0231',  8.75, 'Hemograma sin autorización previa de la aseguradora',
        'Examen solicitado en la misma consulta; se adjunta la orden médica', 'RECHAZADA', '2026-10-13', '2026-10-14', 14),
    (5, 'GL-PAC-0105',  9.00, 'Código de procedimiento no coincide con el tarifario del convenio',
        NULL, 'REGISTRADA', '2026-10-14', NULL, 13),
    (3, 'GL-RIM-0415', 44.00, 'Copago cobrado por encima del pactado',
        'Se demostró la aplicación del tarifario vigente', 'RECUPERADA', '2026-10-14', '2026-10-14', 13);

-- T3 - Notificaciones
INSERT INTO outbox_notificaciones (id_cita, tipo_evento, canal, destinatario, mensaje, programado_para,
                                   estado, intentos, error_detalle, procesado_en) VALUES
    (8,    'RECORDATORIO_24H',  'SMS',      '987650010',
        'Clínica San Rafael: recuerde su cita de Cardiología el 16/10/2026 a las 10:00 en el consultorio C05.',
        '2026-10-15 10:00', 'PENDIENTE', 0, NULL, NULL),
    (10,   'RECORDATORIO_24H',  'EMAIL',    'raul.castillo@correo.test',
        'Clínica San Rafael: recuerde su cita de Cardiología el 16/10/2026 a las 11:00 en el consultorio C05.',
        '2026-10-15 11:00', 'PENDIENTE', 0, NULL, NULL),
    (9,    'RECORDATORIO_24H',  'SMS',      '987650004',
        'Clínica San Rafael: recuerde la cita de Pediatría el 15/10/2026 a las 08:00 en el consultorio C02.',
        '2026-10-14 08:00', 'ENVIADO', 1, NULL, '2026-10-14 08:00:05'),
    (2,    'RECORDATORIO_24H',  'WHATSAPP', '987650003',
        'Clínica San Rafael: recuerde su cita de Cardiología el 14/10/2026 a las 09:00 en el consultorio C05.',
        '2026-10-13 09:00', 'ENVIADO', 1, NULL, '2026-10-13 09:00:04'),
    (5,    'RECORDATORIO_24H',  'SMS',      '987650007',
        'Clínica San Rafael: recuerde su cita de Medicina General el 13/10/2026 a las 11:00 en el consultorio C01.',
        '2026-10-12 11:00', 'FALLIDO', 3, 'Tiempo de espera agotado con el proveedor de SMS', NULL),
    (NULL, 'AVISO_RESULTADO',   'EMAIL',    'jose.herrera@correo.test',
        'Clínica San Rafael: sus resultados de laboratorio ya están disponibles. Consúltelos con su médico tratante.',
        '2026-10-14 12:45', 'ENVIADO', 1, NULL, '2026-10-14 12:45:03'),
    (8,    'CONFIRMACION_CITA', 'SMS',      '987650010',
        'Clínica San Rafael: su cita de Cardiología fue reprogramada para el 16/10/2026 a las 10:00.',
        '2026-10-14 08:30', 'ENVIADO', 1, NULL, '2026-10-14 08:30:02');

-- T2 - Bitácora de auditoría
INSERT INTO bitacora_auditoria (id_usuario, nombre_tabla, id_registro_afectado, accion, direccion_ip,
                                datos_anteriores, datos_nuevos, motivo, fecha_hora) VALUES
    (4,  'atenciones', 2, 'SELECT',          '10.20.1.15', NULL, NULL, NULL, '2026-10-14 09:10'),
    (4,  'atenciones', 2, 'UPDATE',          '10.20.1.15',
        '{"estado": "EN_CURSO"}', '{"estado": "FINALIZADA"}', NULL, '2026-10-14 09:35'),
    (13, 'pacientes',  3, 'ACCESO_DENEGADO', '10.20.3.21', NULL, NULL,
        'Rol CAJA sin permiso para consultar la HCE', '2026-10-14 09:40'),
    (15, 'atenciones', 6, 'ANULAR',          '10.20.5.10',
        '{"anulado": false}', '{"anulado": true}',
        'Registro duplicado por error de digitación', '2026-10-12 12:00'),
    (9,  'triajes',    2, 'INSERT',          '10.20.2.11', NULL, NULL, NULL, '2026-10-14 09:00'),
    (11, 'resultados', 1, 'INSERT',          '10.20.4.30', NULL, NULL, NULL, '2026-10-14 12:40');

COMMIT;
