"""Schemas para operaciones de usuario"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal

class NotificationPreferencesSchema(BaseModel):
    """Preferencias de notificación"""
    in_app: bool = True
    email: bool = True
    email_address: Optional[str] = None

class UserBase(BaseModel):
    """Schema base de usuario"""
    external_id: str  # OAuth provider ID
    provider: Literal["google", "facebook"]  # Solo "google" o "facebook"
    email: EmailStr
    display_name: str
    avatar_url: Optional[str] = None
    notification_preferences: NotificationPreferencesSchema = NotificationPreferencesSchema()

class UserCreate(UserBase):
    """Schema para crear un usuario con OAuth"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "external_id": "google_123456789",
                "provider": "google",
                "email": "usuario@ejemplo.com",
                "display_name": "Juan Pérez",
                "avatar_url": "https://lh3.googleusercontent.com/a/default-user",
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
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    notification_preferences: Optional[NotificationPreferencesSchema] = None
    followed_calendar_ids: Optional[list[str]] = None

class UserResponse(UserBase):
    """Schema de respuesta de usuario"""
    id: str
    followed_calendar_ids: list[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
