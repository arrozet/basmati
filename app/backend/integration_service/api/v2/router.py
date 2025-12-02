from fastapi import APIRouter
from api.v2.endpoints import integrations

api_router = APIRouter()
api_router.include_router(integrations.router, tags=["integrations"])
