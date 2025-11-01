"""Lógica de negocio para usuarios"""
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserModel, NotificationPreferences
from schemas.user import UserCreate, UserUpdate, UserResponse

class UserService:
    """Servicio para manejar operaciones de usuarios"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Inicializa el servicio de usuarios.
        
        Args:
            db: Instancia de la base de datos MongoDB
        """
        self.collection = db["users"]
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Crea un nuevo usuario.
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            UserResponse: Usuario creado
        """
        user_dict = user_data.model_dump()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return self._document_to_response(user_dict)
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            UserResponse: Usuario encontrado o None
        """
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return self._document_to_response(user)
        return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario
            user_data: Datos a actualizar
            
        Returns:
            UserResponse: Usuario actualizado o None
        """
        update_dict = user_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_user(user_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            return self._document_to_response(result)
        return None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Elimina un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    async def search_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Busca un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            UserResponse: Usuario encontrado o None
        """
        user = await self.collection.find_one({"email": email})
        if user:
            return self._document_to_response(user)
        return None
    
    async def search_by_name(self, name: str) -> List[UserResponse]:
        """
        Busca usuarios por nombre parcial.
        
        Args:
            name: Nombre o parte del nombre
            
        Returns:
            List[UserResponse]: Lista de usuarios encontrados
        """
        cursor = self.collection.find({"name": {"$regex": name, "$options": "i"}})
        users = await cursor.to_list(length=100)
        return [self._document_to_response(user) for user in users]
    
    def _document_to_response(self, document: dict) -> UserResponse:
        """
        Convierte un documento de MongoDB a UserResponse.
        
        Args:
            document: Documento de MongoDB
            
        Returns:
            UserResponse: Schema de respuesta
        """
        document["id"] = str(document["_id"])
        return UserResponse(**document)
