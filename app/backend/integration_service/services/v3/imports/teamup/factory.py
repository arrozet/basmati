"""
Teamup Import Factory - Factoría concreta para Teamup.

Implementa IImportFactory para crear la familia completa de objetos
necesarios para importar desde Teamup.
"""

from services.v3.imports.interfaces import (
    IImportFactory,
    ICalendarConnector,
    IEventParser,
    ICalendarImporter,
)
from services.v3.imports.teamup.connector import TeamupConnector
from services.v3.imports.teamup.parser import TeamupEventParser
from services.v3.imports.teamup.importer import TeamupCalendarImporter


class TeamupImportFactory(IImportFactory):
    """
    Factoría concreta para crear objetos de importación de Teamup.
    
    Esta factoría garantiza que todos los componentes (Connector, Parser,
    Importer) sean compatibles entre sí y trabajen correctamente juntos.
    
    Ejemplo de uso:
        factory = TeamupImportFactory(
            api_key="abc123...",
            calendar_service_url="http://calendar-service:8003",
            event_service_url="http://event-service:8002"
        )
        
        # Crear importador completo
        importer = factory.create_importer()
        result = await importer.import_calendar("ksfogsn8nf72mjdfcv", "user_123")
        
        # O usar componentes individuales
        connector = factory.create_connector()
        result = await connector.fetch_calendar_info("ksfogsn8nf72mjdfcv")
    """
    
    PROVIDER_TYPE = "teamup"
    
    def __init__(
        self,
        api_key: str,
        calendar_service_url: str,
        event_service_url: str,
    ):
        """
        Inicializa la factoría con las credenciales y URLs necesarias.
        
        Args:
            api_key: API Key de Teamup
            calendar_service_url: URL del CalendarService de Basmati
            event_service_url: URL del EventService de Basmati
        """
        self._api_key = api_key
        self._calendar_service_url = calendar_service_url
        self._event_service_url = event_service_url
    
    def create_connector(self) -> ICalendarConnector:
        """
        Crea un TeamupConnector configurado.
        
        Returns:
            TeamupConnector: Conector para Teamup API
        """
        return TeamupConnector(
            api_key=self._api_key
        )
    
    def create_parser(self) -> IEventParser:
        """
        Crea un TeamupEventParser.
        
        Returns:
            TeamupEventParser: Parser para datos de Teamup
        """
        return TeamupEventParser()
    
    def create_importer(self) -> ICalendarImporter:
        """
        Crea un TeamupCalendarImporter con todas sus dependencias.
        
        El importador se crea con el Connector y Parser de esta misma
        factoría, garantizando compatibilidad.
        
        Returns:
            TeamupCalendarImporter: Importador completo configurado
        """
        return TeamupCalendarImporter(
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
            str: "teamup"
        """
        return cls.PROVIDER_TYPE
