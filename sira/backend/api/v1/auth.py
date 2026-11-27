from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend import seed
from backend.core.config import config
from backend.core.errores import NoEncontrado, Prohibido
from backend.database import get_db
from backend.modulos.agenda import service as agenda
from backend.modulos.auditoria import service as auditoria
from backend.modulos.seguridad import service as seguridad
from backend.modulos.seguridad.dependencias import Contexto, contexto_actual, ip_cliente
from backend.modulos.seguridad.models import Usuario
from backend.modulos.seguridad.schemas import (
    CuentaDemo,
    CuentasDemo,
    LoginEntrada,
    MedicoSesion,
    TokenSalida,
    UsuarioSesion,
)

router = APIRouter(prefix="/auth", tags=["T1 · Autenticación"])


def usuario_sesion(db: Session, usuario: Usuario) -> UsuarioSesion:
    medico = agenda.medico_de_usuario(db, usuario.id_usuario)
    return UsuarioSesion(
        id_usuario=usuario.id_usuario,
        username=usuario.username,
        email=usuario.email,
        rol=usuario.rol.nombre,
        medico=MedicoSesion(
            id_medico=medico.id_medico,
            nombre_completo=medico.nombre_completo,
            especialidad=medico.especialidad.nombre,
            cmp=medico.cmp,
        )
        if medico
        else None,
    )


@router.post(
    "/login",
    response_model=TokenSalida,
    summary="Iniciar sesión y obtener el token JWT",
    responses={401: {"description": "Usuario o contraseña incorrectos"}, 403: {"description": "Usuario inactivo"}},
)
def login(datos: LoginEntrada, request: Request, db: Session = Depends(get_db)):
    usuario = seguridad.buscar_por_username(db, datos.username)
    if usuario is None or not seguridad.verificar_password(datos.password, usuario.password_hash):
        if usuario is not None:
            auditoria.registrar(
                db,
                Contexto(usuario=usuario, ip=ip_cliente(request)),
                "usuarios",
                usuario.id_usuario,
                "ACCESO_DENEGADO",
                motivo="Intento de inicio de sesión con contraseña incorrecta",
            )
            db.commit()
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    if not usuario.activo:
        raise Prohibido("El usuario está inactivo")
    return TokenSalida(
        access_token=seguridad.crear_token(usuario),
        expira_en=config.token_minutos * 60,
        usuario=usuario_sesion(db, usuario),
    )


@router.get("/me", response_model=UsuarioSesion, summary="Datos del usuario autenticado")
def usuario_actual(ctx: Contexto = Depends(contexto_actual), db: Session = Depends(get_db)):
    return usuario_sesion(db, ctx.usuario)


@router.get(
    "/demo",
    response_model=CuentasDemo,
    summary="Cuentas ficticias para la demostración",
    responses={404: {"description": "Modo demostración desactivado"}},
)
def cuentas_demo():
    if not config.modo_demo:
        raise NoEncontrado("El modo demostración está desactivado")
    return CuentasDemo(
        password=seed.PASSWORD_DEMO,
        cuentas=[CuentaDemo(username=u, rol=r, descripcion=d) for u, r, d in seed.CUENTAS_DEMO],
    )
