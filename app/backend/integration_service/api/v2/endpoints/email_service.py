"""Servicio de envío de correos electrónicos usando SendGrid.

Nuevo en V2: Este módulo implementa la funcionalidad de envío de correos
usando la API de SendGrid desde la cuenta amcgil@uma.es.
"""
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal
import httpx
import os

router = APIRouter()


class EmailRequest(BaseModel):
    """Schema para solicitud de envío de correo electrónico."""
    to_email: EmailStr = Field(..., description="Correo electrónico del destinatario")
    subject: str = Field(..., description="Asunto del correo")
    content: str = Field(..., description="Contenido del correo en texto plano")
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
    """Schema de respuesta para envío de correo."""
    success: bool = Field(..., description="Si el correo se envió correctamente")
    message: str = Field(..., description="Mensaje de estado")
    message_id: str | None = Field(None, description="ID del mensaje si fue exitoso")
    
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
    """Schema para envío de correos en lote (resumen diario)."""
    to_email: EmailStr = Field(..., description="Correo electrónico del destinatario")
    subject: str = Field(..., description="Asunto del correo")
    notifications: list[dict] = Field(..., description="Lista de notificaciones para el resumen")
    
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


# Configuración de SendGrid
SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
SENDER_EMAIL = "amcgil@uma.es"
SENDER_NAME = "Basmati Calendar"


