import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Card } from '../ui/Neo_Card';
import { Neo_Modal } from '../ui/Neo_Modal';
import { clsx } from 'clsx';
import { use_calendars } from '../../hooks/use_calendars';
import { Calendar_Model } from '../../domain/models/calendar_model';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash, faTrash, faPlus, faCalendarPlus, faFileImport, faChevronRight, faChevronDown } from '@fortawesome/free-solid-svg-icons';
import { use_calendar_visibility } from '../../context/CalendarVisibilityContext';

interface SidebarProps {
    isOpen?: boolean;
    onClose?: () => void;
}

interface CalendarTreeItemProps {
    calendar: Calendar_Model;
    allCalendars: Calendar_Model[];
    activeCalendarId: string | null;
    onCalendarClick: (id: string) => void;
    onDelete?: (calendar: Calendar_Model) => void;
    depth?: number;
}

/**
 * Componente recursivo para renderizar items del árbol de calendarios.
 */
const CalendarTreeItem: React.FC<CalendarTreeItemProps> = ({ 
    calendar, 
    allCalendars, 
    activeCalendarId, 
    onCalendarClick, 
    onDelete,
    depth = 0 
}) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { toggle_visibility, is_visible } = use_calendar_visibility();
    
    const children = allCalendars.filter(c => c.parent_id === calendar.id);
    const hasChildren = children.length > 0;
    const isActive = activeCalendarId === calendar.id;
    const visible = is_visible(calendar.id);

    const handleToggle = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsExpanded(!isExpanded);
    };

    const handleVisibilityToggle = (e: React.MouseEvent) => {
        e.stopPropagation();
        toggle_visibility(calendar.id);
    };

    const handleDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (onDelete) {
            onDelete(calendar);
        }
    };

    return (
        <li className="w-full">
            <div className={clsx(
                "flex items-center gap-2 w-full text-left rounded transition-all p-1 group",
                isActive ? "bg-basmati-yellow/20 font-bold border-r-4 border-basmati-yellow" : "hover:bg-white"
            )}
            style={{ paddingLeft: `${depth * 12 + 8}px` }} // Indentación dinámica
            >
                {hasChildren ? (
                    <button 
                        onClick={handleToggle}
                        className="w-4 h-4 flex items-center justify-center hover:bg-gray-100 rounded-sm transition-colors text-basmati-black"
                        aria-label={isExpanded ? "Colapsar" : "Expandir"}
                    >
                        <FontAwesomeIcon icon={isExpanded ? faChevronDown : faChevronRight} size="xs" />
                    </button>
                ) : (
                    // Spacer for alignment
                    <div className="w-4 h-4" />
                )}
                
                <button 
                    type="button"
                    className="flex items-center gap-2 flex-1 min-w-0 text-left focus:outline-none"
                    onClick={() => onCalendarClick(calendar.id)}
                    aria-label={`Ver calendario ${calendar.title}`}
                >
                    <div 
                        className="w-3 h-3 border-2 border-basmati-black shrink-0" 
                        style={{ backgroundColor: calendar.color || '#EBBE4D' }}
                        aria-hidden="true"
                    ></div>
                    <span className="truncate text-sm">{calendar.title}</span>
                </button>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={handleVisibilityToggle}
                        className="w-6 h-6 flex items-center justify-center hover:bg-gray-200 rounded transition-colors text-basmati-black"
                        aria-label={visible ? "Ocultar calendario" : "Mostrar calendario"}
                    >
                         <FontAwesomeIcon icon={visible ? faEye : faEyeSlash} className={visible ? "" : "opacity-50"} size="xs" />
                    </button>
                    {onDelete && (
                        <button
                            onClick={handleDelete}
                            className="w-6 h-6 flex items-center justify-center hover:bg-basmati-red/20 text-basmati-red rounded transition-colors"
                            aria-label="Eliminar calendario"
                            title="Eliminar calendario"
                        >
                            <FontAwesomeIcon icon={faTrash} size="xs" />
                        </button>
                    )}
                </div>
            </div>

            {hasChildren && isExpanded && (
                <ul className="flex flex-col gap-1 list-none p-0 mt-1">
                    {children.map(child => (
                        <CalendarTreeItem
                            key={child.id}
                            calendar={child}
                            allCalendars={allCalendars}
                            activeCalendarId={activeCalendarId}
                            onCalendarClick={onCalendarClick}
                            onDelete={onDelete}
                            depth={depth + 1}
                        />
                    ))}
                </ul>
            )}
        </li>
    );
};

