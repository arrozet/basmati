import { Event_Model } from "../models/event_model";

export interface Event_Repository_Interface {
    get_events(calendar_id: string): Promise<Event_Model[]>;
    create(event: Omit<Event_Model, 'id'>): Promise<Event_Model>;
    
    /**
     * Obtiene eventos en un rango de fechas.
     * @param start Fecha inicio.
     * @param end Fecha fin.
     */
    get_events_by_date_range(start: Date, end: Date): Promise<Event_Model[]>;

    /**
     * Busca eventos por texto.
     * @param query Texto a buscar.
     */
    search_events(query: string): Promise<Event_Model[]>;

    /**
     * Búsqueda avanzada de eventos.
     * @param params Objeto con criterios de búsqueda.
     */
    search_advanced(params: { title?: string; organizer?: string; keywords?: string }): Promise<Event_Model[]>;
}

