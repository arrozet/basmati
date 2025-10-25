"""
API v1 Router

Agrupa todos los routers de la versión 1 de la API.
"""
from fastapi import APIRouter

from api.v1.endpoints import users


# Router principal de v1
api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(users.router)

# Aquí se pueden agregar más routers en el futuro:
# api_router.include_router(products.router)
# api_router.include_router(orders.router)
# etc.
