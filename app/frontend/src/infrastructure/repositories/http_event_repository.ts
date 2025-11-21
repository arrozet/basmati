import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";
import { api_client } from "../api/axios_client";

export class Http_Event_Repository implements Event_Repository_Interface {
    async get_events(calendar_id: string): Promise<Event_Model[]> {
         // Mock implementation for scaffolding
        return Promise.resolve([]);
    }
    async create(event: Omit<Event_Model, 'id'>): Promise<Event_Model> {
        // TODO: Hardcoded values for now as we don't have auth/calendar selection fully implemented
        const payload = {
            ...event,
            calendar_id: event.calendar_id || "507f1f77bcf86cd799439011", // Default mock ID
            calendar_title: "Personal",
            creator_external_id: "user_dev_1", // Mock user
            visibility: "private"
        };

        const response = await api_client.post("/v1/events", payload);
        
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            color: item.color
        };
    }

    async get_events_by_date_range(start: Date, end: Date): Promise<Event_Model[]> {
        const response = await api_client.get("/v1/events/search/by-date-range", {
            params: {
                start: start.toISOString(),
                end: end.toISOString()
            }
        });

        return response.data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            end_time: new Date(item.end_time),
            description: item.description,
            calendar_id: item.calendar_id,
            color: item.color
        }));
    }

    async search_events(query: string): Promise<Event_Model[]> {
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
            color: item.color
        }));
    }

    async search_advanced(params: { title?: string; organizer?: string; keywords?: string }): Promise<Event_Model[]> {
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
            color: item.color
        }));
    }
}

