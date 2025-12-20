"""Endpoints de integraciones - Solo importación de calendarios"""
from fastapi import APIRouter, HTTPException, status, Body
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
    "/google",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar calendarios desde Google Calendar",
    description="Importa calendarios desde Google Calendar creándolos directamente en Basmati.",
    responses={
        201: {"description": "Calendarios importados exitosamente."},
        400: {"description": "Error de validación en los datos de importación."},
        500: {"description": "Error interno del servidor al importar desde Google Calendar."}
    }
)
async def import_from_google_calendar(
    import_request: GoogleCalendarImportRequest = Body(..., description="Datos de importación (token, calendar_ids)")
):
    """
    Importa calendarios desde Google Calendar creándolos directamente en Basmati.
    
    Args:
        import_request: Datos de importación (token, calendar_ids)
        
    Returns:
        ImportResponse: Resultado con IDs de calendarios creados
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
    "/teamup",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar calendarios desde Teamup",
    description="Importa calendarios desde Teamup creándolos directamente en Basmati. La API Key puede proporcionarse en el request (opcional) o usar la configurada en el servidor.",
    responses={
        201: {"description": "Calendarios importados exitosamente."},
        400: {"description": "Error de validación en los datos de importación."},
        500: {"description": "Error interno del servidor al importar desde Teamup."}
    }
)
async def import_from_teamup(
    import_request: TeamupImportRequest = Body(..., description="Datos de importación (user_external_id, calendar_keys, teamup_api_key opcional)")
):
    """
    Importa calendarios desde Teamup creándolos directamente en Basmati.
    
    **Seguridad de API Key:**
    - La API Key puede proporcionarse en el request (opcional)
    - Si no se proporciona, se usa la configurada en el servidor
    
    **Para usar con API Key personalizada:**
    ```json
    {
        "user_external_id": "uma_admin",
        "teamup_api_key": "tu_api_key_aqui",
        "calendar_keys": ["ksfogsn8nf72mjdfcv"]
    }
    ```
    
    Args:
        import_request: Datos de importación (user_external_id, calendar_keys, teamup_api_key opcional)
        
    Returns:
        ImportResponse: Resultado con IDs de calendarios creados y eventos importados
    """
    try:
        service = get_integration_service()
        return await service.import_from_teamup(import_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Teamup: {str(e)}"
        )
