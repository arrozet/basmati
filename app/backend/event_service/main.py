"""Punto de entrada del Event Service"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.router import api_router
from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación.

    Startup: conecta con MongoDB
    Shutdown: cierra la conexión
    """

    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Basmati Event Service",
    description="Servicio de gestión de eventos, comentarios y adjuntos",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(api_router, prefix="/v1")


@app.get("/health")
async def health_check():
    """Verifica el estado del servicio de eventos"""
    return {
        "status": "healthy",
        "service": "event-service",
        "port": settings.service_port,
    }
