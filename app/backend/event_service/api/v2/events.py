"""Endpoints específicos de la API v2 del Event Service.

Este módulo contiene SOLO los endpoints que tienen cambios respecto a v1.
Los endpoints sin cambios deben usarse desde /v1/.

Cambios en V2:
- search_by_date_range: Añade filtro opcional por calendar_id
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.interface import IEventService
from schemas.event import EventResponse


def create_v2_events_router(get_service_dependency) -> APIRouter:
    """Crea un router con los endpoints específicos de v2.
    
    Solo incluye los endpoints que tienen cambios respecto a v1.
    
    Args:
        get_service_dependency: Función de dependencia que retorna IEventService
        
    Returns:
        APIRouter: Router con endpoints modificados en v2
    """
    router = APIRouter()

    @router.get(
        "/search/by-date-range",
        response_model=list[EventResponse],
        summary="Buscar eventos por rango de fechas",
        description="""
Busca eventos dentro de un rango de fechas.

**Mejora en V2**: Permite filtrar opcionalmente por `calendar_id`.

Ejemplo de uso:
- `/v2/events/search/by-date-range?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59`
- `/v2/events/search/by-date-range?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59&calendar_id=507f1f77bcf86cd799439011`
        """,
        responses={
            200: {"description": "Lista de eventos en el rango de fechas."},
            400: {"description": "Error de validación en el rango de fechas."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_date_range(
        start: datetime = Query(..., description="Fecha inicio ISO 8601"),
        end: datetime = Query(..., description="Fecha fin ISO 8601"),
        calendar_id: str | None = Query(
            None, 
            description="ID del calendario para filtrar (nuevo en V2)"
        ),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Busca eventos dentro de un rango de fechas con filtro opcional por calendario."""
        try:
            return await service.search_by_date_range(start, end, calendar_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    return router

