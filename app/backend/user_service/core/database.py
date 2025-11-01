"""
Gestión de conexión a MongoDB para el User Service.

Reutiliza la lógica centralizada de shared.database pero
permite sobrescrituras específicas del servicio si es necesario.
"""
from shared.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    db
)
from repositories.user_repository import UserRepository

# Función de inyección de dependencias para UserRepository
def get_user_repository(database = get_database()) -> UserRepository:
    """
    Proporciona una instancia de UserRepository.
    
    Args:
        database: Instancia de base de datos (inyectada por FastAPI)
        
    Returns:
        UserRepository: Repository para usuarios
    """
    return UserRepository(database)

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "get_user_repository",
    "db"
]
