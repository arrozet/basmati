import { User_Repository_Interface } from "../../domain/repositories/user_repository_interface";
import { User_Model, Notification_Preferences } from "../../domain/models/user_model";
import { api_client } from "../api/axios_client";

/**
 * Implementación HTTP del repositorio de usuarios.
 * Realiza llamadas al backend usando Axios.
 */
export class Http_User_Repository implements User_Repository_Interface {
    /**
     * Obtiene la información de un usuario desde el backend.
     * @param user_id - ID del usuario a consultar.
     * @returns Promesa con el modelo de usuario.
     */
    async get_user(user_id: string): Promise<User_Model> {
        const response = await api_client.get(`/v1/users/${user_id}`);
        return this.map_to_user_model(response.data);
    }

    /**
     * Actualiza las preferencias de notificación del usuario.
     * @param user_id - ID del usuario.
     * @param preferences - Nuevas preferencias de notificación.
     * @returns Promesa con el usuario actualizado.
     */
    async update_notification_preferences(user_id: string, preferences: Notification_Preferences): Promise<User_Model> {
        const response = await api_client.put(`/v1/users/${user_id}`, {
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
        const response = await api_client.put(`/v1/users/${user_id}`, updates);
        return this.map_to_user_model(response.data);
    }

    /**
     * Mapea la respuesta del backend al modelo del dominio.
     * @param data - Datos recibidos del backend.
     * @returns Modelo de usuario del dominio.
     */
    private map_to_user_model(data: any): User_Model {
        return {
            id: data.id,
            external_id: data.external_id,
            provider: data.provider,
            email: data.email,
            display_name: data.display_name,
            avatar_url: data.avatar_url,
            notification_preferences: {
                in_app: data.notification_preferences?.in_app ?? true,
                email: data.notification_preferences?.email ?? true,
                email_address: data.notification_preferences?.email_address ?? null
            },
            followed_calendar_ids: data.followed_calendar_ids || [],
            created_at: data.created_at,
            last_login: data.last_login
        };
    }
}
