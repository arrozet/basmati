import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";
import { api_client } from "../api/axios_client";

export class Http_Calendar_Repository implements Calendar_Repository_Interface {
    /**
     * Obtiene todos los calendarios del usuario.
     */
    async get_all(user_id: string): Promise<Calendar_Model[]> {
        let myCalendars: Calendar_Model[] = [];
        let otherCalendars: Calendar_Model[] = [];

        try {
            // 1. Obtener mis calendarios (creados por mi)
            const response = await api_client.get(`/v1/calendars/search/by-creator?creator_external_id=${user_id}`);
            myCalendars = response.data.map((item: any) => ({
                id: item.id,
                title: item.title,
                color: item.color || '#EBBE4D',
                // Ensure we map the owner_id back to the user_id we know if it matches, or keep backend value
                // The backend might return creator_external_id OR creator_id
                owner_id: item.creator_external_id || item.creator_id || item.owner_id || user_id, 
                icon: item.icon,
                is_public: item.is_public,
                parent_id: item.parent_calendar_id
            }));
        } catch (error) {
            console.error("Error fetching my calendars:", error);
        }

        try {
            // 2. Obtener otros calendarios (seguidos/públicos pero no míos)
            // Usamos el endpoint de visibilidad para traer todos los calendarios públicos
            const response_others = await api_client.get(`/v1/calendars/search/by-visibility?visibility=public`);
            
            const allPublicCalendars = response_others.data.map((item: any) => ({
                id: item.id,
                title: item.title,
                color: item.color || '#5496FF',
                owner_id: item.creator_external_id || item.creator_id || item.owner_id,
                icon: item.icon,
                is_public: item.is_public,
                parent_id: item.parent_calendar_id
            }));

            // Filtramos para que "otros" no incluya los "míos"
            otherCalendars = allPublicCalendars.filter((cal: Calendar_Model) => 
                cal.owner_id !== user_id && 
                !myCalendars.some(my => my.id === cal.id)
            );

        } catch (error) {
            console.error("Error fetching other calendars:", error);
        }

        return [...myCalendars, ...otherCalendars];
    }
    
    /**
     * Crea un nuevo calendario.
     */
    async create(calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model> {
        // Mapear modelo de dominio a DTO del backend
        const backend_payload = {
            title: calendar.title,
            color: calendar.color,
            creator_external_id: calendar.owner_id, // Mapeo correcto
            creator_display_name: "Usuario Dev", // TODO: Obtener del contexto de usuario real cuando exista auth
            keywords: [], // Campo opcional pero recomendado
            icon: calendar.icon,
            visibility: calendar.is_public ? "public" : "private", // Mapeo de booleano a enum
            description: "",
            parent_calendar_id: calendar.parent_id
        };

        const response = await api_client.post("/v1/calendars", backend_payload);
        
        // Mapear respuesta del backend al modelo de dominio
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            color: item.color,
            owner_id: item.creator_external_id || item.owner_id, // Adaptable a lo que devuelva el backend
            icon: item.icon,
            is_public: item.visibility === "public",
            parent_id: item.parent_calendar_id
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
            is_public: calendar.is_public,
            parent_calendar_id: calendar.parent_id
        });
        const item = response.data;
        return {
            id: item.id,
            title: item.title,
            color: item.color,
            owner_id: item.owner_id,
            icon: item.icon,
            is_public: item.is_public,
            parent_id: item.parent_calendar_id
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
                owner_id: item.creator_external_id || item.owner_id || item.creator_id,
                icon: item.icon,
                is_public: item.is_public,
                parent_id: item.parent_calendar_id
            };
        } catch (error) {
            console.error("Error fetching calendar:", error);
            return null;
        }
    }

    /**
     * Busca calendarios por texto.
     */
    async search(query: string): Promise<Calendar_Model[]> {
        try {
            const response = await api_client.get(`/v1/calendars/search/by-text`, {
                params: { query }
            });
            return response.data.map((item: any) => ({
                id: item.id,
                title: item.title,
                color: item.color || '#EBBE4D',
                owner_id: item.creator_external_id || item.owner_id || item.creator_id,
                icon: item.icon,
                is_public: item.is_public,
                parent_id: item.parent_calendar_id
            }));
        } catch (error) {
            console.error("Error searching calendars:", error);
            return [];
        }
    }
}

