"""
Configuración específica del servicio de búsqueda.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings

class SearchServiceSettings(Settings):
    """Configuración específica del Search Service"""
    service_port: int = 8005
    service_name: str = "search-service"

# Instancia de configuración para este servicio
settings = SearchServiceSettings()
