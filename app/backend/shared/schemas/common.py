"""
Schemas comunes compartidos entre todos los microservicios.

Incluye modelos Pydantic reutilizables para respuestas estándar
de la API REST de Basmati.
"""
from pydantic import BaseModel
from typing import Optional

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
