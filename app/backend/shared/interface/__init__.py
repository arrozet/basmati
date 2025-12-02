"""Interfaces abstractas compartidas para todos los microservicios.

Este paquete contiene las interfaces base que definen los contratos
para repositorios y servicios en todas las versiones de la API.

Las interfaces específicas de cada dominio (eventos, notificaciones, etc.)
deben heredar de las interfaces base definidas aquí.

Uso:
    from shared.interface import IRepository, IService
    from shared.interface.validation import validate_implementation
"""
from shared.interface.base import IRepository, IService

__all__ = [
    "IRepository",
    "IService",
]

