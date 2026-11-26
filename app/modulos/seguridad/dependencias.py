"""Middleware RBAC (ADR-03): cada endpoint declara qué roles lo pueden usar."""

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errores import Prohibido
from app.database import get_db
from app.modulos.auditoria import service as auditoria

from . import service
from .models import Usuario

esquema_bearer = HTTPBearer(auto_error=False, description="Token JWT obtenido en /api/v1/auth/login")

ROLES_CLINICOS = ("MEDICO", "ENFERMERA")


@dataclass
class Contexto:
    usuario: Usuario
    ip: str

    @property
    def id_usuario(self) -> int:
        return self.usuario.id_usuario

    @property
    def rol(self) -> str:
        return self.usuario.rol.nombre

    @property
    def es_clinico(self) -> bool:
        return self.rol in ROLES_CLINICOS


def ip_cliente(request: Request) -> str:
    return auditoria.ip_valida(request.client.host if request.client else None)


def _no_autenticado(mensaje: str) -> HTTPException:
    return HTTPException(status_code=401, detail=mensaje, headers={"WWW-Authenticate": "Bearer"})


def contexto_actual(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Contexto:
    if credenciales is None:
        raise _no_autenticado("Debe iniciar sesión")
    try:
        datos = service.leer_token(credenciales.credentials)
    except jwt.ExpiredSignatureError:
        raise _no_autenticado("La sesión expiró, vuelva a iniciar sesión") from None
    except jwt.InvalidTokenError:
        raise _no_autenticado("Token no válido") from None
    usuario = db.get(Usuario, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise _no_autenticado("Usuario no válido o inactivo")
    return Contexto(usuario=usuario, ip=ip_cliente(request))


def requiere_roles(*roles: str, tabla: str | None = None, parametro_id: str | None = None):
    """Devuelve una dependencia que responde 403 si el rol no está permitido.

    Si se indica la tabla, el intento denegado queda en la bitácora (HU01, escenario 2).
    """

    def dependencia(
        request: Request,
        ctx: Contexto = Depends(contexto_actual),
        db: Session = Depends(get_db),
    ) -> Contexto:
        if ctx.rol in roles:
            return ctx
        if tabla:
            valor = request.path_params.get(parametro_id or "", 0)
            auditoria.registrar(
                db,
                ctx,
                tabla,
                int(valor) if str(valor).isdigit() else 0,
                "ACCESO_DENEGADO",
                motivo=f"Rol {ctx.rol} sin permiso para {request.method} {request.url.path}",
            )
            db.commit()
        raise Prohibido(f"Acceso denegado: el rol {ctx.rol} no tiene permiso para esta operación")

    return dependencia
