import { Integration_Repository_Interface } from "../../domain/repositories/integration_repository_interface";
import { 
    Google_Import_Request, 
    Teamup_Import_Request, 
    Import_Response,
    Geocode_Response,
    Reverse_Geocode_Response 
} from "../../domain/models/integration_models";
import { api_client } from "../api/axios_client";

export class Http_Integration_Repository implements Integration_Repository_Interface {
    async import_google_calendar(request: Google_Import_Request): Promise<Import_Response> {
        const response = await api_client.post('/v2/integrations/imports/google', request);
        return response.data;
    }

    async import_teamup_calendar(request: Teamup_Import_Request): Promise<Import_Response> {
        const response = await api_client.post('/v2/integrations/imports/teamup', request);
        return response.data;
    }

    /**
     * Geocodifica una dirección usando OpenStreetMap (Nominatim).
     * Convierte texto de dirección en coordenadas geográficas.
     * @param address Dirección a buscar
     * @param limit Número máximo de resultados (default: 5)
     */
    async geocode_address(address: string, limit: number = 5): Promise<Geocode_Response> {
        const response = await api_client.get('/v2/integrations/osm/geocode', {
            params: { address, limit }
        });
        return response.data;
    }

    /**
     * Realiza geocodificación inversa: coordenadas a dirección.
     * @param latitude Latitud
     * @param longitude Longitud
     */
    async reverse_geocode(latitude: number, longitude: number): Promise<Reverse_Geocode_Response> {
        const response = await api_client.get('/v2/integrations/osm/reverse-geocode', {
            params: { latitude, longitude }
        });
        return response.data;
    }

    /**
     * Busca lugares por nombre o tipo.
     * @param query Término de búsqueda
     * @param near_latitude Latitud para priorizar cercanía (opcional)
     * @param near_longitude Longitud para priorizar cercanía (opcional)
     * @param limit Número máximo de resultados (default: 5)
     */
    async search_places(
        query: string, 
        near_latitude?: number, 
        near_longitude?: number, 
        limit: number = 5
    ): Promise<Geocode_Response> {
        const params: Record<string, any> = { query, limit };
        if (near_latitude !== undefined) params.near_latitude = near_latitude;
        if (near_longitude !== undefined) params.near_longitude = near_longitude;
        
        const response = await api_client.get('/v2/integrations/osm/search-places', { params });
        return response.data;
    }
}
