"""NotificationService - Puerto: 8004"""
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Basmati Notification Service", version="1.0.0")
app.include_router(api_router, prefix="/v1")

@app.on_event("startup")
async def startup_event():
    """Evento de inicio: conecta a MongoDB"""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre: desconecta de MongoDB"""
    await close_mongo_connection()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service", "port": settings.service_port}
