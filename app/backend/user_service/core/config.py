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
    
    # Emails de usuarios de desarrollo (configurables desde .env)
    dev_user_1_email: str = "amcgil@uma.es"
    dev_user_2_email: str = "rubenoliva@uma.es"
    dev_user_3_email: str = "daily_digest_test@example.com"

# Instancia de configuración para este servicio
settings = UserServiceSettings()
