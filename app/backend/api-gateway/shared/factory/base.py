"""Fábrica abstracta base para el patrón Abstract Factory.

Define la interfaz que deben implementar todas las fábricas de servicios,
independientemente del dominio (eventos, notificaciones, etc.).
"""
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

from shared.interface import IRepository, IService

# Type variables para tipado genérico
R = TypeVar('R', bound=IRepository)  # Tipo de repositorio
S = TypeVar('S', bound=IService)      # Tipo de servicio


class IServiceFactory(ABC, Generic[R, S]):
    """Fábrica abstracta base para crear familias de objetos.
    
    Cada versión de la API debe implementar esta fábrica para crear
    sus propios Repository y Service.
    
    Type Parameters:
        R: Tipo del repositorio que crea la fábrica
        S: Tipo del servicio que crea la fábrica
        
    Ventajas del patrón:
    - Encapsula la creación de objetos relacionados
    - Garantiza consistencia entre Repository y Service de la misma versión
    - Facilita añadir nuevas versiones sin modificar código existente
    
    Ejemplo:
        class EventServiceFactoryV1(IServiceFactory[IEventRepository, IEventService]):
            def create_repository(self) -> IEventRepository:
                return EventRepository(self._database)
            
            def create_service(self) -> IEventService:
                return EventService(self.create_repository())
    """
    
    def __init__(self, database: Any):
        """Inicializa la fábrica con la conexión a la base de datos.
        
        Args:
            database: Instancia de la base de datos (ej: AsyncIOMotorDatabase)
        """
        self._database = database
    
    @abstractmethod
    def create_repository(self) -> R:
        """Crea el repositorio correspondiente a esta versión.
        
        Returns:
            R: Instancia del repositorio que implementa la interfaz
        """
        pass
    
    @abstractmethod
    def create_service(self) -> S:
        """Crea el servicio correspondiente a esta versión.
        
        El servicio creado debe usar el repositorio de la misma versión.
        
        Returns:
            S: Instancia del servicio que implementa la interfaz
        """
        pass
    
    @property
    def database(self) -> Any:
        """Acceso de solo lectura a la base de datos.
        
        Returns:
            Any: Instancia de la base de datos
        """
        return self._database

