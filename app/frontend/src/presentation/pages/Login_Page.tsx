import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { use_page_title } from '../hooks/use_page_title';
import { use_user_context } from '../context/UserContext';

/**
 * Página de inicio de sesión simplificada para desarrollo.
 * Solo requiere el external_id del usuario (sin contraseña).
 * Valida que el usuario exista en la base de datos.
 */
export const Login_Page = () => {
    use_page_title('Login');
    const navigate = useNavigate();
    const { switch_user } = use_user_context();
    const [username, set_username] = useState('');
    const [loading, set_loading] = useState(false);
    const [error, set_error] = useState<string | null>(null);

    const handle_login = async (e: React.FormEvent) => {
        e.preventDefault();
        set_error(null);
        set_loading(true);

        try {
            // switch_user valida que el usuario existe y actualiza el contexto
            await switch_user(username.trim());
            // Navegar al dashboard
            navigate('/dashboard');
        } catch (err: any) {
            console.error('Error al iniciar sesión:', err);
            if (err.response?.status === 404) {
                set_error('Usuario no encontrado. Por favor, usa uno de los usuarios registrados.');
            } else {
                set_error('Error al verificar el usuario. Inténtalo de nuevo.');
            }
        } finally {
            set_loading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-basmati-bg p-4">
            <Neo_Card className="w-full max-w-md flex flex-col gap-6 bg-white">
                <header className="text-center">
                    <h1 className="text-4xl font-black uppercase mb-2">Basmati</h1>
                    <p className="text-gray-600">Organiza tu caos.</p>
                </header>

                <form onSubmit={handle_login} className="flex flex-col gap-4" aria-label="Formulario de inicio de sesión">
                    <Neo_Input 
                        label="Usuario" 
                        placeholder="Ej: user_dev_1, user_dev_2" 
                        value={username}
                        onChange={(e) => set_username(e.target.value)}
                        autoComplete="username"
                        required
                        id="login-username"
                        helper_text="Introduce el external_id de un usuario existente"
                    />
                    
                    {error && (
                        <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-2 rounded" role="alert">
                            {error}
                        </div>
                    )}

                    <Neo_Button type="submit" className="mt-4 w-full" loading={loading} disabled={loading}>
                        {loading ? 'Verificando...' : 'Iniciar sesión'}
                    </Neo_Button>
                </form>

                <div className="relative my-4" role="separator" aria-label="Usuarios de desarrollo disponibles">
                     <div className="absolute inset-0 flex items-center" aria-hidden="true">
                        <div className="w-full border-t-3 border-gray-200"></div>
                     </div>
                     <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-gray-500 font-bold">Usuarios disponibles</span>
                     </div>
                </div>

                <div className="space-y-2 text-sm">
                    <p className="text-gray-600 text-center mb-3">
                        Para probar la aplicación, usa uno de estos usuarios:
                    </p>
                    <div className="grid grid-cols-1 gap-2">
                        <button
                            type="button"
                            onClick={() => set_username('user_dev_1')}
                            className="text-left p-3 border-2 border-gray-200 rounded hover:border-basmati-yellow hover:bg-basmati-yellow/10 transition-all"
                        >
                            <span className="font-bold text-basmati-black">user_dev_1</span>
                            <span className="text-gray-500 text-xs block">matemes897@badfist.com</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => set_username('user_dev_2')}
                            className="text-left p-3 border-2 border-gray-200 rounded hover:border-basmati-blue hover:bg-basmati-blue/10 transition-all"
                        >
                            <span className="font-bold text-basmati-black">user_dev_2</span>
                            <span className="text-gray-500 text-xs block">mbduz@comfythings.com</span>
                        </button>
                    </div>
                </div>
            </Neo_Card>
        </div>
    );
};

