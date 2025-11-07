"""Schemas para operaciones de integración externa"""
from pydantic import BaseModel, ConfigDict, Field


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
    """
    Schema para importar desde Teamup.
    
    NOTA: Teamup requiere API Key para TODOS los calendarios, incluso los públicos.
    La API Key la debe proporcionar el administrador del calendario.
    """
    user_external_id: str = Field(..., description="External ID del usuario")
    teamup_api_key: str = Field(
        ..., 
        description="API Key de Teamup"
    )
    calendar_keys: list[str] = Field(..., description="Calendar keys de Teamup a importar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "uma_admin",
                "teamup_api_key": "5f207dbbaeafdc37ec0b89d1e716e7f2362889c4481c16d21d0a0a2c70110b6d",
                "calendar_keys": ["ksfogsn8nf72mjdfcv"]
            }
        }
    )


class ImportedCalendar(BaseModel):
    """Schema para un calendario importado"""
    external_id: str = Field(..., description="ID del calendario en el servicio externo")
    basmati_calendar_id: str = Field(..., description="ID del calendario creado en Basmati")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "external_id": "ksfogsn8nf72mjdfcv",
                "basmati_calendar_id": "6908a63eec57fb2153e7593a"
            }
        }
    )


class ImportResponse(BaseModel):
    """Schema de respuesta de importación"""
    success: bool
    message: str
    imported_sources: list[ImportedCalendar] = []
    errors: list[str] = []
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Se importaron 1 calendarios correctamente",
                "imported_sources": [
                    {
                        "external_id": "ksfogsn8nf72mjdfcv",
                        "basmati_calendar_id": "6908a63eec57fb2153e7593a"
                    }
                ],
                "errors": []
            }
        }
    )
