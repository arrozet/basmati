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

# Instancia de configuración para este servicio
settings = IntegrationServiceSettings()
