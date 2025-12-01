"""Modelo de evento para MongoDB"""
from datetime import datetime
from typing import Any, Literal
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema


class PyObjectId(ObjectId):
	"""ObjectId personalizado para compatibilidad con Pydantic v2"""

	@classmethod
	def __get_pydantic_core_schema__(cls, source_type: Any, handler):
		"""Permite validar ObjectId nativos o strings válidos"""
		return core_schema.union_schema([
			core_schema.is_instance_schema(ObjectId),
			core_schema.no_info_plain_validator_function(cls.validate),
		])

	@classmethod
	def validate(cls, value):
		"""Valida y convierte valores a ObjectId"""
		if isinstance(value, ObjectId):
			return value
		if isinstance(value, str) and ObjectId.is_valid(value):
			return ObjectId(value)
		raise ValueError("Invalid ObjectId")

	@classmethod
	def __get_pydantic_json_schema__(cls, schema, handler):
		"""Representa el ObjectId como string en OpenAPI"""
		return {"type": "string"}


class EventLocationModel(BaseModel):
	"""Ubicación estructurada del evento"""

	address: str = Field(..., description="Dirección física")
	latitude: float = Field(..., ge=-90, le=90, description="Latitud en grados")
	longitude: float = Field(..., ge=-180, le=180, description="Longitud en grados")
	place_name: str | None = Field(None, description="Nombre del lugar")
	map_provider: Literal["google_maps", "openstreetmap"] = Field(
		..., description="Proveedor del mapa"
	)


class EventAttachmentModel(BaseModel):
	"""Adjunto asociado a un evento"""

	id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
	filename: str = Field(..., description="Nombre del archivo")
	url: str = Field(..., description="URL del adjunto en almacenamiento externo")
	size: int = Field(..., ge=0, description="Tamaño en bytes")
	mime_type: str = Field(..., description="Tipo MIME del adjunto")
	uploaded_at: datetime = Field(..., description="Fecha de subida del adjunto")
	uploaded_by: str = Field(..., description="External ID del usuario que sube el adjunto")
	is_image: bool = Field(..., description="Indica si el adjunto es una imagen")
	thumbnail_url: str | None = Field(None, description="Miniatura opcional para imágenes")

	model_config = {
		"populate_by_name": True,
		"arbitrary_types_allowed": True,
		"json_encoders": {ObjectId: str},
	}


class EventCommentModel(BaseModel):
	"""Comentario realizado sobre un evento"""

	id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
	author_external_id: str = Field(..., description="External ID del autor")
	author_display_name: str = Field(..., description="Nombre visible del autor")
	text: str = Field(..., description="Contenido del comentario")
	created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha del comentario")

	model_config = {
		"populate_by_name": True,
		"arbitrary_types_allowed": True,
		"json_encoders": {ObjectId: str},
	}


class EventRecurrenceModel(BaseModel):
	"""Configuración de recurrencia para eventos repetitivos"""

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
		description="Fechas a omitir dentro de la recurrencia",
	)


class EventModel(BaseModel):
	"""Modelo principal del evento almacenado en MongoDB"""

	id: PyObjectId | None = Field(alias="_id", default=None)
	calendar_id: PyObjectId = Field(..., description="ID del calendario propietario")
	calendar_title: str = Field(..., description="Título del calendario")
	creator_external_id: str = Field(..., description="External ID del creador")
	title: str = Field(..., description="Título del evento")
	description: str | None = Field(None, description="Descripción detallada")
	start_time: datetime = Field(..., description="Fecha y hora de inicio")
	end_time: datetime = Field(..., description="Fecha y hora de finalización")
	location: EventLocationModel | None = Field(None, description="Ubicación del evento")
	attachments: list[EventAttachmentModel] = Field(
		default_factory=list,
		description="Adjuntos relacionados con el evento",
	)
	comments: list[EventCommentModel] = Field(
		default_factory=list,
		description="Comentarios asociados al evento",
	)
	visibility: Literal["public", "private", "inherited"] = Field(
		..., description="Visibilidad del evento"
	)
	recurrence: EventRecurrenceModel | None = Field(
		None, description="Configuración de recurrencia si aplica"
	)
	created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
	updated_at: datetime = Field(default_factory=datetime.utcnow, description="Última actualización")

	model_config = {
		"populate_by_name": True,
		"arbitrary_types_allowed": True,
		"json_encoders": {ObjectId: str},
	}

