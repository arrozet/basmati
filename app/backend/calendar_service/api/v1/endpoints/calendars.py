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

@router.post(
    "",
    response_model=CalendarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo calendario",
    description="""
Crea un nuevo calendario en el sistema.

Características:
- Permite crear calendarios **raíz** (sin padre) o **subcalendarios** (con padre)
- Gestiona automáticamente la **jerarquía** mediante el campo `path`
- Asigna automáticamente la fecha de creación
- Inicializa el contador de suscriptores a 0

**Campos requeridos:**
- **title**: Título del calendario
- **creator_external_id**: ID externo del creador (del sistema OAuth)
- **creator_display_name**: Nombre visible del creador
- **visibility**: Visibilidad ("public", "private", "unlisted")

**Campos opcionales:**
- **description**: Descripción del calendario
- **keywords**: Array de palabras clave para búsqueda
- **color**: Color en formato HEX (#RRGGBB)
- **icon**: Nombre del icono
- **parent_calendar_id**: ID del calendario padre (para subcalendarios)

**Ejemplo de uso:**
```json
{
  "title": "Eventos Universidad de Sevilla",
  "description": "Calendario oficial de eventos",
  "creator_external_id": "google_123456",
  "creator_display_name": "Juan Pérez",
  "keywords": ["universidad", "educación", "sevilla"],
  "color": "#1E88E5",
  "visibility": "public"
}
```
"""
)
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


