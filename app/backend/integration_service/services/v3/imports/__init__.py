"""
V3 Calendar Import Module - Abstract Factory Implementation

Este módulo implementa el patrón Abstract Factory para la importación
de calendarios desde múltiples proveedores externos.

Patrón Abstract Factory:
- IImportFactory: Factoría abstracta que define la familia de productos
- ICalendarConnector: Producto abstracto para conexión con APIs externas
- IEventParser: Producto abstracto para parseo de eventos
- ICalendarImporter: Producto abstracto para importación a Basmati

Implementaciones concretas:
- Google Calendar: GoogleImportFactory + productos
- Teamup: TeamupImportFactory + productos

Extensibilidad:
Para añadir un nuevo proveedor (ej: Outlook):
1. Crear carpeta v3/imports/outlook/
2. Implementar OutlookConnector, OutlookParser, OutlookImporter
3. Implementar OutlookImportFactory
4. Registrar en FactoryRegistry
"""

from services.v3.imports.interfaces import (
    IImportFactory,
    ICalendarConnector,
    IEventParser,
    ICalendarImporter,
)
from services.v3.imports.service import ImportServiceV3
from services.v3.imports.schemas import ProviderType

# Importar factories concretas para auto-registro
from services.v3.imports import google
from services.v3.imports import teamup

__all__ = [
    # Interfaces
    "IImportFactory",
    "ICalendarConnector",
    "IEventParser",
    "ICalendarImporter",
    # Service
    "ImportServiceV3",
    # Types
    "ProviderType",
]
