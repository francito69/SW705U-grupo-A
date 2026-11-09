import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, SessionLocal, engine
from .routers import convenios
from .seed import sembrar_convenios


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        sembrar_convenios(db)
    yield


app = FastAPI(
    title="SIRA — API de la Clínica San Rafael S.A.C.",
    description="Sistema de Información Clínico-Administrativo (SW705, Grupo A). "
    "Solo datos ficticios.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(convenios.router)


@app.get("/salud", tags=["Sistema"], summary="Verificar que la API responde")
def salud():
    return {"estado": "ok"}
