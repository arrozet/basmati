"""Re-exportación de fábricas base desde shared/.

Este módulo re-exporta las clases de shared/factory para mantener
compatibilidad con el código existente y facilitar las importaciones
locales dentro del microservicio.

Para nuevos desarrollos, se recomienda importar directamente de shared/:
    from shared.factory import IServiceFactory, FactoryRegistry
"""
# Re-exportar desde shared (instalado como paquete)
from shared.factory import IServiceFactory, FactoryRegistry

# Alias para compatibilidad con código existente
def register_factory(domain: str, version: str, factory_class):
    """Wrapper para FactoryRegistry.register()"""
    FactoryRegistry.register(domain, version, factory_class)

def get_factory(domain: str, version: str, database):
    """Wrapper para FactoryRegistry.get()"""
    return FactoryRegistry.get(domain, version, database)

def list_registered_factories():
    """Wrapper para FactoryRegistry.list_all()"""
    return FactoryRegistry.list_all()

__all__ = [
    "IServiceFactory",
    "FactoryRegistry",
    "register_factory",
    "get_factory",
    "list_registered_factories",
]
