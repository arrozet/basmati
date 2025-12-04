"""Schemas para IntegrationService"""
from .integration import (
    GoogleCalendarImportRequest,
    TeamupImportRequest,
    ImportResponse,
    ImportedCalendar
)
from .openstreetmap import (
    GeocodeRequest,
    ReverseGeocodeRequest,
    SearchPlaceRequest,
    GeocodeResponse,
    ReverseGeocodeResponse,
    LocationResult
)
from .email import (
    EmailRequest,
    EmailResponse,
    BulkEmailRequest,
    CommentNotificationRequest
)
from .daily_digest import (
    DailyDigestUserInfo,
    NotificationSummary,
    DigestRequest,
    BulkDigestResponse,
    DigestSendResponse,
    DigestPreviewResponse
)

__all__ = [
    # Integration
    "GoogleCalendarImportRequest",
    "TeamupImportRequest",
    "ImportResponse",
    "ImportedCalendar",
    # OpenStreetMap
    "GeocodeRequest",
    "ReverseGeocodeRequest",
    "SearchPlaceRequest",
    "GeocodeResponse",
    "ReverseGeocodeResponse",
    "LocationResult",
    # Email
    "EmailRequest",
    "EmailResponse",
    "BulkEmailRequest",
    "CommentNotificationRequest",
    # Daily Digest
    "DailyDigestUserInfo",
    "NotificationSummary",
    "DigestRequest",
    "BulkDigestResponse",
    "DigestSendResponse",
    "DigestPreviewResponse"
]
