/**
 * Configuración de usuarios de desarrollo.
 * 
 * Los valores se obtienen de las variables de entorno de Vite (.env)
 * o usan valores por defecto si no están configurados.
 */

export interface Dev_User_Config {
    id: string;
    email: string;
    display_name: string;
}

/**
 * Usuario de desarrollo 1 (principal).
 */
export const DEV_USER_1: Dev_User_Config = {
    id: 'user_dev_1',
    email: import.meta.env.VITE_DEV_USER_1_EMAIL || 'amcgil@uma.es',
    display_name: 'Usuario Desarrollo 1'
};

/**
 * Usuario de desarrollo 2 (secundario).
 */
export const DEV_USER_2: Dev_User_Config = {
    id: 'user_dev_2',
    email: import.meta.env.VITE_DEV_USER_2_EMAIL || 'rubenoliva@uma.es',
    display_name: 'Usuario Desarrollo 2'
};

/**
 * Usuario de desarrollo 3 (para pruebas de digest).
 */
export const DEV_USER_3: Dev_User_Config = {
    id: 'user_dev_3',
    email: import.meta.env.VITE_DEV_USER_3_EMAIL || 'bamasti-dailydigest@yopmail.com',
    display_name: 'Usuario Resumen Diario'
};

/**
 * Lista de todos los usuarios de desarrollo disponibles.
 */
export const DEV_USERS: Dev_User_Config[] = [DEV_USER_1, DEV_USER_2, DEV_USER_3];
