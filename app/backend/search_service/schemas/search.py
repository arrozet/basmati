"""
Schemas para operaciones de búsqueda.

Define los modelos de datos para los resultados de búsqueda
en calendarios y eventos.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CalendarSearchResult(BaseModel):
    """
    Resultado de búsqueda de calendario.
    
    Representa un calendario encontrado en las búsquedas,
    con los campos más relevantes para mostrar en resultados.
    """
    id: str = Field(..., description="ID del calendario", example="507f1f77bcf86cd799439011")
    title: str = Field(..., description="Título del calendario", example="Eventos de la Universidad")
    creator_external_id: str = Field(..., description="ID externo del creador", example="google_123456789")
    creator_display_name: str = Field(..., description="Nombre del creador", example="Juan Pérez")
    keywords: list[str] = Field(default_factory=list, description="Palabras clave del calendario", example=["universidad", "educación", "eventos"])
    color: str = Field(..., description="Color del calendario en formato HEX", example="#FF5733")
    icon: str | None = Field(None, description="Icono del calendario", example="📚")
    description: str | None = Field(None, description="Descripción del calendario", example="Calendario de eventos universitarios")
    visibility: str = Field(..., description="Visibilidad del calendario", example="public")
    subscriber_count: int = Field(default=0, description="Número de suscriptores", example=42)
    created_at: datetime = Field(..., description="Fecha de creación", example="2024-01-15T10:30:00Z")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "Eventos de la Universidad",
                "creator_external_id": "google_123456789",
                "creator_display_name": "Juan Pérez",
                "keywords": ["universidad", "educación", "eventos"],
                "color": "#FF5733",
                "icon": "📚",
                "description": "Calendario de eventos universitarios y académicos",
                "visibility": "public",
                "subscriber_count": 42,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class EventSearchResult(BaseModel):
    """
    Resultado de búsqueda de evento.
    
    Representa un evento encontrado en las búsquedas,
    con los campos más relevantes para mostrar en resultados.
    """
    id: str = Field(..., description="ID del evento", example="507f1f77bcf86cd799439012")
    title: str = Field(..., description="Título del evento", example="Conferencia de IA")
    description: str | None = Field(None, description="Descripción del evento", example="Conferencia sobre inteligencia artificial aplicada")
    calendar_id: str = Field(..., description="ID del calendario", example="507f1f77bcf86cd799439011")
    calendar_title: str = Field(..., description="Título del calendario", example="Eventos de la Universidad")
    creator_external_id: str = Field(..., description="ID externo del creador", example="google_987654321")
    start_time: datetime = Field(..., description="Fecha y hora de inicio", example="2024-03-20T14:00:00Z")
    end_time: datetime = Field(..., description="Fecha y hora de fin", example="2024-03-20T16:00:00Z")
    location: dict | None = Field(None, description="Ubicación del evento", example={"address": "Aula Magna", "place_name": "Universidad de Sevilla"})
    visibility: str = Field(..., description="Visibilidad del evento", example="public")
    created_at: datetime = Field(..., description="Fecha de creación", example="2024-01-15T10:30:00Z")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "title": "Conferencia de IA",
                "description": "Conferencia sobre inteligencia artificial aplicada al desarrollo de software",
                "calendar_id": "507f1f77bcf86cd799439011",
                "calendar_title": "Eventos de la Universidad",
                "creator_external_id": "google_987654321",
                "start_time": "2024-03-20T14:00:00Z",
                "end_time": "2024-03-20T16:00:00Z",
                "location": {
                    "address": "Aula Magna, Universidad de Sevilla",
                    "place_name": "Universidad de Sevilla",
                    "latitude": 37.3576,
                    "longitude": -5.9865
                },
                "visibility": "public",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class CombinedSearchResult(BaseModel):
    """
    Resultado de búsqueda combinada.
    
    Contiene tanto calendarios como eventos encontrados,
    permitiendo mostrar resultados unificados al usuario.
    """
    calendars: list[CalendarSearchResult] = Field(
        default_factory=list,
        description="Calendarios encontrados",
        example=[]
    )
    events: list[EventSearchResult] = Field(
        default_factory=list,
        description="Eventos encontrados",
        example=[]
    )
    total_calendars: int = Field(default=0, description="Total de calendarios encontrados", example=5)
    total_events: int = Field(default=0, description="Total de eventos encontrados", example=12)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "calendars": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "title": "Eventos de la Universidad",
                        "creator_external_id": "google_123456789",
                        "creator_display_name": "Juan Pérez",
                        "keywords": ["universidad", "educación"],
                        "color": "#FF5733",
                        "visibility": "public",
                        "subscriber_count": 42,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "events": [
                    {
                        "id": "507f1f77bcf86cd799439012",
                        "title": "Conferencia de IA",
                        "calendar_id": "507f1f77bcf86cd799439011",
                        "calendar_title": "Eventos de la Universidad",
                        "creator_external_id": "google_987654321",
                        "start_time": "2024-03-20T14:00:00Z",
                        "end_time": "2024-03-20T16:00:00Z",
                        "visibility": "public",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total_calendars": 1,
                "total_events": 1
            }
        }
    )
