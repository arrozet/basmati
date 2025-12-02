"""Router principal de la API v1 del Event Service.

Utiliza el patrón Abstract Factory para crear el servicio correspondiente
a esta versión, eliminando duplicación de código con otras versiones.
"""
from fastapi import APIRouter, Depends

from api.endpoints.events import create_events_router
from core.database import get_database
from core.factory import EventServiceFactoryV1
from core.interface import IEventService


async def get_event_service_v1(db=Depends(get_database)) -> IEventService:
    """Proporciona una instancia de EventService V1.
    
    Usa la fábrica V1 para crear el servicio con su repositorio correspondiente.
    
    Args:
        db: Base de datos (inyectada por FastAPI)
        
    Returns:
        IEventService: Instancia del servicio V1
    """
    factory = EventServiceFactoryV1(db)
    return factory.create_service()


# Crear router usando la función factory con la dependencia V1
api_router = APIRouter()
events_router = create_events_router(get_event_service_v1)
api_router.include_router(events_router, prefix="/events", tags=["events-v1"])
