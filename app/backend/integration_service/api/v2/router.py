from fastapi import APIRouter
from api.v2.endpoints import integrations, openstreetmap, s3_images, email, daily_digest

api_router = APIRouter()
api_router.include_router(integrations.router, tags=["Integration: General"])
api_router.include_router(openstreetmap.router, prefix="/osm", tags=["Integration: OpenStreetMap"])
api_router.include_router(s3_images.router, prefix="/s3", tags=["Integration: S3 Images"])
api_router.include_router(email.router, prefix="/email", tags=["Integration: Email"])
api_router.include_router(daily_digest.router, prefix="/digest", tags=["Integration: Daily Digest"])
