"""
Configuración del servicio de autenticación.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de autenticación cargada desde variables de entorno.
    
    Incluye credenciales OAuth de Google y configuración JWT para
    generar y validar tokens de sesión propios.
    """
    # Servicio
    service_port: int = 8005
    service_name: str = "auth-service"
    environment: str = "development"
    
    # MongoDB
    mongo_uri: str | None = None
    database_name: str = "basmati"
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # URL dinámica del API Gateway (se obtiene de variable de entorno en Lambda)
    api_gateway_url: str = "http://api-gateway:8000"
    
    # Computed property para redirect_uri
    @property
    def google_redirect_uri(self) -> str:
        """Construye la URL de callback de Google OAuth"""
        return f"{self.api_gateway_url}/v1/auth/google/callback"
    
    # JWT para tokens propios de sesión
    jwt_secret_key: str = "basmati-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 días
    
    # URLs de otros servicios
    # En Lambda, user_service se invoca a través del API Gateway
    user_service_url: str = "http://user-service:8001"
    
    # Computed property para obtener la URL correcta según el entorno
    @property
    def effective_user_service_url(self) -> str:
        """
        Retorna la URL correcta del user service.
        En Lambda usa API Gateway, en desarrollo usa el servicio directo.
        """
        # Si estamos en Lambda (API_GATEWAY_URL está definido), usar API Gateway
        if self.api_gateway_url.startswith("https://"):
            return self.api_gateway_url
        # En desarrollo local, usar el servicio directo
        return self.user_service_url
    
    # URL del frontend (se obtiene de variable de entorno en Lambda)
    frontend_url: str = "http://localhost:5173"
    
    # CORS
    cors_origins: str = "*"  # En desarrollo permite todos. En producción usar lista separada por comas
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Instancia global de configuración
settings = Settings()

# Validación de seguridad: prevenir uso de clave secreta por defecto en producción
DEFAULT_SECRET_KEY = "basmati-secret-key-change-in-production"
if settings.environment == "production" and settings.jwt_secret_key == DEFAULT_SECRET_KEY:
    raise ValueError(
        "❌ ERROR DE SEGURIDAD: No se puede usar la clave secreta JWT por defecto en producción. "
        "Configure JWT_SECRET_KEY con una clave segura mediante variable de entorno."
    )
