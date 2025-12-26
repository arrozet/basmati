"""Interfaces base para repositorios y servicios.

Define las interfaces abstractas más genéricas que sirven como base
para todas las interfaces específicas de cada dominio.
"""
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

# Type variables para tipado genérico
T = TypeVar('T')  # Tipo de entidad
ID = TypeVar('ID')  # Tipo de identificador


class IRepository(ABC, Generic[T, ID]):
    """Interfaz base para todos los repositorios.
    
    Define las operaciones CRUD básicas que todo repositorio debe implementar.
    Las interfaces específicas (IEventRepository, etc.) deben heredar de esta
    y añadir sus métodos particulares.
    
    Type Parameters:
        T: Tipo de la entidad que maneja el repositorio
        ID: Tipo del identificador de la entidad
        
    Ejemplo:
        class IEventRepository(IRepository[EventModel, str]):
            @abstractmethod
            async def find_by_calendar(self, calendar_id: str) -> list[dict]:
                pass
    """
    
    @abstractmethod
    async def create(self, entity_dict: dict) -> ID:
        """Crea una nueva entidad.
        
        Args:
            entity_dict: Diccionario con los datos de la entidad
            
        Returns:
            ID: Identificador de la entidad creada
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_id: ID) -> dict | None:
        """Obtiene una entidad por su ID.
        
        Args:
            entity_id: Identificador de la entidad
            
        Returns:
            dict | None: Documento de la entidad o None si no existe
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: ID, update_dict: dict) -> dict | None:
        """Actualiza una entidad existente.
        
        Args:
            entity_id: Identificador de la entidad
            update_dict: Campos a actualizar
            
        Returns:
            dict | None: Documento actualizado o None si no existe
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        """Elimina una entidad.
        
        Args:
            entity_id: Identificador de la entidad
            
        Returns:
            bool: True si se eliminó, False en caso contrario
        """
        pass


class IService(ABC, Generic[T]):
    """Interfaz base para todos los servicios.
    
    Define el contrato mínimo que todo servicio debe cumplir.
    Las interfaces específicas (IEventService, etc.) deben heredar de esta
    y añadir sus métodos particulares.
    
    Type Parameters:
        T: Tipo de la respuesta principal del servicio
        
    Ejemplo:
        class IEventService(IService[EventResponse]):
            @abstractmethod
            async def search_by_calendar(self, calendar_id: str) -> list[EventResponse]:
                pass
    """
    
    # Los servicios no tienen métodos abstractos base obligatorios
    # porque cada dominio tiene operaciones muy diferentes.
    # Esta clase sirve como marcador de tipo y para futuras extensiones.
    pass

