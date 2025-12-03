"""
Servicio de Resumen Diario de Notificaciones V2

Este módulo proporciona funcionalidad para:
- Recopilar notificaciones pendientes de usuarios con frecuencia "daily"
- Generar y enviar un email de resumen diario a las 00:00
- Marcar las notificaciones como procesadas

Requiere:
- SendGrid API Key configurada
- Acceso a notification_service y user_service
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import httpx
from datetime import datetime, timedelta
import logging

from core.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = Settings()

# ============================================================================
# Schemas
# ============================================================================

class DailyDigestUserInfo(BaseModel):
    """Información de usuario para el digest"""
    external_id: str
    email: str
    display_name: str


class NotificationSummary(BaseModel):
    """Resumen de una notificación para el digest"""
    title: str
    message: str
    calendar_title: Optional[str] = None
    event_title: Optional[str] = None
    created_at: datetime


class DigestRequest(BaseModel):
    """Solicitud para enviar un digest específico"""
    user_external_id: str


class BulkDigestResponse(BaseModel):
    """Respuesta del envío masivo de digests"""
    total_users: int
    emails_sent: int
    errors: List[str]


# ============================================================================
# Funciones auxiliares
# ============================================================================

async def get_daily_users() -> List[dict]:
    """
    Obtiene todos los usuarios con frecuencia 'daily' y email activado.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Obtener usuarios con preferencia de frecuencia diaria
            response = await client.get(
                f"{settings.user_service_url}/api/v2/users",
                params={
                    "notification_frequency": "daily",
                    "email_notifications": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json().get("users", [])
            else:
                logger.warning(f"Error obteniendo usuarios daily: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error conectando con user_service: {e}")
            return []


async def get_pending_notifications(user_id: str, since: datetime) -> List[dict]:
    """
    Obtiene notificaciones pendientes de un usuario desde una fecha específica.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.notification_service_url}/api/v2/notifications",
                params={
                    "user_id": user_id,
                    "read": False,
                    "since": since.isoformat(),
                    "digest_pending": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json().get("notifications", [])
            return []
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {e}")
            return []


async def mark_notifications_as_digested(notification_ids: List[str]) -> bool:
    """
    Marca notificaciones como incluidas en el digest.
    """
    if not notification_ids:
        return True
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{settings.notification_service_url}/api/v2/notifications/mark-digested",
                json={"notification_ids": notification_ids},
                timeout=30.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error marcando notificaciones: {e}")
            return False


def generate_digest_html(user_name: str, notifications: List[dict]) -> str:
    """
    Genera el HTML del email de resumen diario.
    """
    today = datetime.now().strftime("%d/%m/%Y")
    
    # Agrupar notificaciones por calendario
    by_calendar = {}
    for notif in notifications:
        calendar = notif.get("related_calendar_title", "General")
        if calendar not in by_calendar:
            by_calendar[calendar] = []
        by_calendar[calendar].append(notif)
    
    # Generar secciones HTML
    sections_html = ""
    for calendar, notifs in by_calendar.items():
        notif_items = ""
        for n in notifs:
            event_info = f" en <em>{n.get('related_event_title', '')}</em>" if n.get('related_event_title') else ""
            notif_items += f"""
                <li style="margin-bottom: 12px; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                    <strong>{n.get('title', 'Notificación')}</strong>{event_info}
                    <p style="margin: 5px 0 0 0; color: #555;">{n.get('message', '')}</p>
                </li>
            """
        
        sections_html += f"""
            <div style="margin-bottom: 24px;">
                <h3 style="color: #2563eb; font-size: 16px; margin-bottom: 12px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">
                    📅 {calendar}
                </h3>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    {notif_items}
                </ul>
            </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">🍚 Basmati</h1>
            <p style="margin: 8px 0 0 0; opacity: 0.9;">Resumen Diario de Notificaciones</p>
        </div>
        
        <div style="background: white; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
            <p style="margin-top: 0;">¡Hola <strong>{user_name}</strong>! 👋</p>
            <p>Aquí tienes tu resumen de actividad del <strong>{today}</strong>:</p>
            
            <div style="margin-top: 24px;">
                {sections_html}
            </div>
            
            <div style="margin-top: 32px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
                <a href="{settings.frontend_url}/notifications" 
                   style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 500;">
                    Ver todas las notificaciones
                </a>
            </div>
            
            <p style="margin-top: 32px; font-size: 12px; color: #999; text-align: center;">
                Recibes este email porque tienes activada la frecuencia "Resumen Diario" en tus preferencias.
                <br>
                Puedes cambiar esto en <a href="{settings.frontend_url}/settings" style="color: #2563eb;">ajustes de tu perfil</a>.
            </p>
        </div>
    </body>
    </html>
    """
    
    return html


async def send_digest_email(email: str, user_name: str, html_content: str) -> bool:
    """
    Envía el email de resumen usando SendGrid.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {settings.sendgrid_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{
                        "to": [{"email": email, "name": user_name}]
                    }],
                    "from": {
                        "email": settings.sender_email,
                        "name": "Basmati - Resumen Diario"
                    },
                    "subject": f"📊 Tu resumen diario de Basmati - {datetime.now().strftime('%d/%m/%Y')}",
                    "content": [
                        {
                            "type": "text/html",
                            "value": html_content
                        }
                    ]
                },
                timeout=30.0
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Digest enviado exitosamente a {email}")
                return True
            else:
                logger.error(f"Error enviando digest: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error en send_digest_email: {e}")
            return False


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/digest/send-all", response_model=BulkDigestResponse)
async def send_all_daily_digests():
    """
    Envía el resumen diario a todos los usuarios con frecuencia 'daily'.
    
    Este endpoint debe ser llamado por un cron job a las 00:00.
    """
    logger.info("Iniciando envío masivo de digests diarios")
    
    # Obtener usuarios con frecuencia diaria
    daily_users = await get_daily_users()
    
    if not daily_users:
        return BulkDigestResponse(
            total_users=0,
            emails_sent=0,
            errors=[]
        )
    
    emails_sent = 0
    errors = []
    
    # Fecha desde la que buscar notificaciones (últimas 24 horas)
    since = datetime.utcnow() - timedelta(hours=24)
    
    for user in daily_users:
        user_id = user.get("external_id")
        user_email = user.get("notification_preferences", {}).get("email_address") or user.get("email")
        user_name = user.get("display_name", "Usuario")
        
        if not user_email:
            errors.append(f"Usuario {user_id}: sin email configurado")
            continue
        
        # Obtener notificaciones pendientes
        notifications = await get_pending_notifications(user_id, since)
        
        if not notifications:
            logger.info(f"Usuario {user_id}: sin notificaciones pendientes")
            continue
        
        # Generar y enviar email
        html_content = generate_digest_html(user_name, notifications)
        success = await send_digest_email(user_email, user_name, html_content)
        
        if success:
            emails_sent += 1
            # Marcar notificaciones como procesadas
            notification_ids = [n.get("id") for n in notifications if n.get("id")]
            await mark_notifications_as_digested(notification_ids)
        else:
            errors.append(f"Usuario {user_id}: error enviando email")
    
    logger.info(f"Digest completado: {emails_sent}/{len(daily_users)} emails enviados")
    
    return BulkDigestResponse(
        total_users=len(daily_users),
        emails_sent=emails_sent,
        errors=errors
    )


@router.post("/digest/send-user")
async def send_user_digest(request: DigestRequest):
    """
    Envía el resumen diario a un usuario específico.
    
    Útil para pruebas o envíos manuales.
    """
    user_id = request.user_external_id
    
    # Obtener información del usuario
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.user_service_url}/api/v2/users/{user_id}",
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            user = response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error conectando con user_service: {e}")
    
    user_email = user.get("notification_preferences", {}).get("email_address") or user.get("email")
    user_name = user.get("display_name", "Usuario")
    
    if not user_email:
        raise HTTPException(status_code=400, detail="Usuario sin email configurado")
    
    # Obtener notificaciones de las últimas 24 horas
    since = datetime.utcnow() - timedelta(hours=24)
    notifications = await get_pending_notifications(user_id, since)
    
    if not notifications:
        return {
            "success": True,
            "message": "No hay notificaciones pendientes para enviar",
            "notifications_count": 0
        }
    
    # Generar y enviar email
    html_content = generate_digest_html(user_name, notifications)
    success = await send_digest_email(user_email, user_name, html_content)
    
    if success:
        # Marcar notificaciones como procesadas
        notification_ids = [n.get("id") for n in notifications if n.get("id")]
        await mark_notifications_as_digested(notification_ids)
        
        return {
            "success": True,
            "message": "Digest enviado exitosamente",
            "email": user_email,
            "notifications_count": len(notifications)
        }
    else:
        raise HTTPException(status_code=500, detail="Error enviando el email de digest")


