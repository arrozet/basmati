"""
Endpoints de importación V3 - Abstract Factory Pattern

Este módulo expone los endpoints de la API V3 para importación de calendarios
utilizando la implementación con patrón Abstract Factory.
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import Annotated
import logging
import httpx

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
logger = logging.getLogger(__name__)


def get_import_service_v3() -> ImportServiceV3:
    """
    Crea una instancia del servicio de importación V3.
    
    Inyecta las URLs de servicios y la API Key de Teamup desde la configuración.
    """
    return ImportServiceV3(
        calendar_service_url=settings.CALENDAR_SERVICE_URL,
        event_service_url=settings.EVENT_SERVICE_URL,
        default_teamup_api_key=settings.teamup_api_key,
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
    except httpx.HTTPStatusError as e:
        # Preservar códigos de estado HTTP de APIs externas cuando sea posible
        status_code = e.response.status_code
        error_detail = f"Error de API externa al importar desde Google Calendar: {str(e)}"
        logger.error(f"HTTP error {status_code} en importación de Google: {e}", exc_info=True)
        
        # Mapear códigos comunes a códigos HTTP apropiados
        if status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de Google inválido o expirado"
            )
        elif status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sin permisos para acceder al calendario de Google"
            )
        elif status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendario de Google no encontrado"
            )
        elif status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Límite de tasa de Google Calendar excedido. Intenta más tarde"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_detail
            )
    except httpx.RequestError as e:
        # Errores de conexión/red
        logger.error(f"Error de conexión al importar desde Google Calendar: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con Google Calendar. Verifica tu conexión."
        )
    except Exception as e:
        # Errores inesperados - log completo para debugging
        logger.exception(f"Error inesperado al importar desde Google Calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al importar desde Google Calendar: {str(e)}"
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
    except httpx.HTTPStatusError as e:
        # Preservar códigos de estado HTTP de APIs externas cuando sea posible
        status_code = e.response.status_code
        error_detail = f"Error de API externa al importar desde Teamup: {str(e)}"
        logger.error(f"HTTP error {status_code} en importación de Teamup: {e}", exc_info=True)
        
        # Mapear códigos comunes a códigos HTTP apropiados
        if status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key de Teamup inválida"
            )
        elif status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sin permisos para acceder al calendario de Teamup"
            )
        elif status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendario de Teamup no encontrado"
            )
        elif status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Límite de tasa de Teamup excedido. Intenta más tarde"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_detail
            )
    except httpx.RequestError as e:
        # Errores de conexión/red
        logger.error(f"Error de conexión al importar desde Teamup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con Teamup. Verifica tu conexión."
        )
    except Exception as e:
        # Errores inesperados - log completo para debugging
        logger.exception(f"Error inesperado al importar desde Teamup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al importar desde Teamup: {str(e)}"
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
    except httpx.HTTPStatusError as e:
        # Preservar códigos de estado HTTP de APIs externas cuando sea posible
        status_code = e.response.status_code
        error_detail = f"Error de API externa en importación: {str(e)}"
        logger.error(f"HTTP error {status_code} en importación genérica: {e}", exc_info=True)
        
        # Mapear códigos comunes a códigos HTTP apropiados
        if status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas para el proveedor seleccionado"
            )
        elif status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sin permisos para acceder al calendario del proveedor"
            )
        elif status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendario no encontrado en el proveedor"
            )
        elif status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Límite de tasa del proveedor excedido. Intenta más tarde"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_detail
            )
    except httpx.RequestError as e:
        # Errores de conexión/red
        logger.error(f"Error de conexión en importación genérica: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con el proveedor. Verifica tu conexión."
        )
    except Exception as e:
        # Errores inesperados - log completo para debugging
        logger.exception(f"Error inesperado en importación genérica: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en importación: {str(e)}"
        )
