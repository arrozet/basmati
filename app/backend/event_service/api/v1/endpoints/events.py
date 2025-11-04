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


@router.post(
	"",
	response_model=EventResponse,
	status_code=status.HTTP_201_CREATED,
	summary="Crear un nuevo evento",
	description="""
Crea un nuevo evento en el sistema.

**Campos requeridos:**
- **calendar_id**: ID del calendario al que pertenece
- **title**: Título del evento
- **creator_external_id**: ID externo del creador
- **start_time**: Fecha y hora de inicio (ISO 8601)
- **end_time**: Fecha y hora de fin (ISO 8601)

**Campos opcionales:**
- **description**: Descripción del evento
- **location**: Ubicación con address, coordinates, place_name, map_provider
- **visibility**: Visibilidad ("public", "private", "inherited")
- **recurrence**: Patrón de recurrencia (diario, semanal, mensual, etc.)
- **calendar_title**: Título del calendario (denormalizado)

**Validación:**
- `end_time` debe ser posterior a `start_time`
- `calendar_id` debe ser un ObjectId válido

**Ejemplo de uso:**
```json
{
  "calendar_id": "507f1f77bcf86cd799439011",
  "title": "Conferencia de IA 2024",
  "description": "Conferencia sobre Inteligencia Artificial",
  "creator_external_id": "google_123456",
  "start_time": "2024-06-01T09:00:00Z",
  "end_time": "2024-06-01T18:00:00Z",
  "location": {
    "address": "Av. Reina Mercedes, 41012 Sevilla",
    "latitude": 37.3569,
    "longitude": -5.9869,
    "place_name": "ETSII - Universidad de Sevilla",
    "map_provider": "google_maps"
  },
  "visibility": "public"
}
```
"""
)
async def create_event(
	event: EventCreate,
	service: EventService = Depends(get_event_service),
):
	"""
	Crea un nuevo evento.

	Args:
		event: Datos del evento a crear
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		EventResponse: El evento creado con su ID

	Raises:
		HTTPException 400: Si hay error de validación (ej: end_time <= start_time)
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
	description="""
Obtiene un evento específico por su ID de MongoDB.

Devuelve toda la información del evento incluyendo:
- **Metadatos**: título, descripción, fechas
- **Ubicación**: address, coordinates, place_name
- **Relaciones**: calendar_id, creator_external_id
- **Comentarios**: array completo de comentarios
- **Adjuntos**: array completo de archivos adjuntos
- **Recurrencia**: patrón de recurrencia (si aplica)
- **Timestamps**: created_at, updated_at
"""
)
async def get_event(
	event_id: str,
	service: EventService = Depends(get_event_service),
):
	"""
	Recupera un evento por su ID.

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
	description="""
Actualiza un evento existente.

**Campos actualizables:**
- **title**, **description**: Texto del evento
- **start_time**, **end_time**: Fechas (con validación)
- **location**: Ubicación completa
- **visibility**: Visibilidad del evento
- **recurrence**: Patrón de recurrencia

**Nota:** Actualización parcial - solo envía los campos a modificar.
El campo `updated_at` se actualiza automáticamente.

**Validación:**
- Si actualizas `start_time` o `end_time`, se valida que end > start
"""
)
async def update_event(
	event_id: str,
	event: EventUpdate,
	service: EventService = Depends(get_event_service),
):
	"""
	Actualiza los datos de un evento.

	Args:
		event_id: ID del evento
		event: Datos a actualizar
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		EventResponse: Evento actualizado

	Raises:
		HTTPException 400: Si la validación falla
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
	description="""
Elimina un evento del sistema de forma permanente.

**Importante:**
- La eliminación es **permanente** y no se puede deshacer
- Se eliminan también **todos los comentarios** y **adjuntos** asociados
- Las notificaciones relacionadas NO se eliminan automáticamente
"""
)
async def delete_event(
	event_id: str,
	service: EventService = Depends(get_event_service),
):
	"""
	Elimina un evento.

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
	description="""
Agrega un comentario a un evento y dispara notificación al creador.

**Campos requeridos:**
- **author_external_id**: ID del autor del comentario
- **author_display_name**: Nombre visible del autor
- **text**: Contenido del comentario

**Funcionalidad automática:**
- Se asigna automáticamente un ID único al comentario
- Se registra la fecha de creación (`created_at`)
- **Se envía notificación** al creador del evento (si no es el mismo autor)

**Ejemplo de uso:**
```json
{
  "author_external_id": "google_123456",
  "author_display_name": "Juan Pérez",
  "text": "¿A qué hora empieza exactamente?"
}
```
"""
)
async def add_comment(
	event_id: str,
	comment: CommentCreate,
	service: EventService = Depends(get_event_service),
):
	"""
	Agrega un comentario y dispara notificación.

	Args:
		event_id: ID del evento
		comment: Datos del comentario
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		EventComment: Comentario creado

	Raises:
		HTTPException 400: Si hay error de validación
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
	description="""
Agrega un archivo adjunto a un evento.

