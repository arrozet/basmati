/**
 * Servicio de autenticación para manejar OAuth con Google.
 * 
 * Proporciona métodos para iniciar el flujo OAuth, manejar callbacks,
 * y gestionar el token de sesión.
 */

import { api_client } from '../api/axios_client';

// Clave para almacenar el token en localStorage
const TOKEN_KEY = 'basmati_auth_token';
const USER_KEY = 'basmati_user';

export interface AuthUser {
    external_id: string;
    email: string;
    display_name: string;
    avatar_url: string | null;
    provider: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: AuthUser;
    is_new_user: boolean;
}

/**
 * Obtiene la URL para iniciar el login con Google.
 * @param redirect_to URL a la que redirigir después del login
 */
export async function get_google_login_url(redirect_to: string = '/dashboard'): Promise<string> {
    const response = await api_client.get('/v1/auth/google', {
        params: { redirect_to }
    });
    return response.data.auth_url;
}

/**
 * Verifica un ID token de Google y obtiene un token de sesión.
 * @param id_token Token de Google
 */
export async function verify_google_token(id_token: string): Promise<TokenResponse> {
    const response = await api_client.post('/v1/auth/google/verify', {
        id_token
    });
    return response.data;
}

/**
 * Guarda el token de autenticación en localStorage.
 * @param token Token JWT de sesión
 */
export function save_token(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Obtiene el token de autenticación de localStorage.
 */
export function get_token(): string | null {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Elimina el token de autenticación de localStorage.
 */
export function remove_token(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

/**
 * Guarda la información del usuario en localStorage.
 * @param user Datos del usuario autenticado
 */
export function save_user(user: AuthUser): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Obtiene la información del usuario de localStorage.
 */
export function get_stored_user(): AuthUser | null {
    const user_json = localStorage.getItem(USER_KEY);
    if (user_json) {
        try {
            return JSON.parse(user_json);
        } catch {
            return null;
        }
    }
    return null;
}

/**
 * Verifica si hay un usuario autenticado.
 */
export function is_authenticated(): boolean {
    return get_token() !== null;
}

/**
 * Cierra la sesión del usuario.
 */
export async function logout(): Promise<void> {
    try {
        await api_client.post('/v1/auth/logout');
    } catch {
        // Ignorar errores del servidor, limpiar localmente de todos modos
    }
    remove_token();
}

/**
 * Parsea el token del callback URL.
 * @param url_search La query string de la URL
 */
export function parse_callback_params(url_search: string): {
    token: string | null;
    is_new_user: boolean;
    redirect_to: string;
} {
    const params = new URLSearchParams(url_search);
    return {
        token: params.get('token'),
        is_new_user: params.get('new_user') === 'true',
        redirect_to: params.get('redirect_to') || '/dashboard'
    };
}
