"""Schemas para operaciones de integración externa"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class IntegrationSourceBase(BaseModel):
    """Schema base para fuente de integración"""
    source_type: Literal["google_calendar", "teamup"] = Field(..., description="Tipo de fuente externa")
    external_source_id: str = Field(..., description="ID del calendario en el servicio externo")
    sync_enabled: bool = Field(True, description="Si la sincronización está habilitada")

class IntegrationSourceCreate(IntegrationSourceBase):
    """Schema para crear una fuente de integración"""
    user_external_id: str = Field(..., description="External ID del usuario propietario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "google_123456789",
                "source_type": "google_calendar",
                "external_source_id": "primary",
                "sync_enabled": True
            }
        }
    )

class IntegrationSourceResponse(IntegrationSourceBase):
    """Schema de respuesta de fuente de integración"""
    id: str
    user_external_id: str
    basmati_calendar_id: str | None = None
    last_sync: datetime | None = None
    sync_status: Literal["success", "error", "pending"] = "pending"
    sync_error_message: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GoogleCalendarImportRequest(BaseModel):
    """Schema para importar desde Google Calendar"""
    user_external_id: str = Field(..., description="External ID del usuario")
    google_access_token: str = Field(..., description="Token de acceso de Google OAuth")
    calendar_ids: list[str] | None = Field(None, description="IDs específicos de calendarios a importar (None = todos)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "google_123456789",
                "google_access_token": "ya29.a0AfH6SMBx...",
                "calendar_ids": ["primary", "calendar_id_2"]
            }
        }
    )

class TeamupImportRequest(BaseModel):
    """Schema para importar desde Teamup"""
    user_external_id: str = Field(..., description="External ID del usuario")
    teamup_api_key: str = Field(..., description="API Key de Teamup")
    calendar_keys: list[str] = Field(..., description="Calendar keys de Teamup a importar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "google_123456789",
                "teamup_api_key": "tu_api_key_aqui",
                "calendar_keys": ["ks1234567", "ks7654321"]
            }
        }
    )

class ImportResponse(BaseModel):
    """Schema de respuesta de importación"""
    success: bool
    message: str
    imported_sources: list[IntegrationSourceResponse] = []
    errors: list[str] = []
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Se importaron 2 calendarios correctamente",
                "imported_sources": [],
                "errors": []
            }
        }
    )

class SyncStatusResponse(BaseModel):
    """Schema para estado de sincronización"""
    source_id: str
    source_type: str
    sync_status: str
    last_sync: datetime | None
    sync_error_message: str | None = None
    events_synced: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_id": "507f1f77bcf86cd799439011",
                "source_type": "google_calendar",
                "sync_status": "success",
                "last_sync": "2024-11-03T10:30:00",
                "sync_error_message": None,
                "events_synced": 42
            }
        }
    )
