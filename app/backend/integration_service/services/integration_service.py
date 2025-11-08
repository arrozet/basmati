"""Lógica de negocio para integración con servicios externos"""
import httpx
import traceback
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
        
        Si no se proporciona teamup_api_key en el request, usa la configurada en settings.
        
        Args:
            import_request: Datos de importación (API key opcional, calendar_keys)
            
        Returns:
            ImportResponse: Resultado de la importación con IDs de calendarios creados
        """
        from core.config import settings
        
        # Usar API Key del request o la del .env como fallback
        api_key = import_request.teamup_api_key or settings.teamup_api_key
        
        if not api_key:
            return ImportResponse(
                success=False,
                message="API Key de Teamup no proporcionada y no configurada en el servidor",
                imported_sources=[],
                errors=["Teamup API Key requerida pero no encontrada"]
            )
        
        imported_calendar_ids = []
        errors = []
        
        try:
            for calendar_key in import_request.calendar_keys:
                try:
                    # Crear calendario directamente en CalendarService
                    basmati_calendar_id = await self._create_basmati_calendar_from_teamup(
                        calendar_key,
                        import_request.user_external_id,
                        api_key  # Usar la API Key determinada (request o .env)
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
        
        Hace una llamada real a la API de Teamup para obtener información del calendario.
        
        Args:
            teamup_calendar_key: Key del calendario en Teamup
            user_external_id: ID del usuario propietario
            api_key: API Key de Teamup (SIEMPRE REQUERIDA por Teamup API)
            
        Returns:
            str: ID del calendario creado en Basmati o None si falla
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Obtener información del calendario desde Teamup API
                # NOTA: Teamup requiere el header Teamup-Token para TODOS los calendarios
                teamup_headers = {
                    "Teamup-Token": api_key,
                    "Content-Type": "application/json"
                }
                
                teamup_url = f"https://api.teamup.com/{teamup_calendar_key}/configuration"
                
                print(f"Llamando a Teamup API: {teamup_url}")
                teamup_response = await client.get(teamup_url, headers=teamup_headers)
                
                if teamup_response.status_code != 200:
                    print(f"Error al obtener calendario de Teamup: {teamup_response.status_code}")
                    print(f"Respuesta: {teamup_response.text}")
                    return None
                
                teamup_data = teamup_response.json()
                print(f"Datos recibidos de Teamup: {teamup_data}")
                
                # Extraer información del calendario
                calendar_info = teamup_data.get("calendar", {})
                calendar_title = calendar_info.get("name", f"Calendario Teamup ({teamup_calendar_key})")
                calendar_color = calendar_info.get("color", "#FF6B35")
                
                # 2. Crear el calendario en Basmati
                calendar_payload = {
                    "title": calendar_title,
                    "creator_external_id": user_external_id,
                    "creator_display_name": "Universidad de Málaga",
                    "keywords": ["teamup", "imported", "uma", "universidad"],
                    "color": calendar_color,
                    "description": f"Calendario importado desde Teamup - Universidad de Málaga (Key: {teamup_calendar_key})",
                    "visibility": "public"
                }
                
                print(f"Creando calendario en Basmati: {self.calendar_service_url}/v1/calendars")
                print(f"Payload: {calendar_payload}")
                
                response = await client.post(
                    f"{self.calendar_service_url}/v1/calendars",
                    json=calendar_payload
                )
                
                print(f"Respuesta de CalendarService: {response.status_code}")
                
                if response.status_code == 201:
                    calendar_data = response.json()
                    basmati_calendar_id = calendar_data.get("id")
                    print(f"✅ Calendario creado en Basmati con ID: {basmati_calendar_id}")
                    
                    # 3. Importar eventos del calendario
                    await self._import_teamup_events(
                        teamup_calendar_key,
                        basmati_calendar_id,
                        api_key
                    )
                    
                    return basmati_calendar_id
                else:
                    error_detail = f"Status {response.status_code}"
                    try:
                        error_data = response.json()
                        error_detail = f"Status {response.status_code}: {error_data}"
                    except:
                        error_detail = f"Status {response.status_code}: {response.text}"
                    
                    print(f"❌ Error al crear calendario en Basmati: {error_detail}")
                    return None
        
        except httpx.ConnectError as e:
            print(f"❌ No se pudo conectar a CalendarService en {self.calendar_service_url}")
            print(f"   Error: {str(e)}")
            print(f"   Verifica que el servicio esté corriendo: docker-compose ps calendar-service")
            return None
        except Exception as e:
            print(f"❌ Excepción al crear calendario desde Teamup: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _import_teamup_events(
        self,
        teamup_calendar_key: str,
        basmati_calendar_id: str,
        api_key: str
    ) -> None:
        """
        Importa eventos desde Teamup hacia Basmati.
        
        Args:
            teamup_calendar_key: Key del calendario en Teamup
            basmati_calendar_id: ID del calendario en Basmati
            api_key: API Key de Teamup (SIEMPRE REQUERIDA)
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Obtener eventos desde Teamup API
                teamup_headers = {
                    "Teamup-Token": api_key,
                    "Content-Type": "application/json"
                }
                
                # Obtener eventos de los próximos 90 días
                teamup_events_url = f"https://api.teamup.com/{teamup_calendar_key}/events"
                
                print(f"Obteniendo eventos de Teamup: {teamup_events_url}")
                events_response = await client.get(
                    teamup_events_url,
                    headers=teamup_headers,
                    params={
                        "startDate": "today",
                        "endDate": "+90d"
                    }
                )
                
                if events_response.status_code != 200:
                    print(f"Error al obtener eventos de Teamup: {events_response.status_code}")
                    return
                
                events_data = events_response.json()
                events = events_data.get("events", [])
                
                print(f"Se encontraron {len(events)} eventos en Teamup")
                
                # Crear cada evento en Basmati
                for teamup_event in events:
                    try:
                        event_payload = {
                            "calendar_id": basmati_calendar_id,
                            "calendar_title": "Universidad de Málaga",
                            "creator_external_id": "uma_teamup",
                            "title": teamup_event.get("title", "Evento sin título"),
                            "description": teamup_event.get("notes", None),
                            "start_time": teamup_event.get("start_dt"),
                            "end_time": teamup_event.get("end_dt"),
                            "visibility": "public"
                        }
                        
                        # Agregar ubicación si existe
                        if teamup_event.get("location"):
                            event_payload["location"] = {
                                "address": teamup_event["location"],
                                "place_name": teamup_event.get("location")
                            }
                        
                        # Crear evento en EventService
                        event_response = await client.post(
                            f"{self.event_service_url}/v1/events",
                            json=event_payload
                        )
                        
                        if event_response.status_code == 201:
                            print(f"✓ Evento importado: {event_payload['title']}")
                        else:
                            print(f"✗ Error al crear evento: {event_response.status_code}")
                    
                    except Exception as e:
                        print(f"Error al importar evento: {str(e)}")
                        continue
                
                print(f"Importación de eventos completada")
        
        except Exception as e:
            print(f"Error al importar eventos desde Teamup: {str(e)}")
            import traceback
            traceback.print_exc()
