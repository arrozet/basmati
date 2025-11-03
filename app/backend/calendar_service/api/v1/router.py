"""Router principal de API v1"""
from fastapi import APIRouter
from api.v1.endpoints import calendars

api_router = APIRouter()
api_router.include_router(calendars.router, prefix="/calendars", tags=["calendars"])
