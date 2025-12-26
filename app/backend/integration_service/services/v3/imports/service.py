"""
Import Service V3 - Servicio principal de importación.

Este servicio actúa como orquestador, utilizando el patrón Abstract Factory
para instanciar los componentes correctos según el proveedor seleccionado.
"""

import logging
from typing import Optional, Type

from services.v3.imports.interfaces import IImportFactory
from services.v3.imports.schemas import (
    ProviderType,
    GenericImportRequest,
    GoogleCalendarImportRequestV3,
    TeamupImportRequestV3,
    ImportResponseV3,
    ImportedCalendarV3,
    PROVIDER_CAPABILITIES,
)
from services.v3.imports.google.factory import GoogleImportFactory
from services.v3.imports.teamup.factory import TeamupImportFactory

logger = logging.getLogger(__name__)


class ProviderNotSupportedError(Exception):
    """Error cuando se solicita un proveedor no soportado."""
    pass


class ImportServiceV3:
    """
    Servicio principal de importación V3.
    
    Utiliza el patrón Abstract Factory para crear los componentes
    adecuados según el proveedor seleccionado por el usuario.
    
    Responsabilidades:
    - Validar requests de importación
    - Instanciar la factoría correcta según el proveedor
    - Orquestar la importación de múltiples calendarios
    - Agregar resultados y construir respuesta
    
    Ejemplo de uso:
        service = ImportServiceV3(
            calendar_service_url="http://calendar-service:8003",
            event_service_url="http://event-service:8002"
        )
        
        # Importar desde Google
        response = await service.import_from_google(request)
        
        # Importar desde Teamup
        response = await service.import_from_teamup(request)
        
        # Importación genérica
        response = await service.import_calendars(generic_request)
    """
    
    # Registro de factorías disponibles
    _FACTORY_REGISTRY: dict[ProviderType, Type[IImportFactory]] = {
        ProviderType.GOOGLE: GoogleImportFactory,
        ProviderType.TEAMUP: TeamupImportFactory,
    }
    
    def __init__(
        self,
        calendar_service_url: str,
        event_service_url: str,
        default_teamup_api_key: Optional[str] = None,
    ):
        """
        Inicializa el servicio de importación.
        
        Args:
            calendar_service_url: URL del CalendarService de Basmati
            event_service_url: URL del EventService de Basmati
            default_teamup_api_key: API Key de Teamup por defecto (del .env)
        """
        self._calendar_service_url = calendar_service_url
        self._event_service_url = event_service_url
        self._default_teamup_api_key = default_teamup_api_key
    
    # =========================================================================
    # MÉTODOS PÚBLICOS - IMPORTACIÓN POR PROVEEDOR
    # =========================================================================
    
    async def import_from_google(
        self,
        request: GoogleCalendarImportRequestV3
    ) -> ImportResponseV3:
        """
        Importa calendarios desde Google Calendar.
        
        Args:
            request: Datos de importación con token OAuth2
            
        Returns:
            ImportResponseV3: Resultado de la importación
        """
        logger.info(
            f"[V3] Iniciando importación Google Calendar para usuario: "
            f"{request.user_external_id}"
        )
        
        # Crear factoría de Google
        factory = GoogleImportFactory(
            access_token=request.access_token,
            calendar_service_url=self._calendar_service_url,
            event_service_url=self._event_service_url,
        )
        
        return await self._execute_import(
            factory=factory,
            calendar_ids=request.calendar_ids,
            user_external_id=request.user_external_id,
            provider_type=ProviderType.GOOGLE,
        )
    
    async def import_from_teamup(
        self,
        request: TeamupImportRequestV3
    ) -> ImportResponseV3:
        """
        Importa calendarios desde Teamup.
        
        Args:
            request: Datos de importación con API Key opcional
            
        Returns:
            ImportResponseV3: Resultado de la importación
        """
        logger.info(
            f"[V3] Iniciando importación Teamup para usuario: "
            f"{request.user_external_id}"
        )
        
        # Determinar API Key (request o fallback a .env)
        api_key = request.api_key or self._default_teamup_api_key
        
        if not api_key:
            return ImportResponseV3(
                success=False,
                message="API Key de Teamup no proporcionada y no configurada en el servidor",
                provider=ProviderType.TEAMUP.value,
                errors=["Teamup API Key requerida pero no encontrada"]
            )
        
        # Crear factoría de Teamup
        factory = TeamupImportFactory(
            api_key=api_key,
            calendar_service_url=self._calendar_service_url,
            event_service_url=self._event_service_url,
        )
        
        return await self._execute_import(
            factory=factory,
            calendar_ids=request.calendar_ids,
            user_external_id=request.user_external_id,
            provider_type=ProviderType.TEAMUP,
        )
    
    async def import_calendars(
        self,
        request: GenericImportRequest
    ) -> ImportResponseV3:
        """
        Importa calendarios de cualquier proveedor soportado (método genérico).
        
        Args:
            request: Request genérico con proveedor y credenciales
            
        Returns:
            ImportResponseV3: Resultado de la importación
            
        Raises:
            ProviderNotSupportedError: Si el proveedor no está soportado
        """
        logger.info(
            f"[V3] Importación genérica - Proveedor: {request.provider}, "
            f"Usuario: {request.user_external_id}"
        )
        
        # Validar proveedor
        if request.provider not in self._FACTORY_REGISTRY:
            raise ProviderNotSupportedError(
                f"Proveedor '{request.provider}' no soportado. "
                f"Proveedores disponibles: {list(self._FACTORY_REGISTRY.keys())}"
            )
        
        # Crear request específico y delegar
        if request.provider == ProviderType.GOOGLE:
            access_token = request.credentials.get("access_token")
            if not access_token:
                return ImportResponseV3(
                    success=False,
                    message="Token de acceso de Google requerido",
                    provider=request.provider.value,
                    errors=["Falta 'access_token' en credentials"]
                )
            
            google_request = GoogleCalendarImportRequestV3(
                user_external_id=request.user_external_id,
                calendar_ids=request.calendar_ids,
                access_token=access_token,
            )
            return await self.import_from_google(google_request)
        
        elif request.provider == ProviderType.TEAMUP:
            teamup_request = TeamupImportRequestV3(
                user_external_id=request.user_external_id,
                calendar_ids=request.calendar_ids,
                api_key=request.credentials.get("api_key"),
            )
            return await self.import_from_teamup(teamup_request)
        
        # No debería llegar aquí
        raise ProviderNotSupportedError(f"Proveedor '{request.provider}' no implementado")
    
    # =========================================================================
    # MÉTODOS DE INFORMACIÓN
    # =========================================================================
    
    @classmethod
    def get_supported_providers(cls) -> list[dict]:
        """
        Retorna información sobre los proveedores soportados.
        
        Returns:
            list: Lista de proveedores con sus capacidades
        """
        return [
            cap.model_dump()
            for cap in PROVIDER_CAPABILITIES.values()
        ]
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """
        Verifica si un proveedor está soportado.
        
        Args:
            provider: Nombre del proveedor
            
        Returns:
            bool: True si está soportado
        """
        try:
            provider_type = ProviderType(provider.lower())
            return provider_type in cls._FACTORY_REGISTRY
        except ValueError:
            return False
    
    # =========================================================================
    # MÉTODOS PRIVADOS
    # =========================================================================
    
    async def _execute_import(
        self,
        factory: IImportFactory,
        calendar_ids: list[str],
        user_external_id: str,
        provider_type: ProviderType,
    ) -> ImportResponseV3:
        """
        Ejecuta la importación usando la factoría proporcionada.
        
        Args:
            factory: Factoría configurada para el proveedor
            calendar_ids: Lista de IDs de calendarios a importar
            user_external_id: ID del usuario
            provider_type: Tipo de proveedor para el response
            
        Returns:
            ImportResponseV3: Resultado agregado de todas las importaciones
        """
        imported_calendars: list[ImportedCalendarV3] = []
        errors: list[str] = []
        total_events_imported = 0
        total_events_failed = 0
        
        # Crear importador
        importer = factory.create_importer()
        
        # Importar cada calendario
        for calendar_id in calendar_ids:
            try:
                logger.info(f"Importando calendario: {calendar_id}")
                
                result = await importer.import_calendar(
                    external_calendar_id=calendar_id,
                    user_external_id=user_external_id
                )
                
                if result.success and result.basmati_calendar_id:
                    imported_calendars.append(
                        ImportedCalendarV3(
                            external_id=calendar_id,
                            basmati_calendar_id=result.basmati_calendar_id,
                            events_imported=result.events_imported,
                            events_failed=result.events_failed,
                        )
                    )
                    total_events_imported += result.events_imported
                    total_events_failed += result.events_failed
                    
                    logger.info(
                        f"✅ Calendario '{calendar_id}' importado: "
                        f"{result.events_imported} eventos"
                    )
                else:
                    error_msg = result.error_message or f"Error importando '{calendar_id}'"
                    errors.append(error_msg)
                    logger.error(f"❌ Error en calendario '{calendar_id}': {error_msg}")
                    
            except Exception as e:
                error_msg = f"Excepción importando '{calendar_id}': {str(e)}"
                errors.append(error_msg)
                logger.exception(error_msg)
        
        # Construir respuesta
        success = len(imported_calendars) > 0
        
        if success:
            message = (
                f"Importación completada: {len(imported_calendars)} calendario(s), "
                f"{total_events_imported} evento(s)"
            )
            if errors:
                message += f". {len(errors)} error(es) encontrado(s)"
        else:
            message = "No se pudo importar ningún calendario"
        
        return ImportResponseV3(
            success=success,
            message=message,
            provider=provider_type.value,
            imported_calendars=imported_calendars,
            errors=errors,
            total_events_imported=total_events_imported,
            total_events_failed=total_events_failed,
        )
