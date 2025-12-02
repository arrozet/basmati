"""Endpoints específicos de la API v2 del Event Service.

Este módulo contiene SOLO los endpoints que tienen cambios respecto a v1.
Los endpoints sin cambios deben usarse desde /v1/.

Cambios en V2:
- search_by_date_range: Añade filtro opcional por calendar_id
- get_all_events: Nuevo endpoint para obtener todos los eventos
- delete_events_by_calendar: Nuevo endpoint para eliminar eventos de un calendario
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
        "",
        response_model=list[EventResponse],
        summary="Obtener todos los eventos",
        description="""
Obtiene todos los eventos del sistema.

**Nuevo en V2**: Este endpoint no existe en V1.

Ejemplo de uso:
- `/v2/events` - Obtiene todos los eventos (máximo 200)
- `/v2/events?limit=50` - Obtiene los primeros 50 eventos
        """,
        responses={
            200: {"description": "Lista de eventos."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def get_all_events(
        limit: int = Query(200, ge=1, le=1000, description="Número máximo de eventos a devolver"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Obtiene todos los eventos del sistema."""
        # El servicio v2 tiene el método get_all_events
        return await service.get_all_events(limit)

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

    @router.delete(
        "/by-calendar/{calendar_id}",
        response_model=dict,
        summary="Eliminar eventos de un calendario",
        description="""
Elimina todos los eventos asociados a un calendario específico.

**Nuevo en V2**: Este endpoint no existe en V1.
Utilizado internamente por calendar_service para eliminar calendarios recursivamente.

Ejemplo de uso:
- `DELETE /v2/events/by-calendar/507f1f77bcf86cd799439011`
        """,
        responses={
            200: {"description": "Eventos eliminados correctamente."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def delete_events_by_calendar(
        calendar_id: str,
        service: IEventService = Depends(get_service_dependency),
    ):
        """Elimina todos los eventos de un calendario.
        
        Este endpoint es utilizado por calendar_service para la eliminación
        recursiva de calendarios y sus eventos.
        """
        # El servicio v2 tiene el método delete_events_by_calendar
        deleted_count = await service.delete_events_by_calendar(calendar_id)
        return {
            "message": f"Eventos eliminados del calendario {calendar_id}",
            "deleted_count": deleted_count,
            "calendar_id": calendar_id
        }

    return router

