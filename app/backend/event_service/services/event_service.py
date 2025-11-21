"""Lógica de negocio para eventos"""
from datetime import datetime, timezone

import httpx
from bson import ObjectId

from core.config import settings
from repositories.event_repository import EventRepository
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


class EventService:
    """Servicio de dominio encargado de gestionar eventos"""

    def __init__(
        self,
        event_repository: EventRepository,
        notification_service_url: str | None = None,
    ) -> None:
        """Inicializa el servicio de eventos.

        Args:
            event_repository: Repositorio de eventos
            notification_service_url: URL del NotificationService
        """
        self.event_repository = event_repository
        self.notification_service_url = notification_service_url or settings.notification_service_url

    async def create_event(self, event_data: EventCreate) -> EventResponse:
        """Crea un nuevo evento.

        Args:
            event_data: Datos del evento a crear

        Returns:
            EventResponse: Evento creado

        Raises:
            ValueError: Si la validación falla o la inserción no es posible
        """
        if event_data.end_time <= event_data.start_time:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

        try:
            calendar_object_id = ObjectId(event_data.calendar_id)
        except Exception:
            raise ValueError("calendar_id inválido")

        now = datetime.now(timezone.utc)
        event_dict = event_data.model_dump()
        event_dict["calendar_id"] = calendar_object_id
        event_dict["created_at"] = now
        event_dict["updated_at"] = now
        event_dict["comments"] = []
        event_dict["attachments"] = []

        try:
            event_id = await self.event_repository.create(event_dict)
            event_doc = await self.event_repository.find_by_id(event_id)
            if not event_doc:
                raise ValueError("No se pudo recuperar el evento creado")
            return self._document_to_response(event_doc)
        except ValueError as exc:
            raise ValueError(f"Error al crear evento: {str(exc)}")

    async def get_event(self, event_id: str) -> EventResponse | None:
        """Obtiene un evento por su ID."""
        event = await self.event_repository.find_by_id(event_id)
        if event:
            return self._document_to_response(event)
        return None


    async def update_event(self, event_id: str, event_data: EventUpdate) -> EventResponse | None:
        """Actualiza un evento existente."""
        update_dict = event_data.model_dump(exclude_unset=True)

        if update_dict.get("end_time") and update_dict.get("start_time"):
            if update_dict["end_time"] <= update_dict["start_time"]:
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

        current_event: dict | None = None
        needs_current = (
            ("end_time" in update_dict and "start_time" not in update_dict)
            or ("start_time" in update_dict and "end_time" not in update_dict)
        )
        if needs_current:
            current_event = await self.event_repository.find_by_id(event_id)
            if not current_event:
                return None

        if "end_time" in update_dict and "start_time" not in update_dict:
            assert current_event is not None
            if update_dict["end_time"] <= current_event.get("start_time"):
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        if "start_time" in update_dict and "end_time" not in update_dict:
            assert current_event is not None
            if current_event.get("end_time") <= update_dict["start_time"]:
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")

        try:
            updated_event = await self.event_repository.update(event_id, update_dict)
        except ValueError as exc:
            raise ValueError(f"Error al actualizar evento: {str(exc)}")

        if updated_event:
            return self._document_to_response(updated_event)
        return None

    async def delete_event(self, event_id: str) -> bool:
        """Elimina un evento."""
        return await self.event_repository.delete(event_id)

    async def add_comment(self, event_id: str, comment_data: CommentCreate) -> EventComment | None:
        """Agrega un comentario a un evento y dispara notificación."""
        comment_doc = {
            "_id": ObjectId(),
            "author_external_id": comment_data.author_external_id,
            "author_display_name": comment_data.author_display_name,
            "text": comment_data.text,
            "created_at": datetime.now(timezone.utc),
        }

        try:
            updated_event = await self.event_repository.add_comment(event_id, comment_doc)
        except ValueError as exc:
            raise ValueError(f"Error al agregar comentario: {str(exc)}")

        if not updated_event:
            return None

        await self._notify_new_comment(updated_event, comment_doc)

        return self._serialize_comment(comment_doc)

    async def add_attachment(self, event_id: str, attachment_data: AttachmentCreate) -> EventAttachment | None:
        """Agrega un adjunto a un evento."""
        attachment_doc = {
            "_id": ObjectId(),
            "filename": attachment_data.filename,
            "url": attachment_data.url,
            "size": attachment_data.size,
            "mime_type": attachment_data.mime_type,
            "uploaded_at": datetime.now(timezone.utc),
            "uploaded_by": attachment_data.uploaded_by,
            "is_image": attachment_data.is_image,
            "thumbnail_url": attachment_data.thumbnail_url,
        }

        try:
            updated_event = await self.event_repository.add_attachment(event_id, attachment_doc)
        except ValueError as exc:
            raise ValueError(f"Error al agregar adjunto: {str(exc)}")

        if not updated_event:
            return None

        return self._serialize_attachment(attachment_doc)

    async def search_by_calendar(self, calendar_id: str) -> list[EventResponse]:
        """Busca eventos por calendario (parametrized query 1)."""
        events = await self.event_repository.find_by_calendar(calendar_id)
        return [self._document_to_response(event) for event in events]

    async def search_by_date_range(self, start: datetime, end: datetime) -> list[EventResponse]:
        """Busca eventos dentro de un rango de fechas (parametrized query 2)."""
        if end <= start:
            raise ValueError("El rango de fechas es inválido: 'end' debe ser posterior a 'start'")
        events = await self.event_repository.find_by_date_range(start, end)
        return [self._document_to_response(event) for event in events]

    async def get_comment_users(self, event_id: str) -> list[EventCommentAuthor]:
        """Obtiene los usuarios que comentaron un evento (relationship query 1)."""
        comments = await self.event_repository.get_comments(event_id)
        author_map: dict[str, dict[str, str | int]] = {}
        for comment in comments:
            author_id = comment.get("author_external_id")
            if not author_id:
                continue
            if author_id not in author_map:
                author_map[author_id] = {
                    "author_external_id": author_id,
                    "author_display_name": comment.get("author_display_name", ""),
                    "comment_count": 0,
                }
            author_map[author_id]["comment_count"] = int(author_map[author_id]["comment_count"]) + 1

        return [EventCommentAuthor(**data) for data in author_map.values()]

    async def get_commented_events_by_user(self, user_external_id: str) -> list[EventResponse]:
        """Obtiene eventos comentados por un usuario (relationship query 2)."""
        events = await self.event_repository.find_commented_events_by_user(user_external_id)
        return [self._document_to_response(event) for event in events]

    async def search_by_text(self, query: str) -> list[EventResponse]:
        """Búsqueda full-text en eventos.

        Busca en los campos: title, description, location.address y location.place_name.

        Args:
            query: Término de búsqueda

        Returns:
            list[EventResponse]: Lista de eventos encontrados
        """
        events = await self.event_repository.search_by_text(query)
        return [self._document_to_response(event) for event in events]

    async def search_by_calendar_title(self, calendar_title: str) -> list[EventResponse]:
        """Busca eventos por título del calendario.

        Args:
            calendar_title: Título o parte del título del calendario

        Returns:
            list[EventResponse]: Eventos del calendario con ese título
        """
        events = await self.event_repository.search_by_calendar_title(calendar_title)
        return [self._document_to_response(event) for event in events]

    async def search_by_location(self, location_query: str) -> list[EventResponse]:
        """Busca eventos por ubicación.

        Args:
            location_query: Término de búsqueda para la ubicación

        Returns:
            list[EventResponse]: Eventos en esa ubicación
        """
        events = await self.event_repository.search_by_location(location_query)
        return [self._document_to_response(event) for event in events]

    async def search_advanced(
        self,
        title: str | None = None,
        calendar_title: str | None = None,
        description: str | None = None
    ) -> list[EventResponse]:
        """Búsqueda avanzada de eventos.

        Args:
            title: Título del evento
            calendar_title: Título del calendario
            description: Descripción

        Returns:
            list[EventResponse]: Lista de eventos encontrados
        """
        events = await self.event_repository.search_advanced(title, calendar_title, description)
        return [self._document_to_response(event) for event in events]

    async def _notify_new_comment(self, event_doc: dict, comment_doc: dict) -> None:
        """Envía notificación al creador del evento tras un nuevo comentario."""
        creator_id = event_doc.get("creator_external_id")
        author_id = comment_doc.get("author_external_id")

        if not creator_id or creator_id == author_id:
            return

        payload = {
            "recipient_external_id": creator_id,
            "type": "NEW_COMMENT",
            "title": f"Nuevo comentario en '{event_doc.get('title', 'evento')}'",
            "message": (
                f"{comment_doc.get('author_display_name', 'Un usuario')} comentó: "
                f"{comment_doc.get('text', '')}"
            ),
            "related_event_id": str(event_doc.get("_id")),
            "related_calendar_id": str(event_doc.get("calendar_id")),
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self.notification_service_url}/v1/notifications",
                    json=payload,
                )
        except Exception as exc:
            # Se registra el error sin interrumpir el flujo principal
            print(f"Error enviando notificación de comentario: {str(exc)}")

    def _document_to_response(self, document: dict) -> EventResponse:
        """Convierte un documento de MongoDB a EventResponse."""
        doc = dict(document)
        doc["id"] = str(doc.get("_id"))
        doc.pop("_id", None)

        calendar_id = doc.get("calendar_id")
        doc["calendar_id"] = str(calendar_id) if calendar_id else None

        attachments = doc.get("attachments", [])
        doc["attachments"] = [
            {
                "id": str(item.get("_id")),
                "filename": item.get("filename"),
                "url": item.get("url"),
                "size": item.get("size"),
                "mime_type": item.get("mime_type"),
                "uploaded_at": item.get("uploaded_at"),
                "uploaded_by": item.get("uploaded_by"),
                "is_image": item.get("is_image"),
                "thumbnail_url": item.get("thumbnail_url"),
            }
            for item in attachments
        ]

        comments = doc.get("comments", [])
        doc["comments"] = [
            {
                "id": str(item.get("_id")),
                "author_external_id": item.get("author_external_id"),
                "author_display_name": item.get("author_display_name"),
                "text": item.get("text"),
                "created_at": item.get("created_at"),
            }
            for item in comments
        ]

        return EventResponse(**doc)

    def _serialize_comment(self, comment_doc: dict) -> EventComment:
        """Convierte un documento de comentario a schema de respuesta."""
        return EventComment(
            id=str(comment_doc.get("_id")),
            author_external_id=comment_doc.get("author_external_id", ""),
            author_display_name=comment_doc.get("author_display_name", ""),
            text=comment_doc.get("text", ""),
            created_at=comment_doc.get("created_at"),
        )

    def _serialize_attachment(self, attachment_doc: dict) -> EventAttachment:
        """Convierte un documento de adjunto a schema de respuesta."""
        return EventAttachment(
            id=str(attachment_doc.get("_id")),
            filename=attachment_doc.get("filename", ""),
            url=attachment_doc.get("url", ""),
            size=attachment_doc.get("size", 0),
            mime_type=attachment_doc.get("mime_type", ""),
            uploaded_at=attachment_doc.get("uploaded_at"),
            uploaded_by=attachment_doc.get("uploaded_by", ""),
            is_image=bool(attachment_doc.get("is_image")),
            thumbnail_url=attachment_doc.get("thumbnail_url"),
        )

