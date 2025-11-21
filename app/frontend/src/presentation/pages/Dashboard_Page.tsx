import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Button } from '../components/ui/Neo_Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronLeft, faChevronRight } from '@fortawesome/free-solid-svg-icons';
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

const CalendarGrid: React.FC<{ currentDate: Date, view: ViewType, events: Event_Model[] }> = ({ currentDate, view, events }) => {
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
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {months_labels.map((m_label, idx) => (
                    <Neo_Card key={m_label} className="hover:scale-105 transition-transform cursor-pointer">
                        <h3 className="font-bold text-center mb-2">{m_label}</h3>
                        <div className="grid grid-cols-7 gap-1 text-[0.6rem]">
                            {Array.from({ length: get_days_in_month(year, idx) }).map((_, d_idx) => (
                                <div key={d_idx} className="text-center bg-gray-100 rounded-sm">{d_idx + 1}</div>
                            ))}
                        </div>
                    </Neo_Card>
                ))}
            </div>
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
            const day_events = events.filter(e => {
                const e_date = new Date(e.start_time);
                return e_date.getDate() === i && e_date.getMonth() === month && e_date.getFullYear() === year;
            });

            days.push(
                <div 
                    key={i} 
                    className="bg-white border-3 border-basmati-black shadow-hard p-2 hover:-translate-y-1 hover:shadow-[6px_6px_0px_0px_rgba(26,26,26,1)] transition-all cursor-pointer relative min-h-[100px] md:min-h-[120px] overflow-hidden"
                    onClick={() => handle_day_click(current_day_date)}
                >
                    <span className="font-bold text-gray-800 absolute top-2 right-2">{i}</span>
                    <div className="mt-6 flex flex-col gap-1">
                        {day_events.map(event => (
                            <div 
                                key={event.id} 
                                className="bg-basmati-yellow border-2 border-basmati-black p-1 text-xs font-bold truncate shadow-sm hover:bg-basmati-yellow/80 cursor-pointer" 
                                title={event.title}
                                onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                            >
                                {event.title}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        return (
            <div className="w-full">
                <div className="hidden md:grid grid-cols-7 gap-4 mb-4">
                    {days_labels.map(day => (
                        <div key={day} className="text-center font-black text-xl uppercase">{day}</div>
                    ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
                    {days}
                </div>
            </div>
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
            <div className="grid grid-cols-1 md:grid-cols-7 gap-4 h-[600px]">
                {week_dates.map((date, idx) => {
                    const day_events = events.filter(e => {
                        const e_date = new Date(e.start_time);
                        return e_date.getDate() === date.getDate() && e_date.getMonth() === date.getMonth() && e_date.getFullYear() === date.getFullYear();
                    });

                    return (
                        <div key={idx} className="border-3 border-basmati-black bg-white p-2 flex flex-col">
                            <div className="font-black text-center border-b-3 border-basmati-black pb-2 mb-2">
                                <div className="text-xs uppercase text-gray-500">{days_labels[idx]}</div>
                                <div className="text-xl">{date.getDate()}</div>
                            </div>
                            <div className="flex-1 bg-gray-50 relative overflow-y-auto">
                                {day_events.map(event => (
                                    <div 
                                        key={event.id} 
                                        className="bg-basmati-blue/20 border-l-4 border-basmati-blue p-1 text-xs mb-1 cursor-pointer hover:bg-basmati-blue/30"
                                        onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                    >
                                        {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - {event.title}
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>
        );
    }

    if (view === 'day') {
        const day_events = events.filter(e => {
            const e_date = new Date(e.start_time);
            return e_date.getDate() === currentDate.getDate() && e_date.getMonth() === currentDate.getMonth() && e_date.getFullYear() === currentDate.getFullYear();
        });

        return (
            <div className="border-3 border-basmati-black bg-white p-4 min-h-[600px]">
                <h3 className="font-black text-2xl mb-4">{days_labels[currentDate.getDay() === 0 ? 6 : currentDate.getDay() - 1]} {currentDate.getDate()}</h3>
                <div className="space-y-4">
                    {/* Simple list for now, could be a timeline */}
                    {day_events.length === 0 ? (
                        <div className="text-gray-500 italic">No hay eventos para este día.</div>
                    ) : (
                        day_events.map(event => (
                            <div 
                                key={event.id} 
                                className="flex gap-4 border-b border-gray-200 py-4 cursor-pointer hover:bg-gray-50"
                                onClick={() => handle_event_click(event.id)}
                            >
                                <div className="w-20 font-bold text-gray-500">
                                    {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                </div>
                                <div className="flex-1 bg-basmati-yellow/20 border-l-4 border-basmati-yellow p-2 rounded">
                                    <div className="font-bold">{event.title}</div>
                                    <div className="text-sm">{event.description}</div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        );
    }

    return null;
};

export const Dashboard_Page = () => {
    const [current_date, set_current_date] = useState(new Date());
    const [view, set_view] = useState<ViewType>('month');
    const { events, loading } = use_calendar_events(current_date, view);

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
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
                <div className="flex items-center gap-4">
                    <div className="flex gap-2">
                        <button onClick={handle_prev} className="p-2 border-3 border-basmati-black bg-white shadow-hard hover:translate-y-1 hover:shadow-none transition-all">
                            <FontAwesomeIcon icon={faChevronLeft} />
                        </button>
                        <button onClick={handle_next} className="p-2 border-3 border-basmati-black bg-white shadow-hard hover:translate-y-1 hover:shadow-none transition-all">
                            <FontAwesomeIcon icon={faChevronRight} />
                        </button>
                    </div>
                    <div>
                        <h2 className="text-3xl md:text-4xl font-black uppercase mb-1">{get_header_title()}</h2>
                        <p className="font-medium text-gray-600">La vida es eso que pasa mientras haces otros planes.</p>
                    </div>
                </div>
                <div className="flex gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
                    <Neo_Button 
                        variant={view === 'year' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('year')}
                        className="flex-1 md:flex-none"
                    >
                        Año
                    </Neo_Button>
                    <Neo_Button 
                        variant={view === 'month' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('month')}
                        className="flex-1 md:flex-none"
                    >
                        Mes
                    </Neo_Button>
                    <Neo_Button 
                        variant={view === 'week' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('week')}
                        className="flex-1 md:flex-none"
                    >
                        Semana
                    </Neo_Button>
                    <Neo_Button 
                        variant={view === 'day' ? 'primary' : 'secondary'} 
                        onClick={() => set_view('day')}
                        className="flex-1 md:flex-none"
                    >
                        Día
                    </Neo_Button>
                </div>
            </div>
            
            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-basmati-black"></div>
                </div>
            ) : (
                <CalendarGrid currentDate={current_date} view={view} events={events} />
            )}
        </MainLayout>
    );
};
