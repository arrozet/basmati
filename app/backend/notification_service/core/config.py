"""
Configuración específica del servicio de notificaciones.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings
from typing import Optional

class NotificationServiceSettings(Settings):
    """Configuración específica del Notification Service"""
    service_port: int = 8004
    service_name: str = "notification-service"
    email_service_api_key: Optional[str] = None

# Instancia de configuración para este servicio
settings = NotificationServiceSettings()
