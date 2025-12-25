"""Configuración del API Gateway"""
from shared.config import Settings

class APIGatewaySettings(Settings):
    """Configuración específica del API Gateway"""
    service_port: int = 8000
    service_name: str = "api-gateway"
    auth_service_url: str = "http://auth-service:8005"
    enable_auth_middleware: bool = False  # Desactivado por defecto para desarrollo
    
    # Rutas que NO requieren autenticación
    public_routes: list[str] = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/v1/auth/",  # Todas las rutas de auth son públicas
    ]

# Instancia de configuración para este servicio
settings = APIGatewaySettings()

# Diccionario de servicios para usar en main.py
SERVICES = {
    "users": settings.user_service_url,
    "calendars": settings.calendar_service_url,
    "events": settings.event_service_url,
    "notifications": settings.notification_service_url,
    "integrations": settings.integration_service_url,
    "auth": settings.auth_service_url,
}
