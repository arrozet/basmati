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

        // Construir payload con ubicación si existe
        const payload: Record<string, any> = {
            calendar_id: calendar_id,
            calendar_title: "Personal",
            creator_external_id: "user_dev_1", // Mock user
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
        
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            location: item.location ? {
                address: item.location.address,
                latitude: item.location.latitude,
                longitude: item.location.longitude,
                place_name: item.location.place_name,
                map_provider: item.location.map_provider
            } : undefined
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
            calendar_id: item.calendar_id,
            location: item.location ? {
                address: item.location.address,
                latitude: item.location.latitude,
                longitude: item.location.longitude,
                place_name: item.location.place_name,
                map_provider: item.location.map_provider
            } : undefined
        }));
    }

    async search_events(query: string): Promise<Event_Model[]> {
        // Usar V1 para búsqueda de texto (V2 no tiene este endpoint)
        const response = await api_client.get(`/v1/events/search/by-text`, {
            params: { query }
        });
        
        return response.data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            location: item.location ? {
                address: item.location.address,
                latitude: item.location.latitude,
                longitude: item.location.longitude,
                place_name: item.location.place_name,
                map_provider: item.location.map_provider
            } : undefined
        }));
    }

    async search_advanced(params: { title?: string; organizer?: string; keywords?: string }): Promise<Event_Model[]> {
        // Usar V1 para búsqueda avanzada (V2 no tiene este endpoint)
        const response = await api_client.get(`/v1/events/search/advanced`, {
            params
        });
        
        return response.data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            location: item.location ? {
                address: item.location.address,
                latitude: item.location.latitude,
                longitude: item.location.longitude,
                place_name: item.location.place_name,
                map_provider: item.location.map_provider
            } : undefined
        }));
    }

    async get_event(id: string): Promise<Event_Model | null> {
        try {
            // Usar V1 para obtener evento individual (V2 no tiene este endpoint)
            const response = await api_client.get(`/v1/events/${id}`);
            const item = response.data;
            return {
                id: item.id,
                title: item.title,
                start_time: new Date(item.start_time),
                end_time: new Date(item.end_time),
                description: item.description,
                calendar_id: item.calendar_id,
                location: item.location ? {
                    address: item.location.address,
                    latitude: item.location.latitude,
                    longitude: item.location.longitude,
                    place_name: item.location.place_name,
                    map_provider: item.location.map_provider
                } : undefined
            };
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
        const item = response.data;
        
        return {
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            location: item.location ? {
                address: item.location.address,
                latitude: item.location.latitude,
                longitude: item.location.longitude,
                place_name: item.location.place_name,
                map_provider: item.location.map_provider
            } : undefined
        };
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
}

