"""Servicio de resumen diario de notificaciones V2.

Este módulo implementa la lógica de negocio para:
- Recopilar notificaciones pendientes de usuarios con frecuencia "daily"
- Generar y enviar un email de resumen diario
- Marcar las notificaciones como procesadas
"""
import httpx
import logging
from datetime import datetime, timedelta

from core.config import settings
from schemas.daily_digest import (
    BulkDigestResponse,
    DigestSendResponse,
    DigestPreviewResponse
)

logger = logging.getLogger(__name__)


class DailyDigestServiceV2:
    """
    Servicio para gestión del resumen diario de notificaciones.
    
    Proporciona funcionalidades de:
    - Envío masivo de digests a usuarios con frecuencia diaria
    - Envío individual de digest a un usuario específico
    - Vista previa del contenido del digest
    
    Requiere acceso a user_service y notification_service.
    """
    
    def __init__(
        self,
        user_service_url: str | None = None,
        notification_service_url: str | None = None,
        sendgrid_api_key: str | None = None,
        sender_email: str | None = None,
        frontend_url: str | None = None
    ):
        """
        Inicializa el servicio de daily digest.
        
        Args:
            user_service_url: URL del servicio de usuarios
            notification_service_url: URL del servicio de notificaciones
            sendgrid_api_key: API Key de SendGrid
            sender_email: Email del remitente
            frontend_url: URL del frontend para enlaces
        """
        self.user_service_url = user_service_url or settings.user_service_url
        self.notification_service_url = notification_service_url or settings.notification_service_url
        self.sendgrid_api_key = sendgrid_api_key or settings.sendgrid_api_key
        self.sender_email = sender_email or settings.sender_email
        self.frontend_url = frontend_url or settings.frontend_url
    
    async def send_all_daily_digests(self) -> BulkDigestResponse:
        """
        Envía el resumen diario a todos los usuarios con frecuencia 'daily'.
        
        Este método debe ser llamado por un cron job a las 00:00.
        
        Returns:
            BulkDigestResponse: Resultado del envío masivo
        """
        logger.info("Iniciando envío masivo de digests diarios")
        
        # Obtener usuarios con frecuencia diaria
        daily_users = await self._get_daily_users()
        
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
            notifications = await self._get_pending_notifications(user_id, since)
            
            if not notifications:
                logger.info(f"Usuario {user_id}: sin notificaciones pendientes")
                continue
            
            # Generar y enviar email
            html_content = self._generate_digest_html(user_name, notifications)
            success = await self._send_digest_email(user_email, user_name, html_content)
            
            if success:
                emails_sent += 1
                # Marcar notificaciones como procesadas
                notification_ids = [n.get("id") for n in notifications if n.get("id")]
                await self._mark_notifications_as_digested(notification_ids)
            else:
                errors.append(f"Usuario {user_id}: error enviando email")
        
        logger.info(f"Digest completado: {emails_sent}/{len(daily_users)} emails enviados")
        
        return BulkDigestResponse(
            total_users=len(daily_users),
            emails_sent=emails_sent,
            errors=errors
        )
    
    async def send_user_digest(self, user_external_id: str) -> DigestSendResponse:
        """
        Envía el resumen diario a un usuario específico.
        
        Útil para pruebas o envíos manuales.
        
        Args:
            user_external_id: ID externo del usuario
            
        Returns:
            DigestSendResponse: Resultado del envío
            
        Raises:
            ValueError: Si el usuario no existe o no tiene email
        """
        # Obtener información del usuario
        user = await self._get_user_info(user_external_id)
        
        if not user:
            raise ValueError("Usuario no encontrado")
        
        user_email = user.get("notification_preferences", {}).get("email_address") or user.get("email")
        user_name = user.get("display_name", "Usuario")
        
        if not user_email:
            raise ValueError("Usuario sin email configurado")
        
        # Obtener notificaciones de las últimas 24 horas
        since = datetime.utcnow() - timedelta(hours=24)
        notifications = await self._get_pending_notifications(user_external_id, since)
        
        if not notifications:
            return DigestSendResponse(
                success=True,
                message="No hay notificaciones pendientes para enviar",
                notifications_count=0
            )
        
        # Generar y enviar email
        html_content = self._generate_digest_html(user_name, notifications)
        success = await self._send_digest_email(user_email, user_name, html_content)
        
        if success:
            # Marcar notificaciones como procesadas
            notification_ids = [n.get("id") for n in notifications if n.get("id")]
            await self._mark_notifications_as_digested(notification_ids)
            
            return DigestSendResponse(
                success=True,
                message="Digest enviado exitosamente",
                email=user_email,
                notifications_count=len(notifications)
            )
        else:
            raise ValueError("Error enviando el email de digest")
    
    async def preview_digest(self, user_external_id: str) -> DigestPreviewResponse:
        """
        Genera una vista previa del digest sin enviarlo.
        
        Útil para desarrollo y pruebas.
        
        Args:
            user_external_id: ID externo del usuario
            
        Returns:
            DigestPreviewResponse: Vista previa del digest
        """
        # Obtener información del usuario
        user = await self._get_user_info(user_external_id)
        
        if not user:
            # Para desarrollo, usar datos mock
            user = {
                "external_id": user_external_id,
                "display_name": "Usuario Prueba",
                "email": "test@example.com"
            }
        
        # Obtener notificaciones de las últimas 24 horas
        since = datetime.utcnow() - timedelta(hours=24)
        notifications = await self._get_pending_notifications(user_external_id, since)
        
        # Si no hay notificaciones, usar datos de ejemplo
        if not notifications:
            notifications = self._get_mock_notifications()
        
        user_name = user.get("display_name", "Usuario")
        html_content = self._generate_digest_html(user_name, notifications)
        
        return DigestPreviewResponse(
            user_id=user_external_id,
            user_name=user_name,
            notifications_count=len(notifications),
            html_preview=html_content
        )
    
    async def _get_daily_users(self) -> list[dict]:
        """
        Obtiene todos los usuarios con frecuencia 'daily' y email activado.
        
        Returns:
            list[dict]: Lista de usuarios con frecuencia diaria
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.user_service_url}/api/v2/users",
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
    
    async def _get_user_info(self, user_external_id: str) -> dict | None:
        """
        Obtiene información de un usuario específico.
        
        Args:
            user_external_id: ID externo del usuario
            
        Returns:
            dict: Información del usuario o None si no existe
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.user_service_url}/api/v2/users/{user_external_id}",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                logger.error(f"Error obteniendo usuario: {e}")
                return None
    
    async def _get_pending_notifications(
        self, 
        user_id: str, 
        since: datetime
    ) -> list[dict]:
        """
        Obtiene notificaciones pendientes de un usuario desde una fecha específica.
        
        Args:
            user_id: ID del usuario
            since: Fecha desde la que buscar
            
        Returns:
            list[dict]: Lista de notificaciones pendientes
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.notification_service_url}/api/v2/notifications",
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
    
    async def _mark_notifications_as_digested(self, notification_ids: list[str]) -> bool:
        """
        Marca notificaciones como incluidas en el digest.
        
        Args:
            notification_ids: IDs de las notificaciones a marcar
            
        Returns:
            bool: True si se marcaron correctamente
        """
        if not notification_ids:
            return True
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{self.notification_service_url}/api/v2/notifications/mark-digested",
                    json={"notification_ids": notification_ids},
                    timeout=30.0
                )
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Error marcando notificaciones: {e}")
                return False
    
    async def _send_digest_email(
        self, 
        email: str, 
        user_name: str, 
        html_content: str
    ) -> bool:
        """
        Envía el email de resumen usando SendGrid.
        
        Args:
            email: Email del destinatario
            user_name: Nombre del usuario
            html_content: Contenido HTML del email
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.sendgrid_api_key:
            # Mock para desarrollo
            logger.info(f"[MOCK DIGEST] Enviando digest a {email}")
            return True
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.sendgrid_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [{
                            "to": [{"email": email, "name": user_name}]
                        }],
                        "from": {
                            "email": self.sender_email,
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
    
    def _generate_digest_html(self, user_name: str, notifications: list[dict]) -> str:
        """
        Genera el HTML del email de resumen diario.
        
        Args:
            user_name: Nombre del usuario
            notifications: Lista de notificaciones
            
        Returns:
            str: Contenido HTML del email
        """
        today = datetime.now().strftime("%d/%m/%Y")
        
        # Agrupar notificaciones por calendario
        by_calendar: dict[str, list[dict]] = {}
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
        
        return f"""
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
                <a href="{self.frontend_url}/notifications" 
                   style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 500;">
                    Ver todas las notificaciones
                </a>
            </div>
            
            <p style="margin-top: 32px; font-size: 12px; color: #999; text-align: center;">
                Recibes este email porque tienes activada la frecuencia "Resumen Diario" en tus preferencias.
                <br>
                Puedes cambiar esto en <a href="{self.frontend_url}/settings" style="color: #2563eb;">ajustes de tu perfil</a>.
            </p>
        </div>
    </body>
    </html>
        """
    
    def _get_mock_notifications(self) -> list[dict]:
        """
        Genera notificaciones de ejemplo para desarrollo.
        
        Returns:
            list[dict]: Lista de notificaciones mock
        """
        return [
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

