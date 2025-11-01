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
    email_enabled: bool = True
    in_app_enabled: bool = True

class UserModel(BaseModel):
    """Modelo de usuario en MongoDB"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    name: str
    notification_preferences: NotificationPreferences
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
