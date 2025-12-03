import { Notification_Model } from "../models/notification_model";

/**
 * Interfaz del repositorio de notificaciones.
 * Define las operaciones de acceso a datos relacionados con notificaciones.
 */
export interface Notification_Repository_Interface {
    /**
     * Obtiene las notificaciones de un usuario.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con la lista de notificaciones.
     */
    get_user_notifications(external_id: string): Promise<Notification_Model[]>;

    /**
     * Obtiene las notificaciones no leídas de un usuario.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con la lista de notificaciones no leídas.
     */
    get_unread_notifications(external_id: string): Promise<Notification_Model[]>;

    /**
     * Marca una notificación como leída.
     * @param notification_id - ID de la notificación.
     * @returns Promesa con la notificación actualizada.
     */
    mark_as_read(notification_id: string): Promise<Notification_Model>;

    /**
     * Marca todas las notificaciones de un usuario como leídas.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con el número de notificaciones actualizadas.
     */
    mark_all_as_read(external_id: string): Promise<number>;

    /**
     * Obtiene el conteo de notificaciones no leídas.
     * @param external_id - ID externo del usuario.
     * @returns Promesa con el número de notificaciones no leídas.
     */
    get_unread_count(external_id: string): Promise<number>;
}
