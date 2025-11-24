import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";
import { api_client } from "../api/axios_client";

export class Http_Calendar_Repository implements Calendar_Repository_Interface {
    /**
     * Obtiene todos los calendarios del usuario.
     */
    async get_all(user_id: string): Promise<Calendar_Model[]> {
        try {
            const response = await api_client.get(`/v1/calendars/search/by-creator?creator_external_id=${user_id}`);
            return response.data.map((item: any) => ({
                id: item.id,
                title: item.title,
                color: item.color || '#EBBE4D',
                owner_id: item.creator_id || item.owner_id,
                icon: item.icon,
                is_public: item.is_public
            }));
        } catch (error) {
            console.error("Error fetching calendars:", error);
            return [];
        }
    }
    
    /**
     * Crea un nuevo calendario.
     */
    async create(calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model> {
        const response = await api_client.post("/v1/calendars", calendar);
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            color: item.color,
            owner_id: item.owner_id,
            icon: item.icon,
            is_public: item.is_public
        };
    }
    
    /**
     * Actualiza un calendario existente.
     */
    async update(calendar: Calendar_Model): Promise<Calendar_Model> {
        const response = await api_client.put(`/v1/calendars/${calendar.id}`, {
            title: calendar.title,
            color: calendar.color,
            icon: calendar.icon,
            is_public: calendar.is_public
        });
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            color: item.color,
            owner_id: item.owner_id,
            icon: item.icon,
            is_public: item.is_public
        };
    }
    
    /**
     * Elimina un calendario por su ID.
     */
    async delete(id: string): Promise<void> {
        await api_client.delete(`/v1/calendars/${id}`);
    }
    
    /**
     * Obtiene un calendario específico por su ID.
     */
    async get_by_id(id: string): Promise<Calendar_Model | null> {
        try {
            const response = await api_client.get(`/v1/calendars/${id}`);
            const item = response.data;
            return {
                id: item.id,
                title: item.title,
                color: item.color,
                owner_id: item.owner_id,
                icon: item.icon,
                is_public: item.is_public
            };
        } catch (error) {
            console.error("Error fetching calendar:", error);
            return null;
        }
    }
}

