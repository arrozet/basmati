"""Router principal de la API v2 del Calendar Service.

Solo incluye los endpoints que tienen CAMBIOS respecto a v1.
Para endpoints sin cambios, usar /v1/.

Mejoras V2:
- Endpoint get_all_calendars para obtener todos los calendarios
"""
from fastapi import APIRouter, Depends

from api.v2.calendars import create_v2_calendars_router, get_calendar_service_v2


# Crear router usando SOLO los endpoints específicos de V2
api_router = APIRouter()
calendars_router = create_v2_calendars_router(get_calendar_service_v2)
api_router.include_router(calendars_router, prefix="/calendars", tags=["calendars-v2"])
