"""Endpoints de integraciones - Solo importación de calendarios"""
from fastapi import APIRouter, HTTPException, status
from schemas.integration import (
    GoogleCalendarImportRequest,
    TeamupImportRequest,
    ImportResponse
)
from services.integration_service import IntegrationService
from core.config import settings

router = APIRouter()


def get_integration_service() -> IntegrationService:
    """Crea una instancia del servicio de integración"""
    return IntegrationService(
        settings.CALENDAR_SERVICE_URL,
        settings.EVENT_SERVICE_URL
    )


@router.post(
    "/google/import",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar desde Google Calendar",
    description="""
Importa calendarios desde **Google Calendar** creándolos directamente en Basmati.

**Proceso:**
1. Se conecta a Google Calendar API usando el token OAuth
2. Obtiene información de los calendarios especificados
3. Crea calendarios equivalentes en Basmati vía **Calendar Service**

**Campos requeridos:**
- **user_external_id**: ID del usuario en Basmati
- **user_display_name**: Nombre del usuario
- **access_token**: Token OAuth de Google
- **calendar_ids**: Lista de IDs de calendarios de Google a importar

**Respuesta:**
- **imported_calendars**: Lista con IDs de Basmati creados
- **failed_imports**: Lista de calendarios que fallaron
"""
)
async def import_from_google_calendar(import_request: GoogleCalendarImportRequest):
    """
    Importa calendarios desde **Google Calendar** creándolos directamente en Basmati.

    **Llamada a servicio externo:** Hace peticiones HTTP a Calendar Service para crear los calendarios.

    Args:
        import_request: Datos de importación (token OAuth, calendar_ids de Google)

    Returns:
        ImportResponse: Resultado con IDs de calendarios creados y fallos

    Raises:
        HTTPException 500: Si hay error al importar desde Google Calendar
    """
    try:
        service = get_integration_service()
        return await service.import_from_google_calendar(import_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Google Calendar: {str(e)}"
        )


@router.post(
    "/teamup/import",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar desde Teamup",
    description="""
Importa calendarios desde **Teamup** creándolos directamente en Basmati.

**Proceso:**
1. Se conecta a Teamup API usando la API key
2. Obtiene información de los calendarios especificados
3. Crea calendarios equivalentes en Basmati vía **Calendar Service**

**Campos requeridos:**
- **user_external_id**: ID del usuario en Basmati
- **user_display_name**: Nombre del usuario
- **api_key**: API key de Teamup
- **calendar_keys**: Lista de calendar keys de Teamup a importar

**Respuesta:**
- **imported_calendars**: Lista con IDs de Basmati creados
- **failed_imports**: Lista de calendarios que fallaron
"""
)
async def import_from_teamup(import_request: TeamupImportRequest):
    """
    Importa calendarios desde **Teamup** creándolos directamente en Basmati.

    **Llamada a servicio externo:** Hace peticiones HTTP a Calendar Service para crear los calendarios.

    Args:
        import_request: Datos de importación (API key, calendar_keys de Teamup)

    Returns:
        ImportResponse: Resultado con IDs de calendarios creados y fallos

    Raises:
        HTTPException 500: Si hay error al importar desde Teamup
    """
    try:
        service = get_integration_service()
        return await service.import_from_teamup(import_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Teamup: {str(e)}"
        )
