"""Servicios V2 para IntegrationService"""
from .import_service import ImportServiceV2
from .openstreetmap_service import OpenStreetMapServiceV2
from .s3_service import S3ImageService
from .email_service import EmailServiceV2
from .daily_digest_service import DailyDigestServiceV2

__all__ = [
    "ImportServiceV2",
    "OpenStreetMapServiceV2",
    "S3ImageService",
    "EmailServiceV2",
    "DailyDigestServiceV2"
]

