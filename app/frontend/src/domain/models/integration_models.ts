export interface Google_Import_Request {
    user_external_id: string;
    google_access_token: string;
    calendar_ids?: string[];
}

export interface Teamup_Import_Request {
    user_external_id: string;
    calendar_keys: string[];
    teamup_api_key?: string;
}

export interface Import_Response {
    success: boolean;
    message: string;
    imported_sources: string[];
}

/**
 * Modelos para integración con OpenStreetMap
 */
export interface Location_Result {
    address: string;
    latitude: number;
    longitude: number;
    place_name: string | null;
    city: string | null;
    country: string | null;
    importance: number | null;
    osm_id: string | null;
    map_provider: string;
}

export interface Geocode_Response {
    success: boolean;
    query: string;
    results: Location_Result[];
    total_results: number;
    message: string | null;
}

export interface Reverse_Geocode_Response {
    success: boolean;
    latitude: number;
    longitude: number;
    location: Location_Result | null;
    message: string | null;
}

/**
 * Modelo de ubicación para eventos (compatible con backend)
 */
export interface Event_Location {
    address: string;
    latitude: number;
    longitude: number;
    place_name: string | null;
    map_provider: 'google_maps' | 'openstreetmap';
}
