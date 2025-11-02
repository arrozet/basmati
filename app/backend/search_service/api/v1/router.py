"""
API v1 router para SearchService.

Agrega los routers de endpoints de búsqueda avanzada.
"""
from fastapi import APIRouter
from api.v1.endpoints import search

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["search"])
