"""
Gestión de conexión a MongoDB para el Event Service.

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
from repositories.event_repository import EventRepository


def get_event_repository(database = Depends(get_database)) -> EventRepository:
    """Proporciona una instancia de EventRepository.

    Args:
        database: Instancia de la base de datos inyectada por FastAPI

    Returns:
        EventRepository: Repository listo para operar sobre eventos
    """
    return EventRepository(database)

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "get_event_repository",
    "db"
]
