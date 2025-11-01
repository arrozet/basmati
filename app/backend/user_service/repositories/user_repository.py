"""Repository para usuarios - Acceso a BD"""
from datetime import datetime
from typing import Optional, List, Any
from bson import ObjectId
from models.user import UserModel


class UserRepository:
    """
    Repository para operaciones de acceso a datos de usuarios.
    
    Solo se encarga de comunicarse con MongoDB.
    La lógica de negocio está en UserService.
    """
    
    def __init__(self, db: Any):
        """
        Inicializa el repository de usuarios.
        
        Args:
            db: Instancia de la base de datos MongoDB (AsyncIOMotorDatabase)
        """
        self.collection = db["users"]
    
    # ==================== CRUD ====================
    
    async def create(self, user_dict: dict) -> str:
        """
        Crea un nuevo usuario en la BD.
        
        Valida que user_dict cumpla con la estructura de UserModel antes de insertar.
        
        Args:
            user_dict: Diccionario con los datos del usuario
            
        Returns:
            str: ID del usuario creado (como string)
            
        Raises:
            ValueError: Si los datos no cumplen con la estructura de UserModel
        """
        # Validar contra UserModel para garantizar estructura correcta
        try:
            user_model = UserModel(**user_dict)
            validated_dict = user_model.model_dump(exclude={"id"}, exclude_none=False)
        except Exception as e:
            raise ValueError(f"Datos de usuario inválidos: {str(e)}")
        
        result = await self.collection.insert_one(validated_dict)
        return str(result.inserted_id)
    
    async def find_by_id(self, user_id: str) -> Optional[dict]:
        """
        Busca un usuario por su ID de MongoDB.
        
        Args:
            user_id: ID del usuario (_id de MongoDB)
            
        Returns:
            dict: Usuario encontrado o None
        """
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception:
            return None
    
    async def update(self, user_id: str, update_dict: dict) -> Optional[dict]:
        """
        Actualiza un usuario existente.
        
        Valida los campos que se actualizan antes de hacer la operación.
        
        Args:
            user_id: ID del usuario
            update_dict: Diccionario con los campos a actualizar
            
        Returns:
            dict: Usuario actualizado o None si no existe
            
        Raises:
            ValueError: Si los datos a actualizar son inválidos
        """
        if not update_dict:
            return await self.find_by_id(user_id)
        
        # Validar campos actualizables contra UserModel
        try:
            # Obtener el usuario actual para validar la estructura completa
            current_user = await self.find_by_id(user_id)
            if not current_user:
                return None
            
            # Fusionar datos actuales con actualizaciones
            updated_user = {**current_user, **update_dict}
            # Excluir _id de la validación
            user_data_to_validate = {k: v for k, v in updated_user.items() if k != "_id"}
            
            # Validar estructura completa
            UserModel(**user_data_to_validate)
        except Exception as e:
            raise ValueError(f"Datos de actualización inválidos: {str(e)}")
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_dict},
                return_document=True
            )
            return result
        except Exception as e:
            raise ValueError(f"Error al actualizar usuario: {str(e)}")
    
    async def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario de la BD.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    # ==================== BÚSQUEDAS ====================
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """
        Busca un usuario por email (parametrized query 1).
        
        Args:
            email: Email del usuario
            
        Returns:
            dict: Usuario encontrado o None
        """
        user = await self.collection.find_one({"email": email})
        return user
    
    async def find_by_display_name(self, name: str) -> List[dict]:
        """
        Busca usuarios por display_name parcial (parametrized query 2).
        
        Args:
            name: Nombre o parte del nombre
            
        Returns:
            List[dict]: Lista de usuarios encontrados
        """
        cursor = self.collection.find({"display_name": {"$regex": name, "$options": "i"}})
        users = await cursor.to_list(length=100)
        return users
    
    async def find_by_oauth(self, external_id: str, provider: str) -> Optional[dict]:
        """
        Busca un usuario por sus credenciales OAuth.
        
        Args:
            external_id: ID del proveedor OAuth
            provider: Proveedor OAuth ("google" o "facebook")
            
        Returns:
            dict: Usuario encontrado o None
        """
        user = await self.collection.find_one({
            "external_id": external_id,
            "provider": provider
        })
        return user
    
    # ==================== ACTUALIZACIONES ====================
    
    async def update_last_login(self, user_id: str) -> bool:
        """
        Actualiza la fecha de último login del usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def add_followed_calendar(self, user_id: str, calendar_id: str) -> bool:
        """
        Agrega un calendario a la lista de seguidos del usuario.
        
        Args:
            user_id: ID del usuario
            calendar_id: ID del calendario a seguir
            
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"followed_calendar_ids": ObjectId(calendar_id)}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def remove_followed_calendar(self, user_id: str, calendar_id: str) -> bool:
        """
        Remueve un calendario de la lista de seguidos del usuario.
        
        Args:
            user_id: ID del usuario
            calendar_id: ID del calendario a dejar de seguir
            
        Returns:
            bool: True si se removió correctamente
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"followed_calendar_ids": ObjectId(calendar_id)}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    # ==================== VERIFICACIONES ====================
    
    async def exists_by_id(self, user_id: str) -> bool:
        """
        Verifica si existe un usuario con el ID dado.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            result = await self.collection.find_one({"_id": ObjectId(user_id)})
            return result is not None
        except Exception:
            return False
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado.
        
        Args:
            email: Email del usuario
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        result = await self.collection.find_one({"email": email})
        return result is not None
    
    async def exists_by_oauth(self, external_id: str, provider: str) -> bool:
        """
        Verifica si existe un usuario con las credenciales OAuth dadas.
        
        Args:
            external_id: ID del proveedor OAuth
            provider: Proveedor OAuth
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        result = await self.collection.find_one({
            "external_id": external_id,
            "provider": provider
        })
        return result is not None
