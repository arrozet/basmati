"""Endpoints de integraciones"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from schemas.integration import (
    IntegrationSourceResponse,
    GoogleCalendarImportRequest,
    TeamupImportRequest,
    ImportResponse,
    SyncStatusResponse
)
from services.integration_service import IntegrationService
from core.database import get_integration_repository
from core.config import settings

router = APIRouter()

# Dependency: Inyección de dependencias para IntegrationService
async def get_integration_service(
    integration_repository = Depends(get_integration_repository)
) -> IntegrationService:
    """
    Proporciona una instancia de IntegrationService con el Repository.
    
    Args:
        integration_repository: Repository de integraciones (inyectado por FastAPI)
        
    Returns:
        IntegrationService: Instancia del servicio de integración
    """
    return IntegrationService(
        integration_repository,
        settings.CALENDAR_SERVICE_URL,
        settings.EVENT_SERVICE_URL
    )


# ==================== IMPORTACIÓN ====================

@router.post("/google/import", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_google_calendar(
    import_request: GoogleCalendarImportRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    """
    Importa calendarios desde Google Calendar.
    
    Proceso:
    - Autentica con Google Calendar API
    - Obtiene calendarios del usuario
    - Crea calendarios en Basmati
    - Importa eventos
    
    Args:
        import_request: Datos de importación (token, calendar_ids)
        service: Servicio de integración (inyectado por FastAPI)
        
    Returns:
        ImportResponse: Resultado de la importación con fuentes creadas
    """
    try:
        return await service.import_from_google_calendar(import_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Google Calendar: {str(e)}"
        )


@router.post("/teamup/import", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def import_from_teamup(
    import_request: TeamupImportRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    """
    Importa calendarios desde Teamup.
    
    Proceso:
    - Autentica con Teamup API
    - Obtiene calendarios del usuario
    - Crea calendarios en Basmati
    - Importa eventos
    
    Args:
        import_request: Datos de importación (api_key, calendar_keys)
        service: Servicio de integración (inyectado por FastAPI)
        
    Returns:
        ImportResponse: Resultado de la importación con fuentes creadas
    """
    try:
        return await service.import_from_teamup(import_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar desde Teamup: {str(e)}"
        )


# ==================== BÚSQUEDAS PARAMETRIZADAS ====================

@router.get("/sources", response_model=List[IntegrationSourceResponse])
async def get_integration_sources(
    external_id: str = Query(..., description="External ID del usuario"),
    service: IntegrationService = Depends(get_integration_service)
):
    """
    Obtiene todas las fuentes de integración de un usuario (parametrized query 1).
    
    Args:
        external_id: ID externo del usuario
        service: Servicio de integración (inyectado por FastAPI)
        
    Returns:
        List[IntegrationSourceResponse]: Lista de fuentes del usuario
    """
    try:
        sources = await service.get_user_sources(external_id)
        return sources
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener fuentes: {str(e)}"
        )


@router.get("/sync_status", response_model=SyncStatusResponse)
async def get_sync_status(
    source_id: str = Query(..., description="ID de la fuente de integración"),
    service: IntegrationService = Depends(get_integration_service)
):
    """
    Obtiene el estado de sincronización de una fuente (parametrized query 2).
    
    Args:
        source_id: ID de la fuente
        service: Servicio de integración (inyectado por FastAPI)
        
    Returns:
        SyncStatusResponse: Estado de sincronización
    """
    sync_status = await service.get_sync_status(source_id)
    if not sync_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuente de integración no encontrada"
        )
    
    return sync_status


# ==================== DETALLES DE FUENTE ====================

@router.get("/sources/{source_id}", response_model=IntegrationSourceResponse)
async def get_source_details(
    source_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """
    Obtiene los detalles de una fuente de integración específica.
    
    Args:
        source_id: ID de la fuente
        service: Servicio de integración (inyectado por FastAPI)
        
    Returns:
        IntegrationSourceResponse: Detalles de la fuente
    """
    source = await service.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuente de integración no encontrada"
        )
    
    return source
