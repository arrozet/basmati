import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User_Model, Notification_Preferences } from '../../domain/models/user_model';
import { Http_User_Repository } from '../../infrastructure/repositories/http_user_repository';
import { 
    get_token, 
    get_stored_user, 
    remove_token, 
    is_authenticated,
    AuthUser 
} from '../../infrastructure/services/auth_service';

/**
 * Preferencias de notificación V2 con frecuencia.
 */
export interface Notification_Preferences_V2 extends Notification_Preferences {
    frequency: 'instant' | 'daily';
}

/**
 * Modelo de usuario extendido con preferencias V2.
 */
export interface User_Model_V2 extends Omit<User_Model, 'notification_preferences'> {
    notification_preferences: Notification_Preferences_V2;
}

/**
 * Tipo del contexto de usuario.
 */
interface User_Context_Type {
    user: User_Model_V2 | null;
    loading: boolean;
    error: string | null;
    is_authenticated: boolean;
    update_user: (updates: Partial<User_Model_V2>) => Promise<void>;
    update_preferences: (preferences: Notification_Preferences_V2) => Promise<void>;
    switch_user: (external_id: string) => Promise<void>;
    refresh: () => Promise<void>;
    logout: () => void;
}

// Contexto de usuario
const User_Context = createContext<User_Context_Type | undefined>(undefined);

// Repository de usuario
const user_repository = new Http_User_Repository();

// ID del usuario por defecto para desarrollo
const DEFAULT_USER_EXTERNAL_ID = 'user_dev_1';

interface User_Provider_Props {
    children: ReactNode;
}

/**
 * Proveedor del contexto de usuario.
 * Gestiona el estado del usuario actual de la sesión.
 * 
 * Soporta autenticación OAuth (con token JWT) y login de desarrollo.
 */
export const User_Provider: React.FC<User_Provider_Props> = ({ children }) => {
    const [user, set_user] = useState<User_Model_V2 | null>(null);
    const [loading, set_loading] = useState(true);
    const [error, set_error] = useState<string | null>(null);
    
    // Determinar el external_id: primero del token OAuth, luego del localStorage de desarrollo
    const get_current_external_id = (): string | null => {
        // Primero intentar obtener del token OAuth
        const stored_user = get_stored_user();
        if (stored_user && is_authenticated()) {
            return stored_user.external_id;
        }
        
        // Fallback a usuario de desarrollo
        return localStorage.getItem('basmati_current_user') || null;
    };

    const [current_external_id, set_current_external_id] = useState<string | null>(
        get_current_external_id()
    );

    /**
     * Carga los datos del usuario actual.
     */
    const load_user = async () => {
        // Si no hay external_id, no intentar cargar
        if (!current_external_id) {
            set_loading(false);
            set_user(null);
            return;
        }

        set_loading(true);
        set_error(null);

        try {
            // Buscar usuario por external_id
            const user_data = await user_repository.get_user(current_external_id);
            
            // Asegurar que tenga preferencias V2
            const user_v2: User_Model_V2 = {
                ...user_data,
                notification_preferences: {
                    ...user_data.notification_preferences,
                    frequency: (user_data.notification_preferences as any).frequency || 'instant'
                }
            };
            
            set_user(user_v2);
        } catch (err: any) {
            console.error('Error loading user:', err);
            
            if (err.response?.status === 404) {
                set_error('Usuario no encontrado.');
            } else {
                set_error(err.message || 'Error al cargar usuario');
            }
            set_user(null);
        } finally {
            set_loading(false);
        }
    };

    /**
     * Actualiza los datos del usuario.
     */
    const update_user = async (updates: Partial<User_Model_V2>) => {
        if (!user) return;

        try {
            const updated = await user_repository.update_user_profile(user.id, updates);
            set_user(prev => prev ? { ...prev, ...updated } : null);
        } catch (err: any) {
            console.error('Error updating user:', err);
            throw err;
        }
    };

    /**
     * Actualiza las preferencias de notificación.
     */
    const update_preferences = async (preferences: Notification_Preferences_V2) => {
        if (!user) return;

        try {
            const updated = await user_repository.update_notification_preferences(user.id, preferences);
            set_user(prev => prev ? { 
                ...prev, 
                notification_preferences: {
                    ...updated.notification_preferences,
                    frequency: preferences.frequency
                }
            } : null);
        } catch (err: any) {
            console.error('Error updating preferences:', err);
            throw err;
        }
    };

    /**
     * Cambia el usuario actual (para pruebas con múltiples usuarios).
     * Valida que el usuario exista en la base de datos antes de hacer el cambio.
     * @throws Error si el usuario no existe.
     */
    const switch_user = async (external_id: string) => {
        // Validar que el usuario existe antes de hacer el switch
        const user_data = await user_repository.get_user(external_id);
        
        if (!user_data) {
            throw new Error('Usuario no encontrado');
        }
        
        // Usuario válido, guardar en localStorage y actualizar estado
        localStorage.setItem('basmati_current_user', external_id);
        set_current_external_id(external_id);
        
        // Actualizar el usuario inmediatamente sin esperar al useEffect
        const user_v2: User_Model_V2 = {
            ...user_data,
            notification_preferences: {
                ...user_data.notification_preferences,
                frequency: (user_data.notification_preferences as any).frequency || 'instant'
            }
        };
        set_user(user_v2);
    };

    /**
     * Cierra la sesión del usuario.
     * Limpia tokens y datos de localStorage.
     */
    const logout = () => {
        remove_token();
        localStorage.removeItem('basmati_current_user');
        set_user(null);
        set_current_external_id(null);
    };

    // Cargar usuario al montar o cuando cambia el external_id
    useEffect(() => {
        load_user();
    }, [current_external_id]);

    const value: User_Context_Type = {
        user,
        loading,
        error,
        is_authenticated: is_authenticated() || user !== null,
        update_user,
        update_preferences,
        switch_user,
        refresh: load_user,
        logout
    };

    return (
        <User_Context.Provider value={value}>
            {children}
        </User_Context.Provider>
    );
};

/**
 * Hook para acceder al contexto de usuario.
 * @throws Error si se usa fuera del User_Provider
 */
export const use_user_context = (): User_Context_Type => {
    const context = useContext(User_Context);
    if (context === undefined) {
        throw new Error('use_user_context debe usarse dentro de un User_Provider');
    }
    return context;
};

/**
 * Hook de conveniencia para obtener el ID externo del usuario actual.
 * Útil para pasar a otros hooks como use_notifications.
 */
export const use_current_user_id = (): string => {
    const { user } = use_user_context();
    return user?.external_id || DEFAULT_USER_EXTERNAL_ID;
};
