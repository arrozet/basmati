"""
Integration Service V3 - Calendar Import Module

Implementación usando Abstract Factory Pattern para importación de calendarios
desde proveedores externos (Google Calendar, Teamup).

Estructura:
- imports/: Módulo principal de importación
  - interfaces/: Interfaces abstractas (productos y factoría)
  - google/: Implementación concreta para Google Calendar
  - teamup/: Implementación concreta para Teamup
  - schemas/: DTOs y schemas de entrada/salida
  - service.py: Servicio orquestador principal

Uso:
    from services.v3.imports import ImportServiceV3, ProviderType
    
    service = ImportServiceV3(calendar_service_url, event_service_url)
    result = await service.import_calendar(ProviderType.GOOGLE, request)
"""

from services.v3.imports import (
    ImportServiceV3,
    ProviderType,
    IImportFactory,
    ICalendarConnector,
    IEventParser,
    ICalendarImporter,
)

__all__ = [
    "ImportServiceV3",
    "ProviderType",
    "IImportFactory",
    "ICalendarConnector",
    "IEventParser",
    "ICalendarImporter",
]
