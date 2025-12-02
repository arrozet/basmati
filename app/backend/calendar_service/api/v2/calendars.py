"""Endpoints específicos de la API v2 del Calendar Service.

Este módulo contiene SOLO los endpoints que tienen cambios respecto a v1.
Los endpoints sin cambios deben usarse desde /v1/.

Cambios en V2:
- get_all_calendars: Nuevo endpoint para obtener todos los calendarios
- delete_calendar_recursive: Nuevo endpoint para eliminar calendario recursivamente
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

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

    @router.delete(
        "/{calendar_id}/recursive",
        response_model=dict,
        summary="Eliminar calendario recursivamente",
        description="""
Elimina un calendario junto con todos sus subcalendarios y eventos asociados.

**Nuevo en V2**: Este endpoint no existe en V1.

Orden de eliminación:
1. Eventos de subcalendarios más profundos
2. Subcalendarios (de hijos a padres)
3. Eventos del calendario raíz
4. Calendario raíz

Ejemplo de uso:
- `DELETE /v2/calendars/507f1f77bcf86cd799439011/recursive`
        """,
        responses={
            200: {"description": "Calendario eliminado recursivamente."},
            404: {"description": "Calendario no encontrado."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def delete_calendar_recursive(
        calendar_id: str,
        service: CalendarService = Depends(get_service_dependency),
    ):
        """Elimina un calendario y toda su jerarquía recursivamente.
        
        Elimina todos los eventos del calendario y subcalendarios,
        luego elimina los subcalendarios y finalmente el calendario raíz.
        """
        try:
            result = await service.delete_calendar_recursive(calendar_id)
            return result
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar calendario recursivamente: {str(exc)}",
            ) from exc

    return router
