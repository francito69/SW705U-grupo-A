from datetime import datetime

from pydantic import BaseModel


class RegistroAuditoria(BaseModel):
    id_auditoria: int
    fecha_hora: datetime
    id_usuario: int
    username: str
    rol: str
    accion: str
    nombre_tabla: str
    id_registro_afectado: int
    direccion_ip: str
    datos_anteriores: dict | None
    datos_nuevos: dict | None
    motivo: str | None


class PaginaAuditoria(BaseModel):
    total: int
    registros: list[RegistroAuditoria]
