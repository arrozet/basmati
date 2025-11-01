"""Configuración del servicio de usuarios"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    mongo_uri: str
    service_port: int = 8001
    database_name: str = "basmati"
    
    class Config:
        env_file = ".env"

settings = Settings()
