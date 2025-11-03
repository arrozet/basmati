"""Repository para notificaciones - Acceso a BD"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from models.notification import NotificationModel


class NotificationRepository:
    """
    Repository para operaciones de acceso a datos de notificaciones.
    
    Solo se encarga de comunicarse con MongoDB.
    La lógica de negocio está en NotificationService.
    """

    def __init__(self, db: Any):
        """
        Inicializa el repository de notificaciones.
        
        Args:
            db: Instancia de la base de datos MongoDB (AsyncIOMotorDatabase)
        """
        self.collection = db["notifications"]
    
    # ==================== CRUD ====================
    
    async def create(self, notification_dict: dict) -> str:
        """
        Crea una nueva notificación en la BD.
        
        Valida que notification_dict cumpla con la estructura de NotificationModel antes de insertar.
        
        Args:
            notification_dict: Diccionario con los datos de la notificación
            
        Returns:
            str: ID de la notificación creada (como string)
            
        Raises:
            ValueError: Si hay error al crear la notificación en BD
        """
        # Validar estructura desempaquetando en NotificationModel
        try:
            NotificationModel(**notification_dict)
        except Exception as e:
            raise ValueError(f"Datos de notificación inválidos: {str(e)}")
        
        # Si pasa validación, insertar directamente
        try:
            result = await self.collection.insert_one(notification_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise ValueError(f"Error al insertar notificación en BD: {str(e)}")
    
    async def find_by_id(self, notification_id: str) -> dict | None:
        """
        Busca una notificación por su ID de MongoDB.
        
        Args:
            notification_id: ID de la notificación (_id de MongoDB)
            
        Returns:
            dict: Notificación encontrada o None
        """
        try:
            notification = await self.collection.find_one({"_id": ObjectId(notification_id)})
            return notification
        except Exception:
            return None
    
    async def update(self, notification_id: str, update_dict: dict) -> dict | None:
        """
        Actualiza una notificación existente.
        
        Args:
            notification_id: ID de la notificación
            update_dict: Diccionario con los campos a actualizar
            
        Returns:
            dict: Notificación actualizada o None si no existe
            
        Raises:
            ValueError: Si los datos a actualizar son inválidos
        """
        # Si no hay campos para actualizar, devuelve la notificación actual
        if not update_dict:
            return await self.find_by_id(notification_id)
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(notification_id)},
                {"$set": update_dict},
                return_document=True
            )
            return result
        except Exception as e:
            raise ValueError(f"Error al actualizar notificación: {str(e)}")
    
    async def delete(self, notification_id: str) -> bool:
        """
        Elimina una notificación de la BD.
        
        Args:
            notification_id: ID de la notificación
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(notification_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    # ==================== BÚSQUEDAS ====================
    
    async def find_by_recipient(self, recipient_external_id: str) -> list[dict]:
        """
        Busca todas las notificaciones de un usuario.
        
        Args:
            recipient_external_id: External ID del usuario receptor
            
        Returns:
            list[dict]: Lista de notificaciones encontradas
        """
        cursor = self.collection.find({"recipient_external_id": recipient_external_id}).sort("created_at", -1)
        notifications = await cursor.to_list(length=100)
        return notifications
    
    async def find_unread_by_recipient(self, recipient_external_id: str) -> list[dict]:
        """
        Busca notificaciones no leídas de un usuario (parametrized query 1).
        
        Args:
            recipient_external_id: External ID del usuario receptor
            
        Returns:
            list[dict]: Lista de notificaciones no leídas
        """
        cursor = self.collection.find({
            "recipient_external_id": recipient_external_id,
            "is_read": False
        }).sort("created_at", -1)
        notifications = await cursor.to_list(length=100)
        return notifications
    
    async def find_by_event(self, event_id: str) -> list[dict]:
        """
        Busca notificaciones relacionadas con un evento específico (parametrized query 2).
        
        Args:
            event_id: ID del evento relacionado
            
        Returns:
            list[dict]: Lista de notificaciones del evento
        """
        try:
            cursor = self.collection.find({
                "related_event_id": ObjectId(event_id)
            }).sort("created_at", -1)
            notifications = await cursor.to_list(length=100)
            return notifications
        except Exception:
            return []
    
    async def find_by_type(self, notification_type: str) -> list[dict]:
        """
        Busca notificaciones por tipo.
        
        Args:
            notification_type: Tipo de notificación
            
        Returns:
            list[dict]: Lista de notificaciones del tipo especificado
        """
        cursor = self.collection.find({"type": notification_type}).sort("created_at", -1)
        notifications = await cursor.to_list(length=100)
        return notifications
    
    async def find_by_calendar(self, calendar_id: str) -> list[dict]:
        """
        Busca notificaciones relacionadas con un calendario específico.
        
        Args:
            calendar_id: ID del calendario relacionado
            
        Returns:
            list[dict]: Lista de notificaciones del calendario
        """
        try:
            cursor = self.collection.find({
                "related_calendar_id": ObjectId(calendar_id)
            }).sort("created_at", -1)
            notifications = await cursor.to_list(length=100)
            return notifications
        except Exception:
            return []
    
    # ==================== ACTUALIZACIONES ====================
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """
        Marca una notificación como leída.
        
        Args:
            notification_id: ID de la notificación
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"is_read": True}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def mark_all_as_read(self, recipient_external_id: str) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas.
        
        Args:
            recipient_external_id: External ID del usuario receptor
            
        Returns:
            int: Número de notificaciones actualizadas
        """
        try:
            result = await self.collection.update_many(
                {
                    "recipient_external_id": recipient_external_id,
                    "is_read": False
                },
                {"$set": {"is_read": True}}
            )
            return result.modified_count
        except Exception:
            return 0
