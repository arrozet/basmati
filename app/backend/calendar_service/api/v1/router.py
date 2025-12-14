"""Router principal de API v1"""
from fastapi import APIRouter, Depends
from api.endpoints.calendars import create_calendars_router
from core.database import get_database
from core.factory import CalendarServiceFactoryV1
from core.interface import ICalendarService

async def get_calendar_service_v1(db=Depends(get_database)) -> ICalendarService:
    """Proporciona una instancia de CalendarService V1."""
    factory = CalendarServiceFactoryV1(db)
    return factory.create_service()

api_router = APIRouter()
calendars_router = create_calendars_router(get_calendar_service_v1)
api_router.include_router(calendars_router, prefix="/calendars", tags=["calendars-v1"])
