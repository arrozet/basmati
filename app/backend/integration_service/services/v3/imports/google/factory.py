"""
Google Import Factory - Factoría concreta para Google Calendar.

Implementa IImportFactory para crear la familia completa de objetos
necesarios para importar desde Google Calendar.
"""

from services.v3.imports.interfaces import (
    IImportFactory,
    ICalendarConnector,
    IEventParser,
    ICalendarImporter,
)
from services.v3.imports.google.connector import GoogleCalendarConnector
from services.v3.imports.google.parser import GoogleEventParser
from services.v3.imports.google.importer import GoogleCalendarImporter


class GoogleImportFactory(IImportFactory):
    """
    Factoría concreta para crear objetos de importación de Google Calendar.
    
    Esta factoría garantiza que todos los componentes (Connector, Parser,
    Importer) sean compatibles entre sí y trabajen correctamente juntos.
    
    Ejemplo de uso:
        factory = GoogleImportFactory(
            access_token="ya29.xxx...",
            calendar_service_url="http://calendar-service:8003",
            event_service_url="http://event-service:8002"
        )
        
        # Crear importador completo
        importer = factory.create_importer()
        result = await importer.import_calendar("primary", "user_123")
        
        # O usar componentes individuales
        connector = factory.create_connector()
        if await connector.test_connection():
            print("Conexión válida")
    """
    
    PROVIDER_TYPE = "google"
    
    def __init__(
        self,
        access_token: str,
        calendar_service_url: str,
        event_service_url: str,
    ):
        """
        Inicializa la factoría con las credenciales y URLs necesarias.
        
        Args:
            access_token: Token OAuth2 de Google
            calendar_service_url: URL del CalendarService de Basmati
            event_service_url: URL del EventService de Basmati
        """
        self._access_token = access_token
        self._calendar_service_url = calendar_service_url
        self._event_service_url = event_service_url
    
    def create_connector(self) -> ICalendarConnector:
        """
        Crea un GoogleCalendarConnector configurado.
        
        Returns:
            GoogleCalendarConnector: Conector para Google Calendar API
        """
        return GoogleCalendarConnector(
            access_token=self._access_token
        )
    
    def create_parser(self) -> IEventParser:
        """
        Crea un GoogleEventParser.
        
        Returns:
            GoogleEventParser: Parser para datos de Google Calendar
        """
        return GoogleEventParser()
    
    def create_importer(self) -> ICalendarImporter:
        """
        Crea un GoogleCalendarImporter con todas sus dependencias.
        
        El importador se crea con el Connector y Parser de esta misma
        factoría, garantizando compatibilidad.
        
        Returns:
            GoogleCalendarImporter: Importador completo configurado
        """
        return GoogleCalendarImporter(
            connector=self.create_connector(),
            parser=self.create_parser(),
            calendar_service_url=self._calendar_service_url,
            event_service_url=self._event_service_url,
        )
    
    @classmethod
    def get_provider_type(cls) -> str:
        """
        Retorna el identificador del proveedor.
        
        Returns:
            str: "google"
        """
        return cls.PROVIDER_TYPE
