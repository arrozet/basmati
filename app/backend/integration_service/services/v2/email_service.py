"""Servicio de envío de correos electrónicos usando SendGrid.

Nuevo en V2: Este módulo implementa la lógica de negocio para el envío 
de correos usando la API de SendGrid desde la cuenta amcgil@uma.es.
"""
import httpx
import os
from schemas.email import (
    EmailRequest,
    EmailResponse,
    BulkEmailRequest,
    CommentNotificationRequest
)


class EmailServiceV2:
    """
    Servicio para envío de correos electrónicos usando SendGrid.
    
    Proporciona funcionalidades de:
    - Envío de correos simples (texto o HTML)
    - Envío de resúmenes diarios con notificaciones
    - Envío de notificaciones de comentarios
    
    Si no hay API key de SendGrid configurada, simula el envío
    para entornos de desarrollo.
    """
    
    # Configuración de SendGrid
    SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
    SENDER_EMAIL = "amcgil@uma.es"
    SENDER_NAME = "Basmati Calendar"
    
    def __init__(self, api_key: str | None = None):
        """
        Inicializa el servicio de email.
        
        Args:
            api_key: API Key de SendGrid. Si no se proporciona,
                     se intenta obtener de la variable de entorno SENDGRID_API_KEY.
        """
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
    
    async def send_email(self, request: EmailRequest) -> EmailResponse:
        """
        Envía un correo electrónico usando SendGrid.
        
        Args:
            request: Datos del correo (destinatario, asunto, contenido)
            
        Returns:
            EmailResponse: Resultado del envío con mensaje de estado
        """
        success, message, message_id = await self._send_via_sendgrid(
            to_email=request.to_email,
            subject=request.subject,
            content=request.content,
            content_type=request.content_type
        )
        
        return EmailResponse(
            success=success,
            message=message,
            message_id=message_id
        )
    
    async def send_daily_digest(self, request: BulkEmailRequest) -> EmailResponse:
        """
        Envía un correo con el resumen diario de notificaciones.
        
        Formatea las notificaciones en un correo HTML con estilo Basmati.
        
        Args:
            request: Datos del resumen (destinatario, lista de notificaciones)
            
        Returns:
            EmailResponse: Resultado del envío
        """
        html_content = self._build_digest_html(request)
        
        success, message, message_id = await self._send_via_sendgrid(
            to_email=request.to_email,
            subject=request.subject,
            content=html_content,
            content_type="text/html"
        )
        
        return EmailResponse(
            success=success,
            message=message,
            message_id=message_id
        )
    
    async def send_comment_notification(
        self, 
        request: CommentNotificationRequest
    ) -> EmailResponse:
        """
        Envía un correo notificando sobre un nuevo comentario.
        
        Formatea el correo con estilo Basmati para notificaciones de comentarios.
        
        Args:
            request: Datos de la notificación (destinatario, evento, comentario)
            
        Returns:
            EmailResponse: Resultado del envío
        """
        subject = f"💬 Nuevo comentario en '{request.event_title}' - Basmati"
        html_content = self._build_comment_notification_html(request)
        
        success, message, message_id = await self._send_via_sendgrid(
            to_email=request.to_email,
            subject=subject,
            content=html_content,
            content_type="text/html"
        )
        
        return EmailResponse(
            success=success,
            message=message,
            message_id=message_id
        )
    
    async def _send_via_sendgrid(
        self,
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
        if not self.api_key:
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
                "email": self.SENDER_EMAIL,
                "name": self.SENDER_NAME
            },
            "content": [
                {
                    "type": content_type,
                    "value": content
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.SENDGRID_API_URL,
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
    
    def _build_digest_html(self, request: BulkEmailRequest) -> str:
        """
        Construye el HTML para el correo de resumen diario.
        
        Args:
            request: Datos del resumen con las notificaciones
            
        Returns:
            str: Contenido HTML del correo
        """
        notifications_html = ""
        for notif in request.notifications:
            notifications_html += f"""
        <div style="border: 2px solid #1A1A1A; padding: 15px; margin-bottom: 10px; background: white;">
            <h3 style="margin: 0 0 10px 0; color: #1A1A1A;">{notif.get('title', 'Notificación')}</h3>
            <p style="margin: 0; color: #666;">{notif.get('message', '')}</p>
            <small style="color: #999;">{notif.get('created_at', '')}</small>
        </div>
            """
        
        return f"""
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
    
    def _build_comment_notification_html(
        self, 
        request: CommentNotificationRequest
    ) -> str:
        """
        Construye el HTML para la notificación de comentario.
        
        Args:
            request: Datos de la notificación de comentario
            
        Returns:
            str: Contenido HTML del correo
        """
        return f"""
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
                    <strong>{request.commenter_name}</strong> ha comentado en el evento 
                    <strong>"{request.event_title}"</strong> del calendario <strong>"{request.calendar_title}"</strong>:
                </p>
                
                <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #EBBE4D; margin: 15px 0;">
                    <p style="margin: 0; font-style: italic; color: #333;">"{request.comment_text}"</p>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:5173/event/{request.event_id}" 
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

