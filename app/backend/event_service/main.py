"""
EventService - Servicio de gestión de eventos.
Puerto: 8003
TODO: Implementar por compañeros
"""
from fastapi import FastAPI

app = FastAPI(
    title="Basmati Event Service",
    description="Servicio de gestión de eventos, comentarios y adjuntos",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Verifica el estado del servicio de eventos"""
    return {"status": "healthy", "service": "event-service"}
