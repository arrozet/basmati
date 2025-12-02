"""Interfaces para el dominio de Eventos.

Define los contratos que deben cumplir los repositorios y servicios
de eventos en todas las versiones de la API.

Hereda de las interfaces base definidas en shared/ para garantizar
consistencia entre todos los microservicios.
"""
from abc import abstractmethod
from datetime import datetime

# Importar interfaces base de shared (instalado como paquete)
from shared.interface import IRepository, IService

from schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    CommentCreate,
    AttachmentCreate,
    EventComment,
    EventAttachment,
    EventCommentAuthor,
)


# ============================================================================
# INTERFAZ DE REPOSITORIO DE EVENTOS
# ============================================================================

class IEventRepository(IRepository[dict, str]):
    """Interfaz abstracta para el repositorio de eventos.
    
    Hereda de IRepository[dict, str] donde:
    - dict: tipo de entidad (documentos de MongoDB)
    - str: tipo de identificador (ObjectId como string)
    
    Define el contrato que deben cumplir todas las versiones
    del repositorio de eventos.
    """
    
    @abstractmethod
    async def create(self, event_dict: dict) -> str:
        """Crea un nuevo evento."""
        pass
    
    @abstractmethod
    async def find_by_id(self, event_id: str) -> dict | None:
        """Obtiene un evento por su ID."""
        pass
    
    @abstractmethod
    async def update(self, event_id: str, update_dict: dict) -> dict | None:
        """Actualiza un evento existente."""
        pass
    
    @abstractmethod
    async def delete(self, event_id: str) -> bool:
        """Elimina un evento."""
        pass
    
    @abstractmethod
    async def add_comment(self, event_id: str, comment_dict: dict) -> dict | None:
        """Agrega un comentario a un evento."""
        pass
    
    @abstractmethod
    async def add_attachment(self, event_id: str, attachment_dict: dict) -> dict | None:
        """Agrega un adjunto a un evento."""
        pass
    
    @abstractmethod
    async def find_by_calendar(self, calendar_id: str) -> list[dict]:
        """Busca eventos por calendario."""
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start: datetime, 
        end: datetime, 
        calendar_id: str | None = None
    ) -> list[dict]:
        """Busca eventos por rango de fechas."""
        pass
    
    @abstractmethod
    async def get_comments(self, event_id: str) -> list[dict]:
        """Obtiene los comentarios de un evento."""
        pass
    
    @abstractmethod
    async def find_commented_events_by_user(self, user_external_id: str) -> list[dict]:
        """Obtiene eventos comentados por un usuario."""
        pass
    
    @abstractmethod
    async def search_by_text(self, query: str) -> list[dict]:
        """Búsqueda full-text en eventos."""
        pass
    
    @abstractmethod
    async def search_by_calendar_title(self, calendar_title: str) -> list[dict]:
        """Busca eventos por título del calendario."""
        pass
    
    @abstractmethod
    async def search_by_location(self, location_query: str) -> list[dict]:
        """Busca eventos por ubicación."""
        pass
    
    @abstractmethod
    async def search_advanced(
        self,
        title: str | None = None,
        calendar_title: str | None = None,
        description: str | None = None
    ) -> list[dict]:
        """Búsqueda avanzada de eventos."""
        pass


# ============================================================================
# INTERFAZ DE SERVICIO DE EVENTOS
# ============================================================================

class IEventService(IService[EventResponse]):
    """Interfaz abstracta para el servicio de eventos.
    
    Hereda de IService[EventResponse] donde EventResponse es el tipo
    principal de respuesta del servicio.
    
    Define el contrato que deben cumplir todas las versiones
    del servicio de eventos.
    """
    
    @abstractmethod
    async def create_event(self, event_data: EventCreate) -> EventResponse:
        """Crea un nuevo evento."""
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> EventResponse | None:
        """Obtiene un evento por su ID."""
        pass
    
    @abstractmethod
    async def update_event(self, event_id: str, event_data: EventUpdate) -> EventResponse | None:
        """Actualiza un evento existente."""
        pass
    
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Elimina un evento."""
        pass
    
    @abstractmethod
    async def add_comment(self, event_id: str, comment_data: CommentCreate) -> EventComment | None:
        """Agrega un comentario a un evento."""
        pass
    
    @abstractmethod
    async def add_attachment(self, event_id: str, attachment_data: AttachmentCreate) -> EventAttachment | None:
        """Agrega un adjunto a un evento."""
        pass
    
    @abstractmethod
    async def search_by_calendar(self, calendar_id: str) -> list[EventResponse]:
        """Busca eventos por calendario."""
        pass
    
    @abstractmethod
    async def search_by_date_range(
        self, 
        start: datetime, 
        end: datetime, 
        calendar_id: str | None = None
    ) -> list[EventResponse]:
        """Busca eventos por rango de fechas."""
        pass
    
    @abstractmethod
    async def get_comment_users(self, event_id: str) -> list[EventCommentAuthor]:
        """Obtiene los usuarios que comentaron en un evento."""
        pass
    
    @abstractmethod
    async def get_commented_events_by_user(self, user_external_id: str) -> list[EventResponse]:
        """Obtiene eventos comentados por un usuario."""
        pass
    
    @abstractmethod
    async def search_by_text(self, query: str) -> list[EventResponse]:
        """Búsqueda full-text en eventos."""
        pass
    
    @abstractmethod
    async def search_by_calendar_title(self, calendar_title: str) -> list[EventResponse]:
        """Busca eventos por título del calendario."""
        pass
    
    @abstractmethod
    async def search_by_location(self, location_query: str) -> list[EventResponse]:
        """Busca eventos por ubicación."""
        pass
    
    @abstractmethod
    async def search_advanced(
        self,
        title: str | None = None,
        calendar_title: str | None = None,
        description: str | None = None
    ) -> list[EventResponse]:
        """Búsqueda avanzada de eventos."""
        pass

