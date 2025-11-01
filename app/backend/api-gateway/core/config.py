"""Configuración del API Gateway"""
from shared.config import Settings

class APIGatewaySettings(Settings):
    """Configuración específica del API Gateway"""
    service_port: int = 8000
    service_name: str = "api-gateway"

# Instancia de configuración para este servicio
settings = APIGatewaySettings()

# Diccionario de servicios para usar en main.py
SERVICES = {
    "users": settings.user_service_url,
    "calendars": settings.calendar_service_url,
    "events": settings.event_service_url,
    "notifications": settings.notification_service_url,
    "search": settings.search_service_url,
    "integrations": settings.integration_service_url,
}
