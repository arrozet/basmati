"""Endpoints de notificaciones"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from schemas.notification import NotificationCreate, NotificationResponse
from schemas.common import ResponseMessage
from services.notification_service import NotificationService
from core.database import get_notification_repository

router = APIRouter()

async def get_notification_service(notification_repository = Depends(get_notification_repository)) -> NotificationService:
    """
    Proporciona una instancia de NotificationService con el Repository.
    
    Args:
        notification_repository: Repository de notificaciones (inyectado por FastAPI)
        
    Returns:
        NotificationService: Instancia del servicio de notificaciones
    """
    return NotificationService(notification_repository)

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate, 
    service: NotificationService = Depends(get_notification_service)
):
    """
    Crea una nueva notificación (llamado por EventService u otros servicios).
    
    Args:
        notification: Datos de la notificación a crear
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        NotificationResponse: La notificación creada con su ID
        
    Raises:
        HTTPException 400: Si hay error al crear la notificación
    """
    try:
        return await service.create_notification(notification)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/user/{user_id}", response_model=list[NotificationResponse])
async def get_user_notifications(
    user_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    """
    Obtiene todas las notificaciones de un usuario por su external_id.
    
    Args:
        user_id: External ID del usuario
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        list[NotificationResponse]: Lista de notificaciones del usuario (ordenadas por fecha desc)
    """
    notifications = await service.get_user_notifications(user_id)
    return notifications

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    """
    Marca una notificación como leída.
    
    Args:
        notification_id: ID de la notificación
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        NotificationResponse: Notificación actualizada
        
    Raises:
        HTTPException 404: Si la notificación no existe
    """
    notification = await service.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    return notification

@router.put("/user/{user_id}/read-all", response_model=ResponseMessage)
async def mark_all_as_read(
    user_id: str,
    service: NotificationService = Depends(get_notification_service)
):
    """
    Marca todas las notificaciones de un usuario como leídas.
    
    Args:
        user_id: External ID del usuario
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        ResponseMessage: Mensaje con el número de notificaciones actualizadas
    """
    count = await service.mark_all_as_read(user_id)
    return ResponseMessage(message=f"{count} notificaciones marcadas como leídas")

@router.get("/search/unread", response_model=list[NotificationResponse])
async def search_unread_notifications(
    user_id: str = Query(..., description="External ID del usuario"),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Busca notificaciones no leídas de un usuario (parametrized query 1).
    
    Args:
        user_id: External ID del usuario
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        list[NotificationResponse]: Lista de notificaciones no leídas
    """
    notifications = await service.search_unread(user_id)
    return notifications

@router.get("/search/by-event", response_model=list[NotificationResponse])
async def search_by_event(
    event_id: str = Query(..., description="ID del evento relacionado"),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Busca notificaciones relacionadas con un evento específico (parametrized query 2).
    
    Args:
        event_id: ID del evento relacionado
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        list[NotificationResponse]: Lista de notificaciones del evento
    """
    notifications = await service.search_by_event(event_id)
    return notifications

@router.get("/search/by-type", response_model=list[NotificationResponse])
async def search_by_type(
    type: str = Query(..., description="Tipo de notificación (NEW_COMMENT, EVENT_UPDATE, CALENDAR_INVITE, EVENT_REMINDER)"),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Busca notificaciones por tipo.
    
    Args:
        type: Tipo de notificación
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        list[NotificationResponse]: Lista de notificaciones del tipo especificado
    """
    notifications = await service.search_by_type(type)
    return notifications

@router.get("/search/by-calendar", response_model=list[NotificationResponse])
async def search_by_calendar(
    calendar_id: str = Query(..., description="ID del calendario relacionado"),
    service: NotificationService = Depends(get_notification_service)
):
    """
    Busca notificaciones relacionadas con un calendario específico.
    
    Args:
        calendar_id: ID del calendario relacionado
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        list[NotificationResponse]: Lista de notificaciones del calendario
    """
    notifications = await service.search_by_calendar(calendar_id)
    return notifications

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    """
    Obtiene una notificación por su ID.
    
    Args:
        notification_id: ID de la notificación
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        NotificationResponse: Notificación encontrada
        
    Raises:
        HTTPException 404: Si la notificación no existe
    """
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    return notification

@router.delete("/{notification_id}", response_model=ResponseMessage)
async def delete_notification(
    notification_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    """
    Elimina una notificación del sistema.
    
    Args:
        notification_id: ID de la notificación
        service: Servicio de notificaciones (inyectado por FastAPI)
        
    Returns:
        ResponseMessage: Mensaje de confirmación
        
    Raises:
        HTTPException 404: Si la notificación no existe
    """
    deleted = await service.delete_notification(notification_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    return ResponseMessage(message="Notificación eliminada exitosamente")

