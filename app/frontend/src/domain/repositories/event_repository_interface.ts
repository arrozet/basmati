import { Event_Model, Event_Attachment, Event_Comment } from "../models/event_model";

export interface Event_Repository_Interface {
    /**
     * Obtiene todos los eventos del sistema.
     * @param limit Número máximo de eventos a devolver.
     */
    get_all_events(limit?: number): Promise<Event_Model[]>;
    
    get_events(calendar_id: string): Promise<Event_Model[]>;
    create(event: Omit<Event_Model, 'id'>): Promise<Event_Model>;
    
    /**
     * Obtiene eventos en un rango de fechas.
     * @param start Fecha inicio.
     * @param end Fecha fin.
     * @param calendar_ids Lista de IDs de calendario para filtrar (opcional).
     */
    get_events_by_date_range(start: Date, end: Date, calendar_ids?: string[]): Promise<Event_Model[]>;

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

    /**
     * Obtiene un evento por su ID.
     * @param id ID del evento.
     */
    get_event(id: string): Promise<Event_Model | null>;

    /**
     * Actualiza un evento existente.
     * @param event Evento con los datos actualizados.
     */
    update(event: Event_Model): Promise<Event_Model>;

    /**
     * Elimina un evento por su ID.
     * @param id ID del evento a eliminar.
     */
    delete(id: string): Promise<boolean>;

    /**
     * Añade un adjunto a un evento existente.
     * @param event_id ID del evento.
     * @param attachment Datos del adjunto (url, filename, etc.)
     */
    add_attachment(event_id: string, attachment: Event_Attachment): Promise<Event_Attachment>;

    /**
     * Añade un comentario a un evento.
     * @param event_id ID del evento.
     * @param text Texto del comentario.
     * @param user_id ID del usuario que comenta.
     */
    add_comment(event_id: string, text: string, user_id: string): Promise<Event_Comment>;
}
