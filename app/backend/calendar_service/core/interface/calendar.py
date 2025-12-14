"""Interfaces para el dominio de Calendarios.

Define los contratos que deben cumplir los repositorios y servicios
de calendarios en todas las versiones de la API.

Hereda de las interfaces base definidas en shared/ para garantizar
consistencia entre todos los microservicios.
"""
from abc import abstractmethod
from typing import Any

from shared.interface import IRepository, IService
from schemas.calendar import (
    CalendarCreate,
    CalendarUpdate,
    CalendarResponse,
    CalendarHierarchy
)

# ============================================================================
# INTERFAZ DE REPOSITORIO DE CALENDARIOS
# ============================================================================

class ICalendarRepository(IRepository[dict, str]):
    """Interfaz abstracta para el repositorio de calendarios.
    
    Hereda de IRepository[dict, str] donde:
    - dict: tipo de entidad (documentos de MongoDB)
    - str: tipo de identificador (ObjectId como string)
    """
    
    @abstractmethod
    async def create(self, calendar_dict: dict) -> str:
        """Crea un nuevo calendario."""
        pass
        
    @abstractmethod
    async def find_by_id(self, calendar_id: str) -> dict | None:
        """Obtiene un calendario por su ID."""
        pass
        
    @abstractmethod
    async def update(self, calendar_id: str, update_dict: dict) -> dict | None:
        """Actualiza un calendario existente."""
        pass
        
    @abstractmethod
    async def delete(self, calendar_id: str) -> bool:
        """Elimina un calendario."""
        pass
        
    @abstractmethod
    async def find_all(self, limit: int = 200) -> list[dict]:
        """Obtiene todos los calendarios."""
        pass
        
    @abstractmethod
    async def find_by_creator(self, creator_external_id: str) -> list[dict]:
        """Busca calendarios por creador."""
        pass
        
    @abstractmethod
    async def find_by_keywords(self, keyword: str) -> list[dict]:
        """Busca calendarios por palabras clave."""
        pass
        
    @abstractmethod
    async def find_by_visibility(self, visibility: str) -> list[dict]:
        """Busca calendarios por visibilidad."""
        pass
        
    @abstractmethod
    async def search_by_text(self, query: str) -> list[dict]:
        """Búsqueda full-text."""
        pass
        
    @abstractmethod
    async def search_by_creator_name(self, creator_name: str) -> list[dict]:
        """Busca calendarios por nombre del creador."""
        pass
        
    @abstractmethod
    async def find_children(self, calendar_id: str) -> list[dict]:
        """Obtiene calendarios hijos."""
        pass
        
    @abstractmethod
    async def find_hierarchy(self, calendar_id: str) -> list[dict]:
        """Obtiene toda la jerarquía de un calendario."""
        pass


# ============================================================================
# INTERFAZ DE SERVICIO DE CALENDARIOS
# ============================================================================

class ICalendarService(IService[CalendarResponse]):
    """Interfaz abstracta para el servicio de calendarios.
    
    Hereda de IService[CalendarResponse].
    """
    
    @abstractmethod
    async def create_calendar(self, calendar_data: CalendarCreate) -> CalendarResponse:
        pass
        
    @abstractmethod
    async def get_calendar(self, calendar_id: str) -> CalendarResponse | None:
        pass
        
    @abstractmethod
    async def update_calendar(self, calendar_id: str, calendar_data: CalendarUpdate) -> CalendarResponse | None:
        pass
        
    @abstractmethod
    async def delete_calendar(self, calendar_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_all_calendars(self, limit: int = 200) -> list[CalendarResponse]:
        pass
    
    @abstractmethod
    async def search_by_creator(self, creator_external_id: str) -> list[CalendarResponse]:
        pass
        
    @abstractmethod
    async def search_by_keywords(self, keyword: str) -> list[CalendarResponse]:
        pass
        
    @abstractmethod
    async def search_by_visibility(self, visibility: str) -> list[CalendarResponse]:
        pass

    @abstractmethod
    async def search_by_text(self, query: str) -> list[CalendarResponse]:
        pass

    @abstractmethod
    async def search_by_creator_name(self, creator_name: str) -> list[CalendarResponse]:
        pass
        
    @abstractmethod
    async def get_children(self, calendar_id: str) -> list[CalendarResponse]:
        pass
        
    @abstractmethod
    async def get_hierarchy(self, calendar_id: str) -> CalendarHierarchy | None:
        pass
        
    @abstractmethod
    async def delete_calendar_recursive(self, calendar_id: str) -> dict:
        pass

