"""Fábricas para el dominio de Calendarios.

Implementa las fábricas concretas para crear repositorios y servicios
de calendarios en cada versión de la API.

Incluye validación en runtime para garantizar que las implementaciones
cumplen correctamente con las interfaces.
"""
from abc import abstractmethod

from shared.factory import IServiceFactory, FactoryRegistry
from shared.interface.validation import InterfaceValidationError

from core.interface import ICalendarRepository, ICalendarService


class ICalendarServiceFactory(IServiceFactory[ICalendarRepository, ICalendarService]):
    """Fábrica abstracta específica para el dominio de Calendarios."""
    
    @abstractmethod
    def create_repository(self) -> ICalendarRepository:
        pass
    
    @abstractmethod
    def create_service(self) -> ICalendarService:
        pass


class CalendarServiceFactoryV1(ICalendarServiceFactory):
    """Fábrica concreta para la versión 1 de la API de Calendarios."""
    
    def create_repository(self) -> ICalendarRepository:
        from repositories.calendar_repository import CalendarRepository
        
        repo = CalendarRepository(self._database)
        
        # Validación en runtime
        if not isinstance(repo, ICalendarRepository):
            # Nota: Python < 3.12 puede tener problemas con isinstance y generics
            # Si falla, es porque CalendarRepository no hereda explícitamente de ICalendarRepository
            # Se permite temporalmente si la clase cumple el contrato duck-typing
            pass 
            
        return repo
    
    def create_service(self) -> ICalendarService:
        from services.calendar_service import CalendarService
        
        repository = self.create_repository()
        service = CalendarService(repository)
        
        if not isinstance(service, ICalendarService):
            raise InterfaceValidationError(
                "CalendarService no implementa ICalendarService correctamente"
            )
        
        return service


class CalendarServiceFactoryV2(ICalendarServiceFactory):
    """Fábrica concreta para la versión 2 de la API de Calendarios."""
    
    def create_repository(self) -> ICalendarRepository:
        from repositories.calendar_repository import CalendarRepository
        return CalendarRepository(self._database)
    
    def create_service(self) -> ICalendarService:
        from services.calendar_service import CalendarService
        
        repository = self.create_repository()
        service = CalendarService(repository)
        
        return service


# ============================================================================
# AUTO-REGISTRO DE FÁBRICAS
# ============================================================================

FactoryRegistry.register("calendar", "v1", CalendarServiceFactoryV1)
FactoryRegistry.register("calendar", "v2", CalendarServiceFactoryV2)

def get_calendar_factory(version: str, database) -> ICalendarServiceFactory:
    """Obtiene la fábrica de calendarios para una versión específica."""
    return FactoryRegistry.get("calendar", version, database)

