import { Calendar_Repository_Interface, Delete_Recursive_Result } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";
import { api_client } from "../api/axios_client";

export class Http_Calendar_Repository implements Calendar_Repository_Interface {
    /**
     * Obtiene todos los calendarios del sistema usando el nuevo endpoint v2.
     * Una sola petición en lugar de múltiples.
     * @param limit Número máximo de calendarios a devolver.
     */
    async get_all_calendars(limit: number = 200): Promise<Calendar_Model[]> {
        try {
            const response = await api_client.get(`/v2/calendars`, {
                params: { limit }
            });
            return response.data.map((item: any) => ({
                id: item.id,
                title: item.title,
                color: item.color || '#EBBE4D',
                owner_id: item.creator_external_id || item.creator_id || item.owner_id,
                icon: item.icon,
                is_public: item.visibility === 'public',
                parent_id: item.parent_calendar_id
            }));
        } catch (error) {
            console.error("Error fetching all calendars:", error);
            return [];
        }
    }
    
    /**
     * Obtiene todos los calendarios del usuario (usa v2 getAll internamente).
     * Solo hace UNA petición al backend.
     */
    async get_all(user_id: string): Promise<Calendar_Model[]> {
        // Usar el nuevo endpoint v2 que obtiene todos los calendarios en una sola petición
        const all_calendars = await this.get_all_calendars();
        
        // Separar calendarios propios y públicos de otros usuarios
        const my_calendars = all_calendars.filter(cal => cal.owner_id === user_id);
        const other_public_calendars = all_calendars.filter(cal => 
            cal.owner_id !== user_id && cal.is_public
        );
        
        return [...my_calendars, ...other_public_calendars];
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
     * Elimina un calendario recursivamente junto con todos sus subcalendarios y eventos.
     * Utiliza el endpoint v2 del backend que maneja la eliminación en cascada.
     * @param id - ID del calendario raíz a eliminar.
     * @returns Promesa con el resultado de la eliminación.
     */
    async delete_recursive(id: string): Promise<Delete_Recursive_Result> {
        const response = await api_client.delete(`/v2/calendars/${id}/recursive`);
        return {
            message: response.data.message,
            calendar_id: response.data.calendar_id,
            calendars_deleted: response.data.calendars_deleted,
            events_deleted: response.data.events_deleted,
            errors: response.data.errors
        };
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

