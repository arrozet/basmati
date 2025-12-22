"""Configuración centralizada para todos los microservicios"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Configuración de la aplicación compartida entre todos los microservicios.
    
    Las variables de entorno se cargan desde el archivo .env en la raíz del proyecto.
    Cada microservicio puede sobrescribir SERVICE_PORT según su puerto específico.
    
    NOTA: En producción (AWS Lambda), mongo_uri se obtiene de AWS Secrets Manager
    automáticamente mediante shared.secrets.get_mongo_uri()
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
    integration_service_url: str = "http://integration-service:8006"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_mongo_uri_with_fallback(self) -> Optional[str]:
        """
        Obtiene el URI de MongoDB con fallback a Secrets Manager
        
        Returns:
            URI de MongoDB desde variable de entorno o Secrets Manager
        """
        if self.mongo_uri:
            return self.mongo_uri
        
        # En producción (Lambda), intentar obtener desde Secrets Manager
        if os.environ.get('AWS_EXECUTION_ENV'):  # Detecta si está en Lambda
            try:
                from shared.secrets import get_mongo_uri
                return get_mongo_uri()
            except Exception as e:
                print(f"Error obteniendo mongo_uri desde Secrets Manager: {e}")
                return None
        
        return None

# Instancia global de configuración
settings = Settings()
