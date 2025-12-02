"""Router principal de la API v2 del Event Service.

Solo incluye los endpoints que tienen CAMBIOS respecto a v1.
Para endpoints sin cambios, usar /v1/.

Mejoras V2:
- Filtro opcional por calendar_id en búsqueda por fechas
- Compatibilidad con datos legacy (ObjectId + String)
"""
from fastapi import APIRouter, Depends

from api.v2.events import create_v2_events_router
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


# Crear router usando SOLO los endpoints específicos de V2
api_router = APIRouter()
events_router = create_v2_events_router(get_event_service_v2)
api_router.include_router(events_router, prefix="/events", tags=["events-v2"])
