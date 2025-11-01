"""SearchService - Puerto: 8005"""
from fastapi import FastAPI
from api.v1.router import api_router
from core.config import settings

app = FastAPI(title="Basmati Search Service", version="1.0.0")
app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "search-service", "port": settings.service_port}
