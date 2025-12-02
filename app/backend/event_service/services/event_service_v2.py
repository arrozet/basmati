"""Servicio de eventos V2.

Extiende EventService añadiendo funcionalidades específicas de V2.
Implementa la interfaz IEventService del patrón Abstract Factory.
"""
from datetime import datetime

from core.interface import IEventRepository
from schemas.event import EventResponse
from services.event_service import EventService


class EventServiceV2(EventService):
    """Lógica de negocio para eventos (V2).
    
    Mejoras respecto a V1:
    - Filtrado por calendar_id en búsqueda por fechas
    - Compatibilidad con datos legacy (ObjectId + String)
    """

    def __init__(self, event_repository: IEventRepository):
        """Inicializa el servicio V2.
        
        Args:
            event_repository: Repositorio V2 (implementa IEventRepository)
        """
        super().__init__(event_repository)

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
