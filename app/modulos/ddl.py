"""DDL que replica database/01-esquema.sql y que el ORM no expresa por sí solo.

En PostgreSQL: extensión btree_gist (para las restricciones EXCLUDE), funciones y
triggers que prohíben el borrado físico (RNF-004). En SQLite se crean triggers
equivalentes para que las pruebas verifiquen la misma regla.
"""

from sqlalchemy import DDL, Index, event, text

from app.database import Base

from .auditoria.models import BitacoraAuditoria
from .notificaciones.models import OutboxNotificacion

Index(
    "idx_outbox_pendientes",
    OutboxNotificacion.programado_para,
    postgresql_where=text("estado = 'PENDIENTE'"),
    sqlite_where=text("estado = 'PENDIENTE'"),
)
Index("idx_auditoria_usuario_fecha", BitacoraAuditoria.id_usuario, BitacoraAuditoria.fecha_hora.desc())

TABLAS_SIN_BORRADO = {
    "pacientes": "trg_pacientes_sin_borrado",
    "atenciones": "trg_atenciones_sin_borrado",
    "triajes": "trg_triajes_sin_borrado",
    "atencion_diagnosticos": "trg_diagnosticos_sin_borrado",
    "prescripciones": "trg_prescripciones_sin_borrado",
}

FUNCION_IMPEDIR_BORRADO = """
CREATE OR REPLACE FUNCTION impedir_borrado() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION USING
        MESSAGE = 'No se permite eliminar registros de ' || TG_TABLE_NAME
                  || ': use la anulación lógica (RNF-004)',
        ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql
"""

FUNCION_BITACORA_INMUTABLE = """
CREATE OR REPLACE FUNCTION impedir_cambios_bitacora() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION USING
        MESSAGE = 'La bitácora de auditoría es inmutable: no admite ' || TG_OP,
        ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql
"""

event.listen(
    Base.metadata,
    "before_create",
    DDL("CREATE EXTENSION IF NOT EXISTS btree_gist").execute_if(dialect="postgresql"),
)
event.listen(Base.metadata, "before_create", DDL(FUNCION_IMPEDIR_BORRADO).execute_if(dialect="postgresql"))
event.listen(
    Base.metadata, "before_create", DDL(FUNCION_BITACORA_INMUTABLE).execute_if(dialect="postgresql")
)

for _tabla, _trigger in TABLAS_SIN_BORRADO.items():
    _objeto = Base.metadata.tables[_tabla]
    event.listen(
        _objeto,
        "after_create",
        DDL(
            f"CREATE TRIGGER {_trigger} BEFORE DELETE ON {_tabla} "
            "FOR EACH ROW EXECUTE FUNCTION impedir_borrado()"
        ).execute_if(dialect="postgresql"),
    )
    event.listen(
        _objeto,
        "after_create",
        DDL(
            f"CREATE TRIGGER {_trigger} BEFORE DELETE ON {_tabla} BEGIN "
            f"SELECT RAISE(ABORT, 'No se permite eliminar registros de {_tabla}: "
            "use la anulación lógica (RNF-004)'); END"
        ).execute_if(dialect="sqlite"),
    )

_bitacora = BitacoraAuditoria.__table__
event.listen(
    _bitacora,
    "after_create",
    DDL(
        "CREATE TRIGGER trg_bitacora_inmutable BEFORE UPDATE OR DELETE ON bitacora_auditoria "
        "FOR EACH ROW EXECUTE FUNCTION impedir_cambios_bitacora()"
    ).execute_if(dialect="postgresql"),
)
for _operacion in ("UPDATE", "DELETE"):
    event.listen(
        _bitacora,
        "after_create",
        DDL(
            f"CREATE TRIGGER trg_bitacora_inmutable_{_operacion.lower()} BEFORE {_operacion} "
            "ON bitacora_auditoria BEGIN SELECT RAISE(ABORT, 'La bitácora de auditoría es "
            f"inmutable: no admite {_operacion}'); END"
        ).execute_if(dialect="sqlite"),
    )
