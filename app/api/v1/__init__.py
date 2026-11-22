"""API REST versionada /api/v1 (SAD 5.2.1, capa de aplicación)."""

from fastapi import APIRouter

from . import atenciones, auth, catalogos, citas, pacientes

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(pacientes.router)
api_router.include_router(atenciones.router)
api_router.include_router(citas.router)
api_router.include_router(catalogos.router_convenios)
api_router.include_router(catalogos.router_auditoria)
api_router.include_router(catalogos.router_notificaciones)
