"""Repository para eventos V2 - Acceso a MongoDB"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from bson.int64 import Int64
from models.event import (
    EventModel,
    EventCommentModel,
    EventAttachmentModel,
)
from repositories.event_repository import EventRepository

class EventRepositoryV2(EventRepository):
    """Gestor de operaciones de base de datos para eventos (V2)"""

    async def create(self, event_dict: dict) -> str:
        """Crea un nuevo evento en la base de datos (V2 - Asegura ObjectId)."""
        try:
            # Validar y convertir tipos usando el modelo (esto convierte strings a ObjectIds)
            model = EventModel(**event_dict)
            # Usamos los datos procesados por el modelo
            event_dict = model.model_dump(by_alias=True, exclude={"id"})
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

    async def find_by_date_range(self, start: datetime, end: datetime, calendar_id: str | None = None) -> list[dict]:
        """Busca eventos que ocurren dentro de un rango de fechas (parametrized query 2)."""
        try:
            query = {
                "$and": [
                    {"start_time": {"$lt": end}},
                    {"end_time": {"$gt": start}},
                ]
            }
            
            if calendar_id:
                query["$and"].append({"calendar_id": ObjectId(calendar_id)})

            cursor = self.collection.find(query)
            return await cursor.to_list(length=200)
        except Exception:
            return []
