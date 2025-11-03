"""Lógica de negocio para integración con servicios externos"""
from datetime import datetime, timezone
import httpx
from bson import ObjectId
from schemas.integration import (
    IntegrationSourceCreate,
    IntegrationSourceResponse,
    GoogleCalendarImportRequest,
    TeamupImportRequest,
    ImportResponse,
    SyncStatusResponse
)
from repositories.integration_repository import IntegrationRepository


class IntegrationService:
    """
    Servicio para manejar la lógica de integración con servicios externos.
    
    Gestiona importación y sincronización de calendarios externos.
    """
    
    def __init__(
        self, 
        integration_repository: IntegrationRepository,
        calendar_service_url: str,
        event_service_url: str
    ):
        """
        Inicializa el servicio de integración.
        
        Args:
            integration_repository: Repository para fuentes de integración
            calendar_service_url: URL del CalendarService
            event_service_url: URL del EventService
        """
        self.integration_repository = integration_repository
        self.calendar_service_url = calendar_service_url
        self.event_service_url = event_service_url
    
    # ==================== CRUD BÁSICO ====================
    
    async def create_source(self, source_data: IntegrationSourceCreate) -> IntegrationSourceResponse:
        """
        Crea una nueva fuente de integración.
        
        Args:
            source_data: Datos de la fuente a crear
            
        Returns:
            IntegrationSourceResponse: Fuente creada
        """
        source_dict = source_data.model_dump()
        source_dict["created_at"] = datetime.now(timezone.utc)
        source_dict["sync_status"] = "pending"
        source_dict["last_sync"] = None
        source_dict["sync_error_message"] = None
        source_dict["basmati_calendar_id"] = None
        
        source_id = await self.integration_repository.create(source_dict)
        source_doc = await self.integration_repository.find_by_id(source_id)
        return self._document_to_response(source_doc)
    
    async def get_source(self, source_id: str) -> IntegrationSourceResponse | None:
        """
        Obtiene una fuente de integración por su ID.
        
        Args:
            source_id: ID de la fuente
            
        Returns:
            IntegrationSourceResponse: Fuente encontrada o None
        """
        source = await self.integration_repository.find_by_id(source_id)
        if source:
            return self._document_to_response(source)
        return None
    
    async def get_user_sources(self, user_external_id: str) -> list[IntegrationSourceResponse]:
        """
        Obtiene todas las fuentes de integración de un usuario (parametrized query 1).
        
        Args:
            user_external_id: ID externo del usuario
            
        Returns:
            list[IntegrationSourceResponse]: Lista de fuentes del usuario
        """
        sources = await self.integration_repository.find_by_user(user_external_id)
        return [self._document_to_response(source) for source in sources]
    
    async def get_sync_status(self, source_id: str) -> SyncStatusResponse | None:
        """
        Obtiene el estado de sincronización de una fuente (parametrized query 2).
        
        Args:
            source_id: ID de la fuente
            
        Returns:
            SyncStatusResponse: Estado de sincronización o None
        """
        source = await self.integration_repository.find_by_id(source_id)
        if not source:
            return None
        
        # Contar eventos sincronizados (si hay calendario vinculado)
        events_synced = 0
        if source.get("basmati_calendar_id"):
            # Aquí se podría llamar al EventService para contar eventos
            # Por ahora devolvemos 0
            pass
        
        return SyncStatusResponse(
            source_id=str(source["_id"]),
            source_type=source["source_type"],
            sync_status=source["sync_status"],
            last_sync=source.get("last_sync"),
            sync_error_message=source.get("sync_error_message"),
            events_synced=events_synced
        )
    
    # ==================== IMPORTACIÓN GOOGLE CALENDAR ====================
    
    async def import_from_google_calendar(
        self, 
        import_request: GoogleCalendarImportRequest
    ) -> ImportResponse:
        """
        Importa calendarios desde Google Calendar.
        
        Proceso:
        1. Autenticar con Google Calendar API usando el access_token
        2. Obtener lista de calendarios del usuario
        3. Para cada calendario:
           a. Verificar si ya está importado
           b. Crear fuente de integración
           c. Llamar a CalendarService para crear calendario en Basmati
           d. Obtener eventos del calendario
           e. Llamar a EventService para crear eventos en Basmati
        
        Args:
            import_request: Datos de importación (token, calendar_ids)
            
        Returns:
            ImportResponse: Resultado de la importación
        """
        imported_sources = []
        errors = []
        
        # TODO: Implementar llamada real a Google Calendar API
        # Por ahora, simulamos la importación
        
        # Simular calendario importado
        try:
            # En producción, aquí iría la lógica de Google Calendar API
            # Para el ejemplo, creamos una fuente simulada
            
            calendar_ids_to_import = import_request.calendar_ids or ["primary"]
            
            for calendar_id in calendar_ids_to_import:
                try:
                    # Verificar si ya existe
                    existing = await self.integration_repository.find_by_external_source_id(
                        import_request.user_external_id,
                        calendar_id
                    )
                    
                    if existing:
                        errors.append(f"El calendario '{calendar_id}' ya fue importado anteriormente (ID fuente: {str(existing['_id'])})")
                        continue
                    
                    # Crear fuente de integración
                    source_data = IntegrationSourceCreate(
                        user_external_id=import_request.user_external_id,
                        source_type="google_calendar",
                        external_source_id=calendar_id,
                        sync_enabled=True
                    )
                    
                    source = await self.create_source(source_data)
                    
                    # Llamar a CalendarService para crear calendario
                    basmati_calendar_id = await self._create_basmati_calendar_from_google(
                        calendar_id,
                        import_request.user_external_id,
                        import_request.google_access_token
                    )
                    
                    # Vincular calendario de Basmati con la fuente
                    if basmati_calendar_id:
                        await self.integration_repository.link_basmati_calendar(
                            str(source.id),
                            basmati_calendar_id
                        )
                        
                        # Actualizar estado de sincronización
                        await self.integration_repository.update_sync_status(
                            str(source.id),
                            "success"
                        )
                        
                        # Obtener fuente actualizada
                        updated_source = await self.get_source(str(source.id))
                        if updated_source:
                            imported_sources.append(updated_source)
                    else:
                        await self.integration_repository.update_sync_status(
                            str(source.id),
                            "error",
                            "No se pudo crear el calendario en Basmati"
                        )
                        errors.append(f"Error al crear calendario de Basmati para '{calendar_id}'")
                
                except Exception as e:
                    errors.append(f"Error al importar '{calendar_id}': {str(e)}")
            
            success = len(imported_sources) > 0
            message = f"Se importaron {len(imported_sources)} calendarios correctamente"
            if errors:
                message += f". {len(errors)} errores encontrados"
            
            return ImportResponse(
                success=success,
                message=message,
                imported_sources=imported_sources,
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
        
        Proceso similar a Google Calendar pero con la API de Teamup.
        
        Args:
            import_request: Datos de importación (API key, calendar_keys)
            
        Returns:
            ImportResponse: Resultado de la importación
        """
        imported_sources = []
        errors = []
        
        try:
            for calendar_key in import_request.calendar_keys:
                try:
                    # Verificar si ya existe
                    existing = await self.integration_repository.find_by_external_source_id(
                        import_request.user_external_id,
                        calendar_key
                    )
                    
                    if existing:
                        errors.append(f"El calendario '{calendar_key}' ya fue importado anteriormente (ID fuente: {str(existing['_id'])})")
                        continue
                    
                    # Crear fuente de integración
                    source_data = IntegrationSourceCreate(
                        user_external_id=import_request.user_external_id,
                        source_type="teamup",
                        external_source_id=calendar_key,
                        sync_enabled=True
                    )
                    
                    source = await self.create_source(source_data)
                    
                    # Llamar a CalendarService para crear calendario
                    basmati_calendar_id = await self._create_basmati_calendar_from_teamup(
                        calendar_key,
                        import_request.user_external_id,
                        import_request.teamup_api_key
                    )
                    
                    if basmati_calendar_id:
                        await self.integration_repository.link_basmati_calendar(
                            str(source.id),
                            basmati_calendar_id
                        )
                        
                        await self.integration_repository.update_sync_status(
                            str(source.id),
                            "success"
                        )
                        
                        updated_source = await self.get_source(str(source.id))
                        if updated_source:
                            imported_sources.append(updated_source)
                    else:
                        await self.integration_repository.update_sync_status(
                            str(source.id),
                            "error",
                            "No se pudo crear el calendario en Basmati"
                        )
                        errors.append(f"Error al crear calendario de Basmati para '{calendar_key}'")
                
                except Exception as e:
                    errors.append(f"Error al importar '{calendar_key}': {str(e)}")
            
            success = len(imported_sources) > 0
            message = f"Se importaron {len(imported_sources)} calendarios correctamente"
            if errors:
                message += f". {len(errors)} errores encontrados"
            
            return ImportResponse(
                success=success,
                message=message,
                imported_sources=imported_sources,
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
    
    # ==================== UTILIDADES ====================
    
    def _document_to_response(self, doc: dict) -> IntegrationSourceResponse:
        """
        Convierte un documento MongoDB a IntegrationSourceResponse.
        
        Args:
            doc: Documento de MongoDB
            
        Returns:
            IntegrationSourceResponse: Schema de respuesta
        """
        return IntegrationSourceResponse(
            id=str(doc["_id"]),
            user_external_id=doc["user_external_id"],
            source_type=doc["source_type"],
            external_source_id=doc["external_source_id"],
            basmati_calendar_id=str(doc["basmati_calendar_id"]) if doc.get("basmati_calendar_id") else None,
            sync_enabled=doc["sync_enabled"],
            last_sync=doc.get("last_sync"),
            sync_status=doc["sync_status"],
            sync_error_message=doc.get("sync_error_message"),
            created_at=doc["created_at"]
        )
