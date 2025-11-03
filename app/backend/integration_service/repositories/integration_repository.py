"""Repository para fuentes de integración - Acceso a BD"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from models.integration_source import IntegrationSourceModel


class IntegrationRepository:
    """
    Repository para operaciones de acceso a datos de fuentes de integración.
    
    Solo se encarga de comunicarse con MongoDB.
    La lógica de negocio está en IntegrationService.
    """

    def __init__(self, db: Any):
        """
        Inicializa el repository de fuentes de integración.
        
        Args:
            db: Instancia de la base de datos MongoDB (AsyncIOMotorDatabase)
        """
        self.collection = db["integration_sources"]
    
    # ==================== CRUD ====================
    
    async def create(self, source_dict: dict) -> str:
        """
        Crea una nueva fuente de integración en la BD.
        
        Args:
            source_dict: Diccionario con los datos de la fuente de integración
            
        Returns:
            str: ID de la fuente creada (como string)
            
        Raises:
            ValueError: Si hay error al crear la fuente en BD
        """
        # Validar estructura
        try:
            IntegrationSourceModel(**source_dict)
        except Exception as e:
            raise ValueError(f"Datos de fuente de integración inválidos: {str(e)}")
        
        try:
            result = await self.collection.insert_one(source_dict)
            return str(result.inserted_id)
        except Exception as e:
            raise ValueError(f"Error al insertar fuente de integración en BD: {str(e)}")
    
    async def find_by_id(self, source_id: str) -> dict | None:
        """
        Busca una fuente de integración por su ID de MongoDB.
        
        Args:
            source_id: ID de la fuente (_id de MongoDB)
            
        Returns:
            dict: Fuente encontrada o None
        """
        try:
            source = await self.collection.find_one({"_id": ObjectId(source_id)})
            return source
        except Exception:
            return None
    
    async def update(self, source_id: str, update_dict: dict) -> dict | None:
        """
        Actualiza una fuente de integración existente.
        
        Args:
            source_id: ID de la fuente
            update_dict: Diccionario con los campos a actualizar
            
        Returns:
            dict: Fuente actualizada o None si no existe
            
        Raises:
            ValueError: Si los datos a actualizar son inválidos
        """
        if not update_dict:
            return await self.find_by_id(source_id)
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(source_id)},
                {"$set": update_dict},
                return_document=True
            )
            return result
        except Exception as e:
            raise ValueError(f"Error al actualizar fuente de integración: {str(e)}")
    
    async def delete(self, source_id: str) -> bool:
        """
        Elimina una fuente de integración de la BD.
        
        Args:
            source_id: ID de la fuente
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(source_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    # ==================== BÚSQUEDAS PARAMETRIZADAS ====================
    
    async def find_by_user(self, user_external_id: str) -> list[dict]:
        """
        Busca fuentes de integración por usuario (parametrized query 1).
        
        Args:
            user_external_id: ID del usuario (external_id)
            
        Returns:
            list[dict]: Lista de fuentes encontradas
        """
        cursor = self.collection.find({"user_external_id": user_external_id})
        sources = await cursor.to_list(length=100)
        return sources
    
    async def find_by_status(self, sync_status: str) -> list[dict]:
        """
        Busca fuentes de integración por estado de sincronización (parametrized query 2).
        
        Args:
            sync_status: Estado de sincronización ("success", "error", "pending")
            
        Returns:
            list[dict]: Lista de fuentes encontradas
        """
        cursor = self.collection.find({"sync_status": sync_status})
        sources = await cursor.to_list(length=100)
        return sources
    
    async def find_by_source_type(self, source_type: str) -> list[dict]:
        """
        Busca fuentes de integración por tipo de fuente.
        
        Args:
            source_type: Tipo de fuente ("google_calendar", "teamup")
            
        Returns:
            list[dict]: Lista de fuentes encontradas
        """
        cursor = self.collection.find({"source_type": source_type})
        sources = await cursor.to_list(length=100)
        return sources
    
    async def find_by_external_source_id(
        self, 
        user_external_id: str, 
        external_source_id: str
    ) -> dict | None:
        """
        Busca una fuente específica de un usuario por su external_source_id.
        
        Útil para verificar si ya se importó un calendario externo específico.
        
        Args:
            user_external_id: ID del usuario
            external_source_id: ID del calendario en el servicio externo
            
        Returns:
            dict: Fuente encontrada o None
        """
        source = await self.collection.find_one({
            "user_external_id": user_external_id,
            "external_source_id": external_source_id
        })
        return source
    
    # ==================== ACTUALIZACIONES DE SINCRONIZACIÓN ====================
    
    async def update_sync_status(
        self,
        source_id: str,
        status: str,
        error_message: str | None = None
    ) -> bool:
        """
        Actualiza el estado de sincronización de una fuente.
        
        Args:
            source_id: ID de la fuente
            status: Nuevo estado ("success", "error", "pending")
            error_message: Mensaje de error si status es "error"
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            update_data = {
                "sync_status": status,
                "last_sync": datetime.now(timezone.utc)
            }
            
            if error_message:
                update_data["sync_error_message"] = error_message
            else:
                update_data["sync_error_message"] = None
            
            result = await self.collection.update_one(
                {"_id": ObjectId(source_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def link_basmati_calendar(self, source_id: str, calendar_id: str) -> bool:
        """
        Vincula una fuente de integración con un calendario de Basmati.
        
        Args:
            source_id: ID de la fuente
            calendar_id: ID del calendario de Basmati creado
            
        Returns:
            bool: True si se vinculó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(source_id)},
                {"$set": {"basmati_calendar_id": ObjectId(calendar_id)}}
            )
            return result.modified_count > 0
        except Exception:
            return False
