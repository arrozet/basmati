"""Lógica de negocio para calendarios"""
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
import httpx
from schemas.calendar import CalendarCreate, CalendarUpdate, CalendarResponse, CalendarHierarchy
from repositories.calendar_repository import CalendarRepository
from core.config import settings
from core.interface import ICalendarService


from core.interface import ICalendarService

class CalendarService(ICalendarService):
    """
    Servicio para manejar la lógica de negocio de calendarios.
    
    Delega acceso a BD al CalendarRepository.
    """
    
    def __init__(self, calendar_repository: CalendarRepository):
        """
        Inicializa el servicio de calendarios.
        
        Args:
            calendar_repository: Repository para calendarios
        """
        self.calendar_repository = calendar_repository
    
    async def get_all_calendars(self, limit: int = 200) -> list[CalendarResponse]:
        """
        Obtiene todos los calendarios del sistema.
        
        Args:
            limit: Número máximo de calendarios a devolver
            
        Returns:
            list[CalendarResponse]: Lista de todos los calendarios
        """
        calendars = await self.calendar_repository.find_all(limit)
        return [self._document_to_response(calendar) for calendar in calendars]
        
    async def create_calendar(self, calendar_data: Any) -> CalendarResponse:
        """
        Crea un nuevo calendario.
        
        Lógica:
        - Crea el calendario con fecha de creación
        - Si tiene parent_calendar_id, construye el path jerárquico
        
        Args:
            calendar_data: Datos del calendario a crear
            
        Returns:
            CalendarResponse: Calendario creado
            
        Raises:
            ValueError: Si el calendario padre no existe
        """
        # Preparar datos
        if not isinstance(calendar_data, CalendarCreate) and hasattr(calendar_data, 'model_dump'):
            calendar_dict = calendar_data.model_dump()
        else:
            calendar_dict = calendar_data.model_dump() if hasattr(calendar_data, 'model_dump') else dict(calendar_data)

        calendar_dict["created_at"] = datetime.now(timezone.utc)
        calendar_dict["updated_at"] = datetime.now(timezone.utc)
        calendar_dict["subscriber_count"] = 0
        
        # Manejar jerarquía si tiene calendario padre
        parent_id = getattr(calendar_data, 'parent_calendar_id', None)
        if parent_id:
            # Verificar que el padre exista
            parent = await self.calendar_repository.find_by_id(parent_id)
            if not parent:
                raise ValueError(f"El calendario padre con ID '{parent_id}' no existe")
            
            # Convertir parent_calendar_id a ObjectId
            calendar_dict["parent_calendar_id"] = ObjectId(parent_id)
            
            # Construir path: path del padre + ID del padre
            parent_path = parent.get("path", [])
            calendar_dict["path"] = parent_path + [ObjectId(parent_id)]
        else:
            calendar_dict["parent_calendar_id"] = None
            calendar_dict["path"] = []
        
        # Delegar a repository (valida contra CalendarModel)
        try:
            calendar_id = await self.calendar_repository.create(calendar_dict)
            calendar_doc = await self.calendar_repository.find_by_id(calendar_id)
            if not calendar_doc:
                raise ValueError("No se pudo recuperar el calendario creado")
            return self._document_to_response(calendar_doc)
        except ValueError as e:
            raise ValueError(f"Error al crear calendario: {str(e)}")
    
    async def get_calendar(self, calendar_id: str) -> CalendarResponse | None:
        """
        Obtiene un calendario por su ID de MongoDB.
        
        Args:
            calendar_id: ID del calendario (_id de MongoDB)
            
        Returns:
            CalendarResponse: Calendario encontrado o None
        """
        calendar = await self.calendar_repository.find_by_id(calendar_id)
        if calendar:
            return self._document_to_response(calendar)
        return None
    
    async def update_calendar(self, calendar_id: str, calendar_data: Any) -> CalendarResponse | None:
        """
        Actualiza un calendario existente.
        
        Args:
            calendar_id: ID del calendario
            calendar_data: Datos a actualizar
            
        Returns:
            CalendarResponse: Calendario actualizado o None si no existe
        """
        update_dict = calendar_data.model_dump(exclude_unset=True) if hasattr(calendar_data, 'model_dump') else dict(calendar_data)
        if not update_dict:
            return await self.get_calendar(calendar_id)
        
        # Delegar a repository (valida contra CalendarModel)
        try:
            result = await self.calendar_repository.update(calendar_id, update_dict)
        except ValueError as e:
            raise ValueError(f"Error al actualizar calendario: {str(e)}")
        
        if result:
            return self._document_to_response(result)
        return None
    
    async def delete_calendar(self, calendar_id: str) -> bool:
        """
        Elimina un calendario.
        
        Args:
            calendar_id: ID del calendario
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        return await self.calendar_repository.delete(calendar_id)
    
    async def search_by_creator(self, creator_external_id: str) -> list[CalendarResponse]:
        """
        Busca calendarios por creador (parametrized query 1).
        
        Args:
            creator_external_id: ID del creador (external_id del usuario)
            
        Returns:
            list[CalendarResponse]: Lista de calendarios encontrados
        """
        calendars = await self.calendar_repository.find_by_creator(creator_external_id)
        return [self._document_to_response(calendar) for calendar in calendars]
    
    async def search_by_keywords(self, keyword: str) -> list[CalendarResponse]:
        """
        Busca calendarios por keywords (parametrized query 2).
        
        Args:
            keyword: Palabra clave a buscar
            
        Returns:
            list[CalendarResponse]: Lista de calendarios encontrados
        """
        calendars = await self.calendar_repository.find_by_keywords(keyword)
        return [self._document_to_response(calendar) for calendar in calendars]
    
    async def search_by_visibility(self, visibility: str) -> list[CalendarResponse]:
        """
        Busca calendarios por visibilidad.

        Args:
            visibility: Visibilidad del calendario ("public", "private", "unlisted")

        Returns:
            list[CalendarResponse]: Lista de calendarios encontrados
        """
        calendars = await self.calendar_repository.find_by_visibility(visibility)
        return [self._document_to_response(calendar) for calendar in calendars]

    async def search_by_text(self, query: str) -> list[CalendarResponse]:
        """
        Búsqueda full-text en calendarios.

        Busca en los campos: title, description y keywords del calendario.

        Args:
            query: Término de búsqueda

        Returns:
            list[CalendarResponse]: Lista de calendarios encontrados
        """
        calendars = await self.calendar_repository.search_by_text(query)
        return [self._document_to_response(calendar) for calendar in calendars]

    async def search_by_creator_name(self, creator_name: str) -> list[CalendarResponse]:
        """
        Busca calendarios por nombre del creador.

        Args:
            creator_name: Nombre o parte del nombre del creador

        Returns:
            list[CalendarResponse]: Calendarios creados por usuarios con ese nombre
        """
        calendars = await self.calendar_repository.search_by_creator_name(creator_name)
        return [self._document_to_response(calendar) for calendar in calendars]

    async def get_children(self, calendar_id: str) -> list[CalendarResponse]:
        """
        Obtiene los calendarios hijos directos (relationship query 1).
        
        Args:
            calendar_id: ID del calendario padre
            
        Returns:
            list[CalendarResponse]: Lista de calendarios hijos
        """
        children = await self.calendar_repository.find_children(calendar_id)
        return [self._document_to_response(calendar) for calendar in children]
    
    async def get_hierarchy(self, calendar_id: str) -> CalendarHierarchy | None:
        """
        Obtiene toda la jerarquía de calendarios (relationship query 2).
        
        Usa find_hierarchy() del repository (1 sola query eficiente) y 
        construye el árbol jerárquico en memoria.
        
        Args:
            calendar_id: ID del calendario raíz
            
        Returns:
            CalendarHierarchy: Jerarquía completa de calendarios o None si no existe
        """
        # Obtener todos los calendarios de la jerarquía con UNA sola query
        all_calendars = await self.calendar_repository.find_hierarchy(calendar_id)
        
        if not all_calendars:
            return None
        
        # El primer calendario es la raíz
        root_calendar = all_calendars[0]
        
        # Construir árbol jerárquico en memoria
        return self._build_hierarchy_from_list(root_calendar, all_calendars)
    
    def _build_hierarchy_from_list(self, calendar_doc: dict, all_calendars: list[dict]) -> CalendarHierarchy:
        """
        Construye la jerarquía de calendarios en memoria a partir de una lista plana.
        
        Este método es más eficiente porque no hace queries adicionales a MongoDB.
        Solo trabaja con los datos ya obtenidos en memoria.
        
        Args:
            calendar_doc: Documento del calendario actual
            all_calendars: Lista de todos los calendarios de la jerarquía
            
        Returns:
            CalendarHierarchy: Jerarquía con el calendario y sus hijos
        """
        calendar_response = self._document_to_response(calendar_doc)
        current_id = calendar_doc["_id"]
        
        # Encontrar hijos directos (aquellos cuyo parent_calendar_id es el actual)
        children_docs = [
            cal for cal in all_calendars 
            if cal.get("parent_calendar_id") == current_id
        ]
        
        # Construir jerarquía recursiva para cada hijo
        children_hierarchy = [
            self._build_hierarchy_from_list(child, all_calendars)
            for child in children_docs
        ]
        
        return CalendarHierarchy(
            calendar=calendar_response,
            children=children_hierarchy
        )
    
    def _document_to_response(self, document: dict) -> CalendarResponse:
        """
        Convierte un documento de MongoDB a CalendarResponse.
        
        Args:
            document: Documento de MongoDB
            
        Returns:
            CalendarResponse: Schema de respuesta
        """
        document["id"] = str(document["_id"])
        
        # Convertir ObjectId de parent_calendar_id a string
        if "parent_calendar_id" in document and document["parent_calendar_id"]:
            document["parent_calendar_id"] = str(document["parent_calendar_id"])
        
        # Convertir ObjectIds del path a strings
        if "path" in document:
            document["path"] = [str(obj_id) for obj_id in document.get("path", [])]
        
        return CalendarResponse(**document)

    # ==================== PERMISOS ====================

    async def can_view_calendar(self, calendar_id: str, user_id: str) -> bool:
        """
        Verifica si un usuario puede ver un calendario.
        
        Reglas:
        - Calendarios públicos: todos pueden ver
        - Calendarios unlisted: todos pueden ver (si tienen el enlace)
        - Calendarios privados: solo el creador puede ver
        
        Args:
            calendar_id: ID del calendario
            user_id: ID externo del usuario
            
        Returns:
            bool: True si el usuario puede ver el calendario
        """
        calendar = await self.calendar_repository.find_by_id(calendar_id)
        if not calendar:
            return False
        
        visibility = calendar.get("visibility", "public")
        
        # Public y unlisted: todos pueden ver
        if visibility in ["public", "unlisted"]:
            return True
        
        # Private: solo el creador
        return calendar.get("creator_external_id") == user_id

    async def can_edit_calendar(self, calendar_id: str, user_id: str) -> bool:
        """
        Verifica si un usuario puede editar un calendario.
        
        Reglas:
        - Solo el creador puede editar, independientemente de la visibilidad
        
        Args:
            calendar_id: ID del calendario
            user_id: ID externo del usuario
            
        Returns:
            bool: True si el usuario puede editar el calendario
        """
        calendar = await self.calendar_repository.find_by_id(calendar_id)
        if not calendar:
            return False
        
        return calendar.get("creator_external_id") == user_id

    # ==================== COMENTARIOS ====================

    async def add_comment(self, calendar_id: str, comment_data: Any) -> Any:
        """
        Agrega un comentario a un calendario.
        
        Args:
            calendar_id: ID del calendario
            comment_data: Datos del comentario (CommentCreate)
            
        Returns:
            CalendarComment: Comentario agregado o None si el calendario no existe
        """
        from schemas.calendar import CalendarComment, CommentCreate
        from models.calendar import CalendarCommentModel
        
        # Convertir a dict
        comment_dict = comment_data.model_dump() if hasattr(comment_data, 'model_dump') else dict(comment_data)
        
        # Agregar timestamp
        comment_dict["created_at"] = datetime.now(timezone.utc)
        comment_dict["_id"] = ObjectId()
        
        # Agregar al calendario
        result = await self.calendar_repository.add_comment(calendar_id, comment_dict)
        
        if result:
            # Convertir a CalendarComment para respuesta
            result["id"] = str(result["_id"])
            return CalendarComment(**result)
        
        return None


    async def delete_calendar_recursive(self, calendar_id: str, event_service_url: str | None = None) -> dict:
        """
        Elimina un calendario y todos sus subcalendarios recursivamente,
        junto con todos los eventos asociados.
        
        Orden de eliminación:
        1. Obtener la jerarquía completa del calendario
        2. Eliminar eventos de cada calendario (empezando por los hijos más profundos)
        3. Eliminar subcalendarios (de hijos a padres)
        4. Eliminar el calendario raíz
        
        Args:
            calendar_id: ID del calendario a eliminar
            event_service_url: URL del servicio de eventos (usa settings si no se proporciona)
            
        Returns:
            dict: Resumen de la eliminación con contadores
            
        Raises:
            ValueError: Si el calendario no existe
        """
        # Verificar que el calendario existe
        calendar = await self.calendar_repository.find_by_id(calendar_id)
        if not calendar:
            raise ValueError(f"El calendario con ID '{calendar_id}' no existe")
        
        # URL del event service
        event_url = event_service_url or settings.event_service_url
        
        # Obtener toda la jerarquía del calendario
        all_calendars = await self.calendar_repository.find_hierarchy(calendar_id)
        
        # Contadores para el resumen
        total_events_deleted = 0
        calendars_deleted = 0
        errors = []
        
        # Ordenar calendarios por profundidad (hijos primero) basándose en la longitud del path
        # Los que tienen path más largo son los más profundos
        all_calendars_sorted = sorted(
            all_calendars, 
            key=lambda c: len(c.get("path", [])), 
            reverse=True
        )
        
        # Eliminar eventos de cada calendario (usando el endpoint V2 del event_service)
        async with httpx.AsyncClient(timeout=30.0) as client:
            for cal in all_calendars_sorted:
                cal_id = str(cal["_id"])
                try:
                    # Llamar al endpoint V2 de event_service para eliminar eventos
                    response = await client.delete(
                        f"{event_url}/v2/events/by-calendar/{cal_id}"
                    )
                    if response.status_code == 200:
                        result = response.json()
                        total_events_deleted += result.get("deleted_count", 0)
                    else:
                        # Si el evento no existe o hay error, continuamos
                        errors.append(f"Error eliminando eventos del calendario {cal_id}: {response.status_code}")
                except Exception as exc:
                    errors.append(f"Error de conexión al eliminar eventos del calendario {cal_id}: {str(exc)}")
        
        # Eliminar calendarios (de hijos a padres)
        for cal in all_calendars_sorted:
            cal_id = str(cal["_id"])
            try:
                deleted = await self.calendar_repository.delete(cal_id)
                if deleted:
                    calendars_deleted += 1
            except Exception as exc:
                errors.append(f"Error eliminando calendario {cal_id}: {str(exc)}")
        
        return {
            "message": f"Calendario '{calendar.get('title', calendar_id)}' eliminado recursivamente",
            "calendar_id": calendar_id,
            "calendars_deleted": calendars_deleted,
            "events_deleted": total_events_deleted,
            "errors": errors if errors else None
        }
