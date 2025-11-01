"""
Schemas comunes para el Notification Service.

Reutiliza los schemas centralizados de shared.schemas.common
"""
from shared.schemas.common import (
    ResponseMessage,
    ErrorResponse,
    PaginationParams,
    TimestampedModel
)

# Reexportar los schemas centralizados
__all__ = [
    "ResponseMessage",
    "ErrorResponse",
    "PaginationParams",
    "TimestampedModel"
]
