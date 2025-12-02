from fastapi import APIRouter
from api.v2.endpoints import integrations, openstreetmap

api_router = APIRouter()
api_router.include_router(integrations.router, tags=["integrations"])
api_router.include_router(openstreetmap.router, prefix="/osm", tags=["openstreetmap"])
