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
    
    # URLs de otros servicios (necesarios para este servicio)
    notification_service_url: str = "http://notification-service:8004"
    user_service_url: str = "http://user-service:8001"
    integration_service_url: str = "http://integration-service:8006"
    calendar_service_url: str = "http://calendar-service:8002"

# Instancia de configuración para este servicio
settings = EventServiceSettings()
