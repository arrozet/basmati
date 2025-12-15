import { Notification_Repository_Interface } from "../../domain/repositories/notification_repository_interface";
import { Notification_Model } from "../../domain/models/notification_model";
import { api_client } from "../api/axios_client";

/**
 * Implementación HTTP del repositorio de notificaciones.
 * Realiza llamadas al backend usando Axios.
 */
export class Http_Notification_Repository implements Notification_Repository_Interface {
    /**
     * Obtiene las notificaciones de un usuario.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con la lista de notificaciones.
     */
    async get_user_notifications(external_id: string): Promise<Notification_Model[]> {
        try {
            const response = await api_client.get(`/v1/notifications/user/${external_id}`);
            return response.data.map(this.map_to_notification_model);
        } catch (error) {
            console.error("Error obteniendo notificaciones:", error);
            return [];
        }
    }

    /**
     * Obtiene las notificaciones no leídas de un usuario.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con la lista de notificaciones no leídas.
     */
    async get_unread_notifications(external_id: string): Promise<Notification_Model[]> {
        try {
            const response = await api_client.get(`/v1/notifications/search/unread`, {
                params: {
                    // El backend espera el parámetro 'user_id'
                    user_id: external_id
                }
            });
            return response.data.map(this.map_to_notification_model);
        } catch (error) {
            console.error("Error obteniendo notificaciones no leídas:", error);
            return [];
        }
    }

    /**
     * Marca una notificación como leída.
     * @param notification_id - ID de la notificación.
     * @returns Promesa con la notificación actualizada.
     */
    async mark_as_read(notification_id: string): Promise<Notification_Model> {
        const response = await api_client.put(`/v1/notifications/${notification_id}/read`);
        return this.map_to_notification_model(response.data);
    }

    /**
     * Marca todas las notificaciones de un usuario como leídas.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con el número de notificaciones actualizadas.
     */
    async mark_all_as_read(external_id: string): Promise<number> {
        try {
            // Usar el endpoint bulk del backend
            const response = await api_client.put(`/v1/notifications/user/${external_id}/read-all`);
            // El backend devuelve un mensaje con el formato: "X notificaciones marcadas como leídas"
            // Extraer el número de la respuesta
            const match = response.data.message?.match(/(\d+)/);
            return match ? parseInt(match[1], 10) : 0;
        } catch (error) {
            console.error("Error marcando todas las notificaciones como leídas:", error);
            return 0;
        }
    }

    /**
     * Obtiene el conteo de notificaciones no leídas.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con el número de notificaciones no leídas.
     */
    async get_unread_count(external_id: string): Promise<number> {
        const unread = await this.get_unread_notifications(external_id);
        return unread.length;
    }

    /**
     * Mapea la respuesta del backend al modelo del dominio.
     * @param data - Datos recibidos del backend.
     * @returns Modelo de notificación del dominio.
     */
    private map_to_notification_model(data: any): Notification_Model {
        return {
            id: data.id,
            recipient_external_id: data.recipient_external_id,
            type: data.type,
            title: data.title,
            message: data.message,
            is_read: data.is_read,
            related_event_id: data.related_event_id,
            related_calendar_id: data.related_calendar_id,
            created_at: data.created_at,
            expires_at: data.expires_at
        };
    }
}
