"""Servicios V2 para IntegrationService"""
from .integration_service import IntegrationServiceV2
from .openstreetmap_service import OpenStreetMapServiceV2
from .s3_service import S3ServiceV2
from .email_service import EmailServiceV2
from .daily_digest_service import DailyDigestServiceV2

__all__ = [
    "IntegrationServiceV2",
    "OpenStreetMapServiceV2",
    "S3ServiceV2",
    "EmailServiceV2",
    "DailyDigestServiceV2"
]

