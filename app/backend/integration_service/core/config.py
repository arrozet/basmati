"""Configuración del servicio de integraciones"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    mongo_uri: str
    service_port: int = 8006
    database_name: str = "basmati"
    calendar_service_url: str = "http://calendar-service:8002"
    event_service_url: str = "http://event-service:8003"
    google_calendar_api_key: str = ""
    teamup_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
