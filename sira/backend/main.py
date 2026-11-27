import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import modulos  # noqa: F401  (registra todos los modelos)
from .api.v1 import api_router
from .core.config import config
from .core.errores import registrar_manejadores
from .database import Base, SessionLocal, engine
from .modulos.notificaciones import worker
from .seed import sembrar

_registro = logging.getLogger("sira")
if not _registro.handlers:
    _salida = logging.StreamHandler()
    _salida.setFormatter(logging.Formatter("%(levelname)s:     %(name)s - %(message)s"))
    _registro.addHandler(_salida)
    _registro.setLevel(logging.INFO)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        sembrar(db, demo=config.modo_demo)
    tarea = asyncio.create_task(worker.bucle(config.worker_segundos)) if config.worker_activo else None
    yield
    if tarea is not None:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea


app = FastAPI(
    title="SIRA — API de la Clínica San Rafael S.A.C.",
    description="Sistema de Información Clínico-Administrativo (SW705, Grupo A). "
    "Incremento del Sprint 1: M1 Historia clínica y triaje, M2 Agenda y citas. "
    "Solo datos ficticios. Use POST /api/v1/auth/login y el botón Authorize con el token.",
    version="0.2.0",
    lifespan=lifespan,
)
registrar_manejadores(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(config.cors_origenes),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/salud", tags=["Sistema"], summary="Verificar que la API responde")
def salud():
    return {"estado": "ok"}


if FRONTEND.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def frontend(ruta: str):
        if ruta.startswith(("api/", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        archivo = FRONTEND / ruta
        if ruta and archivo.is_file() and FRONTEND in archivo.resolve().parents:
            return FileResponse(archivo)
        return FileResponse(FRONTEND / "index.html")
