"""Servicio de eventos V2.

Extiende EventService añadiendo funcionalidades específicas de V2.
Implementa la interfaz IEventService del patrón Abstract Factory.

Mejoras V2:
- Filtrado por calendar_id en búsqueda por fechas
- Notificaciones inteligentes según preferencias del usuario
- Soporte para frecuencia instantánea y diaria
- Envío de correos electrónicos vía integration_service
"""
from datetime import datetime, timezone

import httpx
from bson import ObjectId

from core.config import settings
from core.interface import IEventRepository
from schemas.event import (
    EventResponse,
    CommentCreate,
    EventComment,
)
from services.event_service import EventService


class EventServiceV2(EventService):
    """Lógica de negocio para eventos (V2).
    
    Mejoras respecto a V1:
    - Filtrado por calendar_id en búsqueda por fechas
    - Compatibilidad con datos legacy (ObjectId + String)
    - Endpoint getAll para obtener todos los eventos
    - Notificaciones según preferencias del usuario (in_app, email, frequency)
    """

    def __init__(self, event_repository: IEventRepository):
        """Inicializa el servicio V2.
        
        Args:
            event_repository: Repositorio V2 (implementa IEventRepository)
        """
        super().__init__(event_repository)
        self.user_service_url = settings.user_service_url
        self.integration_service_url = settings.integration_service_url

    async def get_all_events(self, limit: int = 200) -> list[EventResponse]:
        """Obtiene todos los eventos del sistema.
        
        Args:
            limit: Número máximo de eventos a devolver
            
        Returns:
            list[EventResponse]: Lista de todos los eventos
        """
        events = await self.event_repository.find_all(limit)
        return [self._document_to_response(event) for event in events]

    async def search_by_date_range(
        self, 
        start: datetime, 
        end: datetime, 
        calendar_id: str | None = None
    ) -> list[EventResponse]:
        """Busca eventos dentro de un rango de fechas (parametrized query 2).
        
        V2 permite filtrar opcionalmente por calendar_id.
        """
        if end <= start:
            raise ValueError("El rango de fechas es inválido: 'end' debe ser posterior a 'start'")
        events = await self.event_repository.find_by_date_range(start, end, calendar_id)
        return [self._document_to_response(event) for event in events]

    async def delete_events_by_calendar(self, calendar_id: str) -> int:
        """Elimina todos los eventos de un calendario.
        
        Este método es utilizado por calendar_service para eliminar
        recursivamente los eventos de un calendario y sus subcalendarios.
        
        Args:
            calendar_id: ID del calendario cuyos eventos se eliminarán
            
        Returns:
            int: Número de eventos eliminados
        """
        return await self.event_repository.delete_by_calendar_id(calendar_id)

    async def add_comment(self, event_id: str, comment_data: CommentCreate) -> EventComment | None:
        """Agrega un comentario a un evento y dispara notificación según preferencias.
        
        V2: Verifica las preferencias del usuario creador del evento:
        - Si tiene in_app activado, envía notificación a notification_service
        - Si tiene email activado y frecuencia 'instant', envía correo inmediatamente
        - Si tiene email activado y frecuencia 'daily', la notificación queda pendiente
        
        Args:
            event_id: ID del evento
            comment_data: Datos del comentario
            
        Returns:
            EventComment: Comentario creado o None si no se encontró el evento
        """
        comment_doc = {
            "_id": ObjectId(),
            "author_external_id": comment_data.author_external_id,
            "author_display_name": comment_data.author_display_name,
            "text": comment_data.text,
            "created_at": datetime.now(timezone.utc),
        }

        try:
            updated_event = await self.event_repository.add_comment(event_id, comment_doc)
        except ValueError as exc:
            raise ValueError(f"Error al agregar comentario: {str(exc)}")

        if not updated_event:
            return None

        # Notificar según preferencias del usuario (V2)
        await self._notify_new_comment_v2(updated_event, comment_doc)

        return self._serialize_comment(comment_doc)

    async def _notify_new_comment_v2(self, event_doc: dict, comment_doc: dict) -> None:
        """Envía notificación al creador del evento según sus preferencias.
        
        V2: Verifica las preferencias del usuario antes de enviar notificaciones.
        
        Args:
            event_doc: Documento del evento
            comment_doc: Documento del comentario
        """
        creator_id = event_doc.get("creator_external_id")
        author_id = comment_doc.get("author_external_id")

        # No notificar si el creador comenta en su propio evento
        if not creator_id or creator_id == author_id:
            return

        # Obtener el nombre real del calendario desde calendar_service
        calendar_title = "Calendario"
        calendar_id = event_doc.get("calendar_id")
        if calendar_id:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    cal_response = await client.get(
                        f"{settings.calendar_service_url}/v1/calendars/{str(calendar_id)}"
                    )
                    if cal_response.status_code == 200:
                        cal_data = cal_response.json()
                        calendar_title = cal_data.get("title", "Calendario")
            except Exception as exc:
                print(f"Error obteniendo nombre del calendario: {str(exc)}")

        # Obtener preferencias del usuario creador del evento
        user_prefs = await self._get_user_preferences(creator_id)
        
        if user_prefs is None:
            # Si no se pueden obtener las preferencias, usar comportamiento V1
            await self._notify_new_comment(event_doc, comment_doc)
            return
        
        in_app_enabled = user_prefs.get("in_app", True)
        email_enabled = user_prefs.get("email", True)
        frequency = user_prefs.get("frequency", "instant")
        user_email = user_prefs.get("email_address") or user_prefs.get("user_email")
        
        notification_payload = {
            "recipient_external_id": creator_id,
            "type": "NEW_COMMENT",
            "title": f"Nuevo comentario en '{event_doc.get('title', 'evento')}'",
            "message": (
                f"{comment_doc.get('author_display_name', 'Un usuario')} comentó: "
                f"{comment_doc.get('text', '')}"
            ),
            "related_event_id": str(event_doc.get("_id")),
            "related_calendar_id": str(event_doc.get("calendar_id")),
        }
        
        # Enviar notificación in_app si está activada
        if in_app_enabled:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"{self.notification_service_url}/v1/notifications",
                        json=notification_payload,
                    )
            except Exception as exc:
                print(f"Error enviando notificación in_app: {str(exc)}")
        
        # Enviar correo si está activado y la frecuencia es instantánea
        if email_enabled and frequency == "instant" and user_email:
            await self._send_comment_email(
                to_email=user_email,
                event_title=event_doc.get("title", "Evento"),
                calendar_title=calendar_title,
                commenter_name=comment_doc.get("author_display_name", "Un usuario"),
                comment_text=comment_doc.get("text", ""),
                event_id=str(event_doc.get("_id"))
            )
        
        # Si la frecuencia es 'daily', las notificaciones se acumulan y se envían
        # mediante un proceso scheduler separado

    async def _get_user_preferences(self, external_id: str) -> dict | None:
        """Obtiene las preferencias de notificación de un usuario.
        
        Args:
            external_id: ID externo del usuario
            
        Returns:
            dict: Preferencias de notificación o None si hay error
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Primero buscar el usuario por external_id
                response = await client.get(
                    f"{self.user_service_url}/v1/users/search/by-oauth",
                    params={"external_id": external_id, "provider": "google"}
                )
                
                if response.status_code == 404:
                    # Intentar con provider facebook
                    response = await client.get(
                        f"{self.user_service_url}/v1/users/search/by-oauth",
                        params={"external_id": external_id, "provider": "facebook"}
                    )
                
                if response.status_code != 200:
                    # Si no se encuentra por OAuth, intentar obtener por ID directamente
                    # (para usuarios de desarrollo como user_dev_1)
                    try:
                        # Intentar buscar todos los usuarios y filtrar por external_id
                        search_response = await client.get(
                            f"{self.user_service_url}/v1/users/search/by-display-name",
                            params={"display_name": ""}
                        )
                        if search_response.status_code == 200:
                            users = search_response.json()
                            for user in users:
                                if user.get("external_id") == external_id:
                                    prefs = user.get("notification_preferences", {})
                                    prefs["user_email"] = user.get("email")
                                    return prefs
                    except Exception:
                        pass
                    return None
                
                user_data = response.json()
                prefs = user_data.get("notification_preferences", {})
                prefs["user_email"] = user_data.get("email")
                return prefs
                
        except Exception as exc:
            print(f"Error obteniendo preferencias de usuario: {str(exc)}")
            return None

    async def _send_comment_email(
        self,
        to_email: str,
        event_title: str,
        calendar_title: str,
        commenter_name: str,
        comment_text: str,
        event_id: str
    ) -> None:
        """Envía un correo electrónico notificando sobre un nuevo comentario.
        
        Args:
            to_email: Correo del destinatario
            event_title: Título del evento
            calendar_title: Título del calendario
            commenter_name: Nombre de quien comentó
            comment_text: Texto del comentario
            event_id: ID del evento
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.post(
                    f"{self.integration_service_url}/v2/email/send-comment-notification",
                    json={
                        "to_email": to_email,
                        "event_title": event_title,
                        "calendar_title": calendar_title,
                        "commenter_name": commenter_name,
                        "comment_text": comment_text,
                        "event_id": event_id
                    }
                )
        except Exception as exc:
            # No interrumpir el flujo principal si falla el envío de email
            print(f"Error enviando correo de comentario: {str(exc)}")
