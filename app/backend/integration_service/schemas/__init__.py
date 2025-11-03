"""Schemas para IntegrationService"""
from .integration import (
    GoogleCalendarImportRequest,
    TeamupImportRequest,
    ImportResponse,
    ImportedCalendar
)

__all__ = [
    "GoogleCalendarImportRequest",
    "TeamupImportRequest",
    "ImportResponse",
    "ImportedCalendar"
]
