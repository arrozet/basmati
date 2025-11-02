"""
Configuración específica del servicio de búsqueda.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings

class SearchServiceSettings(Settings):
    """
    Configuración específica del Search Service.
    
    Define las variables de entorno necesarias para el servicio de búsqueda,
    incluyendo conexiones a otros microservicios.
    """
    service_port: int = 8005
    service_name: str = "search-service"
    
    # URLs de otros microservicios (para futuras integraciones)
    calendar_service_url: str = "http://calendar-service:8002"
    event_service_url: str = "http://event-service:8003"
    
    # Configuración de la API
    project_name: str = "Search Service"
    api_v1_str: str = "/api/v1"

# Instancia de configuración para este servicio
settings = SearchServiceSettings()
