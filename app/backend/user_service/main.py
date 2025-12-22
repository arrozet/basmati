"""
UserService - Servicio de gestión de usuarios.
Puerto: 8001
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.v1.router import api_router
from api.v2.router import api_router as api_router_v2
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
    title="Basmati User Service",
    description="Servicio de gestión de usuarios y preferencias",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/v1")
app.include_router(api_router_v2, prefix="/v2")

@app.get("/health")
async def health_check():
    """
    Verifica el estado del servicio de usuarios.
    
    Returns:
        dict: Estado del servicio
    """
    return {"status": "healthy", "service": "user-service", "port": settings.service_port}

# Lambda handler usando Mangum
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum no disponible en desarrollo local
    handler = None
