"""Router principal de la API v2 del Event Service.

Utiliza el patrón Abstract Factory para crear el servicio correspondiente
a esta versión, eliminando duplicación de código con otras versiones.

Mejoras V2:
- Compatibilidad con datos legacy (ObjectId + String)
- Filtro opcional por calendar_id en búsqueda por fechas
"""
from fastapi import APIRouter, Depends

from api.endpoints.events import create_events_router
from core.database import get_database
from core.factory import EventServiceFactoryV2
from core.interface import IEventService


async def get_event_service_v2(db=Depends(get_database)) -> IEventService:
    """Proporciona una instancia de EventService V2.
    
    Usa la fábrica V2 para crear el servicio con su repositorio correspondiente.
    
    Args:
        db: Base de datos (inyectada por FastAPI)
        
    Returns:
        IEventService: Instancia del servicio V2
    """
    factory = EventServiceFactoryV2(db)
    return factory.create_service()


# Crear router usando la función factory con la dependencia V2
api_router = APIRouter()
events_router = create_events_router(get_event_service_v2)
api_router.include_router(events_router, prefix="/events", tags=["events-v2"])
