import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Input } from '../ui/Neo_Input';

interface NavbarProps {
    onMenuClick?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
    const [search_query, set_search_query] = useState("");
    const navigate = useNavigate();

    const handle_search = (e: React.FormEvent) => {
        e.preventDefault();
        if (search_query.trim()) {
            navigate(`/search?q=${encodeURIComponent(search_query)}`);
        }
    };

    return (
        <nav className="h-16 border-b-3 border-basmati-black bg-white flex items-center justify-between px-4 md:px-6 sticky top-0 z-50">
            <div className="flex items-center gap-4">
                <button 
                    onClick={onMenuClick}
                    className="md:hidden p-2 font-bold border-3 border-basmati-black shadow-hard active:shadow-none active:translate-x-[2px] active:translate-y-[2px] transition-all"
                >
                    ☰
                </button>
                <Link to="/" className="text-xl md:text-2xl font-black tracking-tighter uppercase hover:text-basmati-yellow transition-colors">
                    Basmati
                </Link>
            </div>

            <div className="hidden md:block flex-1 max-w-xl mx-4">
                <form onSubmit={handle_search}>
                    <Neo_Input 
                        placeholder="Buscar eventos, calendarios..." 
                        className="w-full h-10"
                        value={search_query}
                        onChange={(e) => set_search_query(e.target.value)}
                    />
                </form>
            </div>

            <div className="flex items-center gap-2 md:gap-4">
                <Neo_Button variant="secondary" className="px-3 py-1 text-sm md:text-base md:px-4">
                    Mi perfil
                </Neo_Button>
                <Neo_Button variant="primary" className="hidden md:block px-4 py-1">
                    Notificaciones
                </Neo_Button>
            </div>
        </nav>
    );
};
