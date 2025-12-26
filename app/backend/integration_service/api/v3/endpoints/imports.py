"""
Endpoints de importación V3 - Abstract Factory Pattern

Este módulo expone los endpoints de la API V3 para importación de calendarios
utilizando la implementación con patrón Abstract Factory.
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import Annotated

from services.v3.imports import ImportServiceV3, ProviderType
from services.v3.imports.schemas import (
    GoogleCalendarImportRequestV3,
    TeamupImportRequestV3,
    GenericImportRequest,
    ImportResponseV3,
    PROVIDER_CAPABILITIES,
)
from services.v3.imports.service import ProviderNotSupportedError
from core.config import settings

router = APIRouter()


def get_import_service_v3() -> ImportServiceV3:
    """
    Crea una instancia del servicio de importación V3.
    
    Inyecta las URLs de servicios y la API Key de Teamup desde la configuración.
    """
    return ImportServiceV3(
        calendar_service_url=settings.CALENDAR_SERVICE_URL,
        event_service_url=settings.EVENT_SERVICE_URL,
        default_teamup_api_key=getattr(settings, 'teamup_api_key', None),
    )


# =============================================================================
# ENDPOINTS DE INFORMACIÓN
# =============================================================================

@router.get(
    "/providers",
    summary="Listar proveedores soportados",
    description="Retorna la lista de proveedores de calendario soportados con sus capacidades.",
    response_model=list[dict],
    tags=["V3: Info"],
)
async def list_providers():
    """
    Lista los proveedores de calendario soportados.
    
    Returns:
        Lista de proveedores con sus capacidades (OAuth, API Key, etc.)
    """
    return [cap.model_dump() for cap in PROVIDER_CAPABILITIES.values()]


@router.get(
    "/providers/{provider}",
    summary="Obtener información de un proveedor",
    description="Retorna información detallada de un proveedor específico.",
    tags=["V3: Info"],
)
async def get_provider_info(provider: str):
    """
    Obtiene información de un proveedor específico.
    
    Args:
        provider: Nombre del proveedor (google, teamup)
        
    Returns:
        Información del proveedor o error 404
    """
    try:
        provider_type = ProviderType(provider.lower())
        if provider_type in PROVIDER_CAPABILITIES:
            return PROVIDER_CAPABILITIES[provider_type].model_dump()
    except ValueError:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proveedor '{provider}' no encontrado. "
               f"Proveedores disponibles: {[p.value for p in ProviderType]}"
    )


# =============================================================================
# ENDPOINTS DE IMPORTACIÓN ESPECÍFICOS
# =============================================================================

@router.post(
    "/google",
    response_model=ImportResponseV3,
    status_code=status.HTTP_201_CREATED,
    summary="Importar desde Google Calendar (V3)",
    description="""
Importa calendarios desde Google Calendar usando el patrón Abstract Factory.

**Mejoras V3:**
- Arquitectura limpia con separación de responsabilidades
- Manejo de errores mejorado
- Paginación automática de eventos
- Soporte completo para eventos recurrentes

**Requisitos:**
- Token OAuth2 válido de Google
- El token debe tener scope `calendar.readonly` o superior
    """,
    responses={
        201: {"description": "Importación completada (puede ser parcial)"},
        400: {"description": "Error de validación"},
        500: {"description": "Error interno del servidor"},
    },
    tags=["V3: Import"],
)
async def import_from_google(
    request: Annotated[
        GoogleCalendarImportRequestV3,
        Body(
            description="Datos de importación de Google Calendar",
            examples=[{
                "user_external_id": "google_123456789",
                "access_token": "ya29.a0AfH6SMBx...",
                "calendar_ids": ["primary"]
            }]
        )
    ]
) -> ImportResponseV3:
    """
    Importa calendarios desde Google Calendar.
    
    Args:
        request: Token OAuth2 y lista de calendarios a importar
        
    Returns:
        ImportResponseV3: Resultado detallado de la importación
    """
    try:
        service = get_import_service_v3()
        return await service.import_from_google(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Google Calendar: {str(e)}"
        )


@router.post(
    "/teamup",
    response_model=ImportResponseV3,
    status_code=status.HTTP_201_CREATED,
    summary="Importar desde Teamup (V3)",
    description="""
Importa calendarios desde Teamup usando el patrón Abstract Factory.

**Mejoras V3:**
- Arquitectura limpia con separación de responsabilidades
- Manejo de errores mejorado
- API Key opcional (usa servidor por defecto)
- Soporte para subcalendarios

**API Key:**
- Si no se proporciona, se usa la configurada en el servidor
- La API Key del request tiene prioridad sobre la del servidor
    """,
    responses={
        201: {"description": "Importación completada (puede ser parcial)"},
        400: {"description": "Error de validación o API Key faltante"},
        500: {"description": "Error interno del servidor"},
    },
    tags=["V3: Import"],
)
async def import_from_teamup(
    request: Annotated[
        TeamupImportRequestV3,
        Body(
            description="Datos de importación de Teamup",
            examples=[{
                "user_external_id": "uma_admin",
                "calendar_ids": ["ksfogsn8nf72mjdfcv"],
                "api_key": None
            }]
        )
    ]
) -> ImportResponseV3:
    """
    Importa calendarios desde Teamup.
    
    Args:
        request: Calendar keys y API Key opcional
        
    Returns:
        ImportResponseV3: Resultado detallado de la importación
    """
    try:
        service = get_import_service_v3()
        return await service.import_from_teamup(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Teamup: {str(e)}"
        )


# =============================================================================
# ENDPOINT GENÉRICO
# =============================================================================

@router.post(
    "/",
    response_model=ImportResponseV3,
    status_code=status.HTTP_201_CREATED,
    summary="Importar calendarios (genérico)",
    description="""
Endpoint genérico para importar desde cualquier proveedor soportado.

Permite especificar el proveedor dinámicamente en el request.

**Proveedores soportados:**
- `google`: Requiere `access_token` en credentials
- `teamup`: Acepta `api_key` opcional en credentials

**Ejemplo Google:**
```json
{
    "provider": "google",
    "user_external_id": "user_123",
    "calendar_ids": ["primary"],
    "credentials": {
        "access_token": "ya29.xxx..."
    }
}
```

**Ejemplo Teamup:**
```json
{
    "provider": "teamup",
    "user_external_id": "uma_admin",
    "calendar_ids": ["ksfogsn8nf72mjdfcv"],
    "credentials": {}
}
```
    """,
    responses={
        201: {"description": "Importación completada"},
        400: {"description": "Proveedor no soportado o validación fallida"},
        500: {"description": "Error interno"},
    },
    tags=["V3: Import"],
)
async def import_calendars(
    request: Annotated[
        GenericImportRequest,
        Body(description="Request genérico de importación")
    ]
) -> ImportResponseV3:
    """
    Importa calendarios de cualquier proveedor soportado.
    
    Args:
        request: Request con proveedor, calendarios y credenciales
        
    Returns:
        ImportResponseV3: Resultado de la importación
    """
    try:
        service = get_import_service_v3()
        return await service.import_calendars(request)
    except ProviderNotSupportedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en importación: {str(e)}"
        )
