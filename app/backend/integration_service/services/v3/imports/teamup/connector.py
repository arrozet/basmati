"""
Teamup Connector - Comunicación con Teamup API.

Implementa ICalendarConnector para manejar todas las operaciones HTTP
con la API de Teamup.
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


class TeamupConnector(ICalendarConnector):
    """
    Conector concreto para Teamup API.
    
    Maneja autenticación con API Key y comunicación HTTP con la API.
    
    Attributes:
        api_key: API Key de Teamup
        base_url: URL base de Teamup API
        timeout: Timeout para requests HTTP
        
    Nota:
        Teamup usa "calendar_key" como identificador del calendario en las URLs,
        no un ID numérico. El calendar_key es una cadena alfanumérica.
    """
    
    BASE_URL = "https://api.teamup.com"
    
    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0
    ):
        """
        Inicializa el conector con credenciales de Teamup.
        
        Args:
            api_key: API Key de Teamup (obtenida desde dashboard de Teamup)
            timeout: Timeout en segundos para requests HTTP
        """
        self._api_key = api_key
        self._timeout = timeout
        self._headers = {
            "Teamup-Token": api_key,
            "Content-Type": "application/json",
        }
    
    async def fetch_calendar_info(self, calendar_id: str) -> ConnectionResult:
        """
        Obtiene información de un calendario desde Teamup API.
        
        Args:
            calendar_id: Calendar Key de Teamup (ej: "ksfogsn8nf72mjdfcv")
            
        Returns:
            ConnectionResult: Datos del calendario o error
        """
        url = f"{self.BASE_URL}/{calendar_id}/configuration"
        
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
                        error_message="API Key de Teamup inválida",
                        status_code=401
                    )
                elif response.status_code == 404:
                    return ConnectionResult(
                        success=False,
                        error_message=f"Calendario '{calendar_id}' no encontrado en Teamup",
                        status_code=404
                    )
                else:
                    error_text = response.text
                    try:
                        error_data = response.json()
                        error_text = error_data.get("error", {}).get(
                            "message", error_text
                        )
                    except Exception:
                        pass
                    
                    return ConnectionResult(
                        success=False,
                        error_message=f"Error HTTP {response.status_code}: {error_text}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            logger.error(f"Error de conexión con Teamup API: {e}")
            return ConnectionResult(
                success=False,
                error_message="No se pudo conectar con Teamup API"
            )
        except httpx.TimeoutException:
            logger.error("Timeout conectando con Teamup API")
            return ConnectionResult(
                success=False,
                error_message="Timeout al conectar con Teamup API"
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
        Obtiene eventos de un calendario desde Teamup API.
        
        Args:
            calendar_id: Calendar Key de Teamup
            start_date: Fecha inicio (por defecto: hoy - 365 días)
            end_date: Fecha fin (por defecto: hoy + 365 días)
            
        Returns:
            ConnectionResult: Lista de eventos o error
        """
        url = f"{self.BASE_URL}/{calendar_id}/events"
        
        # Configurar rango de fechas amplio para incluir pasado y futuro
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.utcnow() + timedelta(days=365)
        
        # Teamup usa formato de fecha simple: YYYY-MM-DD
        params = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    events = data.get("events", [])
                    logger.info(f"Obtenidos {len(events)} eventos de Teamup")
                    
                    return ConnectionResult(
                        success=True,
                        data=data,
                        status_code=200
                    )
                else:
                    error_text = response.text
                    try:
                        error_data = response.json()
                        error_text = error_data.get("error", {}).get(
                            "message", error_text
                        )
                    except Exception:
                        pass
                    
                    return ConnectionResult(
                        success=False,
                        error_message=f"Error HTTP {response.status_code}: {error_text}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            logger.error(f"Error de conexión obteniendo eventos de Teamup: {e}")
            return ConnectionResult(
                success=False,
                error_message="No se pudo conectar con Teamup API"
            )
        except httpx.TimeoutException:
            return ConnectionResult(
                success=False,
                error_message="Timeout al obtener eventos de Teamup"
            )
        except Exception as e:
            logger.exception(f"Error inesperado en fetch_events: {e}")
            return ConnectionResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    async def fetch_subcalendars(self, calendar_id: str) -> ConnectionResult:
        """
        Obtiene la lista de subcalendarios de un calendario de Teamup.
        
        Teamup soporta subcalendarios dentro de un calendario principal.
        
        Args:
            calendar_id: Calendar Key del calendario principal
            
        Returns:
            ConnectionResult: Lista de subcalendarios
        """
        url = f"{self.BASE_URL}/{calendar_id}/subcalendars"
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=self._headers)
                
                if response.status_code == 200:
                    return ConnectionResult(
                        success=True,
                        data=response.json(),
                        status_code=200
                    )
                else:
                    return ConnectionResult(
                        success=False,
                        error_message=f"Error obteniendo subcalendarios: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except Exception as e:
            logger.exception(f"Error obteniendo subcalendarios: {e}")
            return ConnectionResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    async def test_connection(self) -> bool:
        """
        Prueba la validez de la API Key.
        
        Nota: Teamup no tiene un endpoint de verificación directo que no requiera
        un calendar_id. Este método intenta verificar la API Key haciendo un request
        a un endpoint que requiere autenticación. Si la API Key es inválida, Teamup
        devolverá 401. Sin embargo, este método no puede garantizar completamente la
        validez de la key sin un calendar_id válido.
        
        Para una verificación más confiable, use fetch_calendar_info() con un
        calendar_id conocido.
        
        Returns:
            bool: True si la API Key parece válida (no devuelve 401)
        """
        # Teamup no tiene un endpoint de verificación directo sin calendar_id.
        # Intentamos hacer un request a un endpoint que requiere autenticación.
        # Usamos un calendar_id de prueba que probablemente no existe, pero
        # el objetivo es verificar que la API Key es válida (no 401).
        # Si obtenemos 404, significa que la key es válida pero el calendario no existe.
        # Si obtenemos 401, la key es inválida.
        
        # Usamos un calendar_id de prueba (formato válido pero probablemente inexistente)
        test_calendar_id = "test_connection_verification"
        url = f"{self.BASE_URL}/{test_calendar_id}/configuration"
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=self._headers)
                
                # 401 = API Key inválida
                if response.status_code == 401:
                    return False
                
                # 404 = API Key válida pero calendario no existe (esto es lo esperado)
                # 200 = API Key válida y calendario existe (caso improbable pero válido)
                # Cualquier otro código también indica que la key es válida
                return True
                
        except Exception as e:
            logger.error(f"Error probando conexión con Teamup: {e}")
            return False
