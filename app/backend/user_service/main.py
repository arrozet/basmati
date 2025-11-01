"""
UserService - Servicio de gestión de usuarios.
Puerto: 8001
"""
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings

app = FastAPI(
    title="Basmati User Service",
    description="Servicio de gestión de usuarios y preferencias",
    version="1.0.0"
)

app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    """
    Verifica el estado del servicio de usuarios.
    
    Returns:
        dict: Estado del servicio
    """
    return {"status": "healthy", "service": "user-service", "port": settings.service_port}
