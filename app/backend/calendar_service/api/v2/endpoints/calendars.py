"""Endpoints específicos de la API v2 del Calendar Service.

Este módulo contiene SOLO los endpoints que tienen cambios respecto a v1.
Los endpoints sin cambios deben usarse desde /v1/.

Cambios en V2:
- get_all_calendars: Nuevo endpoint para obtener todos los calendarios
- delete_calendar_recursive: Nuevo endpoint para eliminar calendario recursivamente
- search_by_text: Búsqueda de texto completo en calendarios
- search_by_creator_name: Nuevo endpoint para buscar por nombre de creador
- add_comment: Nuevo endpoint para agregar comentarios a calendarios
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from core.interface import ICalendarService
from schemas.calendar import CalendarResponse, CalendarComment, CommentCreate


def create_v2_calendars_router(get_service_dependency) -> APIRouter:
    """Crea un router con los endpoints específicos de v2.
    
    Solo incluye los endpoints que tienen cambios respecto a v1.
    
    Args:
        get_service_dependency: Función de dependencia que retorna ICalendarService
        
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

**Nuevo en V2**: Este endpoint no existe en V1 o está limitado.

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
        service: ICalendarService = Depends(get_service_dependency),
    ):
        """Obtiene todos los calendarios del sistema.
        
        Mejoras V2:
        - Soporte para paginación mejorada
        - Límite configurable hasta 1000 calendarios
        - Mejor rendimiento en consultas grandes
        
        Args:
            limit: Número máximo de resultados (1-1000)
            service: Servicio de calendarios inyectado
            
        Returns:
            Lista de calendarios
        """
        return await service.get_all_calendars(limit)

    @router.delete(
        "/{calendar_id}/recursive",
        response_model=dict,
        summary="Eliminar calendario recursivamente",
        description="""
Elimina un calendario y todos sus subcalendarios y eventos asociados de forma recursiva.

**Nuevo en V2**: Este endpoint no existe en V1.
Utilizado para limpieza completa de jerarquías de calendarios.

Ejemplo de uso:
- `DELETE /v2/calendars/507f1f77bcf86cd799439011/recursive`
        """,
        responses={
            200: {"description": "Calendario y subcalendarios eliminados correctamente."},
            404: {"description": "El calendario no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def delete_calendar_recursive(
        calendar_id: str = Path(..., description="ID del calendario raíz a eliminar"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        """Elimina un calendario y toda su jerarquía de forma recursiva.
        
        Exclusivo de V2:
        - Elimina el calendario especificado
        - Elimina todos los subcalendarios (hijos, nietos, etc.)
        - Elimina todos los eventos asociados a cada calendario
        - Operación atómica y segura
        
        Args:
            calendar_id: ID del calendario raíz
            service: Servicio de calendarios inyectado
            
        Returns:
            dict: Estadísticas de la eliminación (calendarios eliminados, eventos eliminados)
            
        Raises:
            404: Si el calendario no existe
            500: Si hay un error en la eliminación
        """
        try:
            return await service.delete_calendar_recursive(calendar_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    # ========================================================================
    # BÚSQUEDA DE TEXTO - NUEVO EN V2
    # ========================================================================

    @router.get(
        "/search/by-text",
        response_model=list[CalendarResponse],
        summary="Búsqueda de texto completo en calendarios",
        description="""
Búsqueda full-text en calendarios. Busca en los campos: title, description y keywords del calendario.

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            200: {"description": "Lista de calendarios encontrados."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_text(
        query: str = Query(..., description="Término de búsqueda"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        """Búsqueda full-text en calendarios.

        Busca en los campos: title, description y keywords del calendario.

        Args:
            query: Término de búsqueda
            service: Servicio de calendarios inyectado

        Returns:
            list[CalendarResponse]: Lista de calendarios encontrados
        """
        return await service.search_by_text(query)

    @router.get(
        "/search/by-creator-name",
        response_model=list[CalendarResponse],
        summary="Buscar calendarios por nombre del creador",
        description="""
Busca calendarios por nombre del creador.

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            200: {"description": "Lista de calendarios encontrados."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_creator_name(
        name: str = Query(..., description="Nombre del creador"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        """Busca calendarios por nombre del creador.

        Args:
            name: Nombre o parte del nombre del creador
            service: Servicio de calendarios inyectado

        Returns:
            list[CalendarResponse]: Calendarios creados por usuarios con ese nombre
        """
        return await service.search_by_creator_name(name)

    # ========================================================================
    # COMENTARIOS - NUEVO EN V2
    # ========================================================================

    @router.post(
        "/{calendar_id}/comments",
        response_model=CalendarComment,
        status_code=status.HTTP_201_CREATED,
        summary="Agregar comentario a un calendario",
        description="""
Agrega un comentario a un calendario público o unlisted.

**Nuevo en V2**: Este endpoint no existe en V1.
        """,
        responses={
            201: {"description": "Comentario creado exitosamente."},
            403: {"description": "No tienes permiso para comentar en este calendario."},
            404: {"description": "Calendario no encontrado."},
            400: {"description": "Error de validación."}
        }
    )
    async def add_comment(
        calendar_id: str = Path(..., description="ID del calendario"),
        comment: CommentCreate = Body(..., description="Datos del comentario"),
        current_user_id: str = Query(..., description="ID del usuario actual"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        """Agrega un comentario a un calendario.
        
        Nuevo en V2:
        - Permite comentar en calendarios públicos y unlisted
        - Verifica permisos de visualización antes de permitir comentar
        
        Args:
            calendar_id: ID del calendario
            comment: Datos del comentario
            current_user_id: ID del usuario que comenta
            service: Servicio de calendarios inyectado
            
        Returns:
            CalendarComment: Comentario agregado
            
        Raises:
            403: Si el usuario no puede ver el calendario
            404: Si el calendario no existe
            400: Si hay error de validación
        """
        # Verificar que el usuario puede ver el calendario (para comentar debe poder verlo)
        can_view = await service.can_view_calendar(calendar_id, current_user_id)
        if not can_view:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permiso para comentar en este calendario"
            )
        
        try:
            new_comment = await service.add_comment(calendar_id, comment)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        if not new_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendario no encontrado",
            )
        return new_comment

    return router

