import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Neo_Modal } from '../components/ui/Neo_Modal';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronLeft, faChevronRight, faTrash } from '@fortawesome/free-solid-svg-icons';
import { use_calendar_events } from '../hooks/use_calendar_events';
import { Event_Model } from '../../domain/models/event_model';

type ViewType = 'year' | 'month' | 'week' | 'day';

// Helper to get days in month
const get_days_in_month = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
};

// Helper to get day of week of the first day (0-6, 0=Sunday)
const get_first_day_of_month = (year: number, month: number) => {
    let day = new Date(year, month, 1).getDay();
    // Adjust to make Monday = 0, Sunday = 6
    return day === 0 ? 6 : day - 1;
};

const CalendarGrid: React.FC<{ 
    currentDate: Date, 
    view: ViewType, 
    events: Event_Model[],
    onViewChange: (view: ViewType) => void,
    onDateChange: (date: Date) => void,
    onDeleteEvent: (event_id: string) => void
}> = ({ currentDate, view, events, onViewChange, onDateChange, onDeleteEvent }) => {
    const navigate = useNavigate();
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const days_labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    const months_labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    const handle_event_click = (event_id: string) => {
        navigate(`/events/edit/${event_id}`);
    };

    const handle_day_click = (date: Date) => {
        // Format date as YYYY-MM-DD using local time
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        navigate(`/events/new?date=${dateStr}`);
    };

    if (view === 'year') {
        return (
            <section className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4" aria-label="Vista anual del calendario">
                {months_labels.map((m_label, idx) => (
                    <Neo_Card 
                        key={m_label} 
                        className="hover:scale-105 transition-transform cursor-pointer"
                        onClick={() => {
                            const newDate = new Date(currentDate);
                            newDate.setMonth(idx);
                            onDateChange(newDate);
                            onViewChange('month');
                        }}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                const newDate = new Date(currentDate);
                                newDate.setMonth(idx);
                                onDateChange(newDate);
                                onViewChange('month');
                            }
                        }}
                        aria-label={`Ver mes de ${m_label}`}
                    >
                        <h3 className="font-bold text-center mb-2">{m_label}</h3>
                        <div className="grid grid-cols-7 gap-1 text-[0.6rem]" aria-hidden="true">
                            {Array.from({ length: get_days_in_month(year, idx) }).map((_, d_idx) => (
                                <div key={d_idx} className="text-center bg-gray-100 rounded-sm">{d_idx + 1}</div>
                            ))}
                        </div>
                    </Neo_Card>
                ))}
            </section>
        );
    }

    if (view === 'month') {
        const days_in_month = get_days_in_month(year, month);
        const first_day = get_first_day_of_month(year, month);
        const days = [];
        
        // Empty slots for previous month
        for (let i = 0; i < first_day; i++) {
            days.push(<div key={`empty-${i}`} className="bg-gray-50 border-3 border-transparent min-h-[100px] md:min-h-[120px]"></div>);
        }

        // Days of current month
        for (let i = 1; i <= days_in_month; i++) {
            const current_day_date = new Date(year, month, i);
            const day_name = days_labels[current_day_date.getDay() === 0 ? 6 : current_day_date.getDay() - 1];
            const day_events = events.filter(e => {
                const e_date = new Date(e.start_time);
                return e_date.getDate() === i && e_date.getMonth() === month && e_date.getFullYear() === year;
            });

            days.push(
                <div 
                    key={i} 
                    className="bg-white border-3 border-basmati-black shadow-hard p-2 hover:-translate-y-1 hover:shadow-[6px_6px_0px_0px_rgba(26,26,26,1)] transition-all cursor-pointer relative min-h-[80px] md:min-h-[120px] overflow-hidden focus-within:ring-4 focus-within:ring-basmati-yellow"
                    onClick={() => handle_day_click(current_day_date)}
                    role="gridcell"
                    tabIndex={0}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            handle_day_click(current_day_date);
                        }
                    }}
                    aria-label={`${day_name} ${i}, ${day_events.length} evento${day_events.length !== 1 ? 's' : ''}`}
                >
                    <div className="flex justify-between items-start">
                        <span className="md:hidden font-bold text-gray-500 text-xs uppercase">{day_name}</span>
                        <time className="font-bold text-gray-800 absolute top-2 right-2" dateTime={current_day_date.toISOString()}>
                            {i}
                        </time>
                    </div>
                    <div className="mt-6 flex flex-col gap-1">
                        {day_events.map(event => (
                            <div 
                                key={event.id} 
                                className="bg-basmati-yellow border-2 border-basmati-black p-1 pl-2 pr-8 text-xs font-bold truncate shadow-sm hover:bg-basmati-yellow/80 cursor-pointer group relative" 
                                title={event.title}
                                onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                            >
                                <span>{event.title}</span>
                                <button
                                    type="button"
                                    className="absolute right-0.5 top-0 bottom-0 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity bg-basmati-red text-white px-1.5 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-basmati-red focus:opacity-100 z-10"
                                    onClick={(e) => { 
                                        e.stopPropagation(); 
                                        onDeleteEvent(event.id);
                                    }}
                                    aria-label={`Eliminar evento ${event.title}`}
                                    tabIndex={0}
                                >
                                    <FontAwesomeIcon icon={faTrash} className="w-3 h-3" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        return (
            <section className="w-full" aria-label="Vista mensual del calendario">
                <div className="hidden md:grid grid-cols-7 gap-4 mb-4" role="row">
                    {days_labels.map(day => (
                        <div key={day} className="text-center font-black text-xl uppercase" role="columnheader">{day}</div>
                    ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-7 gap-2 md:gap-4" role="grid" aria-label="Días del mes">
                    {days}
                </div>
            </section>
        );
    }

    if (view === 'week') {
        // Calculate week dates
        const start_of_week = new Date(currentDate);
        const day = start_of_week.getDay() || 7; // Make Sunday 7
        start_of_week.setDate(start_of_week.getDate() - (day - 1)); // Set to Monday

        const week_dates = Array.from({ length: 7 }).map((_, i) => {
            const d = new Date(start_of_week);
            d.setDate(d.getDate() + i);
            return d;
        });

        return (
            <section className="grid grid-cols-1 md:grid-cols-7 gap-4 h-auto md:h-[600px]" aria-label="Vista semanal del calendario">
                {week_dates.map((date, idx) => {
                    const day_events = events.filter(e => {
                        const e_date = new Date(e.start_time);
                        return e_date.getDate() === date.getDate() && e_date.getMonth() === date.getMonth() && e_date.getFullYear() === date.getFullYear();
                    });

                    return (
                        <article 
                            key={idx} 
                            className="border-3 border-basmati-black bg-white p-2 flex flex-col cursor-pointer hover:bg-gray-50 transition-colors"
                            onClick={() => handle_day_click(date)}
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    handle_day_click(date);
                                }
                            }}
                            aria-label={`${days_labels[idx]}, ${date.getDate()}, ${day_events.length} evento${day_events.length !== 1 ? 's' : ''}`}
                        >
                            <header className="font-black text-center border-b-3 border-basmati-black pb-2 mb-2">
                                <div className="text-xs uppercase text-gray-500">{days_labels[idx]}</div>
                                <time className="text-xl" dateTime={date.toISOString()}>{date.getDate()}</time>
                            </header>
                            <div className="flex-1 bg-gray-50 relative overflow-y-auto">
                                {day_events.map(event => (
                                    <div 
                                        key={event.id} 
                                        className="bg-basmati-blue/20 border-l-4 border-basmati-blue p-1 pl-2 pr-8 text-xs mb-1 cursor-pointer hover:bg-basmati-blue/30 group relative"
                                        onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                    >
                                        <div className="truncate">
                                            {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - {event.title}
                                        </div>
                                        <button
                                            type="button"
                                            className="absolute right-0.5 top-0 bottom-0 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity bg-basmati-red text-white px-1 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-basmati-red focus:opacity-100 z-10"
                                            onClick={(e) => { 
                                                e.stopPropagation(); 
                                                onDeleteEvent(event.id);
                                            }}
                                            aria-label={`Eliminar evento ${event.title}`}
                                            tabIndex={0}
                                        >
                                            <FontAwesomeIcon icon={faTrash} className="w-3 h-3" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </article>
                    );
                })}
            </section>
        );
    }

    if (view === 'day') {
        const day_events = events.filter(e => {
            const e_date = new Date(e.start_time);
            return e_date.getDate() === currentDate.getDate() && e_date.getMonth() === currentDate.getMonth() && e_date.getFullYear() === currentDate.getFullYear();
        });

        return (
            <section 
                className="border-3 border-basmati-black bg-white p-4 min-h-[600px] cursor-pointer"
                onClick={() => handle_day_click(currentDate)}
                tabIndex={0}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handle_day_click(currentDate);
                    }
                }}
                aria-label={`Vista de día, ${day_events.length} evento${day_events.length !== 1 ? 's' : ''}`}
            >
                <h3 className="font-black text-2xl mb-4">{days_labels[currentDate.getDay() === 0 ? 6 : currentDate.getDay() - 1]} {currentDate.getDate()}</h3>
                <div className="space-y-4">
                    {/* Simple list for now, could be a timeline */}
                    {day_events.length === 0 ? (
                        <p className="text-gray-500 italic">No hay eventos para este día. Haz click para crear uno.</p>
                    ) : (
                        day_events.map(event => (
                            <article 
                                key={event.id} 
                                className="flex gap-4 border-b border-gray-200 py-4 cursor-pointer hover:bg-gray-50 group relative"
                                onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                            >
                                <time className="w-20 font-bold text-gray-500" dateTime={event.start_time.toISOString()}>
                                    {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                </time>
                                <div className="flex-1 bg-basmati-yellow/20 border-l-4 border-basmati-yellow p-2 rounded">
                                    <h4 className="font-bold">{event.title}</h4>
                                    <p className="text-sm">{event.description}</p>
                                </div>
                                <button
                                    type="button"
                                    className="opacity-0 group-hover:opacity-100 transition-opacity self-center"
                                    onClick={(e) => { 
                                        e.stopPropagation(); 
                                        onDeleteEvent(event.id);
                                    }}
                                    aria-label={`Eliminar evento ${event.title}`}
                                >
                                    <Neo_Button variant="danger" className="py-1 px-3">
                                        <FontAwesomeIcon icon={faTrash} />
                                    </Neo_Button>
                                </button>
                            </article>
                        ))
                    )}
                </div>
            </section>
        );
    }

    return null;
};

export const Dashboard_Page = () => {
    const [current_date, set_current_date] = useState(new Date());
    const [view, set_view] = useState<ViewType>('month');
    const { events, loading } = use_calendar_events(current_date, view);
    
    // Modal de confirmación para borrar
    const [delete_modal_open, set_delete_modal_open] = useState(false);
    const [event_to_delete, set_event_to_delete] = useState<{ id: string, title: string } | null>(null);
    const [deleting, set_deleting] = useState(false);

    const handle_delete_request = (event_id: string) => {
        const event = events.find(e => e.id === event_id);
        if (event) {
            set_event_to_delete({ id: event.id, title: event.title });
            set_delete_modal_open(true);
        }
    };

    const handle_confirm_delete = async () => {
        if (!event_to_delete) return;
        
        set_deleting(true);
        try {
            // Simular borrado (no conectado al backend)
            console.log(`Evento ${event_to_delete.id} eliminado visualmente`);
            
            // Esperar un poco para simular la llamada
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Cerrar modal
            set_delete_modal_open(false);
            set_event_to_delete(null);
            
            // Aquí normalmente recargarías los eventos o los eliminarías del estado
            // Por ahora solo mostramos feedback visual
        } catch (error) {
            console.error('Error al eliminar evento:', error);
        } finally {
            set_deleting(false);
        }
    };

    const handle_close_delete_modal = () => {
        if (!deleting) {
            set_delete_modal_open(false);
            set_event_to_delete(null);
        }
    };

    const handle_prev = () => {
        const new_date = new Date(current_date);
        if (view === 'month') new_date.setMonth(new_date.getMonth() - 1);
        if (view === 'year') new_date.setFullYear(new_date.getFullYear() - 1);
        if (view === 'week') new_date.setDate(new_date.getDate() - 7);
        if (view === 'day') new_date.setDate(new_date.getDate() - 1);
        set_current_date(new_date);
    };

    const handle_next = () => {
        const new_date = new Date(current_date);
        if (view === 'month') new_date.setMonth(new_date.getMonth() + 1);
        if (view === 'year') new_date.setFullYear(new_date.getFullYear() + 1);
        if (view === 'week') new_date.setDate(new_date.getDate() + 7);
        if (view === 'day') new_date.setDate(new_date.getDate() + 1);
        set_current_date(new_date);
    };

    const get_header_title = () => {
        const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        if (view === 'year') return `${current_date.getFullYear()}`;
        if (view === 'month') return `${months[current_date.getMonth()]} ${current_date.getFullYear()}`;
        if (view === 'week') {
            // Calculate week range
            const start = new Date(current_date);
            const day = start.getDay() || 7; 
            if (day !== 1) start.setHours(-24 * (day - 1));
            const end = new Date(start);
            end.setDate(end.getDate() + 6);
            return `Semana del ${start.getDate()} al ${end.getDate()} de ${months[end.getMonth()]}`;
        }
        if (view === 'day') return `${current_date.getDate()} de ${months[current_date.getMonth()]} ${current_date.getFullYear()}`;
    };

    return (
        <MainLayout>
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
                <div className="flex items-center gap-4">
                    <nav aria-label="Navegación del calendario" className="flex gap-2">
                        <button 
                            type="button"
                            onClick={handle_prev} 
                            className="p-2 border-3 border-basmati-black bg-white shadow-hard hover:translate-y-1 hover:shadow-none transition-all focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2"
                            aria-label={`Ir a ${view === 'year' ? 'año anterior' : view === 'month' ? 'mes anterior' : view === 'week' ? 'semana anterior' : 'día anterior'}`}
                        >
                            <FontAwesomeIcon icon={faChevronLeft} aria-hidden="true" />
                        </button>
                        <button 
                            type="button"
                            onClick={handle_next} 
                            className="p-2 border-3 border-basmati-black bg-white shadow-hard hover:translate-y-1 hover:shadow-none transition-all focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2"
                            aria-label={`Ir a ${view === 'year' ? 'año siguiente' : view === 'month' ? 'mes siguiente' : view === 'week' ? 'semana siguiente' : 'día siguiente'}`}
                        >
                            <FontAwesomeIcon icon={faChevronRight} aria-hidden="true" />
                        </button>
                    </nav>
                    <div>
                        <h1 className="text-3xl md:text-4xl font-black uppercase mb-1">{get_header_title()}</h1>
                        <p className="font-medium text-gray-600">La vida es eso que pasa mientras haces otros planes.</p>
                    </div>
                </div>
                <div className="grid grid-cols-2 md:flex gap-2 w-full md:w-auto" role="group" aria-label="Seleccionar vista del calendario">
                    <Neo_Button 
                        variant={view === 'year' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('year')}
                        className="flex-1 md:flex-none"
                        aria-pressed={view === 'year'}
                        aria-label="Vista por año"
                    >
                        Año
                    </Neo_Button>
                    <Neo_Button 
                        variant={view === 'month' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('month')}
                        className="flex-1 md:flex-none"
                        aria-pressed={view === 'month'}
                        aria-label="Vista por mes"
                    >
                        Mes
                    </Neo_Button>
                    <Neo_Button 
                        variant={view === 'week' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('week')}
                        className="flex-1 md:flex-none"
                        aria-pressed={view === 'week'}
                        aria-label="Vista por semana"
                    >
                        Semana
                    </Neo_Button>
                    <Neo_Button 
                        variant={view === 'day' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('day')}
                        className="flex-1 md:flex-none"
                        aria-pressed={view === 'day'}
                        aria-label="Vista por día"
                    >
                        Día
                    </Neo_Button>
                </div>
            </header>
            
            {loading ? (
                <div className="flex justify-center items-center h-64" role="status" aria-live="polite">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-basmati-black" aria-hidden="true"></div>
                    <span className="sr-only">Cargando eventos del calendario...</span>
                </div>
            ) : (
                <>
                    <CalendarGrid 
                        currentDate={current_date} 
                        view={view} 
                        events={events} 
                        onViewChange={set_view}
                        onDateChange={set_current_date}
                        onDeleteEvent={handle_delete_request}
                    />
                    
                    {/* Modal de confirmación de borrado */}
                    <Neo_Modal
                        is_open={delete_modal_open}
                        on_close={handle_close_delete_modal}
                        on_confirm={handle_confirm_delete}
                        title="¿Eliminar evento?"
                        variant="danger"
                        confirm_text="Eliminar"
                        cancel_text="Cancelar"
                        loading={deleting}
                    >
                        <p className="text-base">
                            ¿Estás seguro de que deseas eliminar el evento <strong>"{event_to_delete?.title}"</strong>?
                        </p>
                        <p className="text-sm text-gray-600 mt-2">
                            Esta acción no se puede deshacer.
                        </p>
                    </Neo_Modal>
                </>
            )}
        </MainLayout>
    );
};
