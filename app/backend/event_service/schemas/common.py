"""
Schemas comunes para el Event Service.

Reutiliza los schemas centralizados de shared.schemas.common
"""
from shared.schemas.common import (
    ResponseMessage,
    ErrorResponse
)

# Reexportar los schemas centralizados
__all__ = [
    "ResponseMessage",
    "ErrorResponse"
]
