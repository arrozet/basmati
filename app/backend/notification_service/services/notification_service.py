"""Lógica de negocio para notificaciones"""
from datetime import datetime, timezone
from bson import ObjectId
from schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from repositories.notification_repository import NotificationRepository

class NotificationService:
    """
    Servicio para manejar la lógica de negocio de notificaciones.
    
    Delega acceso a BD al NotificationRepository.
    """
    
    def __init__(self, notification_repository: NotificationRepository):
        """
        Inicializa el servicio de notificaciones.
        
        Args:
            notification_repository: Repository para notificaciones
        """
        self.notification_repository = notification_repository
    
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """
        Crea una nueva notificación.
        
        Lógica:
        - Crea la notificación con fecha de creación automática
        - Puede ser llamada por otros servicios (EventService)
        
        Args:
            notification_data: Datos de la notificación a crear
            
        Returns:
            NotificationResponse: Notificación creada
            
        Raises:
            ValueError: Si hay error al crear la notificación
        """
        # Preparar datos
        notification_dict = notification_data.model_dump()
        notification_dict["created_at"] = datetime.now(timezone.utc)
        notification_dict["is_read"] = False
        
        # Convertir IDs de string a ObjectId si están presentes
        if notification_dict.get("related_event_id"):
            try:
                notification_dict["related_event_id"] = ObjectId(notification_dict["related_event_id"])
            except Exception:
                raise ValueError("related_event_id inválido")
        
        if notification_dict.get("related_calendar_id"):
            try:
                notification_dict["related_calendar_id"] = ObjectId(notification_dict["related_calendar_id"])
            except Exception:
                raise ValueError("related_calendar_id inválido")
        
        # Delegar a repository
        try:
            notification_id = await self.notification_repository.create(notification_dict)
            notification_doc = await self.notification_repository.find_by_id(notification_id)
            if not notification_doc:
                raise ValueError("No se pudo recuperar la notificación creada")
            return self._document_to_response(notification_doc)
        except ValueError as e:
            raise ValueError(f"Error al crear notificación: {str(e)}")
    
    async def get_notification(self, notification_id: str) -> NotificationResponse | None:
        """
        Obtiene una notificación por su ID.
        
        Args:
            notification_id: ID de la notificación
            
        Returns:
            NotificationResponse: Notificación encontrada o None
        """
        notification = await self.notification_repository.find_by_id(notification_id)
        if notification:
            return self._document_to_response(notification)
        return None
    
    async def get_user_notifications(self, recipient_external_id: str) -> list[NotificationResponse]:
        """
        Obtiene todas las notificaciones de un usuario.
        
        Args:
            recipient_external_id: External ID del usuario receptor
            
        Returns:
            list[NotificationResponse]: Lista de notificaciones del usuario
        """
        notifications = await self.notification_repository.find_by_recipient(recipient_external_id)
        return [self._document_to_response(notif) for notif in notifications]
    
    async def mark_as_read(self, notification_id: str) -> NotificationResponse | None:
        """
        Marca una notificación como leída.
        
        Args:
            notification_id: ID de la notificación
            
        Returns:
            NotificationResponse: Notificación actualizada o None si no existe
        """
        success = await self.notification_repository.mark_as_read(notification_id)
        if success:
            notification = await self.notification_repository.find_by_id(notification_id)
            if notification:
                return self._document_to_response(notification)
        return None
    
    async def mark_all_as_read(self, recipient_external_id: str) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas.
        
        Args:
            recipient_external_id: External ID del usuario receptor
            
        Returns:
            int: Número de notificaciones marcadas como leídas
        """
        return await self.notification_repository.mark_all_as_read(recipient_external_id)
    
    async def search_unread(self, recipient_external_id: str) -> list[NotificationResponse]:
        """
        Busca notificaciones no leídas de un usuario (parametrized query 1).
        
        Args:
            recipient_external_id: External ID del usuario receptor
            
        Returns:
            list[NotificationResponse]: Lista de notificaciones no leídas
        """
        notifications = await self.notification_repository.find_unread_by_recipient(recipient_external_id)
        return [self._document_to_response(notif) for notif in notifications]
    
    async def search_by_event(self, event_id: str) -> list[NotificationResponse]:
        """
        Busca notificaciones relacionadas con un evento (parametrized query 2).
        
        Args:
            event_id: ID del evento relacionado
            
        Returns:
            list[NotificationResponse]: Lista de notificaciones del evento
        """
        notifications = await self.notification_repository.find_by_event(event_id)
        return [self._document_to_response(notif) for notif in notifications]
    
    async def search_by_type(self, notification_type: str) -> list[NotificationResponse]:
        """
        Busca notificaciones por tipo.
        
        Args:
            notification_type: Tipo de notificación
            
        Returns:
            list[NotificationResponse]: Lista de notificaciones del tipo especificado
        """
        notifications = await self.notification_repository.find_by_type(notification_type)
        return [self._document_to_response(notif) for notif in notifications]
    
    async def search_by_calendar(self, calendar_id: str) -> list[NotificationResponse]:
        """
        Busca notificaciones relacionadas con un calendario.
        
        Args:
            calendar_id: ID del calendario relacionado
            
        Returns:
            list[NotificationResponse]: Lista de notificaciones del calendario
        """
        notifications = await self.notification_repository.find_by_calendar(calendar_id)
        return [self._document_to_response(notif) for notif in notifications]
    
    async def delete_notification(self, notification_id: str) -> bool:
        """
        Elimina una notificación.
        
        Args:
            notification_id: ID de la notificación
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        return await self.notification_repository.delete(notification_id)
    
    def _document_to_response(self, document: dict) -> NotificationResponse:
        """
        Convierte un documento de MongoDB a NotificationResponse.
        
        Args:
            document: Documento de MongoDB
            
        Returns:
            NotificationResponse: Schema de respuesta
        """
        document["id"] = str(document["_id"])
        
        # Convertir ObjectIds a strings
        if document.get("related_event_id"):
            document["related_event_id"] = str(document["related_event_id"])
        if document.get("related_calendar_id"):
            document["related_calendar_id"] = str(document["related_calendar_id"])
        
        return NotificationResponse(**document)

