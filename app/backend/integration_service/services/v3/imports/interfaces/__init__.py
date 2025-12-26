"""
Interfaces abstractas para el patrón Abstract Factory de importación.

Este módulo define:
- Productos Abstractos: ICalendarConnector, IEventParser, ICalendarImporter
- Factoría Abstracta: IImportFactory

Cada proveedor (Google, Teamup, etc.) debe implementar todas estas interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


# =============================================================================
# DATA TRANSFER OBJECTS (Objetos de dominio compartidos)
# =============================================================================

@dataclass
class ExternalCalendarInfo:
    """Información de un calendario externo."""
    external_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    timezone: Optional[str] = None
    
    
@dataclass  
class ExternalEvent:
    """Evento parseado desde un proveedor externo."""
    external_id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    all_day: bool = False
    recurrence: Optional[str] = None
    
    def to_basmati_payload(
        self, 
        calendar_id: str, 
        calendar_title: str,
        creator_external_id: str
    ) -> dict[str, Any]:
        """Convierte el evento al formato esperado por EventService."""
        payload = {
            "calendar_id": calendar_id,
            "calendar_title": calendar_title,
            "creator_external_id": creator_external_id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "visibility": "public",
        }
        
        if self.description:
            payload["description"] = self.description
            
        if self.location:
            payload["location"] = {
                "address": self.location,
                "place_name": self.location
            }
            
        return payload


@dataclass
class ConnectionResult:
    """Resultado de una conexión con API externa."""
    success: bool
    data: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None


@dataclass
class ImportResult:
    """Resultado de una operación de importación."""
    success: bool
    basmati_calendar_id: Optional[str] = None
    events_imported: int = 0
    events_failed: int = 0
    error_message: Optional[str] = None


# =============================================================================
# INTERFACES DE PRODUCTOS (Abstract Products)
# =============================================================================

class ICalendarConnector(ABC):
    """
    Producto Abstracto: Conector de API.
    
    Responsabilidad: Manejar la comunicación HTTP con la API del proveedor.
    - Autenticación
    - Requests HTTP
    - Manejo de errores de red
    """
    
    @abstractmethod
    async def fetch_calendar_info(self, calendar_id: str) -> ConnectionResult:
        """
        Obtiene información de un calendario desde la API externa.
        
        Args:
            calendar_id: ID del calendario en el proveedor externo
            
        Returns:
            ConnectionResult: Resultado con datos del calendario o error
        """
        pass
    
    @abstractmethod
    async def fetch_events(
        self, 
        calendar_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ConnectionResult:
        """
        Obtiene eventos de un calendario desde la API externa.
        
        Args:
            calendar_id: ID del calendario en el proveedor externo
            start_date: Fecha inicio del rango (opcional)
            end_date: Fecha fin del rango (opcional)
            
        Returns:
            ConnectionResult: Resultado con lista de eventos o error
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Prueba la conexión/autenticación con el proveedor.
        
        Returns:
            bool: True si la conexión es válida
        """
        pass


class IEventParser(ABC):
    """
    Producto Abstracto: Parser de eventos.
    
    Responsabilidad: Transformar datos crudos del proveedor a objetos de dominio.
    - Normalización de fechas
    - Mapeo de campos
    - Validación de datos
    """
    
    @abstractmethod
    def parse_calendar_info(self, raw_data: dict[str, Any]) -> ExternalCalendarInfo:
        """
        Parsea información de calendario desde datos crudos.
        
        Args:
            raw_data: Datos JSON de la API del proveedor
            
        Returns:
            ExternalCalendarInfo: Información normalizada del calendario
        """
        pass
    
    @abstractmethod
    def parse_events(self, raw_data: dict[str, Any]) -> list[ExternalEvent]:
        """
        Parsea lista de eventos desde datos crudos.
        
        Args:
            raw_data: Datos JSON de la API del proveedor
            
        Returns:
            list[ExternalEvent]: Lista de eventos normalizados
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna el nombre del proveedor para logging/debugging.
        
        Returns:
            str: Nombre del proveedor (ej: "Google Calendar", "Teamup")
        """
        pass


class ICalendarImporter(ABC):
    """
    Producto Abstracto: Importador de calendarios.
    
    Responsabilidad: Orquestar la importación completa.
    - Usar Connector para obtener datos
    - Usar Parser para transformar datos
    - Crear calendario y eventos en Basmati
    """
    
    @abstractmethod
    async def import_calendar(
        self,
        external_calendar_id: str,
        user_external_id: str
    ) -> ImportResult:
        """
        Importa un calendario completo con sus eventos.
        
        Args:
            external_calendar_id: ID del calendario en el proveedor
            user_external_id: ID del usuario en Basmati
            
        Returns:
            ImportResult: Resultado de la importación
        """
        pass
    
    @abstractmethod
    async def import_events_only(
        self,
        external_calendar_id: str,
        basmati_calendar_id: str,
        user_external_id: str
    ) -> ImportResult:
        """
        Importa solo eventos a un calendario existente.
        
        Args:
            external_calendar_id: ID del calendario en el proveedor
            basmati_calendar_id: ID del calendario destino en Basmati
            user_external_id: ID del usuario
            
        Returns:
            ImportResult: Resultado de la importación
        """
        pass


# =============================================================================
# FACTORÍA ABSTRACTA (Abstract Factory)
# =============================================================================

class IImportFactory(ABC):
    """
    Factoría Abstracta para crear familia de objetos de importación.
    
    Cada proveedor (Google, Teamup) implementa esta factoría para crear
    sus propios Connector, Parser e Importer que trabajan juntos.
    
    Ventajas:
    - Garantiza consistencia entre productos del mismo proveedor
    - Permite añadir nuevos proveedores sin modificar código cliente
    - Aísla la lógica de creación de objetos
    
    Ejemplo de uso:
        factory = GoogleImportFactory(credentials, service_urls)
        importer = factory.create_importer()
        result = await importer.import_calendar("calendar_id", "user_id")
    """
    
    @abstractmethod
    def create_connector(self) -> ICalendarConnector:
        """
        Crea el conector para comunicación con la API externa.
        
        Returns:
            ICalendarConnector: Conector configurado para el proveedor
        """
        pass
    
    @abstractmethod
    def create_parser(self) -> IEventParser:
        """
        Crea el parser para transformar datos del proveedor.
        
        Returns:
            IEventParser: Parser específico del proveedor
        """
        pass
    
    @abstractmethod
    def create_importer(self) -> ICalendarImporter:
        """
        Crea el importador que orquesta la importación completa.
        
        El importador internamente usa Connector y Parser de la misma familia.
        
        Returns:
            ICalendarImporter: Importador configurado
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_provider_type(cls) -> str:
        """
        Retorna el identificador del tipo de proveedor.
        
        Returns:
            str: Identificador único del proveedor (ej: "google", "teamup")
        """
        pass
