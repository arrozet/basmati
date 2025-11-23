import { User_Repository_Interface } from "../../domain/repositories/user_repository_interface";
import { User_Model, Notification_Preferences } from "../../domain/models/user_model";

/**
 * Caso de uso: Actualizar preferencias de notificación.
 * Encapsula la lógica para modificar las preferencias de notificaciones del usuario.
 */
export class Update_Notification_Preferences_Use_Case {
    private repository: User_Repository_Interface;

    constructor(repository: User_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta el caso de uso para actualizar las preferencias de notificación.
     * @param user_id - ID del usuario.
     * @param preferences - Nuevas preferencias de notificación.
     * @returns Promesa con el usuario actualizado.
     * @throws Error si los datos son inválidos.
     */
    async execute(user_id: string, preferences: Notification_Preferences): Promise<User_Model> {
        if (!user_id || user_id.trim() === "") {
            throw new Error("El ID de usuario es requerido");
        }

        // Validación: si el correo está habilitado pero no hay dirección, usar la del perfil
        if (preferences.email && !preferences.email_address) {
            console.warn("Notificaciones por email habilitadas sin dirección específica");
        }

        return await this.repository.update_notification_preferences(user_id, preferences);
    }
}
