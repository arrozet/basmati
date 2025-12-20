"""Router principal de la API v2 del Calendar Service.

Solo incluye los endpoints que tienen CAMBIOS respecto a v1.
Para endpoints sin cambios, usar /v1/.

Mejoras V2:
- Nuevo endpoint get_all_calendars
- Nuevo endpoint delete_calendar_recursive
"""
from fastapi import APIRouter, Depends

from api.v2.endpoints.calendars import create_v2_calendars_router
from core.database import get_database
from core.factory import CalendarServiceFactoryV2
from core.interface import ICalendarService


async def get_calendar_service_v2(db=Depends(get_database)) -> ICalendarService:
    """Proporciona una instancia de CalendarService V2.
    
    Usa la fábrica V2 para crear el servicio con su repositorio correspondiente.
    
    Args:
        db: Base de datos (inyectada por FastAPI)
        
    Returns:
        ICalendarService: Instancia del servicio V2
    """
    factory = CalendarServiceFactoryV2(db)
    return factory.create_service()


# Crear router usando SOLO los endpoints específicos de V2
api_router = APIRouter()
calendars_router = create_v2_calendars_router(get_calendar_service_v2)
api_router.include_router(calendars_router, prefix="/calendars", tags=["calendars-v2"])


