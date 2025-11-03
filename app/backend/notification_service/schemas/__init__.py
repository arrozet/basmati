"""Schemas del Notification Service"""
from .notification import NotificationCreate, NotificationUpdate, NotificationResponse
from .common import ResponseMessage, ErrorResponse

__all__ = [
    "NotificationCreate",
    "NotificationUpdate", 
    "NotificationResponse",
    "ResponseMessage",
    "ErrorResponse"
]

