from fastapi import APIRouter
from api.v2.endpoints import integrations, openstreetmap, s3_images

api_router = APIRouter()
api_router.include_router(integrations.router, tags=["integrations"])
api_router.include_router(openstreetmap.router, prefix="/osm", tags=["openstreetmap"])
api_router.include_router(s3_images.router, prefix="/s3", tags=["s3-images"])
