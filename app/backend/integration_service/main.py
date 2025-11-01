"""IntegrationService - Puerto: 8006"""
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings

app = FastAPI(title="Basmati Integration Service", version="1.0.0")
app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "integration-service", "port": settings.service_port}
