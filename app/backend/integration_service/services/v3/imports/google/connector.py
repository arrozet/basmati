"""
Google Calendar Connector - Comunicación con Google Calendar API.

Implementa ICalendarConnector para manejar todas las operaciones HTTP
con la API de Google Calendar.
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional
import logging

from services.v3.imports.interfaces import (
    ICalendarConnector,
    ConnectionResult,
)

logger = logging.getLogger(__name__)


class GoogleCalendarConnector(ICalendarConnector):
    """
    Conector concreto para Google Calendar API.
    
    Maneja autenticación OAuth2 y comunicación HTTP con la API.
    
    Attributes:
        access_token: Token OAuth2 de Google
        base_url: URL base de Google Calendar API
        timeout: Timeout para requests HTTP
    """
    
    BASE_URL = "https://www.googleapis.com/calendar/v3"
    
    def __init__(
        self,
        access_token: str,
        timeout: float = 30.0
    ):
        """
        Inicializa el conector con credenciales de Google.
        
        Args:
            access_token: Token OAuth2 obtenido del flujo de autenticación
            timeout: Timeout en segundos para requests HTTP
        """
        self._access_token = access_token
        self._timeout = timeout
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
    
    async def fetch_calendar_info(self, calendar_id: str) -> ConnectionResult:
        """
        Obtiene información de un calendario desde Google Calendar API.
        
        Args:
            calendar_id: ID del calendario (usar "primary" para el principal)
            
        Returns:
            ConnectionResult: Datos del calendario o error
        """
        url = f"{self.BASE_URL}/calendars/{calendar_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=self._headers)
                
                if response.status_code == 200:
                    return ConnectionResult(
                        success=True,
                        data=response.json(),
                        status_code=200
                    )
                elif response.status_code == 401:
                    return ConnectionResult(
                        success=False,
                        error_message="Token de Google inválido o expirado",
                        status_code=401
                    )
                elif response.status_code == 404:
                    return ConnectionResult(
                        success=False,
                        error_message=f"Calendario '{calendar_id}' no encontrado",
                        status_code=404
                    )
                else:
                    error_data = response.json() if response.text else {}
                    return ConnectionResult(
                        success=False,
                        error_message=error_data.get("error", {}).get(
                            "message", f"Error HTTP {response.status_code}"
                        ),
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            logger.error(f"Error de conexión con Google Calendar API: {e}")
            return ConnectionResult(
                success=False,
                error_message="No se pudo conectar con Google Calendar API"
            )
        except httpx.TimeoutException:
            logger.error("Timeout conectando con Google Calendar API")
            return ConnectionResult(
                success=False,
                error_message="Timeout al conectar con Google Calendar API"
            )
        except Exception as e:
            logger.exception(f"Error inesperado en fetch_calendar_info: {e}")
            return ConnectionResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    async def fetch_events(
        self,
        calendar_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ConnectionResult:
        """
        Obtiene eventos de un calendario desde Google Calendar API.
        
        Args:
            calendar_id: ID del calendario
            start_date: Fecha inicio (por defecto: hoy)
            end_date: Fecha fin (por defecto: hoy + 90 días)
            
        Returns:
            ConnectionResult: Lista de eventos o error
        """
        url = f"{self.BASE_URL}/calendars/{calendar_id}/events"
        
        # Configurar rango de fechas
        if start_date is None:
            start_date = datetime.utcnow()
        if end_date is None:
            end_date = start_date + timedelta(days=90)
        
        params = {
            "timeMin": start_date.isoformat() + "Z",
            "timeMax": end_date.isoformat() + "Z",
            "singleEvents": "true",  # Expande eventos recurrentes
            "orderBy": "startTime",
            "maxResults": 250,  # Máximo permitido por Google
        }
        
        try:
            all_events = []
            page_token = None
            
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                while True:
                    if page_token:
                        params["pageToken"] = page_token
                    
                    response = await client.get(
                        url, 
                        headers=self._headers,
                        params=params
                    )
                    
                    if response.status_code != 200:
                        error_data = response.json() if response.text else {}
                        return ConnectionResult(
                            success=False,
                            error_message=error_data.get("error", {}).get(
                                "message", f"Error HTTP {response.status_code}"
                            ),
                            status_code=response.status_code
                        )
                    
                    data = response.json()
                    events = data.get("items", [])
                    all_events.extend(events)
                    
                    # Manejar paginación
                    page_token = data.get("nextPageToken")
                    if not page_token:
                        break
                
                logger.info(f"Obtenidos {len(all_events)} eventos de Google Calendar")
                
                return ConnectionResult(
                    success=True,
                    data={"items": all_events},
                    status_code=200
                )
                
        except httpx.ConnectError as e:
            logger.error(f"Error de conexión obteniendo eventos: {e}")
            return ConnectionResult(
                success=False,
                error_message="No se pudo conectar con Google Calendar API"
            )
        except httpx.TimeoutException:
            return ConnectionResult(
                success=False,
                error_message="Timeout al obtener eventos de Google Calendar"
            )
        except Exception as e:
            logger.exception(f"Error inesperado en fetch_events: {e}")
            return ConnectionResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    async def test_connection(self) -> bool:
        """
        Prueba la validez del token de acceso.
        
        Returns:
            bool: True si el token es válido
        """
        # Intentar obtener la lista de calendarios como prueba
        url = f"{self.BASE_URL}/users/me/calendarList"
        params = {"maxResults": 1}
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    params=params
                )
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error probando conexión con Google: {e}")
            return False
