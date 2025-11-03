"""Modelo de fuente de integración para MongoDB"""
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

class IntegrationSourceModel(BaseModel):
    """Modelo de fuente de integración en MongoDB"""
    id: PyObjectId | None = Field(alias="_id", default=None)
    user_external_id: str  # referencia a users.external_id
    source_type: str  # "google_calendar" or "teamup"
    external_source_id: str  # ID del calendario en el servicio externo
    basmati_calendar_id: PyObjectId | None = None  # calendario creado en Basmati
    sync_enabled: bool = True
    last_sync: datetime | None = None
    sync_status: str = "pending"  # "success", "error", "pending"
    sync_error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
