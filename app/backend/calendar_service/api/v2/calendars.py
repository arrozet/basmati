"""Endpoints específicos de la API v2 del Calendar Service.

Este módulo contiene SOLO los endpoints que tienen cambios respecto a v1.
Los endpoints sin cambios deben usarse desde /v1/.

Cambios en V2:
- get_all_calendars: Nuevo endpoint para obtener todos los calendarios
"""
from fastapi import APIRouter, Depends, Query

from schemas.calendar import CalendarResponse
from services.calendar_service import CalendarService
from core.database import get_calendar_repository


async def get_calendar_service_v2(calendar_repository=Depends(get_calendar_repository)) -> CalendarService:
    """Proporciona una instancia de CalendarService V2.
    
    Usa el mismo servicio que v1 pero con métodos adicionales.
    
    Args:
        calendar_repository: Repository de calendarios (inyectado por FastAPI)
        
    Returns:
        CalendarService: Instancia del servicio
    """
    return CalendarService(calendar_repository)


def create_v2_calendars_router(get_service_dependency) -> APIRouter:
    """Crea un router con los endpoints específicos de v2.
    
    Solo incluye los endpoints que tienen cambios respecto a v1.
    
    Args:
        get_service_dependency: Función de dependencia que retorna CalendarService
        
    Returns:
        APIRouter: Router con endpoints modificados en v2
    """
    router = APIRouter()

    @router.get(
        "",
        response_model=list[CalendarResponse],
        summary="Obtener todos los calendarios",
        description="""
Obtiene todos los calendarios del sistema.

**Nuevo en V2**: Este endpoint no existe en V1.

Ejemplo de uso:
- `/v2/calendars` - Obtiene todos los calendarios (máximo 200)
- `/v2/calendars?limit=50` - Obtiene los primeros 50 calendarios
        """,
        responses={
            200: {"description": "Lista de calendarios."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def get_all_calendars(
        limit: int = Query(200, ge=1, le=1000, description="Número máximo de calendarios a devolver"),
        service: CalendarService = Depends(get_service_dependency),
    ):
        """Obtiene todos los calendarios del sistema."""
        return await service.get_all_calendars(limit)

    return router
