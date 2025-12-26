// ============================================================================
// V2 Models (Legacy - mantener para compatibilidad)
// ============================================================================

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

// ============================================================================
// V3 Models (Abstract Factory Pattern)
// ============================================================================

/**
 * Tipos de proveedores soportados para importación V3
 */
export type Provider_Type = 'google' | 'teamup';

/**
 * Request para importar desde Google Calendar (V3)
 */
export interface Google_Import_Request_V3 {
    user_external_id: string;
    access_token: string;
    calendar_ids: string[];
}

/**
 * Request para importar desde Teamup (V3)
 */
export interface Teamup_Import_Request_V3 {
    user_external_id: string;
    calendar_ids: string[];
    api_key?: string;
}

/**
 * Request genérico para importación V3
 */
export interface Generic_Import_Request_V3 {
    provider: Provider_Type;
    user_external_id: string;
    calendar_ids: string[];
    credentials: Record<string, string>;
}

/**
 * Calendario importado en respuesta V3
 */
export interface Imported_Calendar_V3 {
    external_id: string;
    basmati_calendar_id: string;
    events_imported: number;
    events_failed: number;
}

/**
 * Respuesta de importación V3
 */
export interface Import_Response_V3 {
    success: boolean;
    message: string;
    provider: string;
    imported_calendars: Imported_Calendar_V3[];
    errors: string[];
    total_events_imported: number;
    total_events_failed: number;
}

/**
 * Capacidades de un proveedor
 */
export interface Provider_Capabilities {
    provider: Provider_Type;
    name: string;
    supports_oauth: boolean;
    supports_api_key: boolean;
    supports_sync: boolean;
    requires_calendar_selection: boolean;
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
