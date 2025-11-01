"""Modelo de usuario para MongoDB"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId para Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

class NotificationPreferences(BaseModel):
    """Preferencias de notificación del usuario"""
    in_app: bool = True
    email: bool = True
    email_address: Optional[str] = None

class UserModel(BaseModel):
    """Modelo de usuario en MongoDB"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    external_id: str  # OAuth provider ID (Google, Facebook)
    provider: str  # "google" or "facebook"
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    notification_preferences: NotificationPreferences = Field(default_factory=lambda: NotificationPreferences())
    followed_calendar_ids: list[PyObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