**Campos requeridos:**
- **filename**: Nombre del archivo
- **url**: URL del archivo (almacenado externamente)
- **size**: Tamaño en bytes
- **mime_type**: Tipo MIME (ej: "image/png", "application/pdf")
- **uploaded_by**: ID del usuario que sube el archivo

**Campos opcionales:**
- **is_image**: Si es una imagen (default: false)
- **thumbnail_url**: URL de miniatura (para imágenes)

**Nota:** Este endpoint solo guarda los **metadatos** del archivo.
El archivo debe estar previamente subido a un servicio de almacenamiento externo.

**Ejemplo de uso:**
```json
{
  "filename": "presentacion.pdf",
  "url": "https://storage.example.com/files/abc123.pdf",
  "size": 2048576,
  "mime_type": "application/pdf",
  "uploaded_by": "google_123456"
}
```
"""
)
async def add_attachment(
	event_id: str,
	attachment: AttachmentCreate,
	service: EventService = Depends(get_event_service),
):
	"""
	Agrega un adjunto al evento.

	Args:
		event_id: ID del evento
		attachment: Metadatos del adjunto
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		EventAttachment: Adjunto creado

	Raises:
		HTTPException 400: Si hay error de validación
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
	description="""
Lista todos los eventos pertenecientes a un calendario específico.

Utiliza el campo **calendar_id** para encontrar eventos.

**Ejemplo de uso:**
- `calendar_id=507f1f77bcf86cd799439011` → todos los eventos de ese calendario

**Caso de uso:** Mostrar todos los eventos de un calendario en vista de lista o agenda.
"""
)
async def search_by_calendar(
	calendar_id: str = Query(
		...,
		description="ID del calendario",
		example="507f1f77bcf86cd799439011",
		min_length=24,
		max_length=24
	),
	service: EventService = Depends(get_event_service),
):
	"""
	Lista eventos pertenecientes a un calendario.

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
	description="""
Busca eventos que ocurren dentro de un rango de fechas específico.

**Validación:**
- `end` debe ser posterior a `start`
- Fechas en formato ISO 8601

**Lógica de búsqueda:**
Encuentra eventos donde:
- `event.start_time < range.end` Y
- `event.end_time > range.start`

Esto incluye eventos que:
- Empiezan dentro del rango
- Terminan dentro del rango
- Abarcan todo el rango

**Ejemplo de uso:**
- `start=2024-06-01T00:00:00Z&end=2024-06-30T23:59:59Z` → eventos en junio 2024
"""
)
async def search_by_date_range(
	start: datetime = Query(..., description="Fecha inicio (ISO 8601)", example="2024-06-01T00:00:00Z"),
	end: datetime = Query(..., description="Fecha fin (ISO 8601)", example="2024-06-30T23:59:59Z"),
	service: EventService = Depends(get_event_service),
):
	"""
	Busca eventos dentro de un rango de fechas.

	Args:
		start: Fecha de inicio del rango
		end: Fecha de fin del rango
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		list[EventResponse]: Eventos en el rango

	Raises:
		HTTPException 400: Si end <= start
	"""
	try:
		events = await service.search_by_date_range(start, end)
	except ValueError as exc:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(exc),
		) from exc
	return events


@router.get(
	"/{event_id}/comments/users",
	response_model=list[EventCommentAuthor],
	summary="Obtener autores de comentarios",
	description="""
Recupera la lista de usuarios que han comentado en un evento (relationship query 1).

Devuelve cada autor único con el conteo de sus comentarios.

**Respuesta:**
```json
[
  {
    "author_external_id": "google_123456",
    "author_display_name": "Juan Pérez",
    "comment_count": 3
  }
]
```

**Caso de uso:** Mostrar participantes de la discusión del evento.
"""
)
async def get_comment_users(
	event_id: str,
	service: EventService = Depends(get_event_service),
):
	"""
	Recupera autores que comentaron en el evento.

	Args:
		event_id: ID del evento
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		list[EventCommentAuthor]: Lista de autores con conteo de comentarios
	"""
	return await service.get_comment_users(event_id)


@router.get(
	"/users/{user_external_id}/commented",
	response_model=list[EventResponse],
	summary="Obtener eventos comentados por usuario",
	description="""
Obtiene eventos en los que un usuario ha comentado (relationship query 2).

Busca en el array de comentarios usando **author_external_id**.
Los resultados están ordenados por `updated_at` descendente (más recientes primero).

**Ejemplo de uso:**
- `user_external_id=google_123456` → eventos donde ese usuario comentó

**Caso de uso:** Mostrar actividad del usuario, eventos en los que participó.
"""
)
async def get_commented_events_by_user(
	user_external_id: str,
	service: EventService = Depends(get_event_service),
):
	"""
	Obtiene eventos en los que un usuario comentó.

	Args:
		user_external_id: ID externo del usuario
		service: Servicio de eventos (inyectado por FastAPI)

	Returns:
		list[EventResponse]: Eventos donde el usuario comentó (ordenados por updated_at desc)
	"""
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