@router.get("/digest/preview/{user_external_id}")
async def preview_digest(user_external_id: str):
    """
    Genera una vista previa del digest sin enviarlo.
    
    Útil para desarrollo y pruebas.
    """
    # Obtener información del usuario
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.user_service_url}/api/v2/users/{user_external_id}",
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            user = response.json()
        except httpx.RequestError:
            # Para desarrollo, usar datos mock
            user = {
                "external_id": user_external_id,
                "display_name": "Usuario Prueba",
                "email": "test@example.com"
            }
    
    # Obtener notificaciones de las últimas 24 horas
    since = datetime.utcnow() - timedelta(hours=24)
    notifications = await get_pending_notifications(user_external_id, since)
    
    # Si no hay notificaciones, usar datos de ejemplo
    if not notifications:
        notifications = [
            {
                "id": "preview_1",
                "title": "Nuevo comentario",
                "message": "Juan ha comentado en tu evento 'Reunión de equipo'",
                "related_calendar_title": "Trabajo",
                "related_event_title": "Reunión de equipo",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "preview_2",
                "title": "Nuevo comentario",
                "message": "María ha respondido a tu comentario",
                "related_calendar_title": "Trabajo",
                "related_event_title": "Presentación proyecto",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "preview_3",
                "title": "Calendario actualizado",
                "message": "Se ha añadido un nuevo evento a 'Universidad'",
                "related_calendar_title": "Universidad",
                "related_event_title": None,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    user_name = user.get("display_name", "Usuario")
    html_content = generate_digest_html(user_name, notifications)
    
    return {
        "user_id": user_external_id,
        "user_name": user_name,
        "notifications_count": len(notifications),
        "html_preview": html_content
    }
