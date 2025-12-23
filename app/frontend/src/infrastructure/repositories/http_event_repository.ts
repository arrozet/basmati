import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model, Event_Attachment, Event_Comment } from "../../domain/models/event_model";
import { api_client } from "../api/axios_client";
import { Http_Calendar_Repository } from "./http_calendar_repository";

/**
 * Parsea una fecha que viene del backend en UTC.
 * El backend envía fechas sin sufijo "Z", lo que hace que JavaScript
 * las interprete como hora local. Esta función añade "Z" para corregirlo.
 */
const parse_utc_date = (date_string: string): Date => {
    if (!date_string) return new Date();
    const has_timezone = date_string.endsWith('Z') || 
                         date_string.includes('+') || 
                         /T\d{2}:\d{2}:\d{2}.*-\d{2}/.test(date_string);
    return new Date(has_timezone ? date_string : date_string + 'Z');
};

export class Http_Event_Repository implements Event_Repository_Interface {
    private calendar_repository: Http_Calendar_Repository;

    constructor() {
        this.calendar_repository = new Http_Calendar_Repository();
    }

    /**
     * Obtiene todos los eventos del sistema usando el nuevo endpoint v2.
     * Una sola petición en lugar de múltiples.
     * @param limit Número máximo de eventos a devolver.
     */
    async get_all_events(limit: number = 200): Promise<Event_Model[]> {
        try {
            const response = await api_client.get(`/v2/events`, {
                params: { limit }
            });
            return this.map_response(response.data);
        } catch (error) {
            console.error("Error fetching all events:", error);
            return [];
        }
    }
    
    async get_events(_calendar_id: string): Promise<Event_Model[]> {
         // Mock implementation for scaffolding (legacy method)
        return Promise.resolve([]);
    }

    async create(event: Omit<Event_Model, 'id'>): Promise<Event_Model> {
        // Helper to validate ObjectId
        const isValidObjectId = (id: string) => /^[0-9a-fA-F]{24}$/.test(id);

        let calendar_id = event.calendar_id;
        // Fallback if ID is missing or invalid (e.g. ":1" from routing errors)
        if (!calendar_id || !isValidObjectId(calendar_id)) {
             console.warn(`Invalid or missing calendar_id: "${calendar_id}". Using mock default.`);
             calendar_id = "507f1f77bcf86cd799439011"; // Default mock ID
        }

        // Obtener el calendario para usar su creator_external_id
        const calendar = await this.calendar_repository.get_by_id(calendar_id);
        if (!calendar) {
            throw new Error("Calendario no encontrado");
        }

        // Usar el owner_id del calendario (que mapea a creator_external_id del backend)
        // como creator_external_id del evento. Esto asegura que el evento tenga
        // el mismo creador que el calendario, especialmente importante para calendarios
        // creados con Google OAuth.
        const creator_external_id = calendar.owner_id;
        
        // Construir payload con ubicación si existe
        const payload: Record<string, any> = {
            calendar_id: calendar_id,
            calendar_title: calendar.title || "Personal",
            creator_external_id: creator_external_id, // Usar el creator_external_id del calendario
            title: event.title,
            description: event.description,
            visibility: "private",
            // Explicitly format dates to ISO strings to ensure backend compatibility
            start_time: event.start_time instanceof Date ? event.start_time.toISOString() : event.start_time,
            end_time: event.end_time instanceof Date ? event.end_time.toISOString() : event.end_time,
        };

        // Añadir ubicación si existe
        if (event.location) {
            payload.location = {
                address: event.location.address,
                latitude: event.location.latitude,
                longitude: event.location.longitude,
                place_name: event.location.place_name,
                map_provider: event.location.map_provider
            };
        }

        console.log("Sending Create Event Payload:", payload);

        // Usar V1 para crear eventos (V2 no tiene endpoint POST)
        const response = await api_client.post("/v1/events", payload);
        
        return this.map_single_response(response.data);
    }

    async get_events_by_date_range(start: Date, end: Date, calendar_ids?: string[]): Promise<Event_Model[]> {
        const base_params = {
            start: start.toISOString(),
            end: end.toISOString()
        };

        // Una sola petición para obtener todos los eventos en el rango de fechas
        const response = await api_client.get("/v2/events/search/by-date-range", { params: base_params });
        const all_events = this.map_response(response.data);

        // Si no hay filtro de calendarios, devolver todos
        if (!calendar_ids || calendar_ids.length === 0) {
            return all_events;
        }

        // Filtrar en el cliente por los calendar_ids especificados
        const calendar_id_set = new Set(calendar_ids);
        return all_events.filter(event => calendar_id_set.has(event.calendar_id));
    }

    private map_response(data: any[]): Event_Model[] {
        return data.map((item: any) => this.map_single_response(item));
    }

