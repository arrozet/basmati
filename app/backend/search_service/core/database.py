"""
Gestión de conexión a MongoDB para el Search Service.

Reutiliza la lógica centralizada de shared.database pero
permite sobrescrituras específicas del servicio si es necesario.
"""
from shared.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    db
)

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "db"
]
