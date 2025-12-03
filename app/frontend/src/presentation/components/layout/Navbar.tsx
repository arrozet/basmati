import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faBars } from '@fortawesome/free-solid-svg-icons';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Input } from '../ui/Neo_Input';

interface NavbarProps {
    onMenuClick?: () => void;
}

/**
 * Barra de navegación principal accesible.
 * Usa elemento semántico <nav> con landmarks ARIA apropiados.
 */
export const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
    const [search_query, set_search_query] = useState("");
    const [menu_open, set_menu_open] = useState(false);
    const navigate = useNavigate();

    const handle_menu_click = () => {
        set_menu_open(!menu_open);
        onMenuClick?.();
    };

    const handle_search = (e: React.FormEvent) => {
        e.preventDefault();
        if (search_query.trim()) {
            navigate(`/search?q=${encodeURIComponent(search_query)}`);
        }
    };

    return (
        <nav 
            className="h-16 border-b-3 border-basmati-black bg-white flex items-center justify-between px-4 md:px-6 sticky top-0 z-50"
            role="navigation"
            aria-label="Navegación principal"
        >
            <div className="flex items-center gap-4">
                <button 
                    type="button"
                    onClick={handle_menu_click}
                    className="md:hidden p-2 font-bold border-3 border-basmati-black shadow-hard active:shadow-none active:translate-x-[2px] active:translate-y-[2px] transition-all focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 hover:bg-basmati-yellow"
                    aria-label={menu_open ? "Cerrar menú de navegación" : "Abrir menú de navegación"}
                    aria-expanded={menu_open}
                    aria-controls="sidebar-menu"
                >
                    <FontAwesomeIcon icon={faBars} className="text-xl" />
                </button>
                <Link 
                    to="/dashboard"
                    className="flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 p-1 rounded-sm group"
                    aria-label="Ir a página principal de Basmati"
                >
                    <img src="/favicon.webp" alt="" className="h-6 w-6 md:h-8 md:w-8 object-contain" />
                    <span className="text-lg md:text-xl font-bold tracking-tight hover:text-basmati-yellow transition-colors lowercase">
                        basmati
                    </span>
                </Link>
            </div>

            <div className="flex-1 max-w-xl mx-4 hidden md:block">
                <form onSubmit={handle_search} role="search" aria-label="Buscar eventos y calendarios">
                    <Neo_Input 
                        placeholder="Buscar evento..." 
                        className="w-full h-10"
                        value={search_query}
                        onChange={(e) => set_search_query(e.target.value)}
                        aria-label="Campo de búsqueda"
                        type="search"
                    />
                </form>
            </div>

            {/* Mobile Search Icon */}
            <button 
                type="button"
                className="md:hidden p-2 mr-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 rounded hover:bg-basmati-yellow/20 transition-colors"
                onClick={() => navigate('/search')}
                aria-label="Ir a página de búsqueda"
            >
                <FontAwesomeIcon icon={faSearch} className="text-xl" />
            </button>

            <div className="flex items-center gap-2 md:gap-4">
                <Link to="/settings">
                    <Neo_Button 
                        variant="secondary" 
                        className="px-3 py-1 text-sm md:text-base md:px-4"
                        aria-label="Ver configuración de perfil y notificaciones"
                    >
                        Mi perfil
                    </Neo_Button>
                </Link>
            </div>
        </nav>
    );
};
