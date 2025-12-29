"""
Schemas y DTOs para el módulo de importación V3.

Define los tipos de entrada/salida para el servicio de importación,
incluyendo enumeraciones de proveedores y schemas de request/response.
"""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ProviderType(str, Enum):
    """
    Tipos de proveedores soportados para importación.
    
    Extender esta enumeración para añadir nuevos proveedores.
    """
    GOOGLE = "google"
    TEAMUP = "teamup"
    # Futuros proveedores:
    # OUTLOOK = "outlook"
    # ICLOUD = "icloud"


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class BaseImportRequest(BaseModel):
    """Schema base para requests de importación."""
    
    user_external_id: str = Field(
        ...,
        description="ID externo del usuario en Basmati",
        examples=["google_123456789", "uma_admin"]
    )
    calendar_ids: list[str] = Field(
        ...,
        description="Lista de IDs de calendarios a importar",
        min_length=1
    )
    calendar_name: Optional[str] = Field(
        None,
        description="Nombre personalizado para el calendario importado (usa el nombre original si no se especifica)"
    )
    days_past: int = Field(
        30,
        ge=0,
        le=365,
        description="Días hacia el pasado para importar eventos (0-365, por defecto 30)"
    )
    days_future: int = Field(
        90,
        ge=0,
        le=365,
        description="Días hacia el futuro para importar eventos (0-365, por defecto 90)"
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class GoogleCalendarImportRequestV3(BaseImportRequest):
    """Schema para importar desde Google Calendar (V3)."""
    
    access_token: str = Field(
        ...,
        description="Token OAuth2 de Google",
        min_length=10
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "google_123456789",
                "access_token": "ya29.a0AfH6SMBx...",
                "calendar_ids": ["primary"]
            }
        }
    )


class TeamupImportRequestV3(BaseImportRequest):
    """
    Schema para importar desde Teamup (V3).
    
    La API Key puede venir del request o del servidor (fallback a .env).
    """
    
    api_key: Optional[str] = Field(
        None,
        description="API Key de Teamup (opcional, usa servidor por defecto)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "uma_admin",
                "calendar_ids": ["ksfogsn8nf72mjdfcv"],
                "api_key": None
            }
        }
    )


class GenericImportRequest(BaseModel):
    """
    Schema genérico para importación (usado por el servicio principal).
    
    Permite especificar el proveedor y los datos de autenticación de forma genérica.
    """
    
    provider: ProviderType = Field(
        ...,
        description="Tipo de proveedor de calendario"
    )
    user_external_id: str = Field(
        ...,
        description="ID externo del usuario en Basmati"
    )
    calendar_ids: list[str] = Field(
        ...,
        description="Lista de IDs/keys de calendarios a importar",
        min_length=1
    )
    calendar_name: Optional[str] = Field(
        None,
        description="Nombre personalizado para el calendario importado"
    )
    credentials: dict[str, Any] = Field(
        default_factory=dict,
        description="Credenciales específicas del proveedor"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "teamup",
                "user_external_id": "uma_admin",
                "calendar_ids": ["ksfogsn8nf72mjdfcv"],
                "credentials": {
                    "api_key": "optional_api_key"
                }
            }
        }
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ImportedCalendarV3(BaseModel):
    """Schema para un calendario importado exitosamente."""
    
    external_id: str = Field(
        ...,
        description="ID del calendario en el proveedor externo"
    )
    basmati_calendar_id: str = Field(
        ...,
        description="ID del calendario creado en Basmati"
    )
    events_imported: int = Field(
        default=0,
        description="Número de eventos importados"
    )
    events_failed: int = Field(
        default=0,
        description="Número de eventos que fallaron"
    )


class ImportResponseV3(BaseModel):
    """Schema de respuesta de importación V3."""
    
    success: bool = Field(
        ...,
        description="True si al menos un calendario se importó"
    )
    message: str = Field(
        ...,
        description="Mensaje descriptivo del resultado"
    )
    provider: str = Field(
        ...,
        description="Proveedor utilizado para la importación"
    )
    imported_calendars: list[ImportedCalendarV3] = Field(
        default_factory=list,
        description="Lista de calendarios importados exitosamente"
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Lista de errores encontrados"
    )
    total_events_imported: int = Field(
        default=0,
        description="Total de eventos importados"
    )
    total_events_failed: int = Field(
        default=0,
        description="Total de eventos que fallaron"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Importación completada: 1 calendario, 15 eventos",
                "provider": "teamup",
                "imported_calendars": [
                    {
                        "external_id": "ksfogsn8nf72mjdfcv",
                        "basmati_calendar_id": "6908a63eec57fb2153e7593a",
                        "events_imported": 15,
                        "events_failed": 0
                    }
                ],
                "errors": [],
                "total_events_imported": 15,
                "total_events_failed": 0
            }
        }
    )


# =============================================================================
# HELPER CLASSES
# =============================================================================

class ProviderCapabilities(BaseModel):
    """Describe las capacidades de un proveedor."""
    
    provider: ProviderType
    name: str
    supports_oauth: bool
    supports_api_key: bool
    supports_sync: bool = False  # Sincronización bidireccional
    requires_calendar_selection: bool = True
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "google",
                "name": "Google Calendar",
                "supports_oauth": True,
                "supports_api_key": False,
                "supports_sync": False,
                "requires_calendar_selection": True
            }
        }
    )


# Definición de capacidades por proveedor
PROVIDER_CAPABILITIES: dict[ProviderType, ProviderCapabilities] = {
    ProviderType.GOOGLE: ProviderCapabilities(
        provider=ProviderType.GOOGLE,
        name="Google Calendar",
        supports_oauth=True,
        supports_api_key=False,
        supports_sync=False,
        requires_calendar_selection=True,
    ),
    ProviderType.TEAMUP: ProviderCapabilities(
        provider=ProviderType.TEAMUP,
        name="Teamup",
        supports_oauth=False,
        supports_api_key=True,
        supports_sync=False,
        requires_calendar_selection=True,
    ),
}
