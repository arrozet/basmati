import axios from 'axios';

const API_URL = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:8000';

// Clave para el token en localStorage (debe coincidir con auth_service.ts)
const TOKEN_KEY = 'basmati_auth_token';

export const api_client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Interceptor para agregar el token de autenticación a todas las peticiones.
 * Si hay un token guardado, lo agrega como Bearer token en el header Authorization.
 */
api_client.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(TOKEN_KEY);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * Interceptor para manejar errores de autenticación.
 * Si recibe un 401, limpia el token y redirige al login.
 */
api_client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // No limpiar token si estamos en el proceso de autenticación
            const request_url = error.config?.url || '';
            const is_auth_request = request_url.includes('/auth/token') || 
                                    request_url.includes('/auth/google') ||
                                    request_url.includes('/auth/verify');
            
            if (!is_auth_request) {
                // Token inválido o expirado - limpiar solo si no es petición de auth
                localStorage.removeItem(TOKEN_KEY);
                localStorage.removeItem('basmati_user');
                
                // Solo redirigir si no estamos ya en login o callback
                const current_path = window.location.pathname;
                if (!current_path.includes('/login') && !current_path.includes('/auth/callback')) {
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    }
);

