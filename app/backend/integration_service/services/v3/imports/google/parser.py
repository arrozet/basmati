"""
Google Calendar Parser - Transformación de datos de Google Calendar.

Implementa IEventParser para convertir respuestas de Google Calendar API
a objetos de dominio normalizados.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Optional
import logging

from services.v3.imports.interfaces import (
    IEventParser,
    ExternalCalendarInfo,
    ExternalEvent,
)

logger = logging.getLogger(__name__)


class GoogleEventParser(IEventParser):
    """
    Parser concreto para datos de Google Calendar.
    
    Transforma las respuestas JSON de Google Calendar API a objetos
    de dominio normalizados que pueden ser usados por el importador.
    """
    
    PROVIDER_NAME = "Google Calendar"
    DEFAULT_COLOR = "#4285F4"  # Azul de Google

    def __init__(self) -> None:
        self._default_timezone: Optional[str] = None

    def set_default_timezone(self, timezone_name: Optional[str]) -> None:
        self._default_timezone = timezone_name

    def _get_tzinfo(self, timezone_name: Optional[str]) -> ZoneInfo:
        tz = timezone_name or self._default_timezone or "UTC"
        try:
            return ZoneInfo(tz)
        except Exception:
            logger.warning(f"Zona horaria inválida '{tz}', usando UTC")
            return ZoneInfo("UTC")
    
    def parse_calendar_info(self, raw_data: dict[str, Any]) -> ExternalCalendarInfo:
        """
        Parsea información de calendario desde respuesta de Google.
        
        Args:
            raw_data: Respuesta JSON de GET /calendars/{calendarId}
            
        Returns:
            ExternalCalendarInfo: Información normalizada
        """
        return ExternalCalendarInfo(
            external_id=raw_data.get("id", ""),
            name=raw_data.get("summary", "Calendario de Google"),
            description=raw_data.get("description"),
            color=raw_data.get("backgroundColor", self.DEFAULT_COLOR),
            timezone=raw_data.get("timeZone"),
        )
    
    def parse_events(self, raw_data: dict[str, Any]) -> list[ExternalEvent]:
        """
        Parsea lista de eventos desde respuesta de Google.
        
        Args:
            raw_data: Respuesta JSON de GET /calendars/{calendarId}/events
            
        Returns:
            list[ExternalEvent]: Lista de eventos normalizados
        """
        events = []
        items = raw_data.get("items", [])
        
        for item in items:
            try:
                event = self._parse_single_event(item)
                if event:
                    events.append(event)
            except Exception as e:
                logger.warning(
                    f"Error parseando evento de Google: {e}. "
                    f"Evento: {item.get('id', 'unknown')}"
                )
                continue
        
        logger.info(f"Parseados {len(events)} eventos de {len(items)} items")
        return events
    
    def _parse_single_event(self, item: dict[str, Any]) -> Optional[ExternalEvent]:
        """
        Parsea un evento individual de Google Calendar.
        
        Args:
            item: Objeto evento de Google Calendar
            
        Returns:
            ExternalEvent o None si no es válido
        """
        # Ignorar eventos cancelados
        if item.get("status") == "cancelled":
            return None
        
        # Extraer fechas (puede ser dateTime o date para eventos de día completo)
        start_info = item.get("start", {})
        end_info = item.get("end", {})
        
        all_day = "date" in start_info and "dateTime" not in start_info
        
        if all_day:
            # Google usa fecha exclusiva para el final de eventos all-day.
            # Para que el frontend no lo desplace a 01:00, mandamos datetimes con
            # offset (timezone del calendario) en vez de asumir UTC.
            start_date_str = start_info.get("date")  # "2025-11-15"
            end_date_str = end_info.get("date")      # "2025-11-16" (exclusivo)

            tzinfo = self._get_tzinfo(start_info.get("timeZone") or end_info.get("timeZone"))

            if start_date_str:
                start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                start_time = start_dt.replace(hour=0, minute=0, second=0, tzinfo=tzinfo)
            else:
                start_time = None

            if end_date_str:
                end_exclusive = datetime.strptime(end_date_str, "%Y-%m-%d")
                end_inclusive_day = end_exclusive - timedelta(days=1)
                end_time = end_inclusive_day.replace(hour=23, minute=59, second=59, tzinfo=tzinfo)
            else:
                end_time = None
        else:
            start_time = self._parse_datetime(
                start_info.get("dateTime"),
                start_info.get("timeZone")
            )
            end_time = self._parse_datetime(
                end_info.get("dateTime"),
                end_info.get("timeZone")
            )
        
        if not start_time or not end_time:
            logger.warning(f"Evento sin fechas válidas: {item.get('id')}")
            return None
        
        # Extraer ubicación
        location = item.get("location")
        
        # Extraer recurrencia
        recurrence = None
        if item.get("recurrence"):
            recurrence = ";".join(item["recurrence"])
        
        return ExternalEvent(
            external_id=item.get("id", ""),
            title=item.get("summary", "Evento sin título"),
            start_time=start_time,
            end_time=end_time,
            description=item.get("description"),
            location=location,
            all_day=all_day,
            recurrence=recurrence,
        )
    
    def _parse_datetime(
        self, 
        datetime_str: Optional[str],
        timezone: Optional[str] = None
    ) -> Optional[datetime]:
        """
        Parsea una fecha-hora ISO 8601 de Google Calendar.
        
        Args:
            datetime_str: String ISO 8601 (ej: "2024-01-15T10:00:00+01:00")
            timezone: Zona horaria opcional
            
        Returns:
            datetime o None si no se puede parsear
        """
        if not datetime_str:
            return None
        
        try:
            # Google Calendar usa formato ISO 8601 con timezone
            # Ejemplo: "2024-01-15T10:00:00+01:00" o "2024-01-15T10:00:00Z"
            
            # Reemplazar Z por +00:00 para compatibilidad
            datetime_str = datetime_str.replace("Z", "+00:00")
            
            # Python 3.11+ soporta fromisoformat con timezone
            return datetime.fromisoformat(datetime_str)
            
        except ValueError as e:
            logger.warning(f"Error parseando datetime '{datetime_str}': {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parsea una fecha (sin hora) para eventos de día completo.
        
        Args:
            date_str: String de fecha (ej: "2024-01-15")
            
        Returns:
            datetime a las 00:00:00 o None
        """
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            logger.warning(f"Error parseando date '{date_str}': {e}")
            return None
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor."""
        return self.PROVIDER_NAME
