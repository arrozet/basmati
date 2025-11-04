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


@router.get(
	"/search/by-text",
	response_model=list[EventResponse],
	summary="Búsqueda full-text en eventos",
	description="""
Realiza una búsqueda full-text en eventos.

Busca en los siguientes campos:
- **title**: Título del evento
- **description**: Descripción del evento
- **location.address**: Dirección completa del evento
- **location.place_name**: Nombre del lugar

La búsqueda es case-insensitive y utiliza expresiones regulares.

**Ejemplo de uso:**
- `query=conferencia` → encuentra "Conferencia de IA", "Conferencia Anual", etc.
- `query=sevilla` → encuentra eventos en Sevilla o relacionados con la ciudad
- `query=tecnología` → encuentra eventos sobre tecnología en título o descripción
"""
)
async def search_by_text(
	query: str = Query(
		...,
		description="Término de búsqueda",
		example="conferencia",
		min_length=1
	),
	service: EventService = Depends(get_event_service),
):
	"""
	Busca eventos por texto.

	Args:
		query: Término de búsqueda
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		list[EventResponse]: Lista de eventos encontrados
	"""
	return await service.search_by_text(query)


@router.get(
	"/search/by-calendar-title",
	response_model=list[EventResponse],
	summary="Buscar eventos por título de calendario",
	description="""
Busca eventos utilizando el título del calendario al que pertenecen.

Utiliza el campo denormalizado **calendar_title** para realizar
búsquedas eficientes sin necesidad de join con la colección de calendarios.

La búsqueda es parcial y case-insensitive.

**Ejemplo de uso:**
- `calendar_title=Universidad` → encuentra eventos de calendarios "Universidad de Sevilla", "Universidad Complutense", etc.
- `calendar_title=Deportes` → encuentra eventos de calendarios deportivos
- `calendar_title=Conferencias` → encuentra eventos de calendarios de conferencias
"""
)
async def search_by_calendar_title(
	calendar_title: str = Query(
		...,
		description="Título o parte del título del calendario",
		example="Universidad",
		min_length=1
	),
	service: EventService = Depends(get_event_service),
):
	"""
	Busca eventos por título del calendario.

	Args:
		calendar_title: Título del calendario a buscar
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		list[EventResponse]: Eventos del calendario con ese título
	"""
	return await service.search_by_calendar_title(calendar_title)


@router.get(
	"/search/by-location",
	response_model=list[EventResponse],
	summary="Buscar eventos por ubicación",
	description="""
Busca eventos por su ubicación geográfica.

Busca en los siguientes campos del subdocumento **location**:
- **location.address**: Dirección completa del evento
- **location.place_name**: Nombre del lugar o edificio

La búsqueda es case-insensitive y utiliza expresiones regulares.
Útil para encontrar eventos en una ciudad, edificio o lugar específico.

**Ejemplo de uso:**
- `location_query=Sevilla` → encuentra eventos en "Calle Real, Sevilla", "Universidad de Sevilla", etc.
- `location_query=Aula Magna` → encuentra eventos en el Aula Magna
- `location_query=Campus` → encuentra eventos en cualquier campus universitario
"""
)
async def search_by_location(
	location_query: str = Query(
		...,
		description="Término de búsqueda para la ubicación",
		example="Sevilla",
		min_length=1
	),
	service: EventService = Depends(get_event_service),
):
	"""
	Busca eventos por ubicación.

	Args:
		location_query: Término de búsqueda para la ubicación
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		list[EventResponse]: Eventos en esa ubicación
	"""
	return await service.search_by_location(location_query)
