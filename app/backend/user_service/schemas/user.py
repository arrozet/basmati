"""Schemas para operaciones de usuario"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Literal

class NotificationPreferencesSchema(BaseModel):
    """Preferencias de notificación"""
    in_app: bool = True
    email: bool = True
    email_address: str | None = None
    frequency: Literal["instant", "daily"] = "instant"

class UserCreate(BaseModel):
    """Schema base de usuario"""
    external_id: str = Field(..., description="ID del proveedor OAuth")
    provider: Literal["google", "facebook"] = Field(..., description="Proveedor OAuth")
    email: EmailStr = Field(..., description="Email del usuario")
    display_name: str = Field(..., description="Nombre visible del usuario")
    avatar_url: str | None = Field(None, description="URL del avatar")
    notification_preferences: NotificationPreferencesSchema = Field(
        default_factory=NotificationPreferencesSchema,
        description="Preferencias de notificación"
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
                    "email_address": None
                }
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema para actualizar un usuario"""
    email: EmailStr | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    notification_preferences: NotificationPreferencesSchema | None = None
    followed_calendar_ids: list[str] | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "artur@basmati.app",
                "display_name": "Arturo Duro"
            }
        }
    )

class UserResponse(UserCreate):
    """Schema de respuesta de usuario"""
    id: str
    followed_calendar_ids: list[str] = []
    created_at: datetime
    last_login: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
