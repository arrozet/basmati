import React from 'react';
import { Link } from 'react-router-dom';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Input } from '../ui/Neo_Input';

export const Navbar = () => {
    return (
        <nav className="h-16 border-b-3 border-basmati-black bg-white flex items-center justify-between px-6 sticky top-0 z-50">
            <div className="flex items-center gap-4">
                <Link to="/" className="text-2xl font-black tracking-tighter uppercase hover:text-basmati-yellow transition-colors">
                    Basmati
                </Link>
            </div>

            <div className="flex-1 max-w-xl mx-4">
                <Neo_Input 
                    placeholder="Buscar eventos, calendarios..." 
                    className="w-full h-10" 
                />
            </div>

            <div className="flex items-center gap-4">
                <Neo_Button variant="secondary" className="px-4 py-1">
                    Mi Perfil
                </Neo_Button>
                <Neo_Button variant="primary" className="px-4 py-1">
                    Notificaciones
                </Neo_Button>
            </div>
        </nav>
    );
};

