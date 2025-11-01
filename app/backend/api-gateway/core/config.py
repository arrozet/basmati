"""Configuración del API Gateway"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    service_port: int = 8000
    user_service_url: str = "http://user-service:8001"
    calendar_service_url: str = "http://calendar-service:8002"
    event_service_url: str = "http://event-service:8003"
    notification_service_url: str = "http://notification-service:8004"
    search_service_url: str = "http://search-service:8005"
    integration_service_url: str = "http://integration-service:8006"
    
    class Config:
        env_file = ".env"

settings = Settings()
