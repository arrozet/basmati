from fastapi import APIRouter
from api.v2.endpoints import integrations, openstreetmap, s3_images

api_router = APIRouter()
api_router.include_router(integrations.router, tags=["Integration: General"])
api_router.include_router(openstreetmap.router, prefix="/osm", tags=["Integration: OpenStreetMap"])
api_router.include_router(s3_images.router, prefix="/s3", tags=["Integration: S3 Images"])
