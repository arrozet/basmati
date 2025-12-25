"""
Schemas para autenticación y respuestas del auth service.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    """
    Request para login con ID token de Google.
    
    El frontend obtiene el ID token del flujo OAuth de Google
    y lo envía aquí para verificación y obtención de token de sesión.
    """
    id_token: str = Field(..., description="ID token de Google OAuth")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class TokenResponse(BaseModel):
    """Respuesta con token de sesión JWT."""
    access_token: str = Field(..., description="Token JWT de sesión")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración")
    user: "UserInfo" = Field(..., description="Información del usuario")
    is_new_user: bool = Field(default=False, description="True si es un usuario nuevo")


class UserInfo(BaseModel):
    """Información básica del usuario autenticado."""
    external_id: str = Field(..., description="ID externo del usuario (Google ID)")
    email: EmailStr = Field(..., description="Email del usuario")
    display_name: str = Field(..., description="Nombre visible")
    avatar_url: str | None = Field(None, description="URL del avatar")
    provider: str = Field(default="google", description="Proveedor OAuth")


class VerifyTokenRequest(BaseModel):
    """Request para verificar un token de sesión."""
    token: str = Field(..., description="Token JWT a verificar")


class VerifyTokenResponse(BaseModel):
    """Respuesta de verificación de token."""
    valid: bool = Field(..., description="True si el token es válido")
    user: UserInfo | None = Field(None, description="Info del usuario si es válido")
    error: str | None = Field(None, description="Mensaje de error si no es válido")


class AuthUrlResponse(BaseModel):
    """Respuesta con la URL de autorización de Google."""
    auth_url: str = Field(..., description="URL para redirigir al usuario")


class ErrorResponse(BaseModel):
    """Respuesta de error."""
    error: str = Field(..., description="Código de error")
    message: str = Field(..., description="Descripción del error")


# Actualizar forward reference
TokenResponse.model_rebuild()
