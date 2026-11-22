from pydantic import BaseModel, Field


class LoginEntrada(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=72)


class MedicoSesion(BaseModel):
    id_medico: int
    nombre_completo: str
    especialidad: str
    cmp: str


class UsuarioSesion(BaseModel):
    id_usuario: int
    username: str
    email: str
    rol: str
    medico: MedicoSesion | None = None


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en: int = Field(description="Segundos de vigencia del token")
    usuario: UsuarioSesion


class CuentaDemo(BaseModel):
    username: str
    rol: str
    descripcion: str


class CuentasDemo(BaseModel):
    password: str
    cuentas: list[CuentaDemo]
