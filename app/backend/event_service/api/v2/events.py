"""Endpoints específicos de la API v2 del Event Service.

Este módulo contiene SOLO los endpoints que tienen cambios respecto a v1.
Los endpoints sin cambios deben usarse desde /v1/.

Cambios en V2:
- search_by_date_range: Añade filtro opcional por calendar_id
- get_all_events: Nuevo endpoint para obtener todos los eventos
- delete_events_by_calendar: Nuevo endpoint para eliminar eventos de un calendario
- add_comment: Simplificado, solo requiere user_id y text (obtiene display_name del User Service)
"""
from datetime import datetime
import httpx

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from core.interface import IEventService
from core.config import settings
from schemas.event import EventResponse, EventComment, CommentCreateV2, CommentCreate


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
        limit: int = Query(1000, ge=1, le=1000, description="Número máximo de eventos a devolver"),
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

**Mejora en V2**: Permite filtrar opcionalmente por `calendar_id` o `calendar_ids`.

Ejemplo de uso:
- `/v2/events/search/by-date-range?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59`
- `/v2/events/search/by-date-range?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59&calendar_id=507f1f77bcf86cd799439011`
- `/v2/events/search/by-date-range?start=2024-01-01T00:00:00&end=2024-12-31T23:59:59&calendar_ids=id1,id2,id3`
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
            description="ID del calendario para filtrar (un solo calendario)"
        ),
        calendar_ids: str | None = Query(
            None,
            description="IDs de calendarios separados por coma para filtrar (múltiples calendarios)"
        ),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Busca eventos dentro de un rango de fechas con filtro opcional por calendario(s)."""
        try:
            # Combinar calendar_id y calendar_ids en una lista
            ids_list: list[str] | None = None
            if calendar_ids:
                ids_list = [id.strip() for id in calendar_ids.split(",") if id.strip()]
            elif calendar_id:
                ids_list = [calendar_id]
            
            return await service.search_by_date_range(start, end, ids_list)
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

    @router.post(
        "/{event_id}/comments",
        response_model=EventComment,
        status_code=status.HTTP_201_CREATED,
        summary="Agregar comentario a un evento (V2)",
        description="""
Agrega un comentario a un evento.

**Mejora en V2**: Solo requiere `user_id` y `text`. El backend obtiene el display_name
automáticamente consultando el User Service.

Ejemplo de uso:
```json
{
    "user_id": "user_dev_1",
    "text": "¿Podemos mover el evento 30 minutos más tarde?"
}
```
        """,
        responses={
            201: {"description": "Comentario agregado exitosamente."},
            400: {"description": "Error de validación en los datos del comentario."},
            404: {"description": "El evento con el ID especificado no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def add_comment(
        event_id: str = Path(..., description="ID único del evento"),
        comment: CommentCreateV2 = Body(..., description="Datos del comentario"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Agrega un comentario a un evento (versión simplificada).
        
        Esta versión no requiere display_name, el backend lo obtiene del User Service.
        """
        # Obtener el nombre real del usuario desde el User Service
        display_name = f"Usuario {comment.user_id}"  # Fallback por defecto
        
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"{settings.user_service_url}/v2/users/by-external-id/{comment.user_id}",
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    display_name = user_data.get("display_name", display_name)
        except Exception as e:
            # Si falla la consulta al User Service, usamos el fallback
            print(f"Warning: No se pudo obtener display_name del User Service: {e}")
        
        full_comment = CommentCreate(
            author_external_id=comment.user_id,
            author_display_name=display_name,
            text=comment.text
        )
        
        try:
            new_comment = await service.add_comment(event_id, full_comment)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if not new_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado",
            )
        return new_comment

    # ========================================================================
    # BÚSQUEDA DE TEXTO - NUEVO EN V2
    # ========================================================================

    @router.get(
        "/search/by-text",
        response_model=list[EventResponse],
        summary="Búsqueda full-text en eventos",
        description="""
Busca en título, descripción y ubicación.

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            200: {"description": "Lista de eventos que coinciden."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_text(
        query: str = Query(..., description="Término de búsqueda"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Realiza una búsqueda full-text en eventos.
        
        Busca en los campos:
        - title
        - description
        - location.address
        - location.place_name
        
        Args:
            query: Término de búsqueda
            service: Servicio de eventos inyectado
            
        Returns:
            list[EventResponse]: Lista de eventos encontrados
        """
        return await service.search_by_text(query)

    @router.get(
        "/search/by-calendar-title",
        response_model=list[EventResponse],
        summary="Buscar eventos por título del calendario",
        description="""
Busca eventos por título del calendario (campo denormalizado).

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            200: {"description": "Lista de eventos del calendario."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_calendar_title(
        calendar_title: str = Query(..., description="Título del calendario"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Busca eventos por título del calendario.
        
        Args:
            calendar_title: Título o parte del título del calendario
            service: Servicio de eventos inyectado
            
        Returns:
            list[EventResponse]: Eventos del calendario con ese título
        """
        return await service.search_by_calendar_title(calendar_title)

    @router.get(
        "/search/by-location",
        response_model=list[EventResponse],
        summary="Buscar eventos por ubicación",
        description="""
Busca eventos por dirección o nombre del lugar.

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            200: {"description": "Lista de eventos en esa ubicación."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_location(
        location_query: str = Query(..., description="Término de búsqueda para ubicación"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Busca eventos por ubicación.
        
        Busca en los campos:
        - location.address
        - location.place_name
        
        Args:
            location_query: Término de búsqueda para la ubicación
            service: Servicio de eventos inyectado
            
        Returns:
            list[EventResponse]: Eventos en esa ubicación
        """
        return await service.search_by_location(location_query)

    @router.get(
        "/search/advanced",
        response_model=list[EventResponse],
        summary="Búsqueda avanzada de eventos",
        description="""
Busca por título, organizador (calendario) y palabras clave (descripción).

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            200: {"description": "Lista de eventos que coinciden."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_advanced(
        title: str | None = Query(None, description="Título del evento"),
        organizer: str | None = Query(None, description="Organizador (Título del calendario)"),
        keywords: str | None = Query(None, description="Palabras clave (Descripción)"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Realiza una búsqueda avanzada en eventos.
        
        Combina múltiples criterios de búsqueda con lógica AND:
        - title: Busca en el título del evento
        - organizer: Busca en calendar_title
        - keywords: Busca en la descripción
        
        Args:
            title: Título del evento (opcional)
            organizer: Título del calendario (opcional)
            keywords: Palabras clave en descripción (opcional)
            service: Servicio de eventos inyectado
            
        Returns:
            list[EventResponse]: Eventos que coinciden con todos los criterios
        """
        return await service.search_advanced(title, organizer, keywords)

    return router

