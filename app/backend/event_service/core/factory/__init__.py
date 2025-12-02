"""Fábricas abstractas y concretas para el versionado de la API.

Este paquete implementa el patrón Abstract Factory para crear
familias de objetos (Repository + Service) según la versión de la API.

Las clases base están en shared/factory/, este paquete las re-exporta
y añade las fábricas específicas del dominio de eventos.

Organización:
- base.py: Re-exporta desde shared/factory
- event.py: Fábricas de eventos (V1, V2, etc.)
- (futuro) notification.py: Fábricas de notificaciones
"""
from core.factory.base import (
    IServiceFactory,
    FactoryRegistry,
    get_factory,
    register_factory,
    list_registered_factories,
)
from core.factory.event import (
    IEventServiceFactory,
    EventServiceFactoryV1,
    EventServiceFactoryV2,
    get_event_factory,
)

__all__ = [
    # Base (desde shared/)
    "IServiceFactory",
    "FactoryRegistry",
    "get_factory",
    "register_factory",
    "list_registered_factories",
    # Eventos
    "IEventServiceFactory",
    "EventServiceFactoryV1",
    "EventServiceFactoryV2",
    "get_event_factory",
]

