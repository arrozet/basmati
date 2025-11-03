"""
Gestión de conexión a MongoDB para el Integration Service.

Reutiliza la lógica centralizada de shared.database pero
permite sobrescrituras específicas del servicio si es necesario.
"""
from shared.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    db
)
from repositories.integration_repository import IntegrationRepository

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "db",
    "get_integration_repository"
]

# Dependency para FastAPI
async def get_integration_repository() -> IntegrationRepository:
    """
    Proporciona una instancia de IntegrationRepository.
    
    Returns:
        IntegrationRepository: Repository de fuentes de integración
    """
    database = get_database()
    return IntegrationRepository(database)
