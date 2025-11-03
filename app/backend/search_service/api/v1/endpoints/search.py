"""
Endpoints de búsqueda avanzada.

Proporciona endpoints para realizar búsquedas en calendarios y eventos
delegando las consultas a Calendar Service y Event Service mediante HTTP.
"""
from fastapi import APIRouter, Query, Depends
from schemas.search import CalendarSearchResult, EventSearchResult, CombinedSearchResult
from services.search_service import SearchService
from core.config import settings

router = APIRouter()


def get_search_service() -> SearchService:
    """
    Proporciona una instancia de SearchService.

    Returns:
        SearchService: Servicio de búsqueda configurado con URLs de otros servicios
    """
    return SearchService(
        calendar_service_url=settings.calendar_service_url,
        event_service_url=settings.event_service_url
    )


@router.get(
    "/calendars",
    response_model=list[CalendarSearchResult],
    summary="Buscar calendarios",
    description="""
Realiza una búsqueda full-text en la colección de calendarios.

Busca en los siguientes campos:
- **title**: Título del calendario
- **description**: Descripción del calendario
- **keywords**: Palabras clave asociadas

La búsqueda es case-insensitive y utiliza expresiones regulares.

**Ejemplo de uso:**
- `q=universidad` → encuentra "Universidad de Sevilla", "Eventos Universidad", etc.
- `q=deportes` → encuentra calendarios relacionados con deportes
"""
)
async def search_calendars(
    q: str = Query(
        ...,
        description="Término de búsqueda para calendarios",
        example="universidad",
        min_length=1
    ),
    service: SearchService = Depends(get_search_service)
):
    """
    Busca calendarios por texto (parametrized query 1).
    
    Args:
        q: Término de búsqueda
        service: Servicio de búsqueda (inyectado por FastAPI)
        
    Returns:
        list[CalendarSearchResult]: Calendarios encontrados
    """
    return await service.search_calendars_by_text(q)


@router.get(
    "/events",
    response_model=list[EventSearchResult],
    summary="Buscar eventos",
    description="""
Realiza una búsqueda full-text en la colección de eventos.

Busca en los siguientes campos:
- **title**: Título del evento
- **description**: Descripción del evento
- **location.address**: Dirección del evento
- **location.place_name**: Nombre del lugar

La búsqueda es case-insensitive y utiliza expresiones regulares.

**Ejemplo de uso:**
- `q=conferencia` → encuentra "Conferencia de IA", "Conferencia Anual", etc.
- `q=sevilla` → encuentra eventos en Sevilla o relacionados con la ciudad
"""
)
async def search_events(
    q: str = Query(
        ...,
        description="Término de búsqueda para eventos",
        example="conferencia",
        min_length=1
    ),
    service: SearchService = Depends(get_search_service)
):
    """
    Busca eventos por texto (parametrized query 2).
    
    Args:
        q: Término de búsqueda
        service: Servicio de búsqueda (inyectado por FastAPI)
        
    Returns:
        list[EventSearchResult]: Eventos encontrados
    """
    return await service.search_events_by_text(q)


@router.get(
    "/combined",
    response_model=CombinedSearchResult,
    summary="Búsqueda combinada",
    description="""
Realiza una búsqueda simultánea en calendarios y eventos.

Devuelve resultados unificados de ambas colecciones, permitiendo
al usuario ver todos los resultados relevantes en una sola respuesta.

Busca en:
- **Calendarios**: title, description, keywords
- **Eventos**: title, description, location

**Ejemplo de uso:**
- `q=universidad` → encuentra calendarios y eventos relacionados con universidades
- `q=tecnología` → encuentra calendarios de tecnología y eventos tecnológicos
"""
)
async def search_combined(
    q: str = Query(
        ...,
        description="Término de búsqueda para calendarios y eventos",
        example="universidad",
        min_length=1
    ),
    service: SearchService = Depends(get_search_service)
):
    """
    Busca en calendarios y eventos simultáneamente.
    
    Args:
        q: Término de búsqueda
        service: Servicio de búsqueda (inyectado por FastAPI)
        
    Returns:
        CombinedSearchResult: Calendarios y eventos encontrados
    """
    return await service.search_combined(q)


@router.get(
    "/calendars/by_creator",
    response_model=list[CalendarSearchResult],
    summary="Buscar calendarios por creador",
    description="""
Busca calendarios utilizando el nombre del creador (relationship query 1).

Utiliza el campo denormalizado `creator_display_name` para realizar
búsquedas eficientes sin necesidad de join con la colección de usuarios.

La búsqueda es parcial y case-insensitive.

**Ejemplo de uso:**
- `creator_name=Juan` → encuentra calendarios de "Juan Pérez", "María Juan", etc.
- `creator_name=García` → encuentra calendarios de usuarios con apellido García
"""
)
async def get_calendars_by_creator(
    creator_name: str = Query(
        ...,
        description="Nombre o parte del nombre del creador",
        example="Juan",
        min_length=1
    ),
    service: SearchService = Depends(get_search_service)
):
    """
    Busca calendarios por nombre del creador (relationship query 1).
    
    Args:
        creator_name: Nombre del creador a buscar
        service: Servicio de búsqueda (inyectado por FastAPI)
        
    Returns:
        list[CalendarSearchResult]: Calendarios del creador
    """
    return await service.get_calendars_by_creator_name(creator_name)


@router.get(
    "/events/by_calendar_title",
    response_model=list[EventSearchResult],
    summary="Buscar eventos por título de calendario",
    description="""
Busca eventos utilizando el título del calendario al que pertenecen (relationship query 2).

Utiliza el campo denormalizado `calendar_title` para realizar
búsquedas eficientes sin necesidad de join con la colección de calendarios.

La búsqueda es parcial y case-insensitive.

**Ejemplo de uso:**
- `title=Universidad` → encuentra eventos de calendarios "Universidad de Sevilla", etc.
- `title=Deportes` → encuentra eventos de calendarios deportivos
"""
)
async def get_events_by_calendar_title(
    title: str = Query(
        ...,
        description="Título o parte del título del calendario",
        example="Universidad",
        min_length=1
    ),
    service: SearchService = Depends(get_search_service)
):
    """
    Busca eventos por título del calendario (relationship query 2).
    
    Args:
        title: Título del calendario a buscar
        service: Servicio de búsqueda (inyectado por FastAPI)
        
    Returns:
        list[EventSearchResult]: Eventos del calendario
    """
    return await service.get_events_by_calendar_title(title)


@router.get(
    "/events/by_location",
    response_model=list[EventSearchResult],
    summary="Buscar eventos por ubicación",
    description="""
Busca eventos por su ubicación geográfica.

Busca en los campos:
- **location.address**: Dirección completa
- **location.place_name**: Nombre del lugar

Útil para encontrar eventos en una ciudad, edificio o lugar específico.

**Ejemplo de uso:**
- `query=Sevilla` → encuentra eventos en Sevilla
- `query=Aula Magna` → encuentra eventos en el Aula Magna
"""
)
async def search_events_by_location(
    query: str = Query(
        ...,
        description="Término de búsqueda para la ubicación",
        example="Sevilla",
        min_length=1
    ),
    service: SearchService = Depends(get_search_service)
):
    """
    Busca eventos por ubicación.
    
    Args:
        query: Término de búsqueda para la ubicación
        service: Servicio de búsqueda (inyectado por FastAPI)
        
    Returns:
        list[EventSearchResult]: Eventos en esa ubicación
    """
    return await service.search_events_by_location(query)
