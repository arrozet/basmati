"""Modelo de usuario para MongoDB"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from pydantic_core import core_schema
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId para Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.no_info_plain_validator_function(cls.validate),
        ])
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        return {"type": "string"}

class NotificationPreferences(BaseModel):
    """Preferencias de notificación del usuario"""
    in_app: bool = True
    email: bool = True
    email_address: str | None = None
    frequency: str = "instant"  # "instant" o "daily" - solo para nuevos documentos

class UserModel(BaseModel):
    """Modelo de usuario en MongoDB"""
    id: PyObjectId | None = Field(alias="_id", default=None)
    external_id: str  # OAuth provider ID (Google, Facebook)
    provider: str  # "google" or "facebook"
    email: str
    display_name: str
    avatar_url: str | None = None
    notification_preferences: NotificationPreferences = Field(default_factory=lambda: NotificationPreferences())
    followed_calendar_ids: list[PyObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = None
    schema_version: int = Field(default=1, description="Versión del esquema del documento")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
