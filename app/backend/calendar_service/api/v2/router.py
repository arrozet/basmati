"""Router principal de la API v2 del Calendar Service."""
from fastapi import APIRouter, Depends
from api.endpoints.calendars import create_calendars_router
from core.database import get_database
from core.factory import CalendarServiceFactoryV2
from core.interface import ICalendarService

async def get_calendar_service_v2(db=Depends(get_database)) -> ICalendarService:
    """Proporciona una instancia de CalendarService V2."""
    factory = CalendarServiceFactoryV2(db)
    return factory.create_service()

api_router = APIRouter()
# Reutilizamos el router unificado para tener TODOS los endpoints en V2
calendars_router = create_calendars_router(get_calendar_service_v2)
api_router.include_router(calendars_router, prefix="/calendars", tags=["calendars-v2"])

