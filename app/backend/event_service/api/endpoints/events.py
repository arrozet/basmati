"""Endpoints REST unificados para la gestión de eventos.

Este módulo contiene TODOS los endpoints de eventos, compartidos entre
todas las versiones de la API. La versión específica se determina
mediante la fábrica inyectada.

Patrón utilizado: Abstract Factory + Dependency Injection
- Los endpoints son genéricos y trabajan con interfaces (IEventService)
- La fábrica inyectada determina qué implementación concreta se usa
- Esto elimina la duplicación de código entre v1/ y v2/
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from core.interface import IEventService
from schemas.common import ResponseMessage
from schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    CommentCreate,
    AttachmentCreate,
    EventComment,
    EventAttachment,
    EventCommentAuthor,
)


def create_events_router(get_service_dependency) -> APIRouter:
    """Crea un router de eventos con la dependencia de servicio especificada.
    
    Esta función permite crear routers para diferentes versiones de la API,
    cada uno usando su propia fábrica para inyectar el servicio correcto.
    
    Args:
        get_service_dependency: Función de dependencia que retorna IEventService
        
    Returns:
        APIRouter: Router configurado con todos los endpoints de eventos
        
    Ejemplo:
        # En v1/router.py
        from core.factory import EventServiceFactoryV1
        
        async def get_service_v1(db = Depends(get_database)):
            return EventServiceFactoryV1(db).create_service()
        
        router = create_events_router(get_service_v1)
    """
    router = APIRouter()

    # ========================================================================
    # CRUD BÁSICO
    # ========================================================================

    @router.post(
        "",
        response_model=EventResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Crear un nuevo evento",
        description="Crea un nuevo evento en el sistema.",
        responses={
            201: {"description": "Evento creado exitosamente."},
            400: {"description": "Error de validación en los datos del evento."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def create_event(
        event: EventCreate = Body(..., description="Datos del evento a crear"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Crea un nuevo evento en el sistema."""
        try:
            return await service.create_event(event)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    @router.get(
        "/{event_id}",
        response_model=EventResponse,
        summary="Obtener un evento por ID",
        description="Obtiene un evento por su ID.",
        responses={
            200: {"description": "Evento encontrado y devuelto exitosamente."},
            404: {"description": "El evento con el ID especificado no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def get_event(
        event_id: str = Path(..., description="ID único del evento"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Obtiene un evento por su ID."""
        event = await service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado",
            )
        return event

    @router.put(
        "/{event_id}",
        response_model=EventResponse,
        summary="Actualizar un evento",
        description="Actualiza los datos de un evento existente.",
        responses={
            200: {"description": "Evento actualizado exitosamente."},
            400: {"description": "Error de validación en los datos del evento."},
            404: {"description": "El evento con el ID especificado no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def update_event(
        event_id: str = Path(..., description="ID único del evento"),
        event: EventUpdate = Body(..., description="Datos a actualizar del evento"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Actualiza los datos de un evento existente."""
        try:
            updated_event = await service.update_event(event_id, event)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado",
            )
        return updated_event

    @router.delete(
        "/{event_id}",
        response_model=ResponseMessage,
        summary="Eliminar un evento",
        description="Elimina un evento del sistema.",
        responses={
            200: {"description": "Evento eliminado exitosamente."},
            404: {"description": "El evento con el ID especificado no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def delete_event(
        event_id: str = Path(..., description="ID único del evento"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Elimina un evento del sistema."""
        deleted = await service.delete_event(event_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado",
            )
        return ResponseMessage(message="Evento eliminado exitosamente")

    # ========================================================================
    # COMENTARIOS Y ADJUNTOS
    # ========================================================================

    @router.post(
        "/{event_id}/comments",
        response_model=EventComment,
        status_code=status.HTTP_201_CREATED,
        summary="Agregar comentario a un evento",
        description="Agrega un comentario a un evento y dispara notificación.",
        responses={
            201: {"description": "Comentario agregado exitosamente."},
            400: {"description": "Error de validación en los datos del comentario."},
            404: {"description": "El evento con el ID especificado no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def add_comment(
        event_id: str = Path(..., description="ID único del evento"),
        comment: CommentCreate = Body(..., description="Datos del comentario a crear"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Agrega un comentario a un evento y dispara notificación."""
        try:
            new_comment = await service.add_comment(event_id, comment)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if not new_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado",
            )
        return new_comment

    @router.post(
        "/{event_id}/attachments",
        response_model=EventAttachment,
        status_code=status.HTTP_201_CREATED,
        summary="Agregar adjunto a un evento",
        description="Agrega un adjunto (archivo/documento) a un evento.",
        responses={
            201: {"description": "Adjunto agregado exitosamente."},
            400: {"description": "Error de validación en los datos del adjunto."},
            404: {"description": "El evento con el ID especificado no existe."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def add_attachment(
        event_id: str = Path(..., description="ID único del evento"),
        attachment: AttachmentCreate = Body(..., description="Datos del adjunto a crear"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Agrega un adjunto (archivo/documento) a un evento."""
        try:
            new_attachment = await service.add_attachment(event_id, attachment)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if not new_attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado",
            )
        return new_attachment

    # ========================================================================
    # BÚSQUEDAS PARAMETRIZADAS
    # ========================================================================

    @router.get(
        "/search/by-calendar",
        response_model=list[EventResponse],
        summary="Buscar eventos por calendario",
        description="Lista todos los eventos pertenecientes a un calendario específico.",
        responses={
            200: {"description": "Lista de eventos del calendario."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_calendar(
        calendar_id: str = Query(..., description="ID del calendario"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Lista todos los eventos pertenecientes a un calendario específico."""
        return await service.search_by_calendar(calendar_id)

    @router.get(
        "/search/by-date-range",
        response_model=list[EventResponse],
        summary="Buscar eventos por rango de fechas",
        description="Busca eventos dentro de un rango de fechas. En V2, permite filtrar por calendario.",
        responses={
            200: {"description": "Lista de eventos en el rango de fechas."},
            400: {"description": "Error de validación en el rango de fechas."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def search_by_date_range(
        start: datetime = Query(..., description="Fecha inicio ISO 8601"),
        end: datetime = Query(..., description="Fecha fin ISO 8601"),
        calendar_id: str | None = Query(None, description="ID del calendario (opcional, solo V2)"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Busca eventos dentro de un rango de fechas."""
        try:
            return await service.search_by_date_range(start, end, calendar_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    # ========================================================================
    # QUERIES DE RELACIÓN
    # ========================================================================

    @router.get(
        "/{event_id}/comments/users",
        response_model=list[EventCommentAuthor],
        summary="Obtener usuarios que comentaron en un evento",
        description="Recupera los autores que han comentado en un evento específico.",
        responses={
            200: {"description": "Lista de autores."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def get_comment_users(
        event_id: str = Path(..., description="ID único del evento"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Recupera los autores que han comentado en un evento."""
        return await service.get_comment_users(event_id)

    @router.get(
        "/users/{user_external_id}/commented",
        response_model=list[EventResponse],
        summary="Obtener eventos comentados por un usuario",
        description="Obtiene todos los eventos en los que un usuario ha comentado.",
        responses={
            200: {"description": "Lista de eventos."},
            500: {"description": "Error interno del servidor."}
        }
    )
    async def get_commented_events_by_user(
        user_external_id: str = Path(..., description="ID externo del usuario"),
        service: IEventService = Depends(get_service_dependency),
    ):
        """Obtiene todos los eventos en los que un usuario ha comentado."""
        return await service.get_commented_events_by_user(user_external_id)

    return router

