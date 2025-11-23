/**
 * Preferencias de notificación del usuario.
 */
export interface Notification_Preferences {
    in_app: boolean;
    email: boolean;
    email_address: string | null;
}

/**
 * Modelo de usuario del dominio.
 * Representa los datos de un usuario en el sistema.
 */
export interface User_Model {
    id: string;
    external_id: string;
    provider: "google" | "facebook";
    email: string;
    display_name: string;
    avatar_url: string | null;
    notification_preferences: Notification_Preferences;
    followed_calendar_ids: string[];
    created_at: string;
    last_login: string | null;
}
