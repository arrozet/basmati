"""Interfaces para el dominio de Usuarios."""
from abc import ABC, abstractmethod
from typing import Any

from schemas.user import UserCreate, UserUpdate, UserResponse


class IUserRepository(ABC):
    """Interfaz para el repositorio de usuarios."""
    
    @abstractmethod
    def __init__(self, db: Any):
        pass

    @abstractmethod
    async def create(self, user_dict: dict) -> str:
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> dict | None:
        pass
    
    @abstractmethod
    async def update(self, user_id: str, update_dict: dict) -> dict | None:
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> dict | None:
        pass
    
    @abstractmethod
    async def find_by_display_name(self, name: str) -> list[dict]:
        pass
    
    @abstractmethod
    async def find_by_oauth(self, external_id: str, provider: str) -> dict | None:
        pass

    @abstractmethod
    async def find_one(self, query: dict) -> dict | None:
        pass

    @abstractmethod
    async def find_many(self, query: dict, limit: int = 100) -> list:
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> bool:
        pass

    @abstractmethod
    async def add_followed_calendar(self, user_id: str, calendar_id: str) -> bool:
        pass

    @abstractmethod
    async def remove_followed_calendar(self, user_id: str, calendar_id: str) -> bool:
        pass


class IUserService(ABC):
    """Interfaz para el servicio de usuarios."""
    
    @abstractmethod
    def __init__(self, user_repository: IUserRepository):
        pass

    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        pass
    
    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> UserResponse | None:
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse | None:
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def search_by_email(self, email: str) -> UserResponse | None:
        pass
    
    @abstractmethod
    async def search_by_display_name(self, name: str) -> list[UserResponse]:
        pass
    
    @abstractmethod
    async def search_by_oauth(self, external_id: str, provider: str) -> UserResponse | None:
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def get_raw_repository(self) -> IUserRepository:
        pass
