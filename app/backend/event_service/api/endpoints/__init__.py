"""Endpoints unificados del EventService.

Este paquete contiene los endpoints compartidos entre todas las versiones.
"""
from api.endpoints.events import create_events_router

__all__ = ["create_events_router"]

