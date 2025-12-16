"""Modelo de calendario para MongoDB"""
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

class CalendarCommentModel(BaseModel):
    """Comentario realizado sobre un calendario"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author_external_id: str = Field(..., description="External ID del autor")
    author_display_name: str = Field(..., description="Nombre visible del autor")
    text: str = Field(..., description="Contenido del comentario")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha del comentario")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }


class CalendarModel(BaseModel):
    """Modelo de calendario en MongoDB"""
    id: PyObjectId | None = Field(alias="_id", default=None)
    title: str
    creator_external_id: str  # referencia a users.external_id
    creator_display_name: str  # denormalizado para performance
    keywords: list[str] = Field(default_factory=list)
    color: str  # formato HEX (#RRGGBB)
    icon: str | None = None
    parent_calendar_id: PyObjectId | None = None  # para calendarios jerárquicos
    path: list[PyObjectId] = Field(default_factory=list)  # array de IDs ancestros
    description: str | None = None
    visibility: str = "public"  # "public", "private", or "unlisted"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    subscriber_count: int = 0  # contador denormalizado
    comments: list[CalendarCommentModel] = Field(
        default_factory=list,
        description="Comentarios asociados al calendario",
    )

    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
