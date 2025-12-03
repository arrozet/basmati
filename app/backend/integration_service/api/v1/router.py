"""
API v1 router para IntegrationService.
Agrega los routers de endpoints.
"""
from fastapi import APIRouter
from api.v1.endpoints import integrations

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integration: General"])
