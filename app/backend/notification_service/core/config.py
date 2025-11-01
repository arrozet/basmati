"""Configuración del servicio de notificaciones"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    mongo_uri: str
    service_port: int = 8004
    database_name: str = "basmati"
    user_service_url: str = "http://user-service:8001"
    email_service_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
