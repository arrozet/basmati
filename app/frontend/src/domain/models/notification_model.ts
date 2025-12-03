/**
 * Modelo de notificación del dominio.
 * Representa una notificación del sistema Basmati.
 */

/**
 * Tipos de notificación disponibles en el sistema.
 */
export type Notification_Type = 
    | "NEW_COMMENT" 
    | "EVENT_UPDATE" 
    | "CALENDAR_INVITE" 
    | "EVENT_REMINDER";

/**
 * Modelo de notificación del dominio.
 * Representa los datos de una notificación en el sistema.
 */
export interface Notification_Model {
    id: string;
    recipient_external_id: string;
    type: Notification_Type;
    title: string;
    message: string;
    is_read: boolean;
    related_event_id: string | null;
    related_calendar_id: string | null;
    created_at: string;
    expires_at: string | null;
}

/**
 * Datos para crear una nueva notificación.
 */
export interface Notification_Create {
    recipient_external_id: string;
    type: Notification_Type;
    title: string;
    message: string;
    related_event_id?: string;
    related_calendar_id?: string;
    expires_at?: string;
}
