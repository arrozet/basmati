import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';

export const Login_Page = () => {
    const navigate = useNavigate();

    const handle_login = (e: React.FormEvent) => {
        e.preventDefault();
        // Mock login
        navigate('/dashboard');
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-basmati-bg p-4">
            <Neo_Card className="w-full max-w-md flex flex-col gap-6 bg-white">
                <div className="text-center">
                    <h1 className="text-4xl font-black uppercase mb-2">Basmati</h1>
                    <p className="text-gray-600">Organiza tu caos.</p>
                </div>

                <form onSubmit={handle_login} className="flex flex-col gap-4">
                    <Neo_Input 
                        label="Usuario" 
                        placeholder="usuario_dev_1" 
                        defaultValue="user_dev_1"
                    />
                    <Neo_Input 
                        label="Contraseña" 
                        type="password" 
                        placeholder="••••••••" 
                    />
                    
                    <div className="flex items-center justify-between text-sm mt-2">
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" className="accent-basmati-black w-4 h-4" />
                            <span>Recordarme</span>
                        </label>
                        <a href="#" className="text-basmati-blue hover:underline font-bold">¿Olvidaste tu contraseña?</a>
                    </div>

                    <Neo_Button type="submit" className="mt-4 w-full">
                        Iniciar sesión
                    </Neo_Button>
                </form>

                <div className="relative my-4">
                     <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t-3 border-gray-200"></div>
                     </div>
                     <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-gray-500 font-bold">O continúa con</span>
                     </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <Neo_Button variant="secondary" type="button">Google</Neo_Button>
                    <Neo_Button variant="secondary" type="button">GitHub</Neo_Button>
                </div>
            </Neo_Card>
        </div>
    );
};

