import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";
import { api_client } from "../api/axios_client";

export class Http_Event_Repository implements Event_Repository_Interface {
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

        // TODO: Hardcoded values for now as we don't have auth/calendar selection fully implemented
        const payload = {
            ...event,
            calendar_id: calendar_id,
            calendar_title: "Personal",
            creator_external_id: "user_dev_1", // Mock user
            visibility: "private",
            // Explicitly format dates to ISO strings to ensure backend compatibility
            start_time: event.start_time instanceof Date ? event.start_time.toISOString() : event.start_time,
            end_time: event.end_time instanceof Date ? event.end_time.toISOString() : event.end_time,
        };

        console.log("Sending Create Event Payload:", payload);

        const response = await api_client.post("/v2/events", payload);
        
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id
        };
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
        return data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id
        }));
    }

    async search_events(query: string): Promise<Event_Model[]> {
        const response = await api_client.get(`/v2/events/search/by-text`, {
            params: { query }
        });
        
        return response.data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id
        }));
    }

    async search_advanced(params: { title?: string; organizer?: string; keywords?: string }): Promise<Event_Model[]> {
        const response = await api_client.get(`/v2/events/search/advanced`, {
            params
        });
        
        return response.data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id
        }));
    }

    async get_event(id: string): Promise<Event_Model | null> {
        try {
            const response = await api_client.get(`/v2/events/${id}`);
            const item = response.data;
            return {
                id: item.id,
                title: item.title,
                start_time: new Date(item.start_time),
                end_time: new Date(item.end_time),
                description: item.description,
                calendar_id: item.calendar_id
            };
        } catch (error) {
            console.error("Error fetching event:", error);
            return null;
        }
    }

    async update(event: Event_Model): Promise<Event_Model> {
        const payload = {
            title: event.title,
            description: event.description,
            start_time: event.start_time.toISOString(),
            end_time: event.end_time.toISOString()
            // Include other fields if necessary, but these are the main ones for update
        };

        const response = await api_client.put(`/v2/events/${event.id}`, payload);
        const item = response.data;
        
        return {
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id
        };
    }

    async delete(id: string): Promise<boolean> {
        try {
            await api_client.delete(`/v2/events/${id}`);
            return true;
        } catch (error) {
            console.error("Error deleting event:", error);
            return false;
        }
    }
}

