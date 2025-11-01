"""Schemas comunes para respuestas"""
from pydantic import BaseModel
from typing import Optional

class ResponseMessage(BaseModel):
    """Mensaje de respuesta genérico"""
    message: str
    detail: Optional[str] = None

class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error: str
    detail: str
