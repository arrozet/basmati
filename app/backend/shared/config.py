"""Configuración centralizada para todos los microservicios"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Configuración de la aplicación compartida entre todos los microservicios.
    
    Las variables de entorno se cargan desde el archivo .env en la raíz del proyecto.
    Cada microservicio puede sobrescribir SERVICE_PORT según su puerto específico.
    """
    # MongoDB
    mongo_uri: Optional[str] = None
    database_name: str = "basmati"
    
    # Servicio
    service_port: int = 8000
    service_name: str = "microservice"
    environment: str = "development"
    
    # URLs de otros servicios (para comunicación inter-servicio)
    user_service_url: str = "http://user-service:8001"
    calendar_service_url: str = "http://calendar-service:8002"
    event_service_url: str = "http://event-service:8003"
    notification_service_url: str = "http://notification-service:8004"
    search_service_url: str = "http://search-service:8005"
    integration_service_url: str = "http://integration-service:8006"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()
