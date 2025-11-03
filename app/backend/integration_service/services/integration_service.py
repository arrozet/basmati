"""Lógica de negocio para integración con servicios externos"""
import httpx
from schemas.integration import (
    GoogleCalendarImportRequest,
    TeamupImportRequest,
    ImportResponse,
    ImportedCalendar
)


class IntegrationService:
    """
    Servicio para importar calendarios desde servicios externos.
    
    Simplemente crea calendarios en CalendarService sin guardar metadatos de integración.
    """
    
    def __init__(
        self, 
        calendar_service_url: str,
        event_service_url: str
    ):
        """
        Inicializa el servicio de integración.
        
        Args:
            calendar_service_url: URL del CalendarService
            event_service_url: URL del EventService
        """
        self.calendar_service_url = calendar_service_url
        self.event_service_url = event_service_url
    
    # ==================== IMPORTACIÓN GOOGLE CALENDAR ====================
    
    async def import_from_google_calendar(
        self, 
        import_request: GoogleCalendarImportRequest
    ) -> ImportResponse:
        """
        Importa calendarios desde Google Calendar.
        
        Simplemente crea calendarios en CalendarService sin guardar metadatos.
        
        Args:
            import_request: Datos de importación (token, calendar_ids)
            
        Returns:
            ImportResponse: Resultado de la importación con IDs de calendarios creados
        """
        imported_calendar_ids = []
        errors = []
        
        try:
            calendar_ids_to_import = import_request.calendar_ids or ["primary"]
            
            for calendar_id in calendar_ids_to_import:
                try:
                    # Crear calendario directamente en CalendarService
                    basmati_calendar_id = await self._create_basmati_calendar_from_google(
                        calendar_id,
                        import_request.user_external_id,
                        import_request.google_access_token
                    )
                    
                    if basmati_calendar_id:
                        imported_calendar_ids.append(
                            ImportedCalendar(
                                external_id=calendar_id,
                                basmati_calendar_id=basmati_calendar_id
                            )
                        )
                    else:
                        errors.append(f"Error al crear calendario de Basmati para '{calendar_id}'")
                
                except Exception as e:
                    errors.append(f"Error al importar '{calendar_id}': {str(e)}")
            
            success = len(imported_calendar_ids) > 0
            message = f"Se importaron {len(imported_calendar_ids)} calendarios correctamente"
            if errors:
                message += f". {len(errors)} errores encontrados"
            
            return ImportResponse(
                success=success,
                message=message,
                imported_sources=imported_calendar_ids,
                errors=errors
            )
        
        except Exception as e:
            return ImportResponse(
                success=False,
                message=f"Error general en la importación: {str(e)}",
                imported_sources=[],
                errors=[str(e)]
            )
    
    async def _create_basmati_calendar_from_google(
        self,
        google_calendar_id: str,
        user_external_id: str,
        access_token: str
    ) -> str | None:
        """
        Crea un calendario en Basmati a partir de datos de Google Calendar.
        
        Args:
            google_calendar_id: ID del calendario en Google
            user_external_id: ID del usuario propietario
            access_token: Token de acceso de Google
            
        Returns:
            str: ID del calendario creado en Basmati o None si falla
        """
        try:
            # TODO: Llamar a Google Calendar API para obtener detalles del calendario
            # Por ahora, simulamos los datos
            
            # Simular datos de Google Calendar
            calendar_title = f"Calendario de Google ({google_calendar_id})"
            calendar_color = "#4285F4"  # Azul de Google
            
            # Llamar a CalendarService para crear el calendario
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.calendar_service_url}/v1/calendars",
                    json={
                        "title": calendar_title,
                        "creator_external_id": user_external_id,
                        "creator_display_name": "Usuario importado",
                        "keywords": ["google_calendar", "imported"],
                        "color": calendar_color,
                        "description": f"Importado desde Google Calendar (ID: {google_calendar_id})",
                        "visibility": "private"
                    }
                )
                
                if response.status_code == 201:
                    calendar_data = response.json()
                    return calendar_data.get("id")
                else:
                    # Log del error para debugging
                    print(f"Error al crear calendario: {response.status_code} - {response.text}")
                    return None
        
        except Exception as e:
            print(f"Excepción al crear calendario desde Google: {str(e)}")
            return None
    
    # ==================== IMPORTACIÓN TEAMUP ====================
    
    async def import_from_teamup(self, import_request: TeamupImportRequest) -> ImportResponse:
        """
        Importa calendarios desde Teamup.
        
        Simplemente crea calendarios en CalendarService sin guardar metadatos.
        
        Args:
            import_request: Datos de importación (API key, calendar_keys)
            
        Returns:
            ImportResponse: Resultado de la importación con IDs de calendarios creados
        """
        imported_calendar_ids = []
        errors = []
        
        try:
            for calendar_key in import_request.calendar_keys:
                try:
                    # Crear calendario directamente en CalendarService
                    basmati_calendar_id = await self._create_basmati_calendar_from_teamup(
                        calendar_key,
                        import_request.user_external_id,
                        import_request.teamup_api_key
                    )
                    
                    if basmati_calendar_id:
                        imported_calendar_ids.append(
                            ImportedCalendar(
                                external_id=calendar_key,
                                basmati_calendar_id=basmati_calendar_id
                            )
                        )
                    else:
                        errors.append(f"Error al crear calendario de Basmati para '{calendar_key}'")
                
                except Exception as e:
                    errors.append(f"Error al importar '{calendar_key}': {str(e)}")
            
            success = len(imported_calendar_ids) > 0
            message = f"Se importaron {len(imported_calendar_ids)} calendarios correctamente"
            if errors:
                message += f". {len(errors)} errores encontrados"
            
            return ImportResponse(
                success=success,
                message=message,
                imported_sources=imported_calendar_ids,
                errors=errors
            )
        
        except Exception as e:
            return ImportResponse(
                success=False,
                message=f"Error general en la importación: {str(e)}",
                imported_sources=[],
                errors=[str(e)]
            )
    
    async def _create_basmati_calendar_from_teamup(
        self,
        teamup_calendar_key: str,
        user_external_id: str,
        api_key: str
    ) -> str | None:
        """
        Crea un calendario en Basmati a partir de datos de Teamup.
        
        Args:
            teamup_calendar_key: Key del calendario en Teamup
            user_external_id: ID del usuario propietario
            api_key: API Key de Teamup
            
        Returns:
            str: ID del calendario creado en Basmati o None si falla
        """
        try:
            # TODO: Llamar a Teamup API para obtener detalles del calendario
            # Por ahora, simulamos los datos
            
            calendar_title = f"Calendario de Teamup ({teamup_calendar_key})"
            calendar_color = "#FF6B35"  # Color naranja de Teamup
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.calendar_service_url}/v1/calendars",
                    json={
                        "title": calendar_title,
                        "creator_external_id": user_external_id,
                        "creator_display_name": "Usuario importado",
                        "keywords": ["teamup", "imported"],
                        "color": calendar_color,
                        "description": f"Importado desde Teamup (Key: {teamup_calendar_key})",
                        "visibility": "private"
                    }
                )
                
                if response.status_code == 201:
                    calendar_data = response.json()
                    return calendar_data.get("id")
                else:
                    # Log del error para debugging
                    print(f"Error al crear calendario: {response.status_code} - {response.text}")
                    return None
        
        except Exception as e:
            print(f"Excepción al crear calendario desde Teamup: {str(e)}")
            return None
