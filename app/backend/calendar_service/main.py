"""
CalendarService - Servicio de gestión de calendarios.
Puerto: 8002
TODO: Implementar por compañeros
"""
from fastapi import FastAPI

app = FastAPI(
    title="Basmati Calendar Service",
    description="Servicio de gestión de calendarios y jerarquías",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Verifica el estado del servicio de calendarios"""
    return {"status": "healthy", "service": "calendar-service"}
