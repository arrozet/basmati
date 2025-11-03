"""Endpoints REST para la gestión de eventos"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.database import get_event_repository
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
from services.event_service import EventService


router = APIRouter()


async def get_event_service(event_repository = Depends(get_event_repository)) -> EventService:
	"""Inyecta una instancia de EventService configurada"""
	return EventService(event_repository)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
	event: EventCreate,
	service: EventService = Depends(get_event_service),
):
	"""Crea un nuevo evento"""
	try:
		return await service.create_event(event)
	except ValueError as exc:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(exc),
		) from exc


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
	event_id: str,
	service: EventService = Depends(get_event_service),
):
	"""Recupera un evento por su ID"""
	event = await service.get_event(event_id)
	if not event:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Evento no encontrado",
		)
	return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
	event_id: str,
	event: EventUpdate,
	service: EventService = Depends(get_event_service),
):
	"""Actualiza los datos de un evento"""
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


@router.delete("/{event_id}", response_model=ResponseMessage)
async def delete_event(
	event_id: str,
	service: EventService = Depends(get_event_service),
):
	"""Elimina un evento"""
	deleted = await service.delete_event(event_id)
	if not deleted:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Evento no encontrado",
		)
	return ResponseMessage(message="Evento eliminado exitosamente")


@router.post(
	"/{event_id}/comments",
	response_model=EventComment,
	status_code=status.HTTP_201_CREATED,
)
async def add_comment(
	event_id: str,
	comment: CommentCreate,
	service: EventService = Depends(get_event_service),
):
	"""Agrega un comentario y dispara notificación"""
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
)
async def add_attachment(
	event_id: str,
	attachment: AttachmentCreate,
	service: EventService = Depends(get_event_service),
):
	"""Agrega un adjunto al evento"""
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


@router.get("/search/by-calendar", response_model=list[EventResponse])
async def search_by_calendar(
	calendar_id: str = Query(..., description="ID del calendario"),
	service: EventService = Depends(get_event_service),
):
	"""Lista eventos pertenecientes a un calendario"""
	events = await service.search_by_calendar(calendar_id)
	return events


@router.get("/search/by-date-range", response_model=list[EventResponse])
async def search_by_date_range(
	start: datetime = Query(..., description="Fecha inicio ISO 8601"),
	end: datetime = Query(..., description="Fecha fin ISO 8601"),
	service: EventService = Depends(get_event_service),
):
	"""Busca eventos dentro de un rango de fechas"""
	try:
		events = await service.search_by_date_range(start, end)
	except ValueError as exc:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(exc),
		) from exc
	return events


@router.get("/{event_id}/comments/users", response_model=list[EventCommentAuthor])
async def get_comment_users(
	event_id: str,
	service: EventService = Depends(get_event_service),
):
	"""Recupera autores que comentaron en el evento"""
	return await service.get_comment_users(event_id)


@router.get("/users/{user_external_id}/commented", response_model=list[EventResponse])
async def get_commented_events_by_user(
	user_external_id: str,
	service: EventService = Depends(get_event_service),
):
	"""Obtiene eventos en los que un usuario comentó"""
	return await service.get_commented_events_by_user(user_external_id)
