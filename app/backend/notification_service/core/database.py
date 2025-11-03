"""
Gestión de conexión a MongoDB para el Notification Service.

Reutiliza la lógica centralizada de shared.database pero
permite sobrescrituras específicas del servicio si es necesario.
"""
from fastapi import Depends
from shared.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    db
)
from repositories.notification_repository import NotificationRepository

# Función de inyección de dependencias para NotificationRepository
def get_notification_repository(database = Depends(get_database)) -> NotificationRepository:
    """
    Proporciona una instancia de NotificationRepository.
    
    Args:
        database: Instancia de base de datos (inyectada por FastAPI)
        
    Returns:
        NotificationRepository: Repository para notificaciones
    """
    return NotificationRepository(database)

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "get_notification_repository",
    "db"
]
