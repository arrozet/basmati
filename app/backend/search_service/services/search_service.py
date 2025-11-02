"""
Lógica de negocio para búsqueda avanzada.

Este servicio NO tiene estado propio ni repositories.
Todas las consultas se realizan directamente contra las colecciones
'calendars' y 'events' de MongoDB usando motor.
"""
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.search import CalendarSearchResult, EventSearchResult, CombinedSearchResult


class SearchService:
    """
    Servicio para manejar la lógica de búsqueda avanzada.
    
    SearchService es un servicio de solo lectura que consulta directamente
    las colecciones de calendarios y eventos sin modificar datos.
    No tiene models ni repositories propios - actúa como agregador de consultas.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Inicializa el servicio de búsqueda.
        
        Args:
            database: Instancia de la base de datos MongoDB
        """
        self.db = database
        self.calendars_collection = database["calendars"]
        self.events_collection = database["events"]
    
    async def search_calendars_by_text(self, query: str) -> list[CalendarSearchResult]:
        """
        Búsqueda full-text en calendarios (parametrized query 1).
        
        Busca en los campos: title, description y keywords del calendario.
        Utiliza expresiones regulares para búsqueda case-insensitive.
        
        Args:
            query: Término de búsqueda
            
        Returns:
            list[CalendarSearchResult]: Lista de calendarios encontrados
            
        Ejemplo:
            Si query="universidad", encontrará calendarios con:
            - title: "Eventos Universidad"
            - keywords: ["universidad", "educacion"]
            - description: "Calendario de la Universidad de Sevilla"
        """
        # Búsqueda case-insensitive con regex en múltiples campos
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"keywords": {"$regex": query, "$options": "i"}}
            ]
        }
        
        cursor = self.calendars_collection.find(search_filter)
        calendars = await cursor.to_list(length=100)  # Limitar a 100 resultados
        
        return [self._calendar_document_to_result(cal) for cal in calendars]
    
    async def search_events_by_text(self, query: str) -> list[EventSearchResult]:
        """
        Búsqueda full-text en eventos (parametrized query 2).
        
        Busca en los campos: title, description, location.address y location.place_name.
        Utiliza expresiones regulares para búsqueda case-insensitive.
        
        Args:
            query: Término de búsqueda
            
        Returns:
            list[EventSearchResult]: Lista de eventos encontrados
            
        Ejemplo:
            Si query="conferencia", encontrará eventos con:
            - title: "Conferencia de IA"
            - description: "Conferencia sobre machine learning"
            - location.place_name: "Centro de Conferencias"
        """
        # Búsqueda case-insensitive con regex en múltiples campos
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"location.address": {"$regex": query, "$options": "i"}},
                {"location.place_name": {"$regex": query, "$options": "i"}}
            ]
        }
        
        cursor = self.events_collection.find(search_filter)
        events = await cursor.to_list(length=100)  # Limitar a 100 resultados
        
        return [self._event_document_to_result(event) for event in events]
    
    async def search_combined(self, query: str) -> CombinedSearchResult:
        """
        Búsqueda combinada en calendarios y eventos.
        
        Realiza búsquedas paralelas en ambas colecciones y devuelve
        un resultado unificado con ambos tipos de resultados.
        
        Args:
            query: Término de búsqueda
            
        Returns:
            CombinedSearchResult: Calendarios y eventos encontrados
            
        Ejemplo:
            Si query="universidad", devolverá:
            - calendars: todos los calendarios que contengan "universidad"
            - events: todos los eventos que contengan "universidad"
        """
        # Ejecutar búsquedas en paralelo (await para ambas)
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
        
        Utiliza el campo denormalizado creator_display_name para búsqueda
        eficiente sin necesidad de join con la colección users.
        
        Args:
            creator_name: Nombre o parte del nombre del creador
            
        Returns:
            list[CalendarSearchResult]: Calendarios creados por usuarios con ese nombre
            
        Ejemplo:
            Si creator_name="Juan", encontrará calendarios de:
            - "Juan Pérez"
            - "María Juan"
            - "Juan Carlos Rodríguez"
        """
        search_filter = {
            "creator_display_name": {"$regex": creator_name, "$options": "i"}
        }
        
        cursor = self.calendars_collection.find(search_filter)
        calendars = await cursor.to_list(length=100)
        
        return [self._calendar_document_to_result(cal) for cal in calendars]
    
    async def get_events_by_calendar_title(self, calendar_title: str) -> list[EventSearchResult]:
        """
        Busca eventos por título del calendario (relationship query 2).
        
        Utiliza el campo denormalizado calendar_title para búsqueda eficiente
        sin necesidad de join con la colección calendars.
        
        Args:
            calendar_title: Título o parte del título del calendario
            
        Returns:
            list[EventSearchResult]: Eventos del calendario con ese título
            
        Ejemplo:
            Si calendar_title="Universidad", encontrará eventos de calendarios como:
            - "Eventos Universidad de Sevilla"
            - "Universidad - Deportes"
            - "Calendario Universidad"
        """
        search_filter = {
            "calendar_title": {"$regex": calendar_title, "$options": "i"}
        }
        
        cursor = self.events_collection.find(search_filter)
        events = await cursor.to_list(length=100)
        
        return [self._event_document_to_result(event) for event in events]
    
    async def search_events_by_location(self, location_query: str) -> list[EventSearchResult]:
        """
        Busca eventos por ubicación.
        
        Busca en los campos address y place_name del subdocumento location.
        Útil para encontrar eventos en una ciudad, edificio o lugar específico.
        
        Args:
            location_query: Término de búsqueda para la ubicación
            
        Returns:
            list[EventSearchResult]: Eventos en esa ubicación
            
        Ejemplo:
            Si location_query="Sevilla", encontrará eventos con:
            - location.address: "Calle Real, Sevilla"
            - location.place_name: "Universidad de Sevilla"
        """
        search_filter = {
            "$or": [
                {"location.address": {"$regex": location_query, "$options": "i"}},
                {"location.place_name": {"$regex": location_query, "$options": "i"}}
            ]
        }
        
        cursor = self.events_collection.find(search_filter)
        events = await cursor.to_list(length=100)
        
        return [self._event_document_to_result(event) for event in events]
    
    def _calendar_document_to_result(self, document: dict) -> CalendarSearchResult:
        """
        Convierte un documento de MongoDB a CalendarSearchResult.
        
        Args:
            document: Documento de la colección calendars
            
        Returns:
            CalendarSearchResult: Schema de resultado de búsqueda
        """
        document["id"] = str(document["_id"])
        return CalendarSearchResult(**document)
    
    def _event_document_to_result(self, document: dict) -> EventSearchResult:
        """
        Convierte un documento de MongoDB a EventSearchResult.
        
        Args:
            document: Documento de la colección events
            
        Returns:
            EventSearchResult: Schema de resultado de búsqueda
        """
        document["id"] = str(document["_id"])
        document["calendar_id"] = str(document["calendar_id"])
        return EventSearchResult(**document)
