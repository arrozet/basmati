"""NotificationService - Puerto: 8004"""
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings

app = FastAPI(title="Basmati Notification Service", version="1.0.0")
app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service", "port": settings.service_port}
