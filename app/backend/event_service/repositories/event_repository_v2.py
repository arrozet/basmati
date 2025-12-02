"""Repository para eventos V2 - Acceso a MongoDB.

Extiende EventRepository añadiendo compatibilidad con datos legacy.
Implementa la interfaz IEventRepository del patrón Abstract Factory.
"""
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
    """Gestor de operaciones de base de datos para eventos (V2).
    
    Mejoras respecto a V1:
    - Compatibilidad con datos legacy (busca por ObjectId Y String)
    - Filtrado por calendar_id en búsqueda por fechas
    """

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
                if ObjectId.is_valid(calendar_id):
                    # Buscar tanto por ObjectId como por String para compatibilidad con datos legacy
                    query["$and"].append({
                        "$or": [
                            {"calendar_id": ObjectId(calendar_id)},
                            {"calendar_id": calendar_id}
                        ]
                    })
                else:
                    query["$and"].append({"calendar_id": calendar_id})

            # DEBUG LOG
            print(f"DEBUG SEARCH: Querying events with filter: {query}")
            count = await self.collection.count_documents(query)
            print(f"DEBUG SEARCH: Found {count} documents")

            cursor = self.collection.find(query)
            return await cursor.to_list(length=200)
        except Exception as e:
            print(f"DEBUG SEARCH ERROR: {e}")
            return []

    async def find_by_calendar(self, calendar_id: str) -> list[dict]:
        """Busca eventos por ID de calendario (parametrized query 1)."""
        try:
            query = {}
            if ObjectId.is_valid(calendar_id):
                # Buscar tanto por ObjectId como por String para compatibilidad con datos legacy
                query = {
                    "$or": [
                        {"calendar_id": ObjectId(calendar_id)},
                        {"calendar_id": calendar_id}
                    ]
                }
            else:
                query = {"calendar_id": calendar_id}

            cursor = self.collection.find(query)
            return await cursor.to_list(length=200)
        except Exception:
            return []

    async def find_all(self, limit: int = 200) -> list[dict]:
        """Obtiene todos los eventos de la base de datos.
        
        Args:
            limit: Número máximo de eventos a devolver
            
        Returns:
            list[dict]: Lista de todos los eventos
        """
        try:
            cursor = self.collection.find({}).sort("start_time", -1)
            return await cursor.to_list(length=limit)
        except Exception:
            return []

    async def delete_by_calendar_id(self, calendar_id: str) -> int:
        """Elimina todos los eventos de un calendario.
        
        Busca por ObjectId y String para compatibilidad con datos legacy.
        
        Args:
            calendar_id: ID del calendario cuyos eventos se eliminarán
            
        Returns:
            int: Número de eventos eliminados
        """
        try:
            query = {}
            if ObjectId.is_valid(calendar_id):
                # Eliminar tanto por ObjectId como por String para compatibilidad con datos legacy
                query = {
                    "$or": [
                        {"calendar_id": ObjectId(calendar_id)},
                        {"calendar_id": calendar_id}
                    ]
                }
            else:
                query = {"calendar_id": calendar_id}

            result = await self.collection.delete_many(query)
            return result.deleted_count
        except Exception:
            return 0
