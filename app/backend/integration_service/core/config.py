"""
Configuración específica del servicio de integraciones.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings
from typing import Optional

class IntegrationServiceSettings(Settings):
    """Configuración específica del Integration Service"""
    service_port: int = 8006
    service_name: str = "integration-service"
    google_calendar_api_key: Optional[str] = None
    teamup_api_key: Optional[str] = None
    
    # URLs de otros servicios (necesarios para este servicio)
    CALENDAR_SERVICE_URL: str = "http://calendar-service:8002"
    EVENT_SERVICE_URL: str = "http://event-service:8003"
    USER_SERVICE_URL: str = "http://user-service:8001"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8004"
    
    # URLs accesibles por los aliases usados en el código
    user_service_url: str = "http://user-service:8001"
    notification_service_url: str = "http://notification-service:8004"
    
    # URL del frontend para enlaces en emails
    frontend_url: str = "http://localhost:3000"
    
    # Configuración de AWS S3 para almacenamiento de imágenes
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "eu-north-1"
    aws_s3_bucket_name: str | None = None
    
    # Configuración de SendGrid para envío de correos
    sendgrid_api_key: str | None = None
    sender_email: str = "amcgil+noreply-basmati@uma.es"

# Instancia de configuración para este servicio
settings = IntegrationServiceSettings()