@router.get(
    "/{calendar_id}",
    response_model=CalendarResponse,
    summary="Obtener un calendario por ID",
    description="""
Obtiene un calendario específico por su ID de MongoDB.

Devuelve toda la información del calendario incluyendo:
- **Metadatos básicos**: título, descripción, color, icono
- **Información del creador**: external_id y display_name (denormalizados)
- **Keywords**: Palabras clave para búsqueda
- **Jerarquía**: parent_calendar_id y path completo de ancestros
- **Estadísticas**: contador de suscriptores
- **Visibilidad**: public, private o unlisted
- **Timestamps**: created_at y updated_at

**Ejemplo de uso:**
- `GET /v1/calendars/507f1f77bcf86cd799439011` → obtiene el calendario con ese ID
"""
)
async def get_calendar(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
    """
    Obtiene un calendario por su ID.

    Args:
        calendar_id: ID del calendario
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        CalendarResponse: Calendario encontrado

    Raises:
        HTTPException 404: Si el calendario no existe
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
    description="""
Actualiza un calendario existente.

**Campos actualizables:**
- **title**: Título del calendario
- **description**: Descripción
- **keywords**: Palabras clave
- **color**: Color en formato HEX
- **icon**: Nombre del icono
- **visibility**: Visibilidad (public/private/unlisted)

**Nota:** Solo envía los campos que quieres actualizar (actualización parcial).
El campo `updated_at` se actualiza automáticamente.

**Ejemplo de uso:**
```json
{
  "title": "Nuevo título del calendario",
  "color": "#FF5722",
  "keywords": ["actualizado", "nuevo"]
}
```

⚠️ **Restricción:** Solo el creador puede actualizar el calendario (a implementar en middleware de autenticación).
"""
)
async def update_calendar(calendar_id: str, calendar: CalendarUpdate, service: CalendarService = Depends(get_calendar_service)):
    """
    Actualiza un calendario existente.

    Args:
        calendar_id: ID del calendario
        calendar: Datos a actualizar
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        CalendarResponse: Calendario actualizado

    Raises:
        HTTPException 404: Si el calendario no existe
        HTTPException 400: Si los datos de actualización son inválidos
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
    description="""
Elimina un calendario del sistema de forma permanente.

**Importante:**
- La eliminación es **permanente** y no se puede deshacer
- Se recomienda verificar que no haya dependencias antes de eliminar
- Los eventos asociados al calendario **NO** se eliminan automáticamente

⚠️ **Restricción:** Solo el creador puede eliminar el calendario (a implementar en middleware de autenticación).

**Respuesta exitosa:**
```json
{
  "message": "Calendario eliminado exitosamente"
}
```
"""
)
async def delete_calendar(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
    """
    Elimina un calendario del sistema.

    Args:
        calendar_id: ID del calendario
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        ResponseMessage: Mensaje de confirmación

    Raises:
        HTTPException 404: Si el calendario no existe
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
    summary="Buscar calendarios por ID del creador",
    description="""
Busca calendarios por el ID externo del creador.

Utiliza el campo **creator_external_id** (ID del proveedor OAuth) para encontrar
todos los calendarios creados por un usuario específico.

**Diferencia con /search/by-creator-name:**
- Este endpoint busca por **ID exacto** del usuario (del sistema OAuth)
- `/search/by-creator-name` busca por **nombre** del usuario (parcial)

**Ejemplo de uso:**
- `creator_external_id=google_123456` → encuentra todos los calendarios del usuario con ese ID de Google
- `creator_external_id=facebook_789012` → encuentra todos los calendarios del usuario con ese ID de Facebook
"""
)
async def search_by_creator(
    creator_external_id: str = Query(
        ...,
        description="ID del creador (external_id del proveedor OAuth)",
        example="google_123456",
        min_length=1
    ),
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
    summary="Buscar calendarios por palabras clave",
    description="""
Busca calendarios por palabras clave (keywords).

Busca en el array de **keywords** de cada calendario usando coincidencia parcial.
La búsqueda es case-insensitive y utiliza expresiones regulares.

**Uso recomendado:**
Los keywords permiten categorizar y etiquetar calendarios para facilitar su búsqueda.
Por ejemplo: ["universidad", "educación", "sevilla", "ingeniería"]

**Ejemplo de uso:**
- `keyword=universidad` → encuentra calendarios con keywords que contengan "universidad"
- `keyword=deportes` → encuentra calendarios etiquetados con "deportes", "deportivos", etc.
- `keyword=tecnología` → encuentra calendarios sobre tecnología

**Diferencia con /search/by-text:**
- Este endpoint busca solo en el campo **keywords** (array)
- `/search/by-text` busca en title, description y keywords
"""
)
async def search_by_keywords(
    keyword: str = Query(
        ...,
        description="Palabra clave a buscar",
        example="universidad",
        min_length=1
    ),
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
    description="""
Busca calendarios por su nivel de visibilidad.

**Tipos de visibilidad:**
- **public**: Calendario público, visible para todos los usuarios
- **private**: Calendario privado, solo visible para el creador
- **unlisted**: Calendario no listado, accesible por link pero no aparece en búsquedas públicas

**Ejemplo de uso:**
- `visibility=public` → obtiene todos los calendarios públicos
- `visibility=private` → obtiene todos los calendarios privados
- `visibility=unlisted` → obtiene todos los calendarios no listados

**Caso de uso típico:**
- Mostrar calendarios públicos en la página principal
- Filtrar calendarios privados del usuario actual
- Obtener calendarios compartidos (unlisted) por link
"""
)
async def search_by_visibility(
    visibility: str = Query(
        ...,
        description="Visibilidad del calendario",
        example="public",
        regex="^(public|private|unlisted)$"
    ),
    service: CalendarService = Depends(get_calendar_service)
):
    """
    Busca calendarios por visibilidad.

    Args:
        visibility: Visibilidad del calendario (public/private/unlisted)
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

@router.get(
    "/{calendar_id}/children",
    response_model=List[CalendarResponse],
    summary="Obtener calendarios hijos directos",
    description="""
Obtiene los subcalendarios directos de un calendario (relationship query 1).

Solo devuelve los **hijos inmediatos** (primer nivel), no todos los descendientes.

**Ejemplo de jerarquía:**
```
Universidad (ID: 123)
├── Ingeniería (ID: 456)      ← hijo directo
│   └── Informática (ID: 789) ← nieto, NO se incluye
└── Medicina (ID: 101)         ← hijo directo
```

**Ejemplo de uso:**
- `GET /v1/calendars/123/children` → devuelve [Ingeniería, Medicina]
- Útil para mostrar subcalendarios en una UI de navegación

**Diferencia con /hierarchy:**
- Este endpoint devuelve solo **hijos directos** (un nivel)
- `/hierarchy` devuelve **toda la jerarquía** completa (árbol)
"""
)
async def get_children(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
    """
    Obtiene los calendarios hijos directos (relationship query 1).

    Args:
        calendar_id: ID del calendario padre
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        List[CalendarResponse]: Lista de calendarios hijos directos
    """
    children = await service.get_children(calendar_id)
    return children


@router.get(
    "/{calendar_id}/hierarchy",
    response_model=CalendarHierarchy,
    summary="Obtener jerarquía completa de calendarios",
    description="""
Obtiene la jerarquía completa de un calendario y todos sus descendientes (relationship query 2).

Devuelve un **árbol jerárquico completo** con el calendario raíz y todos sus subcalendarios
en estructura anidada.

**Características:**
- Utiliza el campo **path** para consulta eficiente (una sola query a la BD)
- Devuelve estructura anidada recursiva tipo árbol
- Incluye todos los niveles de profundidad

**Ejemplo de jerarquía:**
```
Universidad
├── Ingeniería
│   ├── Informática
│   │   └── Redes
│   └── Industrial
└── Medicina
    └── Cardiología
```

**Respuesta:**
```json
{
  "calendar": {...},  // Universidad
  "children": [
    {
      "calendar": {...},  // Ingeniería
      "children": [
        {
          "calendar": {...},  // Informática
          "children": [...]
        }
      ]
    }
  ]
}
```

**Diferencia con /children:**
- Este endpoint devuelve **toda la jerarquía** (árbol completo)
- `/children` devuelve solo **hijos directos** (un nivel)

**Caso de uso:**
- Renderizar árbol completo de calendarios en la UI
- Exportar estructura completa
- Análisis de profundidad de jerarquía
"""
)
async def get_hierarchy(calendar_id: str, service: CalendarService = Depends(get_calendar_service)):
    """
    Obtiene toda la jerarquía de calendarios (relationship query 2).

    Utiliza el array path para construir la jerarquía completa.

    Args:
        calendar_id: ID del calendario raíz
        service: Servicio de calendarios (inyectado por FastAPI)

    Returns:
        CalendarHierarchy: Jerarquía completa de calendarios

    Raises:
        HTTPException 404: Si el calendario no existe
    """
    hierarchy = await service.get_hierarchy(calendar_id)
    if not hierarchy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado"
        )

    return hierarchy