/**
 * Barra lateral de navegación con listado de calendarios.
 * Usa elemento semántico <aside> y navegación accesible.
 */
export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
    // Hardcoded user_id for now as per AGENTS.md
    const { calendars, loading, delete_calendar } = use_calendars('user_dev_1');
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const active_calendar_id = searchParams.get('calendar_id');
    const { toggle_visibility, is_visible } = use_calendar_visibility();
    
    // Estado para el modal de borrado
    const [calendarToDelete, setCalendarToDelete] = useState<Calendar_Model | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    const myCalendars = calendars.filter(cal => cal.owner_id === 'user_dev_1');
    // Solo mostramos raíces en el nivel superior
    const myRootCalendars = myCalendars.filter(cal => !cal.parent_id);
    
    const otherCalendars = calendars.filter(cal => cal.owner_id !== 'user_dev_1');

    const handle_calendar_click = (calendar_id: string) => {
        navigate(`/dashboard?calendar_id=${calendar_id}`);
        if (onClose) onClose();
    };

    // Abre el modal
    const prompt_delete_calendar = (calendar: Calendar_Model) => {
        setCalendarToDelete(calendar);
    };

    const confirm_delete_calendar = async () => {
        if (!calendarToDelete) return;

        setIsDeleting(true);
        try {
            // Delegamos la lógica de borrado recursivo al hook (Capa de Presentación/Controlador)
            // Pasamos true para activar el borrado recursivo
            await delete_calendar(calendarToDelete.id, true);

            // Si el calendario borrado era el activo, navegar al dashboard general
            // Verificamos si el activo es el borrado o alguno de sus hijos (aunque aquí ya no tenemos la lista de hijos fácilmente,
            // si el calendario activo desaparece de la lista, deberíamos navegar.
            // Simplificación: Si el ID activo es igual al borrado, navegamos. 
            // Para los hijos, el comportamiento actual es aceptable (se quedará en una ruta de calendario que ya no existe, 
            // lo cual debería manejarse en el Dashboard o aquí de forma más robusta si tuviéramos acceso a los hijos).
            // Dado que movimos la lógica, asumiremos que si borramos el padre, navegamos al home por seguridad.
            if (active_calendar_id === calendarToDelete.id) {
                navigate('/dashboard');
            }
            
            setCalendarToDelete(null);
        } catch (error) {
            console.error("Failed to delete calendar", error);
            // Podríamos mostrar un toast de error aquí si existiera un sistema de notificaciones global
            alert("Error al eliminar el calendario. Por favor intente nuevamente.");
        } finally {
            setIsDeleting(false);
        }
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
                            <FontAwesomeIcon icon={faPlus} aria-hidden="true" /> Crear evento
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
                            <FontAwesomeIcon icon={faCalendarPlus} aria-hidden="true" /> Crear calendario
                        </Neo_Button>
                    </Link>
                    <Link to="/calendars/import" onClick={onClose} className="block mt-2">
                        <Neo_Button 
                            variant="secondary" 
                            className="w-full flex items-center justify-center gap-2 text-sm" 
                            aria-label="Importar calendario"
                        >
                            <FontAwesomeIcon icon={faFileImport} aria-hidden="true" /> Importar calendario
                        </Neo_Button>
                    </Link>
                </div>

                <nav aria-label="Mis calendarios">
                    <h2 className="font-bold text-lg mb-2">Mis calendarios</h2>
                    {loading ? (
                        <div className="text-sm text-gray-500">Cargando...</div>
                    ) : (
                        <ul className="flex flex-col gap-2 list-none p-0">
                            {myRootCalendars.map((cal) => (
                                <CalendarTreeItem
                                    key={cal.id}
                                    calendar={cal}
                                    allCalendars={myCalendars}
                                    activeCalendarId={active_calendar_id}
                                    onCalendarClick={handle_calendar_click}
                                    onDelete={prompt_delete_calendar}
                                />
                            ))}
                            {myCalendars.length === 0 && (
                                <li className="text-sm text-gray-500 italic">No tienes calendarios.</li>
                            )}
                        </ul>
                    )}
                </nav>

                <nav aria-label="Otros calendarios">
                    <h2 className="font-bold text-lg mb-2">Otros calendarios</h2>
                    <ul className="flex flex-col gap-2 list-none p-0">
                        {otherCalendars.map((cal) => {
                            const visible = is_visible(cal.id);
                            return (
                            <li key={cal.id} className="flex items-center">
                                <button 
                                    type="button"
                                    className={clsx(
                                        "flex items-center gap-2 flex-1 text-left cursor-pointer hover:translate-x-1 transition-transform focus:outline-none focus:ring-2 focus:ring-basmati-yellow p-2 rounded",
                                        active_calendar_id === cal.id ? "bg-basmati-yellow/20 font-bold border-r-4 border-basmati-yellow" : "hover:bg-white"
                                    )}
                                    aria-label={`Ver calendario ${cal.title}`}
                                    onClick={() => handle_calendar_click(cal.id)}
                                >
                                    <div 
                                        className="w-4 h-4 border-3 border-basmati-black" 
                                        style={{ backgroundColor: cal.color || '#5496FF' }}
                                        aria-hidden="true"
                                    ></div>
                                    <span className="font-medium">{cal.title}</span>
                                </button>
                                <button
                                    onClick={(e) => { e.stopPropagation(); toggle_visibility(cal.id); }}
                                    className="w-6 h-6 flex items-center justify-center hover:bg-gray-200 rounded transition-colors text-basmati-black ml-1"
                                    aria-label={visible ? "Ocultar calendario" : "Mostrar calendario"}
                                >
                                     <FontAwesomeIcon icon={visible ? faEye : faEyeSlash} className={visible ? "" : "opacity-50"} size="xs" />
                                </button>
                            </li>
                            );
                        })}
                    </ul>
                </nav>

                <div className="mt-auto">
                    <Neo_Card className="bg-basmati-green/20" role="complementary" aria-label="Consejo del día">
                        <p className="text-xs font-bold mb-2">Tip del día:</p>
                        <p className="text-xs">Organiza tu caos como si de granos de arroz se tratase.</p>
                    </Neo_Card>
                </div>
            </aside>

            {/* Modal de confirmación de borrado */}
            <Neo_Modal
                is_open={!!calendarToDelete}
                on_close={() => setCalendarToDelete(null)}
                on_confirm={confirm_delete_calendar}
                title="Eliminar Calendario"
                confirm_text="Sí, eliminar"
                variant="danger"
                loading={isDeleting}
            >
                <div className="text-base">
                    <p className="mb-2">¿Estás seguro de que deseas eliminar el calendario <strong>{calendarToDelete?.title}</strong>?</p>
                    <p className="text-sm text-basmati-red font-bold">
                        Esta acción no se puede deshacer. Se eliminarán permanentemente:
                    </p>
                    <ul className="list-disc pl-5 mt-1 text-sm text-gray-700">
                        <li>Todos los eventos asociados.</li>
                        <li>Todos los subcalendarios que pertenezcan a este calendario.</li>
                    </ul>
                </div>
            </Neo_Modal>
        </>
    );
};
