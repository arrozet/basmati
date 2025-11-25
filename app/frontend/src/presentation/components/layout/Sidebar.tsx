import React from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Card } from '../ui/Neo_Card';
import { clsx } from 'clsx';
import { use_user_calendars } from '../../hooks/use_user_calendars';

interface SidebarProps {
    isOpen?: boolean;
    onClose?: () => void;
}

/**
 * Barra lateral de navegación con listado de calendarios.
 * Usa elemento semántico <aside> y navegación accesible.
 */
export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
    // Hardcoded user_id for now as per AGENTS.md
    const { calendars, loading } = use_user_calendars('user_dev_1');
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const active_calendar_id = searchParams.get('calendar_id');

    const handle_calendar_click = (calendar_id: string) => {
        navigate(`/dashboard?calendar_id=${calendar_id}`);
        if (onClose) onClose();
    };

    const createEventLink = active_calendar_id 
        ? `/events/new?calendar_id=${active_calendar_id}` 
        : '/events/new';

    return (
        <>
            {/* Overlay for mobile */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-30 md:hidden"
                    onClick={onClose}
                    aria-hidden="true"
                />
            )}

            <aside 
                className={clsx(
                    "fixed md:sticky top-16 h-[calc(100vh-64px)] w-64 border-r-3 border-basmati-black bg-basmati-bg p-4 flex flex-col gap-6 overflow-y-auto transition-transform duration-300 z-40",
                    "md:translate-x-0", // Always visible on desktop
                    isOpen ? "translate-x-0" : "-translate-x-full" // Toggle on mobile
                )}
                aria-label="Menú lateral de calendarios"
                id="sidebar-menu"
            >
                
                <div>
                    <Link to={createEventLink} onClick={onClose}>
                        <Neo_Button className="w-full flex items-center justify-center gap-2" aria-label="Crear nuevo evento">
                            <span aria-hidden="true">+</span> Crear evento
                        </Neo_Button>
                    </Link>
                </div>

                <div>
                    <Link to="/calendars/new" onClick={onClose}>
                        <Neo_Button 
                            variant="secondary" 
                            className="w-full flex items-center justify-center gap-2" 
                            aria-label="Crear nuevo calendario"
                        >
                            <span aria-hidden="true">+</span> Crear calendario
                        </Neo_Button>
                    </Link>
                    <Link to="/calendars/import" onClick={onClose} className="block mt-2">
                        <Neo_Button 
                            variant="secondary" 
                            className="w-full flex items-center justify-center gap-2 text-sm" 
                            aria-label="Importar calendario"
                        >
                            <span aria-hidden="true">↓</span> Importar calendario
                        </Neo_Button>
                    </Link>
                </div>

                <nav aria-label="Mis calendarios">
                    <h2 className="font-bold text-lg mb-2">Mis calendarios</h2>
                    {loading ? (
                        <div className="text-sm text-gray-500">Cargando...</div>
                    ) : (
                        <ul className="flex flex-col gap-2 list-none p-0">
                            {calendars.map((cal) => (
                                <li key={cal.id}>
                                    <button 
                                        type="button"
                                        className={clsx(
                                            "flex items-center gap-2 w-full text-left cursor-pointer hover:translate-x-1 transition-transform focus:outline-none focus:ring-2 focus:ring-basmati-yellow p-2 rounded",
                                            active_calendar_id === cal.id ? "bg-basmati-yellow/20 font-bold border-r-4 border-basmati-yellow" : "hover:bg-white"
                                        )}
                                        aria-label={`Ver calendario ${cal.title}`}
                                        onClick={() => handle_calendar_click(cal.id)}
                                    >
                                        <div 
                                            className="w-4 h-4 border-3 border-basmati-black" 
                                            style={{ backgroundColor: cal.color || '#EBBE4D' }}
                                            aria-hidden="true"
                                        ></div>
                                        <span className="font-medium truncate">{cal.title}</span>
                                    </button>
                                </li>
                            ))}
                            {calendars.length === 0 && (
                                <li className="text-sm text-gray-500 italic">No tienes calendarios.</li>
                            )}
                        </ul>
                    )}
                </nav>

                <nav aria-label="Otros calendarios">
                    <h2 className="font-bold text-lg mb-2">Otros calendarios</h2>
                    <ul className="flex flex-col gap-2 list-none p-0">
                        {['Festivos', 'Cumpleaños'].map((cal) => (
                            <li key={cal}>
                                <button 
                                    type="button"
                                    className="flex items-center gap-2 w-full text-left cursor-pointer hover:translate-x-1 transition-transform focus:outline-none focus:ring-2 focus:ring-basmati-yellow p-2 rounded hover:bg-white"
                                    aria-label={`Ver calendario ${cal}`}
                                    onClick={onClose}
                                >
                                    <div className="w-4 h-4 border-3 border-basmati-black bg-basmati-blue" aria-hidden="true"></div>
                                    <span className="font-medium">{cal}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="mt-auto">
                    <Neo_Card className="bg-basmati-green/20" role="complementary" aria-label="Consejo del día">
                        <p className="text-xs font-bold mb-2">Tip del día:</p>
                        <p className="text-xs">Organiza tu caos como si de granos de arroz se tratase.</p>
                    </Neo_Card>
                </div>
            </aside>
        </>
    );
};
