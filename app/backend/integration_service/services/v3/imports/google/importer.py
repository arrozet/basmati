"""
Google Calendar Importer - Orquestación de importación.

Implementa ICalendarImporter para coordinar la importación completa
de calendarios y eventos desde Google Calendar hacia Basmati.
"""

import httpx
import logging
from typing import Optional

from services.v3.imports.interfaces import (
    ICalendarImporter,
    ICalendarConnector,
    IEventParser,
    ImportResult,
    ExternalCalendarInfo,
)

logger = logging.getLogger(__name__)


class GoogleCalendarImporter(ICalendarImporter):
    """
    Importador concreto para Google Calendar.
    
    Orquesta el proceso completo de importación:
    1. Conectar con Google Calendar API (via Connector)
    2. Parsear datos recibidos (via Parser)
    3. Crear calendario en Basmati
    4. Crear eventos en Basmati
    
    Attributes:
        connector: Conector para comunicación con Google API
        parser: Parser para transformación de datos
        calendar_service_url: URL del CalendarService de Basmati
        event_service_url: URL del EventService de Basmati
    """
    
    def __init__(
        self,
        connector: ICalendarConnector,
        parser: IEventParser,
        calendar_service_url: str,
        event_service_url: str,
    ):
        """
        Inicializa el importador con sus dependencias.
        
        Args:
            connector: Instancia de GoogleCalendarConnector
            parser: Instancia de GoogleEventParser
            calendar_service_url: URL base del CalendarService
            event_service_url: URL base del EventService
        """
        self._connector = connector
        self._parser = parser
        self._calendar_service_url = calendar_service_url
        self._event_service_url = event_service_url
    
    async def import_calendar(
        self,
        external_calendar_id: str,
        user_external_id: str
    ) -> ImportResult:
        """
        Importa un calendario completo con sus eventos.
        
        Args:
            external_calendar_id: ID del calendario en Google (o "primary")
            user_external_id: ID del usuario en Basmati
            
        Returns:
            ImportResult: Resultado de la importación
        """
        logger.info(
            f"Iniciando importación de Google Calendar: {external_calendar_id} "
            f"para usuario: {user_external_id}"
        )
        
        # 1. Obtener información del calendario
        calendar_result = await self._connector.fetch_calendar_info(external_calendar_id)
        
        if not calendar_result.success:
            return ImportResult(
                success=False,
                error_message=f"Error obteniendo calendario: {calendar_result.error_message}"
            )
        
        # 2. Parsear información del calendario
        calendar_info = self._parser.parse_calendar_info(calendar_result.data)
        
        # 3. Crear calendario en Basmati
        basmati_calendar_id = await self._create_basmati_calendar(
            calendar_info,
            user_external_id
        )
        
        if not basmati_calendar_id:
            return ImportResult(
                success=False,
                error_message="Error creando calendario en Basmati"
            )
        
        # 4. Importar eventos
        events_result = await self._import_events(
            external_calendar_id,
            basmati_calendar_id,
            calendar_info.name,
            user_external_id
        )
        
        return ImportResult(
            success=True,
            basmati_calendar_id=basmati_calendar_id,
            events_imported=events_result["imported"],
            events_failed=events_result["failed"],
        )
    
    async def import_events_only(
        self,
        external_calendar_id: str,
        basmati_calendar_id: str,
        user_external_id: str
    ) -> ImportResult:
        """
        Importa solo eventos a un calendario existente.
        
        Args:
            external_calendar_id: ID del calendario en Google
            basmati_calendar_id: ID del calendario destino en Basmati
            user_external_id: ID del usuario
            
        Returns:
            ImportResult: Resultado de la importación
        """
        logger.info(
            f"Importando solo eventos de {external_calendar_id} "
            f"a calendario Basmati: {basmati_calendar_id}"
        )
        
        # Obtener info del calendario para el título
        calendar_result = await self._connector.fetch_calendar_info(external_calendar_id)
        calendar_title = "Calendario importado"
        
        if calendar_result.success:
            calendar_info = self._parser.parse_calendar_info(calendar_result.data)
            calendar_title = calendar_info.name
        
        events_result = await self._import_events(
            external_calendar_id,
            basmati_calendar_id,
            calendar_title,
            user_external_id
        )
        
        return ImportResult(
            success=events_result["imported"] > 0,
            basmati_calendar_id=basmati_calendar_id,
            events_imported=events_result["imported"],
            events_failed=events_result["failed"],
        )
    
    async def _create_basmati_calendar(
        self,
        calendar_info: ExternalCalendarInfo,
        user_external_id: str
    ) -> Optional[str]:
        """
        Crea un calendario en Basmati CalendarService.
        
        Args:
            calendar_info: Información del calendario externo
            user_external_id: ID del usuario propietario
            
        Returns:
            str: ID del calendario creado o None si falla
        """
        payload = {
            "title": calendar_info.name,
            "creator_external_id": user_external_id,
            "creator_display_name": "Usuario importado",
            "keywords": ["google_calendar", "imported", "v3"],
            "color": calendar_info.color or "#4285F4",
            "description": calendar_info.description or f"Importado desde Google Calendar",
            "visibility": "private",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self._calendar_service_url}/v1/calendars",
                    json=payload
                )
                
                if response.status_code == 201:
                    data = response.json()
                    calendar_id = data.get("id")
                    logger.info(f"✅ Calendario creado en Basmati: {calendar_id}")
                    return calendar_id
                else:
                    logger.error(
                        f"Error creando calendario: {response.status_code} - "
                        f"{response.text}"
                    )
                    return None
                    
        except httpx.ConnectError:
            logger.error(
                f"No se pudo conectar con CalendarService en "
                f"{self._calendar_service_url}"
            )
            return None
        except Exception as e:
            logger.exception(f"Error inesperado creando calendario: {e}")
            return None
    
    async def _import_events(
        self,
        external_calendar_id: str,
        basmati_calendar_id: str,
        calendar_title: str,
        user_external_id: str
    ) -> dict[str, int]:
        """
        Importa eventos desde Google Calendar a Basmati.
        
        Args:
            external_calendar_id: ID del calendario en Google
            basmati_calendar_id: ID del calendario en Basmati
            calendar_title: Título del calendario
            user_external_id: ID del usuario
            
        Returns:
            dict: {"imported": N, "failed": M}
        """
        # Obtener eventos de Google
        events_result = await self._connector.fetch_events(external_calendar_id)
        
        if not events_result.success:
            logger.error(f"Error obteniendo eventos: {events_result.error_message}")
            return {"imported": 0, "failed": 0}
        
        # Parsear eventos
        events = self._parser.parse_events(events_result.data)
        
        if not events:
            logger.info("No hay eventos para importar")
            return {"imported": 0, "failed": 0}
        
        # Crear eventos en Basmati
        imported = 0
        failed = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for event in events:
                try:
                    payload = event.to_basmati_payload(
                        calendar_id=basmati_calendar_id,
                        calendar_title=calendar_title,
                        creator_external_id=user_external_id
                    )
                    
                    response = await client.post(
                        f"{self._event_service_url}/v1/events",
                        json=payload
                    )
                    
                    if response.status_code == 201:
                        imported += 1
                        logger.debug(f"✓ Evento importado: {event.title}")
                    else:
                        failed += 1
                        logger.warning(
                            f"✗ Error creando evento '{event.title}': "
                            f"{response.status_code}"
                        )
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"Error importando evento '{event.title}': {e}")
        
        logger.info(f"Importación completada: {imported} eventos, {failed} fallos")
        return {"imported": imported, "failed": failed}
