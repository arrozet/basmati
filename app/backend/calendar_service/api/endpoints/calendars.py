"""
Endpoints unificados para gestión de calendarios.
Utiliza Abstract Factory para soportar múltiples versiones.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from core.interface import ICalendarService
from schemas.calendar import (
    CalendarCreate, 
    CalendarUpdate, 
    CalendarResponse, 
    CalendarHierarchy,
    CalendarComment,
    CommentCreate
)
from schemas.common import ResponseMessage

def create_calendars_router(get_service_dependency) -> APIRouter:
    """
    Crea un router de calendarios con la dependencia de servicio inyectada.
    """
    router = APIRouter()

    # ========================================================================
    # CRUD BÁSICO
    # ========================================================================

    @router.post(
        "",
        response_model=CalendarResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Crear un nuevo calendario",
        description="Crea un nuevo calendario en el sistema.",
    )
    async def create_calendar(
        calendar: CalendarCreate = Body(..., description="Datos del calendario"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        try:
            return await service.create_calendar(calendar)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get(
        "/{calendar_id}",
        response_model=CalendarResponse,
        summary="Obtener un calendario por ID",
    )
    async def get_calendar(
        calendar_id: str = Path(..., description="ID del calendario"),
        current_user_id: str | None = Query(None, description="ID del usuario actual (opcional para verificar permisos)"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        # Verificar permisos de visualización solo si se proporciona current_user_id
        if current_user_id:
            can_view = await service.can_view_calendar(calendar_id, current_user_id)
            if not can_view:
                raise HTTPException(status_code=403, detail="No tienes permiso para ver este calendario")
        
        calendar = await service.get_calendar(calendar_id)
        if not calendar:
            raise HTTPException(status_code=404, detail="Calendario no encontrado")
        return calendar

    @router.put(
        "/{calendar_id}",
        response_model=CalendarResponse,
        summary="Actualizar un calendario",
    )
    async def update_calendar(
        calendar_id: str = Path(..., description="ID del calendario"),
        calendar: CalendarUpdate = Body(..., description="Datos a actualizar"),
        current_user_id: str = Query(..., description="ID del usuario actual"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        # Verificar permisos de edición (solo el creador puede editar)
        can_edit = await service.can_edit_calendar(calendar_id, current_user_id)
        if not can_edit:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este calendario")
        
        try:
            updated = await service.update_calendar(calendar_id, calendar)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
            
        if not updated:
            raise HTTPException(status_code=404, detail="Calendario no encontrado")
        return updated

    @router.delete(
        "/{calendar_id}",
        response_model=ResponseMessage,
        summary="Eliminar un calendario",
    )
    async def delete_calendar(
        calendar_id: str = Path(..., description="ID del calendario"),
        current_user_id: str = Query(..., description="ID del usuario actual"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        # Verificar permisos de eliminación (solo el creador puede eliminar)
        can_edit = await service.can_edit_calendar(calendar_id, current_user_id)
        if not can_edit:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este calendario")
        
        deleted = await service.delete_calendar(calendar_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Calendario no encontrado")
        return ResponseMessage(message="Calendario eliminado exitosamente")

    # ========================================================================
    # BÚSQUEDAS PARAMETRIZADAS
    # ========================================================================

    @router.get(
        "/search/by-creator",
        response_model=list[CalendarResponse],
        summary="Buscar calendarios por creador",
    )
    async def search_by_creator(
        external_id: str = Query(..., description="ID externo del creador"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        return await service.search_by_creator(external_id)

    @router.get(
        "/search/by-keywords",
        response_model=list[CalendarResponse],
        summary="Buscar calendarios por palabras clave",
    )
    async def search_by_keywords(
        keyword: str = Query(..., description="Palabra clave"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        return await service.search_by_keywords(keyword)
        
    @router.get(
        "/search/by-visibility",
        response_model=list[CalendarResponse],
        summary="Buscar calendarios por visibilidad",
    )
    async def search_by_visibility(
        visibility: str = Query(..., description="Visibilidad (public, private, unlisted)"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        return await service.search_by_visibility(visibility)

    # ========================================================================
    # JERARQUÍA
    # ========================================================================

    @router.get(
        "/{calendar_id}/children",
        response_model=list[CalendarResponse],
        summary="Obtener calendarios hijos directos",
    )
    async def get_children(
        calendar_id: str = Path(..., description="ID del calendario padre"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        return await service.get_children(calendar_id)

    @router.get(
        "/{calendar_id}/hierarchy",
        response_model=CalendarHierarchy,
        summary="Obtener jerarquía completa de un calendario",
    )
    async def get_hierarchy(
        calendar_id: str = Path(..., description="ID del calendario raíz"),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        hierarchy = await service.get_hierarchy(calendar_id)
        if not hierarchy:
            raise HTTPException(status_code=404, detail="Calendario no encontrado")
        return hierarchy

    # ========================================================================
    # V2 EXCLUSIVE (Available in V1 interface but implemented differently or exposed here for uniformity)
    # ========================================================================

    @router.get(
        "",
        response_model=list[CalendarResponse],
        summary="Obtener todos los calendarios (Mejorado en V2)",
        description="En V1 retorna lista vacía o limitada. En V2 retorna todos.",
    )
    async def get_all_calendars(
        limit: int = Query(200, ge=1, le=1000),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        return await service.get_all_calendars(limit)

    @router.delete(
        "/{calendar_id}/recursive",
        response_model=dict,
        summary="Eliminar calendario recursivamente (V2)",
    )
    async def delete_recursive(
        calendar_id: str = Path(...),
        service: ICalendarService = Depends(get_service_dependency),
    ):
        try:
            return await service.delete_calendar_recursive(calendar_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return router

