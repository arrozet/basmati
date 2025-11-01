"""
Configuración específica del servicio de eventos.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings

class EventServiceSettings(Settings):
    """Configuración específica del Event Service"""
    service_port: int = 8003
    service_name: str = "event-service"

# Instancia de configuración para este servicio
settings = EventServiceSettings()
