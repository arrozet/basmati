"""Modelo de notificación para MongoDB"""
from datetime import datetime
from typing import Any, Literal
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

class NotificationModel(BaseModel):
    """Modelo de notificación en MongoDB"""
    id: PyObjectId | None = Field(alias="_id", default=None)
    recipient_external_id: str  # reference to users.external_id
    type: Literal["NEW_COMMENT", "EVENT_UPDATE", "CALENDAR_INVITE", "EVENT_REMINDER"]
    title: str
    message: str
    is_read: bool = False
    related_event_id: PyObjectId | None = None
    related_calendar_id: PyObjectId | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None  # for automatic cleanup with TTL index
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
