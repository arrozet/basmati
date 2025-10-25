"""
Common schemas used across the API

Schemas genéricos reutilizables para respuestas estándar.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Schema para respuestas simples con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta", example="Operación exitosa")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operación completada exitosamente"
            }
        }


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""
    error: str = Field(..., description="Tipo de error", example="ValidationError")
    detail: str = Field(..., description="Detalle del error", example="El email ya está registrado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "El email ya está registrado"
            }
        }


class HealthResponse(BaseModel):
    """Schema para health check"""
    status: str = Field(..., description="Estado del servicio", example="healthy")
    database: str = Field(..., description="Estado de la base de datos", example="connected")
    version: str = Field(..., description="Versión de la API", example="1.0.0")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "version": "1.0.0"
            }
        }
