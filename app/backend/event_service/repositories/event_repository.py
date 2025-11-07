"""Repository para eventos - Acceso a MongoDB"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from bson.int64 import Int64
from models.event import (
    EventModel,
    EventCommentModel,
    EventAttachmentModel,
)


class EventRepository:
    """Gestor de operaciones de base de datos para eventos"""

    def __init__(self, database: Any):
        """Inicializa el repository con la colección de eventos.

        Args:
            database: Instancia de la base de datos AsyncIOMotorDatabase
        """
        self.collection = database["events"]

    async def create(self, event_dict: dict) -> str:
        """Crea un nuevo evento en la base de datos.

        Args:
            event_dict: Diccionario con los datos del evento

        Returns:
            str: ID del evento creado

        Raises:
            ValueError: Si los datos no son válidos o falla la inserción
        """
        try:
            EventModel(**event_dict)
        except Exception as exc:
            raise ValueError(f"Datos de evento inválidos: {str(exc)}")

        # Convertir size a int64 en todos los attachments para cumplir con JSON Schema de MongoDB
        if "attachments" in event_dict:
            for attachment in event_dict["attachments"]:
                if "size" in attachment:
                    attachment["size"] = Int64(attachment["size"])

        try:
            result = await self.collection.insert_one(event_dict)
            return str(result.inserted_id)
        except Exception as exc:
            raise ValueError(f"Error al insertar evento en BD: {str(exc)}")

    async def find_by_id(self, event_id: str) -> dict | None:
        """Obtiene un evento por su ID.

        Args:
            event_id: ID del evento en formato string

        Returns:
            dict | None: Documento del evento o None si no existe
        """
        try:
            return await self.collection.find_one({"_id": ObjectId(event_id)})
        except Exception:
            return None

    async def update(self, event_id: str, update_dict: dict) -> dict | None:
        """Actualiza un evento existente.

        Args:
            event_id: ID del evento
            update_dict: Campos a actualizar

        Returns:
            dict | None: Documento actualizado o None si no existe

        Raises:
            ValueError: Si los datos de actualización son inválidos
        """
        if not update_dict:
            return await self.find_by_id(event_id)

        current_event = await self.find_by_id(event_id)
        if not current_event:
            return None

        merged_event = {**current_event, **update_dict}
        merged_event["updated_at"] = datetime.now(timezone.utc)

        try:
            EventModel(**merged_event)
        except Exception as exc:
            raise ValueError(f"Datos de actualización inválidos: {str(exc)}")

        # Convertir size a int64 en attachments si se están actualizando
        if "attachments" in update_dict:
            for attachment in update_dict["attachments"]:
                if "size" in attachment:
                    attachment["size"] = Int64(attachment["size"])

        try:
            update_dict["updated_at"] = datetime.now(timezone.utc)
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(event_id)},
                {"$set": update_dict},
                return_document=True,
            )
            return result
        except Exception as exc:
            raise ValueError(f"Error al actualizar evento: {str(exc)}")

    async def delete(self, event_id: str) -> bool:
        """Elimina un evento.

        Args:
            event_id: ID del evento

        Returns:
            bool: True si se eliminó, False en caso contrario
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(event_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def add_comment(self, event_id: str, comment_dict: dict) -> dict | None:
        """Agrega un comentario al evento especificado.

        Args:
            event_id: ID del evento
            comment_dict: Datos del comentario (incluye _id y created_at)

        Returns:
            dict | None: Evento actualizado o None si no existe

        Raises:
            ValueError: Si los datos del comentario son inválidos o falla la actualización
        """
        try:
            comment_model = EventCommentModel(**comment_dict)
        except Exception as exc:
            raise ValueError(f"Comentario inválido: {str(exc)}")

        serialized_comment = comment_model.model_dump(by_alias=True)

        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(event_id)},
                {
                    "$push": {"comments": serialized_comment},
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                },
                return_document=True,
            )
            return result
        except Exception as exc:
            raise ValueError(f"Error al agregar comentario: {str(exc)}")

    async def add_attachment(self, event_id: str, attachment_dict: dict) -> dict | None:
        """Agrega un adjunto al evento.

        Args:
            event_id: ID del evento
            attachment_dict: Datos del adjunto (incluye _id y uploaded_at)

        Returns:
            dict | None: Evento actualizado o None si no existe

        Raises:
            ValueError: Si los datos del adjunto son inválidos o falla la actualización
        """
        try:
            attachment_model = EventAttachmentModel(**attachment_dict)
        except Exception as exc:
            raise ValueError(f"Adjunto inválido: {str(exc)}")

        serialized_attachment = attachment_model.model_dump(by_alias=True)
        
        # Convertir size a int64 para cumplir con el JSON Schema de MongoDB
        # MongoDB distingue entre int (32-bit) y long (64-bit)
        if "size" in serialized_attachment:
            serialized_attachment["size"] = Int64(serialized_attachment["size"])

        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(event_id)},
                {
                    "$push": {"attachments": serialized_attachment},
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                },
                return_document=True,
            )
            return result
        except Exception as exc:
            raise ValueError(f"Error al agregar adjunto: {str(exc)}")

    async def find_by_calendar(self, calendar_id: str) -> list[dict]:
        """Busca eventos por ID de calendario (parametrized query 1)."""
        try:
            cursor = self.collection.find({"calendar_id": ObjectId(calendar_id)})
            return await cursor.to_list(length=200)
        except Exception:
            return []

    async def find_by_date_range(self, start: datetime, end: datetime) -> list[dict]:
        """Busca eventos que ocurren dentro de un rango de fechas (parametrized query 2)."""
        try:
            cursor = self.collection.find(
                {
                    "$and": [
                        {"start_time": {"$lt": end}},
                        {"end_time": {"$gt": start}},
                    ]
                }
            )
            return await cursor.to_list(length=200)
        except Exception:
            return []

    async def get_comments(self, event_id: str) -> list[dict]:
        """Obtiene todos los comentarios de un evento."""
        event = await self.find_by_id(event_id)
        if not event:
            return []
        return event.get("comments", [])

    async def find_commented_events_by_user(self, user_external_id: str) -> list[dict]:
        """Obtiene eventos en los que un usuario ha comentado (relationship query 2)."""
        try:
            cursor = self.collection.find(
                {"comments.author_external_id": user_external_id}
            ).sort("updated_at", -1)
            return await cursor.to_list(length=200)
        except Exception:
            return []

    async def search_by_text(self, query: str) -> list[dict]:
        """Búsqueda full-text en eventos.

        Busca en los campos: title, description, location.address y location.place_name.
        Utiliza expresiones regulares para búsqueda case-insensitive.

        Args:
            query: Término de búsqueda

        Returns:
            list[dict]: Lista de eventos encontrados
        """
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"location.address": {"$regex": query, "$options": "i"}},
                {"location.place_name": {"$regex": query, "$options": "i"}}
            ]
        }
        try:
            cursor = self.collection.find(search_filter)
            return await cursor.to_list(length=100)
        except Exception:
            return []

    async def search_by_calendar_title(self, calendar_title: str) -> list[dict]:
        """Busca eventos por título del calendario.

        Utiliza el campo denormalizado calendar_title para búsqueda eficiente
        sin necesidad de join con la colección calendars.

        Args:
            calendar_title: Título o parte del título del calendario

        Returns:
            list[dict]: Eventos del calendario con ese título
        """
        search_filter = {
            "calendar_title": {"$regex": calendar_title, "$options": "i"}
        }
        try:
            cursor = self.collection.find(search_filter)
            return await cursor.to_list(length=100)
        except Exception:
            return []

    async def search_by_location(self, location_query: str) -> list[dict]:
        """Busca eventos por ubicación.

        Busca en los campos address y place_name del subdocumento location.

        Args:
            location_query: Término de búsqueda para la ubicación

        Returns:
            list[dict]: Eventos en esa ubicación
        """
        search_filter = {
            "$or": [
                {"location.address": {"$regex": location_query, "$options": "i"}},
                {"location.place_name": {"$regex": location_query, "$options": "i"}}
            ]
        }
        try:
            cursor = self.collection.find(search_filter)
            return await cursor.to_list(length=100)
        except Exception:
            return []
