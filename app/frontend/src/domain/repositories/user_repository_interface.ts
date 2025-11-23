import { User_Model, Notification_Preferences } from "../models/user_model";

/**
 * Interfaz del repositorio de usuarios.
 * Define las operaciones de acceso a datos relacionados con usuarios.
 */
export interface User_Repository_Interface {
    /**
     * Obtiene la información de un usuario por su ID.
     * @param user_id - ID único del usuario.
     * @returns Promesa con el modelo de usuario.
     */
    get_user(user_id: string): Promise<User_Model>;

    /**
     * Actualiza las preferencias de notificación de un usuario.
     * @param user_id - ID del usuario a actualizar.
     * @param preferences - Nuevas preferencias de notificación.
     * @returns Promesa con el usuario actualizado.
     */
    update_notification_preferences(user_id: string, preferences: Notification_Preferences): Promise<User_Model>;

    /**
     * Actualiza los datos básicos del perfil del usuario.
     * @param user_id - ID del usuario a actualizar.
     * @param updates - Objeto con los campos a actualizar (display_name, email, avatar_url).
     * @returns Promesa con el usuario actualizado.
     */
    update_user_profile(user_id: string, updates: Partial<Pick<User_Model, 'display_name' | 'email' | 'avatar_url'>>): Promise<User_Model>;
}
