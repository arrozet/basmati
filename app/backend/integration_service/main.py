"""IntegrationService - Puerto: 8006"""
from fastapi import FastAPI
from api.v1.router import api_router as api_router_v1
from api.v2.router import api_router as api_router_v2
from core.config import settings
from core.database import (
    connect_to_mongo, 
    close_mongo_connection,
    initialize_geocode_cache_indexes
)

# Metadata de tags para organizar la documentación
tags_metadata = [
    {
        "name": "Integration: Imports",
        "description": "Importación de calendarios desde servicios externos (Google Calendar, Teamup).",
    },
    {
        "name": "Integration: OpenStreetMap",
        "description": "Geocodificación y búsqueda de lugares usando OpenStreetMap/Nominatim con caché.",
    },
    {
        "name": "Integration: S3 Images",
        "description": "Gestión de imágenes en AWS S3 con compresión automática.",
    },
]

app = FastAPI(
    title="Basmati Integration Service",
    version="1.0.0",
    openapi_tags=tags_metadata
)
app.include_router(api_router_v1, prefix="/v1")
app.include_router(api_router_v2, prefix="/v2")

@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio: conecta a MongoDB e inicializa índices.
    
    Inicializa los índices del caché de geocodificación para asegurar
    que el TTL y las búsquedas funcionen correctamente.
    """
    await connect_to_mongo()
    await initialize_geocode_cache_indexes()

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre: desconecta de MongoDB"""
    await close_mongo_connection()

# Lambda handler usando Mangum
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum no disponible en desarrollo local
    handler = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "integration-service", "port": settings.service_port}
