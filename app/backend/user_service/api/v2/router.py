"""Router principal de API v2.

Solo incluye los endpoints que tienen CAMBIOS respecto a v1.
Para endpoints sin cambios, usar /v1/.

Mejoras V2:
- Soporte para campo 'frequency' en preferencias de notificación
- Nuevos endpoints para gestión de preferencias de notificación
"""
from fastapi import APIRouter
from api.v2.endpoints import users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users-v2"])
