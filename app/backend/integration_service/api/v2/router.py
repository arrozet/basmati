from fastapi import APIRouter
from api.v2.endpoints import imports, openstreetmap, s3_images, email, daily_digest

api_router = APIRouter()

# Ahora todo cuelga de /integrations para mantener consistencia con V1 y otros servicios
api_router.include_router(imports.router, prefix="/integrations", tags=["Integration: General"])
api_router.include_router(openstreetmap.router, prefix="/integrations/osm", tags=["Integration: OpenStreetMap"])
api_router.include_router(s3_images.router, prefix="/integrations/s3", tags=["Integration: S3 Images"])
api_router.include_router(email.router, prefix="/integrations/email", tags=["Integration: Email"])
api_router.include_router(daily_digest.router, prefix="/integrations/digest", tags=["Integration: Daily Digest"])
