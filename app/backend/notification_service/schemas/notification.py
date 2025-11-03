"""Schemas para operaciones de notificación"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class NotificationCreate(BaseModel):
    """Schema para crear una notificación"""
    recipient_external_id: str = Field(..., description="External ID del usuario receptor")
    type: Literal["NEW_COMMENT", "EVENT_UPDATE", "CALENDAR_INVITE", "EVENT_REMINDER"] = Field(
        ..., 
        description="Tipo de notificación"
    )
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    related_event_id: str | None = Field(None, description="ID del evento relacionado")
    related_calendar_id: str | None = Field(None, description="ID del calendario relacionado")
    expires_at: datetime | None = Field(None, description="Fecha de expiración para limpieza automática")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recipient_external_id": "google_123456789",
                "type": "NEW_COMMENT",
                "title": "Nuevo comentario en evento",
                "message": "Juan Pérez ha comentado en el evento 'Reunión de equipo'",
                "related_event_id": "507f1f77bcf86cd799439011",
                "related_calendar_id": "507f1f77bcf86cd799439012",
                "expires_at": None
            }
        }
    )

class NotificationUpdate(BaseModel):
    """Schema para actualizar una notificación"""
    is_read: bool | None = Field(None, description="Estado de lectura")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_read": True
            }
        }
    )

class NotificationResponse(BaseModel):
    """Schema de respuesta de notificación"""
    id: str = Field(..., description="ID de la notificación")
    recipient_external_id: str = Field(..., description="External ID del usuario receptor")
    type: Literal["NEW_COMMENT", "EVENT_UPDATE", "CALENDAR_INVITE", "EVENT_REMINDER"] = Field(
        ...,
        description="Tipo de notificación"
    )
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    is_read: bool = Field(..., description="Estado de lectura")
    related_event_id: str | None = Field(None, description="ID del evento relacionado")
    related_calendar_id: str | None = Field(None, description="ID del calendario relacionado")
    created_at: datetime = Field(..., description="Fecha de creación")
    expires_at: datetime | None = Field(None, description="Fecha de expiración")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "recipient_external_id": "google_123456789",
                "type": "NEW_COMMENT",
                "title": "Nuevo comentario en evento",
                "message": "Juan Pérez ha comentado en el evento 'Reunión de equipo'",
                "is_read": False,
                "related_event_id": "507f1f77bcf86cd799439011",
                "related_calendar_id": "507f1f77bcf86cd799439012",
                "created_at": "2025-11-03T10:30:00",
                "expires_at": None
            }
        }
    )
