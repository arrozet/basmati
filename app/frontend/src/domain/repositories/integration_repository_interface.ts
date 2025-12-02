import { 
    Google_Import_Request, 
    Teamup_Import_Request, 
    Import_Response,
    Geocode_Response,
    Reverse_Geocode_Response
} from "../models/integration_models";

export interface Integration_Repository_Interface {
    import_google_calendar(request: Google_Import_Request): Promise<Import_Response>;
    import_teamup_calendar(request: Teamup_Import_Request): Promise<Import_Response>;
    
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
