"""
Configuración específica del servicio de usuarios.

Hereda la configuración centralizada de shared.config.Settings
y permite sobrescribir valores específicos para este microservicio.
"""
from shared.config import Settings

class UserServiceSettings(Settings):
    """Configuración específica del User Service"""
    service_port: int = 8001
    service_name: str = "user-service"

# Instancia de configuración para este servicio
settings = UserServiceSettings()
