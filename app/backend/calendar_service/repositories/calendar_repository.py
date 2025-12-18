"""Repository para calendarios - Acceso a BD"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from pymongo import ReturnDocument
from models.calendar import CalendarModel
from core.interface import ICalendarRepository


class CalendarRepository(ICalendarRepository):
    """
    Repository para operaciones de acceso a datos de calendarios.
    
    Solo se encarga de comunicarse con MongoDB.
    La lógica de negocio está en CalendarService.
    """

    def __init__(self, db: Any):
        """
        Inicializa el repository de calendarios.
        
        Args:
            db: Instancia de la base de datos MongoDB (AsyncIOMotorDatabase)
        """
        self.collection = db["calendars"]
    
    # ==================== CRUD ====================
    
    async def find_all(self, limit: int = 200) -> list[dict]:
        """
        Obtiene todos los calendarios de la BD.
        
        Args:
            limit: Número máximo de calendarios a devolver
            
        Returns:
            list[dict]: Lista de todos los calendarios
        """
        try:
            cursor = self.collection.find({}).sort("created_at", -1)
            calendars = await cursor.to_list(length=limit)
            return calendars
        except Exception:
            return []
    
    async def create(self, calendar_dict: dict) -> str:
        """
        Crea un nuevo calendario en la BD.
        
        Valida que calendar_dict cumpla con la estructura de CalendarModel antes de insertar.
        
        Args:
            calendar_dict: Diccionario con los datos del calendario
            
        Returns:
            str: ID del calendario creado (como string)
            
        Raises:
            ValueError: Si hay error al crear el calendario en BD
        """
        # Validar estructura desempaquetando en CalendarModel
        try:
            CalendarModel(**calendar_dict)
        except Exception as e:
            raise ValueError(f"Datos de calendario inválidos: {str(e)}")
        
        # Si pasa validación, insertar directamente
        try:
            result = await self.collection.insert_one(calendar_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise ValueError(f"Error al insertar calendario en BD: {str(e)}")
    
    async def find_by_id(self, calendar_id: str) -> dict | None:
        """
        Busca un calendario por su ID de MongoDB.
        
        Args:
            calendar_id: ID del calendario (_id de MongoDB)
            
        Returns:
            dict: Calendario encontrado o None
        """
        try:
            calendar = await self.collection.find_one({"_id": ObjectId(calendar_id)})
            return calendar
        except Exception:
            return None
    
    async def update(self, calendar_id: str, update_dict: dict) -> dict | None:
        """
        Actualiza un calendario existente.
        
        Valida los campos que se actualizan antes de hacer la operación.
        
        Args:
            calendar_id: ID del calendario
            update_dict: Diccionario con los campos a actualizar
            
        Returns:
            dict: Calendario actualizado o None si no existe
            
        Raises:
            ValueError: Si los datos a actualizar son inválidos
        """
        # Si no hay campos para actualizar, devuelve el calendario actual
        if not update_dict:
            return await self.find_by_id(calendar_id)
        
        # Validar campos actualizables contra CalendarModel
        try:
            # Obtener el calendario actual
            current_calendar = await self.find_by_id(calendar_id)
            if not current_calendar:
                return None
            
            # Fusionar datos actuales con actualizaciones
            updated_calendar = {**current_calendar, **update_dict}
            updated_calendar["updated_at"] = datetime.now(timezone.utc)
            
            # Validar estructura completa
            CalendarModel(**updated_calendar)
        except Exception as e:
            raise ValueError(f"Datos de actualización inválidos: {str(e)}")
        
        try:
            # Agregar updated_at al update_dict
            update_dict["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(calendar_id)},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER
            )
            return result
        except Exception as e:
            raise ValueError(f"Error al actualizar calendario: {str(e)}")
    
    async def delete(self, calendar_id: str) -> bool:
        """
        Elimina un calendario de la BD.
        
        Args:
            calendar_id: ID del calendario
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(calendar_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    # ==================== BÚSQUEDAS PARAMETRIZADAS ====================
    
    async def find_by_creator(self, creator_external_id: str) -> list[dict]:
        """
        Busca calendarios por creador (parametrized query 1).
        
        Args:
            creator_external_id: ID del creador (external_id del usuario)
            
        Returns:
            list[dict]: Lista de calendarios encontrados
        """
        cursor = self.collection.find({"creator_external_id": creator_external_id})
        calendars = await cursor.to_list(length=100)
        return calendars
    
    async def find_by_keywords(self, keyword: str) -> list[dict]:
        """
        Busca calendarios por keywords (parametrized query 2).
        
        Busca en el array de keywords usando regex case-insensitive.
        
        Args:
            keyword: Palabra clave a buscar
            
        Returns:
            list[dict]: Lista de calendarios encontrados
        """
        # Buscar en el array de keywords con regex case-insensitive
        cursor = self.collection.find({"keywords": {"$regex": keyword, "$options": "i"}})
        calendars = await cursor.to_list(length=100)
        return calendars
    
    async def find_by_visibility(self, visibility: str) -> list[dict]:
        """
        Busca calendarios por visibilidad.

        Args:
            visibility: Visibilidad del calendario ("public", "private", "unlisted")

        Returns:
            list[dict]: Lista de calendarios encontrados
        """
        cursor = self.collection.find({"visibility": visibility})
        calendars = await cursor.to_list(length=100)
        return calendars

    async def search_by_text(self, query: str) -> list[dict]:
        """
        Búsqueda full-text en calendarios.

        Busca en los campos: title, description y keywords del calendario.
        Utiliza expresiones regulares para búsqueda case-insensitive.

        Args:
            query: Término de búsqueda

        Returns:
            list[dict]: Lista de calendarios encontrados
        """
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"keywords": {"$regex": query, "$options": "i"}}
            ]
        }
        cursor = self.collection.find(search_filter)
        calendars = await cursor.to_list(length=100)
        return calendars

    async def search_by_creator_name(self, creator_name: str) -> list[dict]:
        """
        Busca calendarios por nombre del creador.

        Utiliza el campo denormalizado creator_display_name para búsqueda
        eficiente sin necesidad de join con la colección users.

        Args:
            creator_name: Nombre o parte del nombre del creador

        Returns:
            list[dict]: Calendarios creados por usuarios con ese nombre
        """
        search_filter = {
            "creator_display_name": {"$regex": creator_name, "$options": "i"}
        }
        cursor = self.collection.find(search_filter)
        calendars = await cursor.to_list(length=100)
        return calendars

    # ==================== BÚSQUEDAS DE RELACIONES ====================
    
    async def find_children(self, calendar_id: str) -> list[dict]:
        """
        Obtiene los calendarios hijos directos (relationship query 1).
        
        Args:
            calendar_id: ID del calendario padre
            
        Returns:
            list[dict]: Lista de calendarios hijos
        """
        try:
            cursor = self.collection.find({"parent_calendar_id": ObjectId(calendar_id)})
            children = await cursor.to_list(length=100)
            return children
        except Exception:
            return []
    
    async def find_hierarchy(self, calendar_id: str) -> list[dict]:
        """
        Obtiene toda la jerarquía de calendarios usando el array path (relationship query 2).
        
        Busca todos los calendarios que tienen este calendar_id en su path,
        lo que significa que son descendientes en la jerarquía.
        
        Args:
            calendar_id: ID del calendario raíz
            
        Returns:
            list[dict]: Lista de todos los calendarios en la jerarquía
        """
        try:
            # Buscar el calendario raíz
            root_calendar = await self.find_by_id(calendar_id)
            if not root_calendar:
                return []
            
            # Buscar todos los calendarios que tienen este ID en su path
            cursor = self.collection.find({"path": ObjectId(calendar_id)})
            descendants = await cursor.to_list(length=100)
            
            # Retornar el calendario raíz + sus descendientes
            return [root_calendar] + descendants
        except Exception:
            return []
    
    # ==================== ACTUALIZACIONES ESPECIALES ====================
    
    async def increment_subscriber_count(self, calendar_id: str) -> bool:
        """
        Incrementa el contador de suscriptores de un calendario.
        
        Args:
            calendar_id: ID del calendario
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(calendar_id)},
                {"$inc": {"subscriber_count": 1}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def decrement_subscriber_count(self, calendar_id: str) -> bool:
        """
        Decrementa el contador de suscriptores de un calendario.
        
        Args:
            calendar_id: ID del calendario
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(calendar_id)},
                {"$inc": {"subscriber_count": -1}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def update_path(self, calendar_id: str, path: list[ObjectId]) -> bool:
        """
        Actualiza el path de un calendario (para mantener la jerarquía).
        
        Args:
            calendar_id: ID del calendario
            path: Array de ObjectIds con los ancestros
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(calendar_id)},
                {"$set": {"path": path}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    # ==================== COMENTARIOS ====================
    
    async def add_comment(self, calendar_id: str, comment_dict: dict) -> dict | None:
        """
        Agrega un comentario a un calendario.
        
        Args:
            calendar_id: ID del calendario
            comment_dict: Diccionario con los datos del comentario
            
        Returns:
            dict: Comentario agregado o None si el calendario no existe
        """
        try:
            # Agregar el comentario al array de comments
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(calendar_id)},
                {"$push": {"comments": comment_dict}},
                return_document=ReturnDocument.AFTER
            )
            
            if result and "comments" in result and len(result["comments"]) > 0:
                # Retornar el último comentario agregado
                return result["comments"][-1]
            return None
        except Exception as e:
            print(f"Error adding comment: {e}")
            return None

