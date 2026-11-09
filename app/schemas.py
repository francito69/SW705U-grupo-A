"""Esquemas Pydantic de entrada y salida de la API."""

from pydantic import BaseModel, ConfigDict


class ConvenioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_convenio: int
    codigo_convenio: str
    nombre_institucion: str
    tipo_convenio: str
