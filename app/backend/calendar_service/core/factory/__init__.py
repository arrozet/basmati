"""Fábricas abstractas y concretas para el versionado de la API.

Este paquete implementa el patrón Abstract Factory para crear
familias de objetos (Repository + Service) según la versión de la API.

Las clases base están en shared/factory/, este paquete las re-exporta
y añade las fábricas específicas del dominio de calendarios.

Organización:
- base.py: Re-exporta desde shared/factory
- calendar.py: Fábricas de calendarios (V1, V2, etc.)
"""
from core.factory.base import (
    IServiceFactory,
    FactoryRegistry,
    get_factory,
    register_factory,
    list_registered_factories,
)
from core.factory.calendar import (
    ICalendarServiceFactory,
    CalendarServiceFactoryV1,
    CalendarServiceFactoryV2,
    get_calendar_factory,
)

__all__ = [
    # Base (desde shared/)
    "IServiceFactory",
    "FactoryRegistry",
    "get_factory",
    "register_factory",
    "list_registered_factories",
    # Calendarios
    "ICalendarServiceFactory",
    "CalendarServiceFactoryV1",
    "CalendarServiceFactoryV2",
    "get_calendar_factory",
]

