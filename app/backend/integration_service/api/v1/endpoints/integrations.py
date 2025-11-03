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


@router.post("/google/import", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_google_calendar(import_request: GoogleCalendarImportRequest):
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


@router.post("/teamup/import", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_teamup(import_request: TeamupImportRequest):
    """
    Importa calendarios desde Teamup creándolos directamente en Basmati.
    
    Args:
        import_request: Datos de importación (api_key, calendar_keys)
        
    Returns:
        ImportResponse: Resultado con IDs de calendarios creados
    """
    try:
        service = get_integration_service()
        return await service.import_from_teamup(import_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Teamup: {str(e)}"
        )