    private map_single_response(item: any): Event_Model {
        return {
            id: item.id,
            title: item.title,
            start_time: parse_utc_date(item.start_time),
            end_time: parse_utc_date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            location: item.location ? {
                address: item.location.address,
                latitude: item.location.latitude,
                longitude: item.location.longitude,
                place_name: item.location.place_name,
                map_provider: item.location.map_provider
            } : undefined,
            attachments: item.attachments ? item.attachments.map((att: any) => ({
                id: att.id,
                filename: att.filename,
                url: att.url,
                size: att.size,
                mime_type: att.mime_type,
                uploaded_at: parse_utc_date(att.uploaded_at),
                uploaded_by: att.uploaded_by,
                is_image: att.is_image,
                thumbnail_url: att.thumbnail_url
            })) : [],
            comments: item.comments ? item.comments.map((com: any) => ({
                id: com.id || com._id,
                author_external_id: com.author_external_id,
                author_display_name: com.author_display_name,
                text: com.text,
                created_at: parse_utc_date(com.created_at)
            })) : []
        };
    }

    async search_events(query: string): Promise<Event_Model[]> {
        // Usar V2 para búsqueda de texto
        const response = await api_client.get(`/v2/events/search/by-text`, {
            params: { query }
        });
        
        return this.map_response(response.data);
    }

    async search_advanced(params: { title?: string; organizer?: string; keywords?: string }): Promise<Event_Model[]> {
        // Usar V2 para búsqueda avanzada
        const response = await api_client.get(`/v2/events/search/advanced`, {
            params
        });
        
        return this.map_response(response.data);
    }

    async get_event(id: string): Promise<Event_Model | null> {
        try {
            // Usar V1 para obtener evento individual (V2 no tiene este endpoint)
            const response = await api_client.get(`/v1/events/${id}`);
            return this.map_single_response(response.data);
        } catch (error) {
            console.error("Error fetching event:", error);
            return null;
        }
    }

    async update(event: Event_Model): Promise<Event_Model> {
        const payload: Record<string, any> = {
            title: event.title,
            description: event.description,
            start_time: event.start_time.toISOString(),
            end_time: event.end_time.toISOString()
        };

        // Incluir adjuntos en la actualización
        if (event.attachments) {
            payload.attachments = event.attachments.map(att => ({
                id: att.id || '', // El backend generará un ObjectId si está vacío o es inválido
                filename: att.filename,
                url: att.url,
                size: att.size,
                mime_type: att.mime_type,
                uploaded_at: att.uploaded_at instanceof Date ? att.uploaded_at.toISOString() : att.uploaded_at,
                uploaded_by: att.uploaded_by,
                is_image: att.is_image,
                thumbnail_url: att.thumbnail_url || null
            }));
        }

        // Añadir ubicación si existe (puede ser null para eliminarla)
        if (event.location) {
            payload.location = {
                address: event.location.address,
                latitude: event.location.latitude,
                longitude: event.location.longitude,
                place_name: event.location.place_name,
                map_provider: event.location.map_provider
            };
        } else {
            // Enviar null explícitamente para eliminar la ubicación
            payload.location = null;
        }

        // Usar V1 para actualizar eventos (V2 no tiene endpoint PUT)
        const response = await api_client.put(`/v1/events/${event.id}`, payload);
        return this.map_single_response(response.data);
    }

    async delete(id: string): Promise<boolean> {
        try {
            // Usar V1 para eliminar evento individual (V2 solo tiene delete by calendar)
            await api_client.delete(`/v1/events/${id}`);
            return true;
        } catch (error) {
            console.error("Error deleting event:", error);
            return false;
        }
    }

    async add_attachment(event_id: string, attachment: Event_Attachment): Promise<Event_Attachment> {
        const payload = {
            filename: attachment.filename,
            url: attachment.url,
            size: attachment.size,
            mime_type: attachment.mime_type,
            uploaded_by: attachment.uploaded_by,
            is_image: attachment.is_image,
            thumbnail_url: attachment.thumbnail_url || null
        };
        
        const response = await api_client.post(`/v1/events/${event_id}/attachments`, payload);
        const item = response.data;
        
        return {
            id: item.id,
            filename: item.filename,
            url: item.url,
            size: item.size,
            mime_type: item.mime_type,
            uploaded_at: parse_utc_date(item.uploaded_at),
            uploaded_by: item.uploaded_by,
            is_image: item.is_image,
            thumbnail_url: item.thumbnail_url
        };
    }

    async add_comment(event_id: string, text: string, user_id: string): Promise<Event_Comment> {
        const payload = {
            user_id: user_id,
            text: text
        };
        
        // Usar V2 para comentarios simplificados (no requiere display_name)
        const response = await api_client.post(`/v2/events/${event_id}/comments`, payload);
        const item = response.data;
        
        return {
            id: item.id || item._id,
            author_external_id: item.author_external_id,
            author_display_name: item.author_display_name,
            text: item.text,
            created_at: parse_utc_date(item.created_at)
        };
    }
}
