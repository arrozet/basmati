"""Fábricas abstractas compartidas para todos los microservicios.

Este paquete implementa el patrón Abstract Factory base que pueden
usar todos los microservicios para el versionado de sus APIs.

Uso:
    from shared.factory import IServiceFactory, FactoryRegistry
    
    # Crear fábrica específica
    class MyServiceFactory(IServiceFactory):
        def create_repository(self):
            return MyRepository(self._database)
        
        def create_service(self):
            return MyService(self.create_repository())
    
    # Registrar fábrica
    FactoryRegistry.register("myservice", "v1", MyServiceFactory)
"""
from shared.factory.base import IServiceFactory
from shared.factory.registry import FactoryRegistry

__all__ = [
    "IServiceFactory",
    "FactoryRegistry",
]

