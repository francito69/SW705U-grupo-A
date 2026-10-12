-- SIRA - Clínica San Rafael S.A.C.
-- 03-verificacion.sql: conteo de registros y pruebas de las restricciones
-- Cada prueba intenta una operación inválida y muestra un NOTICE con el
-- resultado. Ninguna prueba deja cambios en la base de datos.

-- 1. Registros por tabla
SELECT 'roles' AS tabla, COUNT(*) AS registros FROM roles
UNION ALL SELECT 'usuarios', COUNT(*) FROM usuarios
UNION ALL SELECT 'convenios', COUNT(*) FROM convenios
UNION ALL SELECT 'pacientes', COUNT(*) FROM pacientes
UNION ALL SELECT 'especialidades', COUNT(*) FROM especialidades
UNION ALL SELECT 'medicos', COUNT(*) FROM medicos
UNION ALL SELECT 'consultorios', COUNT(*) FROM consultorios
UNION ALL SELECT 'citas', COUNT(*) FROM citas
UNION ALL SELECT 'atenciones', COUNT(*) FROM atenciones
UNION ALL SELECT 'triajes', COUNT(*) FROM triajes
UNION ALL SELECT 'diagnosticos_cie10', COUNT(*) FROM diagnosticos_cie10
UNION ALL SELECT 'atencion_diagnosticos', COUNT(*) FROM atencion_diagnosticos
UNION ALL SELECT 'prescripciones', COUNT(*) FROM prescripciones
UNION ALL SELECT 'servicios_medicos', COUNT(*) FROM servicios_medicos
UNION ALL SELECT 'tarifarios_servicios', COUNT(*) FROM tarifarios_servicios
UNION ALL SELECT 'ordenes_examen', COUNT(*) FROM ordenes_examen
UNION ALL SELECT 'resultados', COUNT(*) FROM resultados
UNION ALL SELECT 'facturas', COUNT(*) FROM facturas
UNION ALL SELECT 'factura_detalle', COUNT(*) FROM factura_detalle
UNION ALL SELECT 'glosas', COUNT(*) FROM glosas
UNION ALL SELECT 'outbox_notificaciones', COUNT(*) FROM outbox_notificaciones
UNION ALL SELECT 'bitacora_auditoria', COUNT(*) FROM bitacora_auditoria;

-- 2. Totales de los comprobantes
SELECT numero_comprobante, estado, monto_total, monto_cubierto_seguro, copago_paciente
FROM v_facturas_totales
ORDER BY numero_comprobante;

-- 3. Pruebas de restricciones
DO $$
BEGIN
    INSERT INTO citas (id_paciente, id_medico, id_consultorio, fecha_hora_inicio, fecha_hora_fin, creado_por)
    VALUES (1, 2, 9, '2026-10-16 10:15', '2026-10-16 10:45', 1);
    RAISE EXCEPTION 'Prueba 1 fallida: se aceptó una cita solapada para el mismo médico';
EXCEPTION WHEN exclusion_violation THEN
    RAISE NOTICE 'Prueba 1 correcta (RF-002): cita solapada del mismo médico rechazada';
END $$;

DO $$
BEGIN
    INSERT INTO citas (id_paciente, id_medico, id_consultorio, fecha_hora_inicio, fecha_hora_fin, creado_por)
    VALUES (1, 6, 5, '2026-10-16 10:00', '2026-10-16 10:30', 1);
    RAISE EXCEPTION 'Prueba 2 fallida: se aceptó una cita solapada en el mismo consultorio';
EXCEPTION WHEN exclusion_violation THEN
    RAISE NOTICE 'Prueba 2 correcta (RF-002): cita solapada en el mismo consultorio rechazada';
END $$;

DO $$
BEGIN
    DELETE FROM atenciones WHERE id_atencion = 1;
    RAISE EXCEPTION 'Prueba 3 fallida: se permitió el borrado físico de una atención';
EXCEPTION WHEN restrict_violation THEN
    RAISE NOTICE 'Prueba 3 correcta (RNF-004): borrado físico de la atención rechazado';
END $$;

DO $$
BEGIN
    UPDATE atenciones
    SET anulado = TRUE, motivo_anulacion = 'Error', anulado_por = 15, anulado_en = '2026-10-14 13:00'
    WHERE id_atencion = 1;
    RAISE EXCEPTION 'Prueba 4 fallida: se aceptó una anulación con motivo insuficiente';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'Prueba 4 correcta (HU08): anulación sin motivo de 20 caracteres rechazada';
END $$;

DO $$
BEGIN
    UPDATE bitacora_auditoria SET motivo = 'Modificado' WHERE id_auditoria = 1;
    RAISE EXCEPTION 'Prueba 5 fallida: se modificó la bitácora de auditoría';
EXCEPTION WHEN restrict_violation THEN
    RAISE NOTICE 'Prueba 5 correcta (RNF-002): la bitácora de auditoría no admite cambios';
END $$;

DO $$
BEGIN
    INSERT INTO pacientes (tipo_documento, numero_documento, nombres, apellido_paterno, apellido_materno,
                           fecha_nacimiento, sexo, telefono, id_convenio)
    VALUES ('DNI', '45892014', 'Prueba', 'Duplicado', 'Paciente', '1990-01-01', 'F', '900000000', 1);
    RAISE EXCEPTION 'Prueba 6 fallida: se registró un paciente con documento duplicado';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Prueba 6 correcta (HU03): paciente con documento duplicado rechazado';
END $$;

DO $$
BEGIN
    INSERT INTO atencion_diagnosticos (id_atencion, codigo_cie10, tipo) VALUES (1, 'J06.9', 'PRINCIPAL');
    RAISE EXCEPTION 'Prueba 7 fallida: se aceptaron dos diagnósticos principales';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Prueba 7 correcta (HU04): segundo diagnóstico principal rechazado';
END $$;

DO $$
BEGIN
    INSERT INTO factura_detalle (id_factura, id_servicio, cantidad, precio_unitario, monto_cubierto, copago)
    VALUES (1, 4, 1, 15.00, 10.00, 2.00);
    RAISE EXCEPTION 'Prueba 8 fallida: se aceptaron montos que no cuadran';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'Prueba 8 correcta (RF-006): monto cubierto + copago distinto del precio rechazado';
END $$;

DO $$
BEGIN
    INSERT INTO tarifarios_servicios (id_servicio, id_convenio, precio_convenido, porcentaje_cobertura,
                                      copago_fijo, vigente_desde)
    VALUES (1, 3, 85.00, 80.00, 20.00, '2026-06-01');
    RAISE EXCEPTION 'Prueba 9 fallida: se aceptaron dos tarifas vigentes a la vez';
EXCEPTION WHEN exclusion_violation THEN
    RAISE NOTICE 'Prueba 9 correcta (RF-006): tarifa con vigencia superpuesta rechazada';
END $$;

DO $$
BEGIN
    INSERT INTO triajes (id_atencion, presion_sistolica, presion_diastolica, temperatura,
                         frecuencia_cardiaca, peso, talla, id_enfermera)
    VALUES (6, 80, 120, 36.5, 70, 60.00, 1.60, 9);
    RAISE EXCEPTION 'Prueba 10 fallida: se aceptó una presión sistólica menor que la diastólica';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'Prueba 10 correcta (HU05): signos vitales incoherentes rechazados';
END $$;
