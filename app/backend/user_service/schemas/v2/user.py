"""Schemas v2 para operaciones de usuario.

Mejoras V2:
- Añade campo 'frequency' a las preferencias de notificación
- Soporta valores 'instant' y 'daily' para la frecuencia de notificaciones
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Literal


class NotificationPreferencesSchemaV2(BaseModel):
    """Preferencias de notificación V2.
    
    Añade campo de frecuencia para controlar cuándo se envían las notificaciones.
    """
    in_app: bool = Field(True, description="Activar notificaciones dentro de la app")
    email: bool = Field(True, description="Activar notificaciones por correo electrónico")
    email_address: str | None = Field(None, description="Correo alternativo para notificaciones")
    frequency: Literal["instant", "daily"] = Field(
        "instant", 
        description="Frecuencia de notificaciones: 'instant' envía inmediatamente, 'daily' envía resumen a las 00:00"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "in_app": True,
                "email": True,
                "email_address": None,
                "frequency": "instant"
            }
        }
    )


class UserCreateV2(BaseModel):
    """Schema v2 para crear usuario.
    
    Incluye preferencias de notificación con frecuencia.
    """
    external_id: str = Field(..., description="ID del proveedor OAuth")
    provider: Literal["google", "facebook"] = Field(..., description="Proveedor OAuth")
    email: EmailStr = Field(..., description="Email del usuario")
    display_name: str = Field(..., description="Nombre visible del usuario")
    avatar_url: str | None = Field(None, description="URL del avatar")
    notification_preferences: NotificationPreferencesSchemaV2 = Field(
        default_factory=NotificationPreferencesSchemaV2,
        description="Preferencias de notificación con frecuencia"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "external_id": "google_123456789",
                "provider": "google",
                "email": "juan@example.com",
                "display_name": "Juan Pérez",
                "avatar_url": "https://example.com/avatar.jpg",
                "notification_preferences": {
                    "in_app": True,
                    "email": True,
                    "email_address": None,
                    "frequency": "instant"
                }
            }
        }
    )


class UserUpdateV2(BaseModel):
    """Schema v2 para actualizar un usuario.
    
    Soporta preferencias de notificación con frecuencia.
    """
    email: EmailStr | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    notification_preferences: NotificationPreferencesSchemaV2 | None = None
    followed_calendar_ids: list[str] | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "artur@basmati.app",
                "display_name": "Arturo Duro",
                "notification_preferences": {
                    "in_app": True,
                    "email": True,
                    "email_address": "otro@email.com",
                    "frequency": "daily"
                }
            }
        }
    )


class UserResponseV2(UserCreateV2):
    """Schema v2 de respuesta de usuario.
    
    Incluye todos los campos de UserCreateV2 más campos de auditoría.
    """
    id: str
    followed_calendar_ids: list[str] = []
    created_at: datetime
    last_login: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
