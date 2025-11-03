"""
Gestión de conexión a MongoDB para el Calendar Service.

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
from repositories.calendar_repository import CalendarRepository

# Función de inyección de dependencias para CalendarRepository
def get_calendar_repository(database = Depends(get_database)) -> CalendarRepository:
    """
    Proporciona una instancia de CalendarRepository.
    
    Args:
        database: Instancia de base de datos (inyectada por FastAPI)
        
    Returns:
        CalendarRepository: Repository para calendarios
    """
    return CalendarRepository(database)

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "get_calendar_repository",
    "db"
]
