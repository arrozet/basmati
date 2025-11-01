"""Schemas para operaciones de usuario"""
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class NotificationPreferencesSchema(BaseModel):
    """Preferencias de notificación"""
    email_enabled: bool = True
    in_app_enabled: bool = True

class UserBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    name: str
    notification_preferences: NotificationPreferencesSchema

class UserCreate(UserBase):
    """Schema para crear un usuario"""
    pass

class UserUpdate(BaseModel):
    """Schema para actualizar un usuario"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    notification_preferences: Optional[NotificationPreferencesSchema] = None

class UserResponse(UserBase):
    """Schema de respuesta de usuario"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
