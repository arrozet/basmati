"""Schemas para operaciones del resumen diario de notificaciones.

Nuevo en V2: Este módulo define los modelos para el servicio de
resumen diario (daily digest).
"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class DailyDigestUserInfo(BaseModel):
    """
    Información de usuario para el digest.
    
    Contiene los datos básicos necesarios para enviar
    el resumen diario a un usuario.
    """
    external_id: str = Field(
        ..., 
        description="ID externo del usuario"
    )
    email: str = Field(
        ..., 
        description="Email del usuario"
    )
    display_name: str = Field(
        ..., 
        description="Nombre para mostrar del usuario"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "external_id": "google_123456789",
                "email": "usuario@example.com",
                "display_name": "Juan Pérez"
            }
        }
    )


class NotificationSummary(BaseModel):
    """
    Resumen de una notificación para el digest.
    
    Representa una notificación individual dentro del
    resumen diario.
    """
    title: str = Field(
        ..., 
        description="Título de la notificación"
    )
    message: str = Field(
        ..., 
        description="Mensaje de la notificación"
    )
    calendar_title: str | None = Field(
        None, 
        description="Título del calendario relacionado"
    )
    event_title: str | None = Field(
        None, 
        description="Título del evento relacionado"
    )
    created_at: datetime = Field(
        ..., 
        description="Fecha de creación de la notificación"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Nuevo comentario",
                "message": "Juan ha comentado en tu evento",
                "calendar_title": "Trabajo",
                "event_title": "Reunión de equipo",
                "created_at": "2025-12-03T10:30:00"
            }
        }
    )


class DigestRequest(BaseModel):
    """
    Solicitud para enviar un digest específico.
    
    Permite enviar el resumen diario a un usuario particular.
    """
    user_external_id: str = Field(
        ..., 
        description="ID externo del usuario al que enviar el digest"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_external_id": "google_123456789"
            }
        }
    )


class BulkDigestResponse(BaseModel):
    """
    Respuesta del envío masivo de digests.
    
    Indica el resultado del envío de resúmenes diarios
    a todos los usuarios configurados.
    """
    total_users: int = Field(
        ..., 
        description="Total de usuarios con frecuencia diaria"
    )
    emails_sent: int = Field(
        ..., 
        description="Número de emails enviados exitosamente"
    )
    errors: list[str] = Field(
        default_factory=list, 
        description="Lista de errores encontrados"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_users": 10,
                "emails_sent": 8,
                "errors": [
                    "Usuario user_123: sin email configurado",
                    "Usuario user_456: error enviando email"
                ]
            }
        }
    )


class DigestSendResponse(BaseModel):
    """
    Respuesta del envío de digest a un usuario específico.
    
    Indica el resultado del envío individual.
    """
    success: bool = Field(
        ..., 
        description="Si el envío fue exitoso"
    )
    message: str = Field(
        ..., 
        description="Mensaje de estado"
    )
    email: str | None = Field(
        None, 
        description="Email al que se envió"
    )
    notifications_count: int = Field(
        0, 
        description="Número de notificaciones incluidas"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Digest enviado exitosamente",
                "email": "usuario@example.com",
                "notifications_count": 5
            }
        }
    )


class DigestPreviewResponse(BaseModel):
    """
    Respuesta de vista previa del digest.
    
    Permite ver el contenido del digest sin enviarlo.
    """
    user_id: str = Field(
        ..., 
        description="ID del usuario"
    )
    user_name: str = Field(
        ..., 
        description="Nombre del usuario"
    )
    notifications_count: int = Field(
        ..., 
        description="Número de notificaciones"
    )
    html_preview: str = Field(
        ..., 
        description="Contenido HTML del digest"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "google_123456789",
                "user_name": "Juan Pérez",
                "notifications_count": 3,
                "html_preview": "<html>...</html>"
            }
        }
    )

