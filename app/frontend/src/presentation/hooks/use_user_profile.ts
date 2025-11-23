import { useState, useEffect } from "react";
import { User_Model, Notification_Preferences } from "../../domain/models/user_model";
import { Get_User_Profile_Use_Case } from "../../application/user/get_user_profile_use_case";
import { Update_Notification_Preferences_Use_Case } from "../../application/user/update_notification_preferences_use_case";
import { Update_User_Profile_Use_Case } from "../../application/user/update_user_profile_use_case";
import { Http_User_Repository } from "../../infrastructure/repositories/http_user_repository";

// Inyección de dependencias manual (Poor man's DI)
const repository = new Http_User_Repository();
const get_user_profile_use_case = new Get_User_Profile_Use_Case(repository);
const update_notification_preferences_use_case = new Update_Notification_Preferences_Use_Case(repository);
const update_user_profile_use_case = new Update_User_Profile_Use_Case(repository);

/**
 * Obtiene el ID del usuario actual desde localStorage o usa uno temporal.
 * @returns ID del usuario actual.
 */
const get_current_user_id = (): string => {
    // Intentar obtener del localStorage
    const stored_user_id = localStorage.getItem('basmati_user_id');
    if (stored_user_id) {
        return stored_user_id;
    }
    
    // Por defecto, usar un ObjectId de MongoDB válido del usuario de ejemplo
    // Este ID debe coincidir con el usuario creado en setup_basmati_db.js
    // IMPORTANTE: Debes reemplazar este ID con el real de tu base de datos
    // Puedes obtenerlo ejecutando: docker exec -it basmati-mongodb mongosh basmati --eval "db.users.findOne({email: 'usuario@example.com'})._id"
    return localStorage.getItem('basmati_user_id') || '';
};

/**
 * Hook personalizado para gestionar el perfil del usuario.
 * Proporciona funcionalidades de lectura y actualización del perfil y preferencias.
 * @returns Objeto con el usuario, estado de carga, funciones de actualización y errores.
 */
export const use_user_profile = () => {
    const [user, set_user] = useState<User_Model | null>(null);
    const [loading, set_loading] = useState<boolean>(true);
    const [error, set_error] = useState<string | null>(null);
    const [saving, set_saving] = useState<boolean>(false);

    /**
     * Carga los datos del usuario actual.
     */
    const load_user = async () => {
        const user_id = get_current_user_id();
        
        if (!user_id) {
            set_loading(false);
            set_error("No hay un usuario autenticado. Por favor, configura un ID de usuario válido.");
            console.error("No user ID found. Please set 'basmati_user_id' in localStorage with a valid MongoDB ObjectId");
            return;
        }
        
        try {
            set_loading(true);
            set_error(null);
            const user_data = await get_user_profile_use_case.execute(user_id);
            set_user(user_data);
        } catch (err) {
            const error_message = err instanceof Error ? err.message : "Error al cargar el perfil del usuario";
            set_error(error_message);
            console.error("Error loading user profile:", err);
        } finally {
            set_loading(false);
        }
    };

    /**
     * Actualiza las preferencias de notificación del usuario.
     * @param preferences - Nuevas preferencias de notificación.
     */
    const update_preferences = async (preferences: Notification_Preferences): Promise<void> => {
        const user_id = get_current_user_id();
        
        try {
            set_saving(true);
            set_error(null);
            const updated_user = await update_notification_preferences_use_case.execute(user_id, preferences);
            set_user(updated_user);
        } catch (err) {
            const error_message = err instanceof Error ? err.message : "Error al actualizar las preferencias";
            set_error(error_message);
            console.error("Error updating preferences:", err);
            throw err; // Re-lanzar para que el componente pueda manejarlo
        } finally {
            set_saving(false);
        }
    };

    /**
     * Actualiza los datos básicos del perfil del usuario.
     * @param updates - Campos del perfil a actualizar.
     */
    const update_profile = async (updates: Partial<Pick<User_Model, 'display_name' | 'email' | 'avatar_url'>>): Promise<void> => {
        const user_id = get_current_user_id();
        
        try {
            set_saving(true);
            set_error(null);
            const updated_user = await update_user_profile_use_case.execute(user_id, updates);
            set_user(updated_user);
        } catch (err) {
            const error_message = err instanceof Error ? err.message : "Error al actualizar el perfil";
            set_error(error_message);
            console.error("Error updating profile:", err);
            throw err;
        } finally {
            set_saving(false);
        }
    };

    // Cargar usuario al montar el hook
    useEffect(() => {
        load_user();
    }, []);

    return {
        user,
        loading,
        error,
        saving,
        update_preferences,
        update_profile,
        reload_user: load_user
    };
};
