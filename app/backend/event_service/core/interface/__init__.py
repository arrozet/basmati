"""Interfaces abstractas para el patrón Abstract Factory.

Este paquete contiene las interfaces (clases abstractas) que definen
los contratos para repositorios y servicios de cada dominio.

Las interfaces base (IRepository, IService) están en shared/interface/,
este paquete las re-exporta y añade las interfaces específicas de eventos.

Organización:
- event.py: Interfaces de eventos (IEventRepository, IEventService)
- (futuro) notification.py: Interfaces de notificaciones
"""
# Re-exportar interfaces base desde shared (instalado como paquete)
from shared.interface import IRepository, IService
from shared.interface.validation import (
    validate_implementation,
    runtime_check,
    InterfaceValidationError,
    ValidatedABCMeta,
)

# Interfaces específicas de eventos
from core.interface.event import IEventRepository, IEventService

__all__ = [
    # Base (desde shared/)
    "IRepository",
    "IService",
    # Validación
    "validate_implementation",
    "runtime_check",
    "InterfaceValidationError",
    "ValidatedABCMeta",
    # Eventos
    "IEventRepository",
    "IEventService",
]

