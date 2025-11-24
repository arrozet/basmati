"""Endpoints REST para la gestión de eventos"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from core.database import get_event_repository, get_database
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
from services.event_service_v2 import EventServiceV2
from repositories.event_repository_v2 import EventRepositoryV2


router = APIRouter()



from core.database import get_database

async def get_event_service_v2(db = Depends(get_database)) -> EventServiceV2:
    repository = EventRepositoryV2(db)
    return EventServiceV2(repository)


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
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Crea un nuevo evento en el sistema.
	
	Args:
		event: Datos del evento a crear
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		EventResponse: El evento creado con su ID
		
	Raises:
		HTTPException 400: Si los datos del evento son inválidos
	"""
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
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Obtiene un evento por su ID.
	
	Args:
		event_id: ID del evento
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		EventResponse: Evento encontrado
		
	Raises:
		HTTPException 404: Si el evento no existe
	"""
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
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Actualiza los datos de un evento existente.
	
	Args:
		event_id: ID del evento
		event: Datos a actualizar
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		EventResponse: Evento actualizado
		
	Raises:
		HTTPException 400: Si los datos del evento son inválidos
		HTTPException 404: Si el evento no existe
	"""
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
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Elimina un evento del sistema.
	
	Args:
		event_id: ID del evento
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		ResponseMessage: Mensaje de confirmación
		
	Raises:
		HTTPException 404: Si el evento no existe
	"""
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
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Agrega un comentario a un evento y dispara notificación.
	
	Args:
		event_id: ID del evento
		comment: Datos del comentario a crear
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		EventComment: El comentario creado
		
	Raises:
		HTTPException 400: Si los datos del comentario son inválidos
		HTTPException 404: Si el evento no existe
	"""
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
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Agrega un adjunto (archivo/documento) a un evento.
	
	Args:
		event_id: ID del evento
		attachment: Datos del adjunto a crear
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		EventAttachment: El adjunto creado
		
	Raises:
		HTTPException 400: Si los datos del adjunto son inválidos
		HTTPException 404: Si el evento no existe
	"""
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


@router.get(
	"/search/by-calendar",
	response_model=list[EventResponse],
	summary="Buscar eventos por calendario",
	description="Lista todos los eventos pertenecientes a un calendario específico (parametrized query 1).",
	responses={
		200: {"description": "Lista de eventos del calendario."},
		500: {"description": "Error interno del servidor."}
	}
)
async def search_by_calendar(
	calendar_id: str = Query(..., description="ID del calendario"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Lista todos los eventos pertenecientes a un calendario específico.
	
	Args:
		calendar_id: ID del calendario
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos del calendario
	"""
	events = await service.search_by_calendar(calendar_id)
	return events


