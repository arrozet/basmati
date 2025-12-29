import { 
    Google_Import_Request, 
    Teamup_Import_Request, 
    Import_Response,
    Geocode_Response,
    Reverse_Geocode_Response,
    // V3 Models
    Google_Import_Request_V3,
    Teamup_Import_Request_V3,
    Generic_Import_Request_V3,
    Import_Response_V3,
    Provider_Capabilities
} from "../models/integration_models";

export interface Integration_Repository_Interface {
    // ========================================================================
    // V2 Methods (Legacy)
    // ========================================================================
    import_google_calendar(request: Google_Import_Request): Promise<Import_Response>;
    import_teamup_calendar(request: Teamup_Import_Request): Promise<Import_Response>;
    
    // ========================================================================
    // V3 Methods (Abstract Factory Pattern)
    // ========================================================================
    
    /**
     * Obtiene la lista de proveedores soportados con sus capacidades.
     */
    get_providers(): Promise<Provider_Capabilities[]>;
    
    /**
     * Obtiene información de un proveedor específico.
     * @param provider Identificador del proveedor (google, teamup)
     */
    get_provider_info(provider: string): Promise<Provider_Capabilities>;
    
    /**
     * Importa calendarios desde Google Calendar usando API V3.
     * @param request Datos de importación con token OAuth2
     */
    import_google_calendar_v3(request: Google_Import_Request_V3): Promise<Import_Response_V3>;
    
    /**
     * Importa calendarios desde Teamup usando API V3.
     * @param request Datos de importación con API Key opcional
     */
    import_teamup_calendar_v3(request: Teamup_Import_Request_V3): Promise<Import_Response_V3>;
    
    /**
     * Importa calendarios usando el endpoint genérico V3.
     * @param request Request con proveedor y credenciales
     */
    import_calendars_v3(request: Generic_Import_Request_V3): Promise<Import_Response_V3>;
    
    // ========================================================================
    // OpenStreetMap Methods
    // ========================================================================
    
    /**
     * Geocodifica una dirección usando OpenStreetMap.
     * @param address Dirección a buscar
     * @param limit Número máximo de resultados
     */
    geocode_address(address: string, limit?: number): Promise<Geocode_Response>;
    
    /**
     * Realiza geocodificación inversa: coordenadas a dirección.
     * @param latitude Latitud
     * @param longitude Longitud
     */
    reverse_geocode(latitude: number, longitude: number): Promise<Reverse_Geocode_Response>;
    
    /**
     * Busca lugares por nombre o tipo.
     * @param query Término de búsqueda
     * @param near_latitude Latitud para priorizar cercanía (opcional)
     * @param near_longitude Longitud para priorizar cercanía (opcional)
     * @param limit Número máximo de resultados
     */
    search_places(
        query: string, 
        near_latitude?: number, 
        near_longitude?: number, 
        limit?: number
    ): Promise<Geocode_Response>;
}
