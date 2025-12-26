"""Registro global de fábricas para acceso dinámico.

Permite registrar y obtener fábricas por dominio y versión,
facilitando la gestión de múltiples versiones de múltiples servicios.
"""
from typing import Any, Type
from shared.factory.base import IServiceFactory


class FactoryNotFoundError(Exception):
    """Error cuando no se encuentra una fábrica registrada."""
    pass


class FactoryRegistry:
    """Registro centralizado de fábricas.
    
    Permite registrar fábricas por dominio (event, notification, etc.)
    y versión (v1, v2, etc.), y obtenerlas dinámicamente.
    
    Es una clase con métodos de clase (singleton implícito) para
    que el registro sea global y compartido.
    
    Uso:
        # Registrar fábricas
        FactoryRegistry.register("event", "v1", EventServiceFactoryV1)
        FactoryRegistry.register("event", "v2", EventServiceFactoryV2)
        
        # Obtener fábrica
        factory = FactoryRegistry.get("event", "v2", database)
        service = factory.create_service()
        
        # Listar fábricas
        print(FactoryRegistry.list_all())
        # {"event": ["v1", "v2"]}
    """
    
    # Registro: dominio -> versión -> clase de fábrica
    _registry: dict[str, dict[str, Type[IServiceFactory]]] = {}
    
    @classmethod
    def register(
        cls,
        domain: str,
        version: str,
        factory_class: Type[IServiceFactory]
    ) -> None:
        """Registra una fábrica para un dominio y versión.
        
        Args:
            domain: Nombre del dominio (ej: "event", "notification")
            version: Versión de la API (ej: "v1", "v2")
            factory_class: Clase de la fábrica a registrar
            
        Ejemplo:
            FactoryRegistry.register("event", "v1", EventServiceFactoryV1)
        """
        domain = domain.lower()
        version = version.lower()
        
        if domain not in cls._registry:
            cls._registry[domain] = {}
        
        cls._registry[domain][version] = factory_class
    
    @classmethod
    def get(
        cls,
        domain: str,
        version: str,
        database: Any
    ) -> IServiceFactory:
        """Obtiene una instancia de fábrica para un dominio y versión.
        
        Args:
            domain: Nombre del dominio
            version: Versión de la API
            database: Conexión a la base de datos
            
        Returns:
            IServiceFactory: Instancia de la fábrica
            
        Raises:
            FactoryNotFoundError: Si no existe la fábrica
            
        Ejemplo:
            factory = FactoryRegistry.get("event", "v2", db)
            service = factory.create_service()
        """
        domain = domain.lower()
        version = version.lower()
        
        if domain not in cls._registry:
            available = list(cls._registry.keys()) or ["(ninguno)"]
            raise FactoryNotFoundError(
                f"Dominio '{domain}' no registrado. "
                f"Disponibles: {available}"
            )
        
        domain_factories = cls._registry[domain]
        
        if version not in domain_factories:
            available = list(domain_factories.keys()) or ["(ninguno)"]
            raise FactoryNotFoundError(
                f"Versión '{version}' no registrada para '{domain}'. "
                f"Disponibles: {available}"
            )
        
        factory_class = domain_factories[version]
        return factory_class(database)
    
    @classmethod
    def exists(cls, domain: str, version: str) -> bool:
        """Verifica si existe una fábrica registrada.
        
        Args:
            domain: Nombre del dominio
            version: Versión de la API
            
        Returns:
            bool: True si existe, False si no
        """
        domain = domain.lower()
        version = version.lower()
        return domain in cls._registry and version in cls._registry[domain]
    
    @classmethod
    def list_all(cls) -> dict[str, list[str]]:
        """Lista todas las fábricas registradas.
        
        Returns:
            dict: Diccionario dominio -> [versiones]
            
        Ejemplo de retorno:
            {"event": ["v1", "v2"], "notification": ["v1"]}
        """
        return {
            domain: list(versions.keys())
            for domain, versions in cls._registry.items()
        }
    
    @classmethod
    def list_versions(cls, domain: str) -> list[str]:
        """Lista las versiones disponibles para un dominio.
        
        Args:
            domain: Nombre del dominio
            
        Returns:
            list[str]: Lista de versiones
        """
        domain = domain.lower()
        if domain not in cls._registry:
            return []
        return list(cls._registry[domain].keys())
    
    @classmethod
    def clear(cls) -> None:
        """Limpia el registro (útil para tests).
        
        ⚠️ CUIDADO: Esto elimina todas las fábricas registradas.
        """
        cls._registry.clear()
    
    @classmethod
    def unregister(cls, domain: str, version: str) -> bool:
        """Elimina una fábrica del registro.
        
        Args:
            domain: Nombre del dominio
            version: Versión de la API
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        domain = domain.lower()
        version = version.lower()
        
        if domain in cls._registry and version in cls._registry[domain]:
            del cls._registry[domain][version]
            # Limpiar dominio si queda vacío
            if not cls._registry[domain]:
                del cls._registry[domain]
            return True
        return False

