"""Router principal de la API v1 del Event Service"""
from fastapi import APIRouter

from api.v1.endpoints import events


api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
