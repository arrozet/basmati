"""
Configuración específica del servicio de calendarios.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings

class CalendarServiceSettings(Settings):
    """Configuración específica del Calendar Service"""
    service_port: int = 8002
    service_name: str = "calendar-service"

# Instancia de configuración para este servicio
settings = CalendarServiceSettings()
