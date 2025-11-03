"""Schemas para operaciones de calendario"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class CalendarCreate(BaseModel):
    """Schema para crear un calendario"""
    title: str = Field(..., description="Título del calendario")
    creator_external_id: str = Field(..., description="ID del usuario creador (external_id)")
    creator_display_name: str = Field(..., description="Nombre del creador")
    keywords: list[str] = Field(default_factory=list, description="Palabras clave para búsqueda")
    color: str = Field(..., description="Color en formato HEX (#RRGGBB)")
    icon: str | None = Field(None, description="Icono del calendario")
    parent_calendar_id: str | None = Field(None, description="ID del calendario padre (opcional)")
    description: str | None = Field(None, description="Descripción del calendario")
    visibility: Literal["public", "private", "unlisted"] = Field("public", description="Visibilidad del calendario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Calendario de Marketing",
                "creator_external_id": "google_123456789",
                "creator_display_name": "Juan Pérez",
                "keywords": ["marketing", "ventas", "campañas"],
                "color": "#FF5733",
                "icon": "📅",
                "parent_calendar_id": None,
                "description": "Calendario principal del departamento de marketing",
                "visibility": "public"
            }
        }
    )

class CalendarUpdate(BaseModel):
    """Schema para actualizar un calendario"""
    title: str | None = None
    keywords: list[str] | None = None
    color: str | None = None
    icon: str | None = None
    description: str | None = None
    visibility: Literal["public", "private", "unlisted"] | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Calendario de Marketing 2024",
                "keywords": ["marketing", "ventas", "campañas", "2024"],
                "color": "#00A8E8"
            }
        }
    )

class CalendarResponse(BaseModel):
    """Schema de respuesta de calendario"""
    id: str
    title: str
    creator_external_id: str
    creator_display_name: str
    keywords: list[str] = []
    color: str
    icon: str | None = None
    parent_calendar_id: str | None = None
    path: list[str] = []
    description: str | None = None
    visibility: str
    created_at: datetime
    updated_at: datetime
    subscriber_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class CalendarHierarchy(BaseModel):
    """Schema para jerarquía de calendarios"""
    calendar: CalendarResponse
    children: list["CalendarHierarchy"] = []
    
    model_config = ConfigDict(from_attributes=True)
