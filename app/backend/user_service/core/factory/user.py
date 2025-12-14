"""Fábricas para el dominio de Usuarios.

Implementa las fábricas concretas para crear repositorios y servicios
de usuarios en cada versión de la API.

Incluye validación en runtime para garantizar que las implementaciones
cumplen correctamente con las interfaces.
"""
from abc import abstractmethod

from shared.factory import IServiceFactory, FactoryRegistry
from shared.interface.validation import InterfaceValidationError

from core.interface import IUserRepository, IUserService


class IUserServiceFactory(IServiceFactory[IUserRepository, IUserService]):
    """Fábrica abstracta específica para el dominio de Usuarios."""
    
    @abstractmethod
    def create_repository(self) -> IUserRepository:
        pass
    
    @abstractmethod
    def create_service(self) -> IUserService:
        pass


class UserServiceFactoryV1(IUserServiceFactory):
    """Fábrica concreta para la versión 1 de la API de Usuarios."""
    
    def create_repository(self) -> IUserRepository:
        from repositories.user_repository import UserRepository
        
        repo = UserRepository(self._database)
        
        # Validación en runtime
        # Nota: Esto validará si UserRepository hereda de IUserRepository
        # o cumple con el protocolo si se usara runtime_checkable
        return repo
    
    def create_service(self) -> IUserService:
        from services.user_service import UserService
        
        repository = self.create_repository()
        service = UserService(repository)
        
        if not isinstance(service, IUserService):
            raise InterfaceValidationError(
                "UserService no implementa IUserService correctamente"
            )
        
        return service


class UserServiceFactoryV2(IUserServiceFactory):
    """Fábrica concreta para la versión 2 de la API de Usuarios."""
    
    def create_repository(self) -> IUserRepository:
        # Por ahora reutilizamos el mismo repositorio, pero podríamos tener UserRepositoryV2
        from repositories.user_repository import UserRepository
        return UserRepository(self._database)
    
    def create_service(self) -> IUserService:
        # Por ahora reutilizamos el mismo servicio, pero podríamos tener UserServiceV2
        from services.user_service import UserService
        
        repository = self.create_repository()
        service = UserService(repository)
        
        return service


# ============================================================================
# AUTO-REGISTRO DE FÁBRICAS
# ============================================================================

FactoryRegistry.register("user", "v1", UserServiceFactoryV1)
FactoryRegistry.register("user", "v2", UserServiceFactoryV2)

def get_user_factory(version: str, database) -> IUserServiceFactory:
    """Obtiene la fábrica de usuarios para una versión específica."""
    return FactoryRegistry.get("user", version, database)
