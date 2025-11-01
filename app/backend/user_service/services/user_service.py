"""Lógica de negocio para usuarios"""
from datetime import datetime
from typing import Optional, List
from schemas.user import UserCreate, UserUpdate, UserResponse
from repositories.user_repository import UserRepository


class UserService:
    """
    Servicio para manejar la lógica de negocio de usuarios.
    
    Delega acceso a BD al UserRepository.
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Inicializa el servicio de usuarios.
        
        Args:
            user_repository: Repository para usuarios
        """
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Crea un nuevo usuario con OAuth.
        
        Lógica:
        - Verifica que no exista un usuario con las mismas credenciales OAuth
        - Crea el usuario con fecha de creación
        
        Args:
            user_data: Datos del usuario a crear (incluye external_id y provider)
            
        Returns:
            UserResponse: Usuario creado
            
        Raises:
            ValueError: Si ya existe un usuario con esas credenciales OAuth
        """
        # Lógica de negocio: Verificar que no exista
        existing = await self.user_repository.find_by_oauth(user_data.external_id, user_data.provider)
        if existing:
            raise ValueError(f"El usuario con external_id '{user_data.external_id}' ya existe para el proveedor '{user_data.provider}'")
        
        # Preparar datos
        user_dict = user_data.model_dump()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["last_login"] = datetime.utcnow()
        user_dict["followed_calendar_ids"] = []
        
        # Delegar a repository (valida contra UserModel)
        try:
            user_id = await self.user_repository.create(user_dict)
        except ValueError as e:
            raise ValueError(f"Error al crear usuario: {str(e)}")
        user_doc = await self.user_repository.find_by_id(user_id)
        
        if not user_doc:
            raise ValueError("Error al crear el usuario")
        
        return self._document_to_response(user_doc)
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """
        Obtiene un usuario por su ID de MongoDB.
        
        Args:
            user_id: ID del usuario (_id de MongoDB)
            
        Returns:
            UserResponse: Usuario encontrado o None
        """
        user = await self.user_repository.find_by_id(user_id)
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
            UserResponse: Usuario actualizado o None si no existe
        """
        update_dict = user_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_user(user_id)
        
        # Delegar a repository (valida contra UserModel)
        try:
            result = await self.user_repository.update(user_id, update_dict)
        except ValueError as e:
            raise ValueError(f"Error al actualizar usuario: {str(e)}")
        
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
        return await self.user_repository.delete(user_id)
    
    async def search_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Busca un usuario por email (parametrized query 1).
        
        Args:
            email: Email del usuario
            
        Returns:
            UserResponse: Usuario encontrado o None
        """
        user = await self.user_repository.find_by_email(email)
        if user:
            return self._document_to_response(user)
        return None
    
    async def search_by_display_name(self, name: str) -> List[UserResponse]:
        """
        Busca usuarios por display_name parcial (parametrized query 2).
        
        Args:
            name: Nombre o parte del nombre
            
        Returns:
            List[UserResponse]: Lista de usuarios encontrados
        """
        users = await self.user_repository.find_by_display_name(name)
        return [self._document_to_response(user) for user in users]
    
    async def search_by_oauth(self, external_id: str, provider: str) -> Optional[UserResponse]:
        """
        Busca un usuario por sus credenciales OAuth.
        
        Args:
            external_id: ID del proveedor OAuth
            provider: Proveedor OAuth ("google" o "facebook")
            
        Returns:
            UserResponse: Usuario encontrado o None
        """
        user = await self.user_repository.find_by_oauth(external_id, provider)
        if user:
            return self._document_to_response(user)
        return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """
        Actualiza la fecha de último login del usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            bool: True si se actualizó correctamente
        """
        return await self.user_repository.update_last_login(user_id)
    
    def _document_to_response(self, document: dict) -> UserResponse:
        """
        Convierte un documento de MongoDB a UserResponse.
        
        Args:
            document: Documento de MongoDB
            
        Returns:
            UserResponse: Schema de respuesta
        """
        document["id"] = str(document["_id"])
        # Convertir ObjectIds de followed_calendar_ids a strings
        if "followed_calendar_ids" in document:
            document["followed_calendar_ids"] = [
                str(cal_id) for cal_id in document.get("followed_calendar_ids", [])
            ]
        return UserResponse(**document)
