"""
Schemas comunes compartidos entre todos los microservicios.

Incluye modelos Pydantic reutilizables para respuestas estándar
de la API REST de Basmati.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResponseMessage(BaseModel):
    """
    Mensaje de respuesta genérico.
    
    Se utiliza para respuestas simples que solo necesitan
    comunicar un mensaje de éxito o información adicional.
    
    Example:
        ```json
        {
            "message": "Usuario eliminado exitosamente",
            "detail": "El usuario con ID 507f191e810c19729de860ea fue eliminado"
        }
        ```
    """
    message: str
    detail: Optional[str] = None

class ErrorResponse(BaseModel):
    """
    Respuesta de error estandarizada.
    
    Se utiliza para comunicar errores de forma consistente
    en todos los microservicios.
    
    Example:
        ```json
        {
            "error": "ValidationError",
            "detail": "El email ya está registrado en el sistema"
        }
        ```
    """
    error: str
    detail: str

class PaginationParams(BaseModel):
    """
    Parámetros de paginación comunes.
    
    Se utiliza para búsquedas que devuelven múltiples resultados.
    """
    skip: int = 0
    limit: int = 10
    
    class Config:
        # skip debe ser >= 0
        # limit debe estar entre 1 y 100
        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 10
            }
        }

class TimestampedModel(BaseModel):
    """
    Modelo base con timestamps automáticos.
    
    Todos los documentos en MongoDB deben tener estos campos
    para auditoría y tracking de cambios.
    """
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
