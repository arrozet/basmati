"""
Lógica de negocio para búsqueda avanzada.

Este servicio actúa como agregador, realizando peticiones HTTP a
Calendar Service y Event Service en lugar de acceder directamente a MongoDB.
Respeta el patrón de microservicios donde cada servicio es dueño de sus datos.
"""
import httpx
from schemas.search import CalendarSearchResult, EventSearchResult, CombinedSearchResult


class SearchService:
    """
    Servicio para manejar la lógica de búsqueda avanzada.

    SearchService es un servicio de solo lectura que agrega resultados
    de Calendar Service y Event Service mediante peticiones HTTP.
    No accede directamente a la base de datos - respeta los patrones de microservicios.
    """

    def __init__(
        self,
        calendar_service_url: str,
        event_service_url: str
    ):
        """
        Inicializa el servicio de búsqueda.

        Args:
            calendar_service_url: URL del Calendar Service
            event_service_url: URL del Event Service
        """
        self.calendar_service_url = calendar_service_url
        self.event_service_url = event_service_url
    
    async def search_calendars_by_text(self, query: str) -> list[CalendarSearchResult]:
        """
        Búsqueda full-text en calendarios (parametrized query 1).

        Delega la búsqueda a Calendar Service mediante petición HTTP.

        Args:
            query: Término de búsqueda

        Returns:
            list[CalendarSearchResult]: Lista de calendarios encontrados
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.calendar_service_url}/v1/calendars/search/by-text",
                    params={"query": query}
                )
                if response.status_code == 200:
                    calendars_data = response.json()
                    return [CalendarSearchResult(**cal) for cal in calendars_data]
                return []
        except Exception as e:
            print(f"Error en búsqueda de calendarios: {str(e)}")
            return []
    
    async def search_events_by_text(self, query: str) -> list[EventSearchResult]:
        """
        Búsqueda full-text en eventos (parametrized query 2).

        Delega la búsqueda a Event Service mediante petición HTTP.

        Args:
            query: Término de búsqueda

        Returns:
            list[EventSearchResult]: Lista de eventos encontrados
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.event_service_url}/v1/events/search/by-text",
                    params={"query": query}
                )
                if response.status_code == 200:
                    events_data = response.json()
                    return [EventSearchResult(**event) for event in events_data]
                return []
        except Exception as e:
            print(f"Error en búsqueda de eventos: {str(e)}")
            return []
    
    async def search_combined(self, query: str) -> CombinedSearchResult:
        """
        Búsqueda combinada en calendarios y eventos.

        Realiza búsquedas en ambos servicios y agrega los resultados.

        Args:
            query: Término de búsqueda

        Returns:
            CombinedSearchResult: Calendarios y eventos encontrados
        """
        # Ejecutar búsquedas (ya delegadas a los servicios correspondientes)
        calendars = await self.search_calendars_by_text(query)
        events = await self.search_events_by_text(query)

        return CombinedSearchResult(
            calendars=calendars,
            events=events,
            total_calendars=len(calendars),
            total_events=len(events)
        )
    
    async def get_calendars_by_creator_name(self, creator_name: str) -> list[CalendarSearchResult]:
        """
        Busca calendarios por nombre del creador (relationship query 1).

        Delega la búsqueda a Calendar Service mediante petición HTTP.

        Args:
            creator_name: Nombre o parte del nombre del creador

        Returns:
            list[CalendarSearchResult]: Calendarios creados por usuarios con ese nombre
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.calendar_service_url}/v1/calendars/search/by-creator-name",
                    params={"creator_name": creator_name}
                )
                if response.status_code == 200:
                    calendars_data = response.json()
                    return [CalendarSearchResult(**cal) for cal in calendars_data]
                return []
        except Exception as e:
            print(f"Error en búsqueda de calendarios por creador: {str(e)}")
            return []
    
    async def get_events_by_calendar_title(self, calendar_title: str) -> list[EventSearchResult]:
        """
        Busca eventos por título del calendario (relationship query 2).

        Delega la búsqueda a Event Service mediante petición HTTP.

        Args:
            calendar_title: Título o parte del título del calendario

        Returns:
            list[EventSearchResult]: Eventos del calendario con ese título
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.event_service_url}/v1/events/search/by-calendar-title",
                    params={"calendar_title": calendar_title}
                )
                if response.status_code == 200:
                    events_data = response.json()
                    return [EventSearchResult(**event) for event in events_data]
                return []
        except Exception as e:
            print(f"Error en búsqueda de eventos por título de calendario: {str(e)}")
            return []
    
    async def search_events_by_location(self, location_query: str) -> list[EventSearchResult]:
        """
        Busca eventos por ubicación.

        Delega la búsqueda a Event Service mediante petición HTTP.

        Args:
            location_query: Término de búsqueda para la ubicación

        Returns:
            list[EventSearchResult]: Eventos en esa ubicación
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.event_service_url}/v1/events/search/by-location",
                    params={"location_query": location_query}
                )
                if response.status_code == 200:
                    events_data = response.json()
                    return [EventSearchResult(**event) for event in events_data]
                return []
        except Exception as e:
            print(f"Error en búsqueda de eventos por ubicación: {str(e)}")
            return []
