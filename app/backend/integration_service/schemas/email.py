"""Schemas para operaciones de envío de correo electrónico.

Nuevo en V2: Este módulo define los modelos para el servicio de email
usando SendGrid.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal


class EmailRequest(BaseModel):
    """
    Schema para solicitud de envío de correo electrónico.
    
    Define los campos necesarios para enviar un correo simple
    a través de SendGrid.
    """
    to_email: EmailStr = Field(
        ..., 
        description="Correo electrónico del destinatario"
    )
    subject: str = Field(
        ..., 
        description="Asunto del correo"
    )
    content: str = Field(
        ..., 
        description="Contenido del correo en texto plano"
    )
    content_type: Literal["text/plain", "text/html"] = Field(
        "text/plain", 
        description="Tipo de contenido del correo"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_email": "usuario@example.com",
                "subject": "Nuevo comentario en tu calendario",
                "content": "Alguien ha comentado en tu evento 'Reunión de equipo'",
                "content_type": "text/plain"
            }
        }
    )


class EmailResponse(BaseModel):
    """
    Schema de respuesta para envío de correo.
    
    Indica el resultado de la operación de envío.
    """
    success: bool = Field(
        ..., 
        description="Si el correo se envió correctamente"
    )
    message: str = Field(
        ..., 
        description="Mensaje de estado"
    )
    message_id: str | None = Field(
        None, 
        description="ID del mensaje si fue exitoso"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Correo enviado correctamente",
                "message_id": "abc123xyz"
            }
        }
    )


class BulkEmailRequest(BaseModel):
    """
    Schema para envío de correos en lote (resumen diario).
    
    Permite enviar un resumen con múltiples notificaciones
    en un solo correo.
    """
    to_email: EmailStr = Field(
        ..., 
        description="Correo electrónico del destinatario"
    )
    subject: str = Field(
        ..., 
        description="Asunto del correo"
    )
    notifications: list[dict] = Field(
        ..., 
        description="Lista de notificaciones para el resumen"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_email": "usuario@example.com",
                "subject": "Resumen diario de Basmati - 3 nuevas notificaciones",
                "notifications": [
                    {
                        "title": "Nuevo comentario en 'Reunión de equipo'",
                        "message": "Juan Pérez comentó: ¿A qué hora quedamos?",
                        "created_at": "2025-12-03T10:30:00"
                    }
                ]
            }
        }
    )


class CommentNotificationRequest(BaseModel):
    """
    Schema para notificación de nuevo comentario.
    
    Define los campos necesarios para enviar una notificación
    cuando alguien comenta en un evento.
    """
    to_email: EmailStr = Field(
        ..., 
        description="Correo del destinatario"
    )
    event_title: str = Field(
        ..., 
        description="Título del evento"
    )
    calendar_title: str = Field(
        ..., 
        description="Título del calendario"
    )
    commenter_name: str = Field(
        ..., 
        description="Nombre de quien comentó"
    )
    comment_text: str = Field(
        ..., 
        description="Texto del comentario"
    )
    event_id: str = Field(
        ..., 
        description="ID del evento"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to_email": "usuario@example.com",
                "event_title": "Reunión de equipo",
                "calendar_title": "Trabajo",
                "commenter_name": "Juan Pérez",
                "comment_text": "¿A qué hora quedamos?",
                "event_id": "507f1f77bcf86cd799439011"
            }
        }
    )

