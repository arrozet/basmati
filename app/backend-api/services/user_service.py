"""
User Service

Contiene toda la lógica de negocio relacionada con usuarios.
Separa la lógica de los endpoints para mejor testabilidad y mantenimiento.
"""
from typing import Optional, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.user import UserModel
from schemas.user import UserCreate, UserUpdate


class UserService:
    """Servicio para gestionar operaciones de usuarios"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[UserModel.collection_name]
    
    async def create_user(self, user_data: UserCreate) -> dict:
        """
        Crear un nuevo usuario
        
        Args:
            user_data: Datos del usuario a crear (name, email, pwd)
            
        Returns:
            Usuario creado con su ID
            
        Raises:
            ValueError: Si el email ya existe
        """
        # Verificar si el email ya existe
        existing_email = await self.collection.find_one({"email": user_data.email})
        if existing_email:
            raise ValueError("El email ya está registrado")
        
        # Crear modelo de usuario
        user_model = UserModel(
            name=user_data.name,
            email=user_data.email,
            pwd=user_data.pwd
        )
        
        # Insertar en base de datos
        result = await self.collection.insert_one(user_model.to_dict())
        
        # Obtener usuario creado
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        created_user["_id"] = str(created_user["_id"])
        
        return created_user
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """
        Obtener usuario por ID
        
        Args:
            user_id: ID del usuario (string)
            
        Returns:
            Usuario encontrado o None
        """
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Obtener usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario encontrado o None
        """
        user = await self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[dict], int]:
        """
        Obtener lista de usuarios con paginación
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a devolver
            
        Returns:
            Tupla con (lista de usuarios, total de usuarios)
        """
        # Obtener total
        total = await self.collection.count_documents({})
        
        # Obtener usuarios
        cursor = self.collection.find({}).skip(skip).limit(limit)
        users = []
        async for user in cursor:
            user["_id"] = str(user["_id"])
            users.append(user)
        
        return users, total
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[dict]:
        """
        Actualizar usuario
        
        Args:
            user_id: ID del usuario a actualizar
            user_data: Datos a actualizar (name, email, pwd opcionales)
            
        Returns:
            Usuario actualizado o None si no existe
            
        Raises:
            ValueError: Si el email ya existe para otro usuario
        """
        # Verificar que el usuario existe
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            return None
        
        # Preparar datos de actualización
        update_data = {}
        
        if user_data.email is not None:
            # Verificar que el email no esté en uso por otro usuario
            email_user = await self.collection.find_one({"email": user_data.email})
            if email_user and str(email_user["_id"]) != user_id:
                raise ValueError("El email ya está en uso por otro usuario")
            update_data["email"] = user_data.email
        
        if user_data.name is not None:
            update_data["name"] = user_data.name
        
        if user_data.pwd is not None:
            update_data["pwd"] = user_data.pwd
        
        # Si no hay nada que actualizar
        if not update_data:
            return existing_user
        
        # Actualizar en base de datos
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Obtener usuario actualizado
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Eliminar usuario
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception:
            return False
