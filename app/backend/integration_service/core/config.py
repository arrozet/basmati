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
    
    # Configuración de AWS S3 para almacenamiento de imágenes
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    aws_s3_bucket_name: str | None = None

# Instancia de configuración para este servicio
settings = IntegrationServiceSettings()
