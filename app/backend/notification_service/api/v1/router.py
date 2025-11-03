"""
API v1 router para NotificationService.
Agrega los routers de endpoints.
"""
from fastapi import APIRouter
from api.v1.endpoints import notifications

api_router = APIRouter()
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

