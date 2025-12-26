"""Módulo compartido de Basmati - Lógica centralizada para todos los microservicios.

Este paquete contiene código reutilizable entre todos los microservicios:

- interface/: Interfaces base (IRepository, IService) y validación
- factory/: Fábrica abstracta base y registro global
- schemas/: Schemas Pydantic comunes
- config.py: Configuración compartida
- database.py: Utilidades de base de datos
"""
# Importaciones principales para facilitar el uso
from shared.interface import IRepository, IService
from shared.factory import IServiceFactory, FactoryRegistry

__all__ = [
    "IRepository",
    "IService", 
    "IServiceFactory",
    "FactoryRegistry",
]