@router.get(
	"/search/by-date-range",
	response_model=list[EventResponse],
	summary="Buscar eventos por rango de fechas",
	description="Busca eventos dentro de un rango de fechas (parametrized query 2).",
	responses={
		200: {"description": "Lista de eventos en el rango de fechas."},
		400: {"description": "Error de validación en el rango de fechas."},
		500: {"description": "Error interno del servidor."}
	}
)
async def search_by_date_range(
	start: datetime = Query(..., description="Fecha inicio ISO 8601"),
	end: datetime = Query(..., description="Fecha fin ISO 8601"),
	calendar_id: str | None = Query(None, description="ID del calendario (opcional)"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Busca eventos dentro de un rango de fechas.
	
	Args:
		start: Fecha de inicio del rango (formato ISO 8601)
		end: Fecha de fin del rango (formato ISO 8601)
		calendar_id: ID del calendario (opcional)
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos en el rango de fechas
		
	Raises:
		HTTPException 400: Si el rango de fechas es inválido
	"""
	try:
		events = await service.search_by_date_range(start, end, calendar_id)
	except ValueError as exc:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(exc),
		) from exc
	return events


@router.get(
	"/{event_id}/comments/users",
	response_model=list[EventCommentAuthor],
	summary="Obtener usuarios que comentaron en un evento",
	description="Recupera los autores que han comentado en un evento específico (relationship query 1).",
	responses={
		200: {"description": "Lista de autores que comentaron en el evento."},
		500: {"description": "Error interno del servidor."}
	}
)
async def get_comment_users(
	event_id: str = Path(..., description="ID único del evento"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Recupera los autores que han comentado en un evento específico.
	
	Args:
		event_id: ID del evento
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventCommentAuthor]: Lista de autores que comentaron en el evento
	"""
	return await service.get_comment_users(event_id)


@router.get(
	"/users/{user_external_id}/commented",
	response_model=list[EventResponse],
	summary="Obtener eventos comentados por un usuario",
	description="Obtiene todos los eventos en los que un usuario ha comentado (relationship query 2).",
	responses={
		200: {"description": "Lista de eventos en los que el usuario comentó."},
		500: {"description": "Error interno del servidor."}
	}
)
async def get_commented_events_by_user(
	user_external_id: str = Path(..., description="ID externo del usuario"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Obtiene todos los eventos en los que un usuario ha comentado.
	
	Args:
		user_external_id: ID externo del usuario
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos en los que el usuario comentó
	"""
	return await service.get_commented_events_by_user(user_external_id)


@router.get(
	"/search/by-text",
	response_model=list[EventResponse],
	summary="Búsqueda full-text en eventos",
	description="Realiza una búsqueda full-text en eventos. Busca en los campos: title, description, location.address y location.place_name.",
	responses={
		200: {"description": "Lista de eventos que coinciden con la búsqueda."},
		500: {"description": "Error interno del servidor."}
	}
)
async def search_by_text(
	query: str = Query(..., description="Término de búsqueda"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Realiza una búsqueda full-text en eventos.
	
	Busca en los campos: title, description, location.address y location.place_name.
	
	Args:
		query: Término de búsqueda
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos que coinciden con la búsqueda
	"""
	return await service.search_by_text(query)


@router.get(
	"/search/by-calendar-title",
	response_model=list[EventResponse],
	summary="Buscar eventos por título del calendario",
	description="Busca eventos por título del calendario (usando campo denormalizado).",
	responses={
		200: {"description": "Lista de eventos que pertenecen a calendarios con ese título."},
		500: {"description": "Error interno del servidor."}
	}
)
async def search_by_calendar_title(
	calendar_title: str = Query(..., description="Título del calendario"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Busca eventos por título del calendario (usando campo denormalizado).
	
	Args:
		calendar_title: Título del calendario
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos que pertenecen a calendarios con ese título
	"""
	return await service.search_by_calendar_title(calendar_title)


@router.get(
	"/search/by-location",
	response_model=list[EventResponse],
	summary="Buscar eventos por ubicación",
	description="Busca eventos por ubicación (address o place_name).",
	responses={
		200: {"description": "Lista de eventos que coinciden con la ubicación buscada."},
		500: {"description": "Error interno del servidor."}
	}
)
async def search_by_location(
	location_query: str = Query(..., description="Término de búsqueda para ubicación"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Busca eventos por ubicación (address o place_name).
	
	Args:
		location_query: Término de búsqueda para ubicación
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos que coinciden con la ubicación buscada
	"""
	return await service.search_by_location(location_query)


@router.get(
	"/search/advanced",
	response_model=list[EventResponse],
	summary="Búsqueda avanzada de eventos",
	description="Busca eventos por título, organizador (título de calendario) y palabras clave (descripción).",
	responses={
		200: {"description": "Lista de eventos que coinciden con la búsqueda."},
		500: {"description": "Error interno del servidor."}
	}
)
async def search_advanced(
	title: str | None = Query(None, description="Título del evento"),
	organizer: str | None = Query(None, description="Organizador (Título del calendario)"),
	keywords: str | None = Query(None, description="Palabras clave (Descripción)"),
	service: EventServiceV2 = Depends(get_event_service_v2),
):
	"""
	Realiza una búsqueda avanzada en eventos.
	
	Args:
		title: Título del evento
		organizer: Organizador (se busca en calendar_title)
		keywords: Palabras clave (se busca en description)
		service: Servicio de eventos (inyectado por FastAPI)
		
	Returns:
		list[EventResponse]: Lista de eventos que coinciden con la búsqueda
	"""
	return await service.search_advanced(title=title, calendar_title=organizer, description=keywords)
