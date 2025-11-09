"""Endpoints de calendarios"""
from fastapi import APIRouter, HTTPException, status, Query, Path, Body, Depends
from typing import List
from schemas.calendar import CalendarCreate, CalendarUpdate, CalendarResponse, CalendarHierarchy
from schemas.common import ResponseMessage
from services.calendar_service import CalendarService
from core.database import get_calendar_repository

router = APIRouter()

# Dependency: Inyección de dependencias para CalendarService
async def get_calendar_service(calendar_repository = Depends(get_calendar_repository)) -> CalendarService:
    """
    Proporciona una instancia de CalendarService con el Repository.
    
    Args:
        calendar_repository: Repository de calendarios (inyectado por FastAPI)
        
    Returns:
        CalendarService: Instancia del servicio de calendarios
    """
    return CalendarService(calendar_repository)


# ==================== CRUD ENDPOINTS ====================

@router.post(
    "",
    response_model=CalendarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo calendario",
    description="Crea un nuevo calendario en el sistema.",
    responses={
        201: {"description": "Calendario creado exitosamente."},
        400: {"description": "Error de validación o el calendario padre no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def create_calendar(
    calendar: CalendarCreate = Body(..., description="Datos del calendario a crear"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Crea un nuevo calendario en el sistema.
    
    Args:
        calendar: Datos del calendario a crear
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        CalendarResponse: El calendario creado con su ID
        
    Raises:
        HTTPException 400: Si el calendario padre no existe o hay error de validación
    """
    try:
        return await service.create_calendar(calendar)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{calendar_id}",
    response_model=CalendarResponse,
    summary="Obtener un calendario por ID",
    description="Obtiene un calendario por su ID.",
    responses={
        200: {"description": "Calendario encontrado y devuelto exitosamente."},
        404: {"description": "El calendario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_calendar(
    calendar_id: str = Path(..., description="ID único del calendario"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Obtiene un calendario por su ID.
    
    Args:
        calendar_id: ID del calendario
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        CalendarResponse: Calendario encontrado
    """
    calendar = await service.get_calendar(calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado"
        )
    
    return calendar


@router.put(
    "/{calendar_id}",
    response_model=CalendarResponse,
    summary="Actualizar un calendario",
    description="Actualiza un calendario existente. Solo el creador puede actualizar el calendario.",
    responses={
        200: {"description": "Calendario actualizado exitosamente."},
        400: {"description": "Error de validación en los datos proporcionados."},
        404: {"description": "El calendario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def update_calendar(
    calendar_id: str = Path(..., description="ID único del calendario"),
    calendar: CalendarUpdate = Body(..., description="Datos a actualizar del calendario"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Actualiza un calendario existente.
    
    Solo el creador puede actualizar el calendario.
    
    Args:
        calendar_id: ID del calendario
        calendar: Datos a actualizar
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        CalendarResponse: Calendario actualizado
    """
    try:
        updated_calendar = await service.update_calendar(calendar_id, calendar)
        if not updated_calendar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendario no encontrado"
            )
        return updated_calendar
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{calendar_id}",
    response_model=ResponseMessage,
    summary="Eliminar un calendario",
    description="Elimina un calendario del sistema. Solo el creador puede eliminar el calendario.",
    responses={
        200: {"description": "Calendario eliminado exitosamente."},
        404: {"description": "El calendario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def delete_calendar(
    calendar_id: str = Path(..., description="ID único del calendario"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Elimina un calendario del sistema.
    
    Solo el creador puede eliminar el calendario.
    
    Args:
        calendar_id: ID del calendario
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        ResponseMessage: Mensaje de confirmación
    """
    deleted = await service.delete_calendar(calendar_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado"
        )
    
    return ResponseMessage(message="Calendario eliminado exitosamente")


# ==================== PARAMETRIZED SEARCH ENDPOINTS ====================

@router.get(
    "/search/by-creator",
    response_model=List[CalendarResponse],
    summary="Buscar calendarios por creador",
    description="Busca calendarios por creador (parametrized query 1).",
    responses={
        200: {"description": "Lista de calendarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_creator(
    creator_external_id: str = Query(..., description="ID del creador (external_id)"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Busca calendarios por creador (parametrized query 1).
    
    Args:
        creator_external_id: ID del creador (external_id del usuario)
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        List[CalendarResponse]: Lista de calendarios encontrados
    """
    calendars = await service.search_by_creator(creator_external_id)
    return calendars


@router.get(
    "/search/by-keywords",
    response_model=List[CalendarResponse],
    summary="Buscar calendarios por keywords",
    description="Busca calendarios por keywords (parametrized query 2).",
    responses={
        200: {"description": "Lista de calendarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_keywords(
    keyword: str = Query(..., description="Palabra clave a buscar"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Busca calendarios por keywords (parametrized query 2).
    
    Args:
        keyword: Palabra clave a buscar
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        List[CalendarResponse]: Lista de calendarios encontrados
    """
    calendars = await service.search_by_keywords(keyword)
    return calendars


@router.get(
    "/search/by-visibility",
    response_model=List[CalendarResponse],
    summary="Buscar calendarios por visibilidad",
    description="Busca calendarios por visibilidad.",
    responses={
        200: {"description": "Lista de calendarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_visibility(
    visibility: str = Query(..., description="Visibilidad (public/private/unlisted)"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Busca calendarios por visibilidad.

    Args:
        visibility: Visibilidad del calendario
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        List[CalendarResponse]: Lista de calendarios encontrados
    """
    calendars = await service.search_by_visibility(visibility)
    return calendars


@router.get(
    "/search/by-text",
    response_model=List[CalendarResponse],
    summary="Búsqueda full-text en calendarios",
    description="Búsqueda full-text en calendarios. Busca en los campos: title, description y keywords del calendario.",
    responses={
        200: {"description": "Lista de calendarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_text(
    query: str = Query(..., description="Término de búsqueda"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Búsqueda full-text en calendarios.

    Busca en los campos: title, description y keywords del calendario.

    Args:
        query: Término de búsqueda
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        List[CalendarResponse]: Lista de calendarios encontrados
    """
    calendars = await service.search_by_text(query)
    return calendars


@router.get(
    "/search/by-creator-name",
    response_model=List[CalendarResponse],
    summary="Buscar calendarios por nombre del creador",
    description="Busca calendarios por nombre del creador.",
    responses={
        200: {"description": "Lista de calendarios encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def search_by_creator_name(
    creator_name: str = Query(..., description="Nombre del creador"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Busca calendarios por nombre del creador.

    Args:
        creator_name: Nombre o parte del nombre del creador
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        List[CalendarResponse]: Calendarios creados por usuarios con ese nombre
    """
    calendars = await service.search_by_creator_name(creator_name)
    return calendars


# ==================== RELATIONSHIP ENDPOINTS ====================

@router.get(
    "/{calendar_id}/children",
    response_model=List[CalendarResponse],
    summary="Obtener calendarios hijos",
    description="Obtiene los calendarios hijos directos (relationship query 1).",
    responses={
        200: {"description": "Lista de calendarios hijos encontrados."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_children(
    calendar_id: str = Path(..., description="ID del calendario padre"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Obtiene los calendarios hijos directos (relationship query 1).
    
    Args:
        calendar_id: ID del calendario padre
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        List[CalendarResponse]: Lista de calendarios hijos
    """
    children = await service.get_children(calendar_id)
    return children


@router.get(
    "/{calendar_id}/hierarchy",
    response_model=CalendarHierarchy,
    summary="Obtener jerarquía de calendarios",
    description="Obtiene toda la jerarquía de calendarios (relationship query 2). Utiliza el array path para construir la jerarquía completa.",
    responses={
        200: {"description": "Jerarquía de calendarios encontrada y devuelta exitosamente."},
        404: {"description": "El calendario con el ID especificado no existe."},
        500: {"description": "Error interno del servidor."}
    }
)
async def get_hierarchy(
    calendar_id: str = Path(..., description="ID del calendario raíz"),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Obtiene toda la jerarquía de calendarios (relationship query 2).
    
    Utiliza el array path para construir la jerarquía completa.
    
    Args:
        calendar_id: ID del calendario raíz
        service: Servicio de calendarios (inyectado por FastAPI)
        
    Returns:
        CalendarHierarchy: Jerarquía completa de calendarios
    """
    hierarchy = await service.get_hierarchy(calendar_id)
    if not hierarchy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado"
        )
    
    return hierarchy
