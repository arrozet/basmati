import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { use_page_title } from '../hooks/use_page_title';

/**
 * Página de inicio de sesión accesible.
 * Usa formulario semántico con labels asociados y autocomplete.
 */
export const Login_Page = () => {
    use_page_title('Login');
    const navigate = useNavigate();
    const [username, set_username] = useState('user_dev_1');
    const [password, set_password] = useState('');
    const [remember_me, set_remember_me] = useState(false);

    const handle_login = (e: React.FormEvent) => {
        e.preventDefault();
        // Mock login
        navigate('/dashboard');
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
                        placeholder="usuario_dev_1" 
                        value={username}
                        onChange={(e) => set_username(e.target.value)}
                        autoComplete="username"
                        required
                        id="login-username"
                    />
                    <Neo_Input 
                        label="Contraseña" 
                        type="password" 
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => set_password(e.target.value)}
                        autoComplete="current-password"
                        required
                        id="login-password"
                    />
                    
                    <div className="flex items-center justify-between text-sm mt-2 flex-wrap gap-2">
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input 
                                type="checkbox" 
                                className="accent-basmati-black w-4 h-4 focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2" 
                                checked={remember_me}
                                onChange={(e) => set_remember_me(e.target.checked)}
                                id="remember-me"
                                aria-label="Recordar sesión"
                            />
                            <span>Recordarme</span>
                        </label>
                        <a 
                            href="#" 
                            className="text-basmati-blue hover:underline font-bold focus:outline-none focus:ring-2 focus:ring-basmati-blue focus:ring-offset-2 rounded px-1"
                            aria-label="Recuperar contraseña olvidada"
                        >
                            ¿Olvidaste tu contraseña?
                        </a>
                    </div>

                    <Neo_Button type="submit" className="mt-4 w-full">
                        Iniciar sesión
                    </Neo_Button>
                </form>

                <div className="relative my-4" role="separator" aria-label="O continúa con">
                     <div className="absolute inset-0 flex items-center" aria-hidden="true">
                        <div className="w-full border-t-3 border-gray-200"></div>
                     </div>
                     <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-gray-500 font-bold">O continúa con</span>
                     </div>
                </div>

                <div className="grid grid-cols-2 gap-4" role="group" aria-label="Opciones de inicio de sesión con terceros">
                    <Neo_Button variant="secondary" type="button" aria-label="Iniciar sesión con Google">
                        Google
                    </Neo_Button>
                    <Neo_Button variant="secondary" type="button" aria-label="Iniciar sesión con GitHub">
                        GitHub
                    </Neo_Button>
                </div>
            </Neo_Card>
        </div>
    );
};

