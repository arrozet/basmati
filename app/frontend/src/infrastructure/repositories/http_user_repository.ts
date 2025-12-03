import { User_Repository_Interface } from "../../domain/repositories/user_repository_interface";
import { User_Model, Notification_Preferences } from "../../domain/models/user_model";
import { api_client } from "../api/axios_client";

/**
 * Implementación HTTP del repositorio de usuarios V2.
 * Realiza llamadas al backend usando Axios.
 * Usa la API v2 para soporte de frecuencia de notificaciones.
 */
export class Http_User_Repository implements User_Repository_Interface {
    /**
     * Obtiene la información de un usuario desde el backend.
     * Primero intenta buscar por external_id (para desarrollo con user_dev_1, etc.)
     * Si falla, busca por MongoDB _id
     * @param user_id - ID o external_id del usuario a consultar.
     * @returns Promesa con el modelo de usuario.
     */
    async get_user(user_id: string): Promise<User_Model> {
        // Primero intentar buscar por external_id (más común en desarrollo)
        try {
            const response = await api_client.get(`/v2/users/by-external-id/${user_id}`);
            return this.map_to_user_model(response.data);
        } catch (error: any) {
            // Si no se encuentra por external_id, intentar por _id
            if (error.response?.status === 404) {
                const response = await api_client.get(`/v2/users/${user_id}`);
                return this.map_to_user_model(response.data);
            }
            throw error;
        }
    }

    /**
     * Obtiene un usuario por su external_id (Google ID, Facebook ID, etc.)
     * @param external_id - ID externo del proveedor OAuth.
     * @returns Promesa con el modelo de usuario.
     */
    async get_user_by_external_id(external_id: string): Promise<User_Model> {
        const response = await api_client.get(`/v2/users/by-external-id/${external_id}`);
        return this.map_to_user_model(response.data);
    }

    /**
     * Actualiza las preferencias de notificación del usuario.
     * @param user_id - ID del usuario (puede ser _id o external_id).
     * @param preferences - Nuevas preferencias de notificación.
     * @returns Promesa con el usuario actualizado.
     */
    async update_notification_preferences(user_id: string, preferences: Notification_Preferences): Promise<User_Model> {
        const response = await api_client.put(`/v2/users/${user_id}`, {
            notification_preferences: preferences
        });
        return this.map_to_user_model(response.data);
    }

    /**
     * Actualiza los datos básicos del perfil del usuario.
     * @param user_id - ID del usuario.
     * @param updates - Campos a actualizar.
     * @returns Promesa con el usuario actualizado.
     */
    async update_user_profile(user_id: string, updates: Partial<Pick<User_Model, 'display_name' | 'email' | 'avatar_url'>>): Promise<User_Model> {
        const response = await api_client.put(`/v2/users/${user_id}`, updates);
        return this.map_to_user_model(response.data);
    }

    /**
     * Mapea la respuesta del backend al modelo del dominio.
     * Incluye soporte para el campo frequency de V2.
     * @param data - Datos recibidos del backend.
     * @returns Modelo de usuario del dominio.
     */
    private map_to_user_model(data: any): User_Model {
        return {
            id: data.id || data._id,
            external_id: data.external_id,
            provider: data.provider,
            email: data.email,
            display_name: data.display_name,
            avatar_url: data.avatar_url,
            notification_preferences: {
                in_app: data.notification_preferences?.in_app ?? true,
                email: data.notification_preferences?.email ?? true,
                email_address: data.notification_preferences?.email_address ?? null,
                frequency: data.notification_preferences?.frequency ?? 'instant'
            },
            followed_calendar_ids: data.followed_calendar_ids || [],
            created_at: data.created_at,
            last_login: data.last_login
        };
    }
}
