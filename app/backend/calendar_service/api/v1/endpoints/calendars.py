"""Endpoints de calendarios"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
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

@router.post("", response_model=CalendarResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar(calendar: CalendarCreate, service: CalendarService = Depends(get_calendar_service)):
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


@router.get("/{calendar_id}", response_model=CalendarResponse)
async def get_calendar(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
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


@router.put("/{calendar_id}", response_model=CalendarResponse)
async def update_calendar(calendar_id: str, calendar: CalendarUpdate, service: CalendarService = Depends(get_calendar_service)):
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


@router.delete("/{calendar_id}", response_model=ResponseMessage)
async def delete_calendar(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
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

@router.get("/search/by-creator", response_model=List[CalendarResponse])
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


@router.get("/search/by-keywords", response_model=List[CalendarResponse])
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


@router.get("/search/by-visibility", response_model=List[CalendarResponse])
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
    description="""
Realiza una búsqueda full-text en calendarios.

Busca en los siguientes campos:
- **title**: Título del calendario
- **description**: Descripción del calendario
- **keywords**: Palabras clave asociadas

La búsqueda es case-insensitive y utiliza expresiones regulares.

**Ejemplo de uso:**
- `query=universidad` → encuentra "Universidad de Sevilla", "Eventos Universidad", etc.
- `query=deportes` → encuentra calendarios con keywords ["deportes", "fitness"]
- `query=tecnología` → encuentra calendarios sobre tecnología
"""
)
async def search_by_text(
    query: str = Query(
        ...,
        description="Término de búsqueda",
        example="universidad",
        min_length=1
    ),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Busca calendarios por texto.

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
    description="""
Busca calendarios utilizando el nombre del creador.

Utiliza el campo denormalizado **creator_display_name** para realizar
búsquedas eficientes sin necesidad de join con la colección de usuarios.

La búsqueda es parcial y case-insensitive.

**Ejemplo de uso:**
- `creator_name=Juan` → encuentra calendarios de "Juan Pérez", "María Juan", etc.
- `creator_name=García` → encuentra calendarios de usuarios con apellido García
- `creator_name=Ana` → encuentra calendarios creados por "Ana López", "Juana Ana", etc.
"""
)
async def search_by_creator_name(
    creator_name: str = Query(
        ...,
        description="Nombre o parte del nombre del creador",
        example="Juan",
        min_length=1
    ),
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

@router.get("/{calendar_id}/children", response_model=List[CalendarResponse])
async def get_children(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
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


@router.get("/{calendar_id}/hierarchy", response_model=CalendarHierarchy)
async def get_hierarchy(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
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
