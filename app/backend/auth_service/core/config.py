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
    google_redirect_uri: str = "http://localhost:8000/v1/auth/google/callback"
    
    # JWT para tokens propios de sesión
    jwt_secret_key: str = "basmati-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 días
    
    # URLs de otros servicios
    user_service_url: str = "http://user-service:8001"
    frontend_url: str = "http://localhost:5173"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Instancia global de configuración
settings = Settings()