async def send_email_via_sendgrid(
    to_email: str,
    subject: str,
    content: str,
    content_type: str = "text/plain"
) -> tuple[bool, str, str | None]:
    """
    Envía un correo electrónico usando la API de SendGrid.
    
    Args:
        to_email: Correo del destinatario
        subject: Asunto del correo
        content: Contenido del correo
        content_type: Tipo de contenido (text/plain o text/html)
        
    Returns:
        Tupla con (éxito, mensaje, message_id)
    """
    api_key = os.getenv("SENDGRID_API_KEY")
    
    if not api_key:
        # Si no hay API key, simular envío exitoso para desarrollo
        print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        print(f"[MOCK EMAIL] Content: {content[:100]}...")
        return True, "Correo simulado (sin API key configurada)", "mock_id_123"
    
    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {
            "email": SENDER_EMAIL,
            "name": SENDER_NAME
        },
        "content": [
            {
                "type": content_type,
                "value": content
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                SENDGRID_API_URL,
                json=payload,
                headers=headers
            )
            
            if response.status_code in [200, 201, 202]:
                message_id = response.headers.get("X-Message-Id", "unknown")
                return True, "Correo enviado correctamente", message_id
            else:
                error_detail = response.text
                print(f"[SENDGRID ERROR] Status: {response.status_code}, Detail: {error_detail}")
                return False, f"Error de SendGrid: {response.status_code}", None
                
    except httpx.TimeoutException:
        return False, "Timeout al conectar con SendGrid", None
    except Exception as e:
        print(f"[SENDGRID ERROR] Exception: {str(e)}")
        return False, f"Error inesperado: {str(e)}", None


@router.post(
    "/send",
    response_model=EmailResponse,
    summary="Enviar correo electrónico",
    description="""
Envía un correo electrónico usando SendGrid.

**Nuevo en V2**: Este endpoint no existe en V1.

El correo se envía desde la cuenta amcgil@uma.es.
Si no hay API key de SendGrid configurada, simula el envío para desarrollo.
    """,
    responses={
        200: {"description": "Correo enviado exitosamente."},
        500: {"description": "Error al enviar el correo."}
    }
)
async def send_email(
    email_request: EmailRequest = Body(..., description="Datos del correo a enviar")
):
    """
    Envía un correo electrónico usando SendGrid.
    
    Args:
        email_request: Datos del correo (destinatario, asunto, contenido)
        
    Returns:
        EmailResponse: Resultado del envío
    """
    success, message, message_id = await send_email_via_sendgrid(
        to_email=email_request.to_email,
        subject=email_request.subject,
        content=email_request.content,
        content_type=email_request.content_type
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return EmailResponse(
        success=success,
        message=message,
        message_id=message_id
    )


@router.post(
    "/send-digest",
    response_model=EmailResponse,
    summary="Enviar resumen diario de notificaciones",
    description="""
Envía un correo con el resumen diario de notificaciones.

**Nuevo en V2**: Este endpoint no existe en V1.

Formatea las notificaciones en un correo HTML con estilo Basmati.
    """,
    responses={
        200: {"description": "Resumen enviado exitosamente."},
        500: {"description": "Error al enviar el resumen."}
    }
)
async def send_daily_digest(
    request: BulkEmailRequest = Body(..., description="Datos del resumen diario")
):
    """
    Envía un correo con el resumen diario de notificaciones.
    
    Args:
        request: Datos del resumen (destinatario, lista de notificaciones)
        
    Returns:
        EmailResponse: Resultado del envío
    """
    # Construir HTML del resumen
    notifications_html = ""
    for notif in request.notifications:
        notifications_html += f"""
        <div style="border: 2px solid #1A1A1A; padding: 15px; margin-bottom: 10px; background: white;">
            <h3 style="margin: 0 0 10px 0; color: #1A1A1A;">{notif.get('title', 'Notificación')}</h3>
            <p style="margin: 0; color: #666;">{notif.get('message', '')}</p>
            <small style="color: #999;">{notif.get('created_at', '')}</small>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{request.subject}</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #FFFAEB; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto;">
            <div style="background: #EBBE4D; padding: 20px; border: 3px solid #1A1A1A; margin-bottom: 20px;">
                <h1 style="margin: 0; color: #1A1A1A; font-size: 24px;">🍚 Basmati Calendar</h1>
                <p style="margin: 10px 0 0 0; color: #1A1A1A;">Tu resumen diario de actividad</p>
            </div>
            
            <h2 style="color: #1A1A1A;">Tienes {len(request.notifications)} nueva(s) notificación(es)</h2>
            
            {notifications_html}
            
            <div style="text-align: center; margin-top: 20px; padding: 15px; background: #f0f0f0; border: 2px solid #1A1A1A;">
                <a href="http://localhost:5173/dashboard" style="color: #5496FF; text-decoration: none; font-weight: bold;">
                    Ver todas las notificaciones en Basmati →
                </a>
            </div>
            
            <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
                Este correo fue enviado automáticamente por Basmati Calendar.
                <br>Puedes cambiar tus preferencias de notificación en tu perfil.
            </p>
        </div>
    </body>
    </html>
    """
    
    success, message, message_id = await send_email_via_sendgrid(
        to_email=request.to_email,
        subject=request.subject,
        content=html_content,
        content_type="text/html"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return EmailResponse(
        success=success,
        message=message,
        message_id=message_id
    )


@router.post(
    "/send-comment-notification",
    response_model=EmailResponse,
    summary="Enviar notificación de nuevo comentario",
    description="""
Envía un correo notificando sobre un nuevo comentario en un calendario.

**Nuevo en V2**: Este endpoint no existe en V1.

Formatea el correo con estilo Basmati para notificaciones de comentarios.
    """,
    responses={
        200: {"description": "Notificación enviada exitosamente."},
        500: {"description": "Error al enviar la notificación."}
    }
)
async def send_comment_notification(
    to_email: EmailStr = Body(..., embed=True, description="Correo del destinatario"),
    event_title: str = Body(..., embed=True, description="Título del evento"),
    calendar_title: str = Body(..., embed=True, description="Título del calendario"),
    commenter_name: str = Body(..., embed=True, description="Nombre de quien comentó"),
    comment_text: str = Body(..., embed=True, description="Texto del comentario"),
    event_id: str = Body(..., embed=True, description="ID del evento")
):
    """
    Envía un correo notificando sobre un nuevo comentario.
    
    Args:
        to_email: Correo del destinatario (dueño del calendario)
        event_title: Título del evento donde se comentó
        calendar_title: Título del calendario
        commenter_name: Nombre de quien hizo el comentario
        comment_text: Contenido del comentario
        event_id: ID del evento para el enlace
        
    Returns:
        EmailResponse: Resultado del envío
    """
    subject = f"💬 Nuevo comentario en '{event_title}' - Basmati"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Nuevo comentario en tu evento</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #FFFAEB; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto;">
            <div style="background: #EBBE4D; padding: 20px; border: 3px solid #1A1A1A; margin-bottom: 20px;">
                <h1 style="margin: 0; color: #1A1A1A; font-size: 24px;">🍚 Basmati Calendar</h1>
            </div>
            
            <div style="background: white; padding: 20px; border: 3px solid #1A1A1A; margin-bottom: 20px;">
                <h2 style="color: #1A1A1A; margin-top: 0;">💬 Nuevo comentario</h2>
                
                <p style="color: #666;">
                    <strong>{commenter_name}</strong> ha comentado en el evento 
                    <strong>"{event_title}"</strong> del calendario <strong>"{calendar_title}"</strong>:
                </p>
                
                <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #EBBE4D; margin: 15px 0;">
                    <p style="margin: 0; font-style: italic; color: #333;">"{comment_text}"</p>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:5173/event/{event_id}" 
                       style="display: inline-block; background: #EBBE4D; color: #1A1A1A; 
                              padding: 12px 24px; text-decoration: none; font-weight: bold;
                              border: 3px solid #1A1A1A; box-shadow: 4px 4px 0px #1A1A1A;">
                        Ver evento y responder
                    </a>
                </div>
            </div>
            
            <p style="text-align: center; color: #999; font-size: 12px;">
                Este correo fue enviado automáticamente por Basmati Calendar.
                <br>Puedes desactivar las notificaciones por correo en tu perfil.
            </p>
        </div>
    </body>
    </html>
    """
    
    success, message, message_id = await send_email_via_sendgrid(
        to_email=to_email,
        subject=subject,
        content=html_content,
        content_type="text/html"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return EmailResponse(
        success=success,
        message=message,
        message_id=message_id
    )
