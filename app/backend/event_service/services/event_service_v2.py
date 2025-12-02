"""Servicio de eventos V2"""
from datetime import datetime
from typing import Any

from models.event import EventModel
from repositories.event_repository_v2 import EventRepositoryV2
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
from services.event_service import EventService

class EventServiceV2(EventService):
    """Lógica de negocio para eventos (V2)"""

    def __init__(self, event_repository: EventRepositoryV2):
        super().__init__(event_repository)
        self.event_repository = event_repository

    async def search_by_date_range(self, start: datetime, end: datetime, calendar_id: str | None = None) -> list[EventResponse]:
        """Busca eventos dentro de un rango de fechas (parametrized query 2)."""
        if end <= start:
            raise ValueError("El rango de fechas es inválido: 'end' debe ser posterior a 'start'")
        events = await self.event_repository.find_by_date_range(start, end, calendar_id)
        return [self._document_to_response(event) for event in events]
