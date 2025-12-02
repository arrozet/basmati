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
from repositories.geocode_cache_repository import GeocodeCacheRepository

# Reexportar las funciones centralizadas
__all__ = [
    "connect_to_mongo",
    "close_mongo_connection", 
    "get_database",
    "db",
    "get_integration_repository",
    "get_geocode_cache_repository",
    "initialize_geocode_cache_indexes"
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


async def get_geocode_cache_repository() -> GeocodeCacheRepository:
    """
    Proporciona una instancia de GeocodeCacheRepository.
    
    Returns:
        GeocodeCacheRepository: Repository de caché de geocodificación
    """
    database = get_database()
    return GeocodeCacheRepository(database)


async def initialize_geocode_cache_indexes() -> None:
    """
    Inicializa los índices necesarios para el caché de geocodificación.
    
    Debe llamarse al iniciar la aplicación para asegurar que los índices
    existan antes de usar el caché. Incluye:
    - Índice único en cache_key
    - Índice TTL para expiración automática
    - Índice en query_type para estadísticas
    """
    database = get_database()
    cache_repo = GeocodeCacheRepository(database)
    await cache_repo.ensure_indexes()
