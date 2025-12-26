import { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Neo_Card } from '../components/ui/Neo_Card';
import { use_page_title } from '../hooks/use_page_title';
import { use_user_context } from '../context/UserContext';
import { 
    parse_callback_params, 
    exchange_auth_code,
    save_token, 
    save_user,
    save_google_token
} from '../../infrastructure/services/auth_service';

/**
 * Página de callback para OAuth.
 * 
 * Esta página recibe el auth_code del backend después del flujo OAuth,
 * lo intercambia por un token JWT, y guarda la sesión antes de redirigir.
 */
export const Auth_Callback_Page = () => {
    use_page_title('Autenticando...');
    const navigate = useNavigate();
    const location = useLocation();
    const { refresh } = use_user_context();
    const [status, set_status] = useState<'processing' | 'success' | 'error'>('processing');
    const [error_message, set_error_message] = useState<string | null>(null);
    
    // Ref para evitar ejecuciones duplicadas (React StrictMode)
    const is_processing = useRef(false);

    useEffect(() => {
        const process_callback = async () => {
            // Evitar ejecuciones duplicadas
            if (is_processing.current) {
                console.log('⏳ Ya se está procesando el callback, ignorando...');
                return;
            }
            is_processing.current = true;
            
            try {
                console.log('🔐 Procesando callback OAuth...', location.search);
                
                // Parsear parámetros de la URL
                const { auth_code, is_new_user, redirect_to } = parse_callback_params(location.search);
                
                console.log('Auth code recibido:', auth_code ? '✅' : '❌');
                console.log('Redirect to:', redirect_to);

                if (!auth_code) {
                    throw new Error('No se recibió código de autenticación');
                }

                // Intercambiar auth_code por token JWT
                console.log('🔄 Intercambiando código por token...');
                const token_response = await exchange_auth_code(auth_code);
                
                console.log('Token obtenido:', token_response.access_token ? '✅' : '❌');

                // Guardar token ANTES de cualquier otra operación
                save_token(token_response.access_token);
                console.log('💾 Token guardado en localStorage');

                // Guardar el token de Google si está disponible (para importar calendarios)
                if (token_response.google_access_token) {
                    save_google_token(token_response.google_access_token);
                    console.log('💾 Google token guardado para importaciones');
                }

                // Guardar información del usuario
                save_user(token_response.user);

                // Refrescar el contexto de usuario con el external_id
                await refresh(token_response.user.external_id);

                set_status('success');

                // Mostrar mensaje de bienvenida si es nuevo usuario
                if (is_new_user || token_response.is_new_user) {
                    console.log('¡Bienvenido! Tu cuenta ha sido creada.');
                }

                // Redirigir después de un pequeño delay
                setTimeout(() => {
                    navigate(redirect_to, { replace: true });
                }, 500);

            } catch (err: any) {
                console.error('Error en callback de autenticación:', err);
                set_status('error');
                set_error_message(err.message || 'Error al procesar la autenticación');
            }
        };

        process_callback();
    }, [location.search, navigate, refresh]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-basmati-bg p-4">
            <Neo_Card className="w-full max-w-md flex flex-col gap-6 bg-white text-center">
                {status === 'processing' && (
                    <>
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-basmati-yellow mx-auto"></div>
                        <h1 className="text-2xl font-bold">Autenticando...</h1>
                        <p className="text-gray-600">Por favor espera mientras verificamos tu identidad.</p>
                    </>
                )}

                {status === 'success' && (
                    <>
                        <div className="text-green-500 text-5xl">✓</div>
                        <h1 className="text-2xl font-bold text-green-600">¡Autenticación exitosa!</h1>
                        <p className="text-gray-600">Redirigiendo...</p>
                    </>
                )}

                {status === 'error' && (
                    <>
                        <div className="text-red-500 text-5xl">✗</div>
                        <h1 className="text-2xl font-bold text-red-600">Error de autenticación</h1>
                        <p className="text-gray-600">{error_message}</p>
                        <button
                            onClick={() => navigate('/login', { replace: true })}
                            className="mt-4 px-4 py-2 bg-basmati-yellow rounded-lg font-bold hover:bg-basmati-yellow/80"
                        >
                            Volver al login
                        </button>
                    </>
                )}
            </Neo_Card>
        </div>
    );
};
