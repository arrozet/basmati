"""Schemas para operaciones de eventos"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class EventLocation(BaseModel):
	"""Ubicación estructurada del evento"""

	address: str = Field(..., description="Dirección física del evento")
	latitude: float = Field(..., ge=-90, le=90, description="Latitud en grados decimales")
	longitude: float = Field(..., ge=-180, le=180, description="Longitud en grados decimales")
	place_name: str | None = Field(None, description="Nombre del lugar si aplica")
	map_provider: Literal["google_maps", "openstreetmap"] = Field(
		..., description="Proveedor del mapa utilizado"
	)


class EventRecurrence(BaseModel):
	"""Datos de recurrencia para eventos repetitivos"""

	pattern: Literal["daily", "weekly", "monthly", "yearly"] = Field(
		..., description="Patrón de recurrencia"
	)
	interval: int = Field(1, ge=1, description="Repetición cada N unidades")
	days_of_week: list[int] | None = Field(
		None,
		description="Días de la semana aplicables (0=Domingo, 6=Sábado)",
	)
	end_date: datetime | None = Field(None, description="Fecha fin de la recurrencia")
	exceptions: list[datetime] = Field(
		default_factory=list,
		description="Fechas específicas a omitir",
	)


class EventAttachment(BaseModel):
	"""Adjunto incluido en la respuesta del evento"""

	id: str = Field(..., description="ID del adjunto")
	filename: str = Field(..., description="Nombre del archivo")
	url: str = Field(..., description="URL firmada o pública del adjunto")
	size: int = Field(..., ge=0, description="Tamaño en bytes")
	mime_type: str = Field(..., description="Tipo MIME del adjunto")
	uploaded_at: datetime = Field(..., description="Fecha de subida del adjunto")
	uploaded_by: str = Field(..., description="External ID del usuario que subió el archivo")
	is_image: bool = Field(..., description="Indica si el adjunto es una imagen")
	thumbnail_url: str | None = Field(None, description="URL de miniatura si aplica")

	model_config = ConfigDict(from_attributes=True)


class EventComment(BaseModel):
	"""Comentario incluido en la respuesta del evento"""

	id: str = Field(..., description="ID del comentario")
	author_external_id: str = Field(..., description="External ID del autor del comentario")
	author_display_name: str = Field(..., description="Nombre visible del autor")
	text: str = Field(..., description="Contenido del comentario")
	created_at: datetime = Field(..., description="Fecha de creación del comentario")

	model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
	"""Payload para crear un comentario"""

	author_external_id: str = Field(..., description="External ID del autor del comentario")
	author_display_name: str = Field(..., description="Nombre visible del autor")
	text: str = Field(..., min_length=1, description="Texto del comentario")

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"author_external_id": "google_123456789",
				"author_display_name": "Juan Pérez",
				"text": "¿Podemos mover el evento 30 minutos más tarde?"
			}
		}
	)


class AttachmentCreate(BaseModel):
	"""Payload para añadir un adjunto"""

	filename: str = Field(..., description="Nombre original del archivo")
	url: str = Field(..., description="URL accesible del archivo")
	size: int = Field(..., ge=0, description="Tamaño del archivo en bytes")
	mime_type: str = Field(..., description="Tipo MIME detectado")
	uploaded_by: str = Field(..., description="External ID del usuario que sube el archivo")
	is_image: bool = Field(..., description="Indica si el archivo es una imagen")
	thumbnail_url: str | None = Field(None, description="Miniatura generada para imágenes")

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"filename": "presentacion.pdf",
				"url": "https://storage.googleapis.com/basmati/events/64fa.../presentacion.pdf",
				"size": 524288,
				"mime_type": "application/pdf",
				"uploaded_by": "google_123456789",
				"is_image": False,
				"thumbnail_url": None
			}
		}
	)


class EventCreate(BaseModel):
	"""Schema para crear un evento"""

	calendar_id: str = Field(..., description="ID del calendario en MongoDB")
	calendar_title: str = Field(..., description="Título del calendario asociado")
	creator_external_id: str = Field(..., description="External ID del creador del evento")
	title: str = Field(..., description="Título del evento")
	description: str | None = Field(None, description="Descripción del evento")
	start_time: datetime = Field(..., description="Fecha y hora de inicio (ISO 8601)")
	end_time: datetime = Field(..., description="Fecha y hora de fin (ISO 8601)")
	location: EventLocation | None = Field(None, description="Ubicación estructurada del evento")
	visibility: Literal["public", "private", "inherited"] = Field(
		..., description="Visibilidad del evento"
	)
	recurrence: EventRecurrence | None = Field(None, description="Configuración de recurrencia si aplica")

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"calendar_id": "507f1f77bcf86cd799439011",
				"calendar_title": "Calendario de Marketing",
				"creator_external_id": "google_987654321",
				"title": "Reunión de planificación Q1",
				"description": "Sesión para definir campañas y presupuesto",
				"start_time": "2025-01-15T09:00:00Z",
				"end_time": "2025-01-15T10:30:00Z",
				"location": {
					"address": "Av. Reforma 123, Ciudad de México",
					"latitude": 19.432608,
					"longitude": -99.133209,
					"place_name": "Oficinas centrales",
					"map_provider": "google_maps"
				},
				"visibility": "private",
				"recurrence": {
					"pattern": "monthly",
					"interval": 1,
					"days_of_week": None,
					"end_date": "2025-06-15T10:30:00Z",
					"exceptions": []
				}
			}
		}
	)


class EventUpdate(BaseModel):
	"""Schema para actualizar un evento"""

	title: str | None = Field(None, description="Nuevo título del evento")
	description: str | None = Field(None, description="Nueva descripción")
	start_time: datetime | None = Field(None, description="Nueva fecha de inicio")
	end_time: datetime | None = Field(None, description="Nueva fecha de fin")
	location: EventLocation | None = Field(None, description="Actualización de la ubicación")
	attachments: list[EventAttachment] | None = Field(None, description="Lista actualizada de adjuntos")
	visibility: Literal["public", "private", "inherited"] | None = Field(
		None, description="Nueva visibilidad"
	)
	recurrence: EventRecurrence | None = Field(None, description="Recurrencia actualizada")

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"title": "Reunión de planificación Q1 (actualizada)",
				"description": "Añadimos revisión de métricas de enero",
				"start_time": "2025-01-15T09:30:00Z",
				"end_time": "2025-01-15T11:00:00Z",
				"visibility": "public"
			}
		}
	)


class EventResponse(EventCreate):
	"""Respuesta estándar para eventos"""

	id: str = Field(..., description="ID del evento")
	attachments: list[EventAttachment] = Field(
		default_factory=list,
		description="Lista de adjuntos del evento",
	)
	comments: list[EventComment] = Field(
		default_factory=list,
		description="Comentarios asociados",
	)
	created_at: datetime = Field(..., description="Fecha de creación")
	updated_at: datetime = Field(..., description="Última actualización")

	model_config = ConfigDict(
		from_attributes=True,
		json_schema_extra={
			"example": {
				"id": "507f1f77bcf86cd799439021",
				"calendar_id": "507f1f77bcf86cd799439011",
				"calendar_title": "Calendario de Marketing",
				"creator_external_id": "google_987654321",
				"title": "Reunión de planificación Q1",
				"description": "Sesión para definir campañas y presupuesto",
				"start_time": "2025-01-15T09:00:00Z",
				"end_time": "2025-01-15T10:30:00Z",
				"location": {
					"address": "Av. Reforma 123, Ciudad de México",
					"latitude": 19.432608,
					"longitude": -99.133209,
					"place_name": "Oficinas centrales",
					"map_provider": "google_maps"
				},
				"visibility": "private",
				"recurrence": None,
				"attachments": [
					{
						"id": "507f1f77bcf86cd799439031",
						"filename": "agenda.pdf",
						"url": "https://storage.googleapis.com/basmati/events/agenda.pdf",
						"size": 65536,
						"mime_type": "application/pdf",
						"uploaded_at": "2025-01-10T12:00:00Z",
						"uploaded_by": "google_987654321",
						"is_image": False,
						"thumbnail_url": None
					}
				],
				"comments": [
					{
						"id": "507f1f77bcf86cd799439041",
						"author_external_id": "google_123456789",
						"author_display_name": "Juan Pérez",
						"text": "¿Podemos añadir la presentación de métricas?",
						"created_at": "2025-01-12T15:45:00Z"
					}
				],
				"created_at": "2025-01-05T08:00:00Z",
				"updated_at": "2025-01-12T15:45:00Z"
			}
		}
	)


class EventCommentAuthor(BaseModel):
	"""Respuesta resumida de autores que comentaron en un evento"""

	author_external_id: str = Field(..., description="External ID del autor")
	author_display_name: str = Field(..., description="Nombre visible del autor")
	comment_count: int = Field(..., ge=1, description="Número de comentarios realizados")

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"author_external_id": "google_123456789",
				"author_display_name": "Juan Pérez",
				"comment_count": 3
			}
		}
	)

