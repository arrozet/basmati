"""
Teamup Parser - Transformación de datos de Teamup.

Implementa IEventParser para convertir respuestas de Teamup API
a objetos de dominio normalizados.
"""

from datetime import datetime
from typing import Any, Optional
import logging

from services.v3.imports.interfaces import (
    IEventParser,
    ExternalCalendarInfo,
    ExternalEvent,
)

logger = logging.getLogger(__name__)


class TeamupEventParser(IEventParser):
    """
    Parser concreto para datos de Teamup.
    
    Transforma las respuestas JSON de Teamup API a objetos de dominio
    normalizados que pueden ser usados por el importador.
    """
    
    PROVIDER_NAME = "Teamup"
    DEFAULT_COLOR = "#FF6B35"  # Naranja de Teamup
    
    def parse_calendar_info(self, raw_data: dict[str, Any]) -> ExternalCalendarInfo:
        """
        Parsea información de calendario desde respuesta de Teamup.
        
        Args:
            raw_data: Respuesta JSON de GET /{calendar_key}/configuration
            
        Returns:
            ExternalCalendarInfo: Información normalizada
        """
        # Teamup devuelve la configuración dentro de un objeto "calendar"
        calendar_data = raw_data.get("calendar", raw_data)
        
        return ExternalCalendarInfo(
            external_id=calendar_data.get("key", ""),
            name=calendar_data.get("name", "Calendario de Teamup"),
            description=calendar_data.get("description"),
            color=calendar_data.get("color", self.DEFAULT_COLOR),
            timezone=calendar_data.get("tz"),
        )
    
    def parse_events(self, raw_data: dict[str, Any]) -> list[ExternalEvent]:
        """
        Parsea lista de eventos desde respuesta de Teamup.
        
        Args:
            raw_data: Respuesta JSON de GET /{calendar_key}/events
            
        Returns:
            list[ExternalEvent]: Lista de eventos normalizados
        """
        events = []
        items = raw_data.get("events", [])
        
        for item in items:
            try:
                event = self._parse_single_event(item)
                if event:
                    events.append(event)
            except Exception as e:
                logger.warning(
                    f"Error parseando evento de Teamup: {e}. "
                    f"Evento: {item.get('id', 'unknown')}"
                )
                continue
        
        logger.info(f"Parseados {len(events)} eventos de {len(items)} items")
        return events
    
    def _parse_single_event(self, item: dict[str, Any]) -> Optional[ExternalEvent]:
        """
        Parsea un evento individual de Teamup.
        
        Teamup tiene estos campos principales:
        - id: ID único del evento
        - title: Título del evento
        - start_dt: Fecha/hora inicio (ISO 8601)
        - end_dt: Fecha/hora fin (ISO 8601)
        - all_day: Boolean indicando si es todo el día
        - notes: Descripción/notas del evento
        - location: Ubicación del evento
        - rrule: Regla de recurrencia (si aplica)
        
        Args:
            item: Objeto evento de Teamup
            
        Returns:
            ExternalEvent o None si no es válido
        """
        # Extraer fechas
        start_str = item.get("start_dt")
        end_str = item.get("end_dt")
        
        if not start_str or not end_str:
            logger.warning(f"Evento sin fechas válidas: {item.get('id')}")
            return None
        
        start_time = self._parse_datetime(start_str)
        end_time = self._parse_datetime(end_str)
        
        if not start_time or not end_time:
            return None
        
        # Detectar eventos de todo el día
        all_day = item.get("all_day", False)
        
        # Extraer recurrencia
        recurrence = item.get("rrule")
        
        return ExternalEvent(
            external_id=str(item.get("id", "")),
            title=item.get("title", "Evento sin título"),
            start_time=start_time,
            end_time=end_time,
            description=item.get("notes"),
            location=item.get("location"),
            all_day=all_day,
            recurrence=recurrence,
        )
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """
        Parsea una fecha-hora de Teamup.
        
        Teamup usa formato ISO 8601: "2024-01-15T10:00:00+01:00"
        
        Args:
            datetime_str: String ISO 8601
            
        Returns:
            datetime o None si no se puede parsear
        """
        if not datetime_str:
            return None
        
        try:
            # Normalizar formato
            datetime_str = datetime_str.replace("Z", "+00:00")
            
            # Python 3.11+ soporta fromisoformat con timezone
            return datetime.fromisoformat(datetime_str)
            
        except ValueError as e:
            logger.warning(f"Error parseando datetime '{datetime_str}': {e}")
            return None
    
    def parse_subcalendars(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parsea la lista de subcalendarios de Teamup.
        
        Args:
            raw_data: Respuesta de GET /{calendar_key}/subcalendars
            
        Returns:
            list: Lista de subcalendarios con sus metadatos
        """
        subcalendars = raw_data.get("subcalendars", [])
        
        result = []
        for sub in subcalendars:
            result.append({
                "id": sub.get("id"),
                "name": sub.get("name"),
                "color": sub.get("color"),
                "active": sub.get("active", True),
            })
        
        return result
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor."""
        return self.PROVIDER_NAME
