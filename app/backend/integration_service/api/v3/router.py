"""
API Router V3 - Integration Service

Router principal para la API V3 que implementa el patrón Abstract Factory
para importación de calendarios.
"""

from fastapi import APIRouter
from api.v3.endpoints import imports

api_router = APIRouter()

# Incluir endpoints de importación V3
api_router.include_router(
    imports.router,
    prefix="/integrations/imports",
    tags=["V3: Calendar Imports"]
)
