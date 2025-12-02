"""Fábricas para el dominio de Eventos.

Implementa las fábricas concretas para crear repositorios y servicios
de eventos en cada versión de la API.

Incluye validación en runtime para garantizar que las implementaciones
cumplen correctamente con las interfaces.
"""
from abc import abstractmethod

# Importar desde shared (instalado como paquete)
from shared.factory import IServiceFactory, FactoryRegistry
from shared.interface.validation import InterfaceValidationError

from core.interface.event import IEventRepository, IEventService


class IEventServiceFactory(IServiceFactory[IEventRepository, IEventService]):
    """Fábrica abstracta específica para el dominio de Eventos.
    
    Extiende IServiceFactory con tipos específicos de retorno
    para el dominio de eventos.
    """
    
    @abstractmethod
    def create_repository(self) -> IEventRepository:
        """Crea el repositorio de eventos.
        
        Returns:
            IEventRepository: Repositorio que implementa la interfaz
        """
        pass
    
    @abstractmethod
    def create_service(self) -> IEventService:
        """Crea el servicio de eventos.
        
        Returns:
            IEventService: Servicio que implementa la interfaz
        """
        pass


class EventServiceFactoryV1(IEventServiceFactory):
    """Fábrica concreta para la versión 1 de la API de Eventos.
    
    Crea instancias de EventRepository y EventService (V1).
    Incluye validación en runtime de las implementaciones.
    """
    
    def create_repository(self) -> IEventRepository:
        """Crea el repositorio V1 con validación."""
        from repositories.event_repository import EventRepository
        
        repo = EventRepository(self._database)
        
        # Validación en runtime
        if not isinstance(repo, IEventRepository):
            raise InterfaceValidationError(
                f"EventRepository no implementa IEventRepository correctamente"
            )
        
        return repo
    
    def create_service(self) -> IEventService:
        """Crea el servicio V1 con validación."""
        from services.event_service import EventService
        
        repository = self.create_repository()
        service = EventService(repository)
        
        # Validación en runtime
        if not isinstance(service, IEventService):
            raise InterfaceValidationError(
                f"EventService no implementa IEventService correctamente"
            )
        
        return service


class EventServiceFactoryV2(IEventServiceFactory):
    """Fábrica concreta para la versión 2 de la API de Eventos.
    
    Crea instancias de EventRepositoryV2 y EventServiceV2.
    Incluye validación en runtime de las implementaciones.
    
    Mejoras de V2:
    - Compatibilidad con datos legacy (ObjectId + String)
    - Filtro opcional por calendar_id en búsqueda por fechas
    - Mejoras en la propagación de datos
    """
    
    def create_repository(self) -> IEventRepository:
        """Crea el repositorio V2 con validación."""
        from repositories.event_repository_v2 import EventRepositoryV2
        
        repo = EventRepositoryV2(self._database)
        
        # Validación en runtime
        if not isinstance(repo, IEventRepository):
            raise InterfaceValidationError(
                f"EventRepositoryV2 no implementa IEventRepository correctamente"
            )
        
        return repo
    
    def create_service(self) -> IEventService:
        """Crea el servicio V2 con validación."""
        from services.event_service_v2 import EventServiceV2
        
        repository = self.create_repository()
        service = EventServiceV2(repository)
        
        # Validación en runtime
        if not isinstance(service, IEventService):
            raise InterfaceValidationError(
                f"EventServiceV2 no implementa IEventService correctamente"
            )
        
        return service


# ============================================================================
# AUTO-REGISTRO DE FÁBRICAS
# ============================================================================
# Las fábricas se registran automáticamente al importar este módulo

FactoryRegistry.register("event", "v1", EventServiceFactoryV1)
FactoryRegistry.register("event", "v2", EventServiceFactoryV2)


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def get_event_factory(version: str, database) -> IEventServiceFactory:
    """Obtiene la fábrica de eventos para una versión específica.
    
    Args:
        version: Versión de la API ("v1", "v2")
        database: Conexión a la base de datos
        
    Returns:
        IEventServiceFactory: Fábrica para esa versión
    """
    return FactoryRegistry.get("event", version, database)

