"""
NotificationService - Servicio de gestión de notificaciones.
Puerto: 8004
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación.
    
    Startup: Conecta a MongoDB
    Shutdown: Desconecta de MongoDB
    """
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Basmati Notification Service",
    description="Servicio de gestión de notificaciones y alertas",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    """
    Verifica el estado del servicio de notificaciones.
    
    Returns:
        dict: Estado del servicio
    """
    return {"status": "healthy", "service": "notification-service", "port": settings.service_port}

# Lambda handler usando Mangum
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum no disponible en desarrollo local
    handler = None

