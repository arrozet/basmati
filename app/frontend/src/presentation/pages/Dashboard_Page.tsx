import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Neo_Modal } from '../components/ui/Neo_Modal';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronLeft, faChevronRight, faTrash, faFilter } from '@fortawesome/free-solid-svg-icons';
import { use_calendar_events } from '../hooks/use_calendar_events';
import { use_calendar_visibility } from '../context/CalendarVisibilityContext';
import { use_user_context } from '../context/UserContext';
import { Event_Model } from '../../domain/models/event_model';
import { Delete_Event_Use_Case } from '../../application/event/delete_event_use_case';
import { Http_Event_Repository } from '../../infrastructure/repositories/http_event_repository';
import { Http_Calendar_Repository } from '../../infrastructure/repositories/http_calendar_repository';
import { use_page_title } from '../hooks/use_page_title';

const event_repository = new Http_Event_Repository();
const calendar_repository = new Http_Calendar_Repository();
const delete_event_use_case = new Delete_Event_Use_Case(event_repository, calendar_repository);

type ViewType = 'year' | 'month' | 'week' | 'day';

/**
 * Convierte un color HEX a rgba con opacidad.
 * @param hex - Color en formato hexadecimal (#RRGGBB).
 * @param opacity - Opacidad entre 0 y 1.
 * @returns String rgba para usar en estilos CSS.
 */
const hex_to_rgba = (hex: string, opacity: number): string => {
    const clean_hex = hex.replace('#', '');
    const r = parseInt(clean_hex.substring(0, 2), 16);
    const g = parseInt(clean_hex.substring(2, 4), 16);
    const b = parseInt(clean_hex.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

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

/**
 * Representa un segmento de evento multi-día para renderizado en el grid mensual.
 */
interface Multi_Day_Event_Segment {
    event: Event_Model;
    /** Índice del slot (fila) donde se muestra el evento. */
    slot_index: number;
    /** Indica si este día es el inicio del evento. */
    is_start: boolean;
    /** Indica si este día es el fin del evento. */
    is_end: boolean;
    /** Número de días que el evento abarca desde este punto hasta el fin de la semana o del evento. */
    span_days: number;
}

/**
 * Obtiene la fecha sin hora para comparaciones de día.
 * @param date - La fecha a normalizar.
 * @returns Fecha con hora reseteada a 00:00:00.
 */
const get_date_only = (date: Date): Date => {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    return d;
};

/**
 * Comprueba si un evento ocurre en un día específico.
 * @param event - El evento a verificar.
 * @param day_date - La fecha del día a comprobar.
 * @returns true si el evento ocurre en ese día.
 */
const event_occurs_on_day = (event: Event_Model, day_date: Date): boolean => {
    const day_start = get_date_only(day_date);
    const day_end = new Date(day_start);
    day_end.setDate(day_end.getDate() + 1);
    
    const event_start = get_date_only(new Date(event.start_time));
    const event_end = get_date_only(new Date(event.end_time));
    
    // El evento ocurre si el día está dentro del rango [start, end]
    return day_start >= event_start && day_start <= event_end;
};

/**
 * Determina si un evento abarca múltiples días.
 * @param event - El evento a verificar.
 * @returns true si el evento dura más de un día.
 */
const is_multi_day_event = (event: Event_Model): boolean => {
    const start = get_date_only(new Date(event.start_time));
    const end = get_date_only(new Date(event.end_time));
    return start.getTime() !== end.getTime();
};

const CalendarGrid: React.FC<{ 
    currentDate: Date, 
    view: ViewType, 
    events: Event_Model[],
    calendar_id?: string,
    onViewChange: (view: ViewType) => void,
    onDateChange: (date: Date) => void,
    onDeleteEvent: (event_id: string) => void
}> = ({ currentDate, view, events, calendar_id, onViewChange, onDateChange, onDeleteEvent }) => {
    const navigate = useNavigate();
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const days_labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    const months_labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    const handle_event_click = (event_id: string) => {
        navigate(`/events/${event_id}`);
    };

    const handle_day_click = (date: Date) => {
        // Format date as YYYY-MM-DD using local time
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        
        const params = new URLSearchParams();
        params.append('date', dateStr);
        if (calendar_id) {
            params.append('calendar_id', calendar_id);
        }
        navigate(`/events/new?${params.toString()}`);
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
        
        // Construir array de todas las celdas del grid (incluyendo días vacíos al inicio)
        const total_cells = first_day + days_in_month;
        const total_rows = Math.ceil(total_cells / 7);
        
        // Calcular posiciones de eventos multi-día para cada semana
        // Estructura: { [event_id]: slot_index } por cada semana
        const week_event_slots: Map<string, number>[] = [];
        
        for (let row = 0; row < total_rows; row++) {
            const slots_map = new Map<string, number>();
            const row_start_cell = row * 7;
            const row_end_cell = Math.min(row_start_cell + 7, total_cells);
            
            // Encontrar eventos que aparecen en esta semana
            const events_in_week: { event: Event_Model; start_cell: number; end_cell: number }[] = [];
            
            for (let cell = row_start_cell; cell < row_end_cell; cell++) {
                const day_index = cell - first_day + 1;
                if (day_index >= 1 && day_index <= days_in_month) {
                    const current_day = new Date(year, month, day_index);
                    
                    events.forEach(event => {
                        if (event_occurs_on_day(event, current_day)) {
                            const existing = events_in_week.find(e => e.event.id === event.id);
                            if (existing) {
                                existing.end_cell = cell;
                            } else {
                                events_in_week.push({
                                    event,
                                    start_cell: cell,
                                    end_cell: cell
                                });
                            }
                        }
                    });
                }
            }
            
            // Ordenar eventos por duración (más largos primero) para asignar slots
            events_in_week.sort((a, b) => {
                const span_a = a.end_cell - a.start_cell;
                const span_b = b.end_cell - b.start_cell;
                if (span_b !== span_a) return span_b - span_a;
                // Si misma duración, ordenar por fecha de inicio
                return new Date(a.event.start_time).getTime() - new Date(b.event.start_time).getTime();
            });
            
            // Asignar slots a eventos
            const used_slots: boolean[][] = Array.from({ length: 7 }, () => []);
            
            events_in_week.forEach(({ event, start_cell, end_cell }) => {
                const local_start = start_cell - row_start_cell;
                const local_end = end_cell - row_start_cell;
                
                // Encontrar el primer slot libre para todas las celdas del evento
                let slot = 0;
                while (true) {
                    let slot_free = true;
                    for (let c = local_start; c <= local_end; c++) {
                        if (used_slots[c][slot]) {
                            slot_free = false;
                            break;
                        }
                    }
                    if (slot_free) break;
                    slot++;
                }
                
                // Marcar slot como usado
                for (let c = local_start; c <= local_end; c++) {
                    used_slots[c][slot] = true;
                }
                
                slots_map.set(event.id, slot);
            });
            
            week_event_slots.push(slots_map);
        }
        
        // Renderizar las filas del calendario
        const rows = [];
        for (let row = 0; row < total_rows; row++) {
            const row_start_cell = row * 7;
            const slots_for_row = week_event_slots[row];
            
            // Calcular eventos que se renderizan en esta fila
            const events_to_render: Multi_Day_Event_Segment[] = [];
            const MAX_VISIBLE_SLOTS = 3;
            
            for (let col = 0; col < 7; col++) {
                const cell = row_start_cell + col;
                const day_index = cell - first_day + 1;
                
                if (day_index >= 1 && day_index <= days_in_month) {
                    const current_day = new Date(year, month, day_index);
                    
                    events.forEach(event => {
                        if (event_occurs_on_day(event, current_day)) {
                            const event_start = get_date_only(new Date(event.start_time));
                            const event_end = get_date_only(new Date(event.end_time));
                            const current_day_normalized = get_date_only(current_day);
                            
                            // Determinar si debemos renderizar el evento desde este día
                            // (solo si es el inicio del evento O el inicio de la semana)
                            const is_event_start = current_day_normalized.getTime() === event_start.getTime();
                            const is_row_start = col === 0;
                            
                            if (is_event_start || is_row_start) {
                                // Calcular cuántos días debe abarcar la barra
                                let span_days = 1;
                                for (let future_col = col + 1; future_col < 7; future_col++) {
                                    const future_cell = row_start_cell + future_col;
                                    const future_day_index = future_cell - first_day + 1;
                                    if (future_day_index >= 1 && future_day_index <= days_in_month) {
                                        const future_day = new Date(year, month, future_day_index);
                                        if (event_occurs_on_day(event, future_day)) {
                                            span_days++;
                                        } else {
                                            break;
                                        }
                                    } else {
                                        break;
                                    }
                                }
                                
                                const is_end = get_date_only(new Date(year, month, day_index + span_days - 1)).getTime() >= event_end.getTime();
                                
                                events_to_render.push({
                                    event,
                                    slot_index: slots_for_row.get(event.id) || 0,
                                    is_start: is_event_start,
                                    is_end,
                                    span_days
                                });
                            }
                        }
                    });
                }
            }
            
            // Generar celdas de día para esta fila
            const day_cells = [];
            for (let col = 0; col < 7; col++) {
                const cell = row_start_cell + col;
                const day_index = cell - first_day + 1;
                
                if (day_index < 1 || day_index > days_in_month) {
                    // Celda vacía
                    day_cells.push(
                        <div key={`empty-${cell}`} className="bg-gray-50 border-3 border-transparent min-h-[100px] md:min-h-[120px]"></div>
                    );
                } else {
                    const current_day_date = new Date(year, month, day_index);
                    const day_name = days_labels[current_day_date.getDay() === 0 ? 6 : current_day_date.getDay() - 1];
                    const day_events = events.filter((e: Event_Model) => event_occurs_on_day(e, current_day_date));
                    const day_events_count = day_events.length;
                    
                    // Calcular eventos ocultos para este día específico en esta fila
                    const hidden_events_count = day_events.filter(e => {
                        const slot = slots_for_row.get(e.id);
                        return slot !== undefined && slot >= MAX_VISIBLE_SLOTS;
                    }).length;

                    day_cells.push(
                        <div 
                            key={day_index} 
                            className="bg-white border-3 border-basmati-black shadow-hard hover:shadow-[6px_6px_0px_0px_rgba(26,26,26,1)] hover:bg-gray-50 transition-all cursor-pointer relative min-h-[100px] md:min-h-[120px] overflow-visible focus-within:ring-4 focus-within:ring-basmati-yellow"
                            onClick={() => handle_day_click(current_day_date)}
                            role="gridcell"
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    handle_day_click(current_day_date);
                                }
                            }}
                            aria-label={`${day_name} ${day_index}, ${day_events_count} evento${day_events_count !== 1 ? 's' : ''}`}
                        >
                            <div className="flex justify-between items-start p-2">
                                <span className="md:hidden font-bold text-gray-500 text-xs uppercase">{day_name}</span>
                                <time className="font-bold text-gray-800 absolute top-2 right-2" dateTime={current_day_date.toISOString()}>
                                    {day_index}
                                </time>
                            </div>
                            
                            {/* Indicador de más eventos (Desktop) */}
                            {hidden_events_count > 0 && (
                                <div className="hidden md:block absolute bottom-1 left-2 text-xs font-bold text-gray-500 hover:text-basmati-black z-10">
                                    +{hidden_events_count} más
                                </div>
                            )}

                            {/* Eventos en móvil (lista simple) */}
                            <div className="md:hidden mt-6 flex flex-col gap-1 px-1">
                                {day_events.map((event: Event_Model) => {
                                    const event_color = event.color || '#EBBE4D';
                                    const multi_day = is_multi_day_event(event);
                                    const event_start = get_date_only(new Date(event.start_time));
                                    const event_end = get_date_only(new Date(event.end_time));
                                    const current_normalized = get_date_only(current_day_date);
                                    const is_start = current_normalized.getTime() === event_start.getTime();
                                    const is_end = current_normalized.getTime() === event_end.getTime();
                                    
                                    return (
                                        <div 
                                            key={event.id}
                                            className={`
                                                p-1 pl-2 pr-6 text-xs font-bold truncate shadow-sm cursor-pointer group relative
                                                border-t-2 border-b-2 border-basmati-black
                                                ${is_start ? 'border-l-2 rounded-l' : ''}
                                                ${is_end ? 'border-r-2 rounded-r' : ''}
                                            `}
                                            style={{ 
                                                backgroundColor: event_color,
                                            }}
                                            title={event.title}
                                            onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                        >
                                            {is_start && <span>{event.title}</span>}
                                            {!is_start && multi_day && <span className="opacity-50">↳ {event.title}</span>}
                                            <button
                                                type="button"
                                                className="absolute right-0.5 top-0 bottom-0 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity text-basmati-red px-1.5 hover:bg-basmati-red/20 focus:outline-none focus:ring-2 focus:ring-basmati-red focus:opacity-100 z-10"
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
                                    );
                                })}
                            </div>
                        </div>
                    );
                }
            }
            
            rows.push(
                <div key={`row-${row}`} className="relative">
                    {/* Grid de celdas de día */}
                    <div className="grid grid-cols-1 md:grid-cols-7 gap-2 md:gap-4">
                        {day_cells}
                    </div>
                    
                    {/* Capa de eventos multi-día superpuestos (solo en desktop) */}
                    <div className="hidden md:block absolute top-8 left-0 right-0 pointer-events-none" style={{ zIndex: 5 }}>
                        {events_to_render
                            .filter(segment => segment.slot_index < MAX_VISIBLE_SLOTS)
                            .map((segment, idx) => {
                            const event = segment.event;
                            const event_color = event.color || '#EBBE4D';
                            
                            // Calcular posición y ancho
                            // Encontrar la columna de inicio
                            let start_col = -1;
                            for (let col = 0; col < 7; col++) {
                                const cell = row_start_cell + col;
                                const day_index = cell - first_day + 1;
                                if (day_index >= 1 && day_index <= days_in_month) {
                                    const current_day = new Date(year, month, day_index);
                                    const event_start = get_date_only(new Date(event.start_time));
                                    const is_event_start = get_date_only(current_day).getTime() === event_start.getTime();
                                    const is_row_start = col === 0;
                                    
                                    if (event_occurs_on_day(event, current_day) && (is_event_start || is_row_start)) {
                                        start_col = col;
                                        break;
                                    }
                                }
                            }
                            
                            if (start_col === -1) return null;
                            
                            // Porcentaje de posición y ancho (cada columna es ~14.28% pero con gaps)
                            const col_width = 100 / 7;
                            const gap_adjustment = 0.5; // Pequeño ajuste para los gaps
                            const left_percent = start_col * col_width + gap_adjustment;
                            const width_percent = segment.span_days * col_width - gap_adjustment * 2;
                            
                            // Offset vertical basado en slot
                            const top_offset = segment.slot_index * 24; // 24px por slot
                            
                            return (
                                <div
                                    key={`${event.id}-${row}-${idx}`}
                                    className="absolute pointer-events-auto cursor-pointer group hover:z-20 hover:scale-[1.01] transition-all duration-200"
                                    style={{
                                        left: `${left_percent}%`,
                                        width: `${width_percent}%`,
                                        top: `${top_offset}px`,
                                    }}
                                    onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                    title={event.title}
                                >
                                    <div 
                                        className={`
                                            flex items-center h-5 text-xs font-bold truncate shadow-sm relative
                                            ${segment.is_start ? 'pl-2 rounded-l border-l-2' : 'pl-1'}
                                            ${segment.is_end ? 'pr-6 rounded-r border-r-2' : 'pr-1'}
                                            border-t-2 border-b-2 border-basmati-black
                                        `}
                                        style={{ 
                                            backgroundColor: event_color,
                                            borderLeftColor: segment.is_start ? '#1A1A1A' : 'transparent',
                                            borderRightColor: segment.is_end ? '#1A1A1A' : 'transparent',
                                        }}
                                    >
                                        {segment.is_start && (
                                            <span className="truncate">
                                                {!is_multi_day_event(event) && (
                                                    <span className="mr-1 opacity-70">
                                                        {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                                    </span>
                                                )}
                                                {event.title}
                                            </span>
                                        )}
                                        {segment.is_end && (
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
                                        )}
                                    </div>
                                </div>
                            );
                        })}
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
                <div className="flex flex-col gap-2 md:gap-4" role="grid" aria-label="Días del mes">
                    {rows}
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

        // Generar array de horas (0-23)
        const hours = Array.from({ length: 24 }, (_, i) => i);
        
        // Altura de cada hora en píxeles (50px permite eventos legibles con scroll)
        const hour_height = 50;
        
        /**
         * Calcula la posición top en píxeles basada en la hora del evento.
         * @param date - La fecha/hora del evento.
         * @returns Posición top en píxeles.
         */
        const get_top_position = (date: Date): number => {
            const hours = date.getHours();
            const minutes = date.getMinutes();
            return (hours * hour_height) + (minutes / 60 * hour_height);
        };
        
        /**
         * Calcula la altura en píxeles basada en la duración del evento.
         * @param start - Fecha/hora de inicio.
         * @param end - Fecha/hora de fin.
         * @returns Altura en píxeles (mínimo 20px).
         */
        const get_event_height = (start: Date, end: Date): number => {
            const duration_ms = end.getTime() - start.getTime();
            const duration_hours = duration_ms / (1000 * 60 * 60);
            return Math.max(20, duration_hours * hour_height);
        };

        // Separar eventos multi-día y eventos de un solo día
        const all_day_events: Event_Model[] = [];
        const timed_events: Event_Model[] = [];
        
        events.forEach((event: Event_Model) => {
            if (is_multi_day_event(event)) {
                all_day_events.push(event);
            } else {
                timed_events.push(event);
            }
        });

        // Calcular slots para eventos multi-día (all-day events)
        const all_day_slots = new Map<string, number>();
        const all_day_in_week: { event: Event_Model; start_col: number; end_col: number }[] = [];
        
        for (let col = 0; col < 7; col++) {
            const current_day = week_dates[col];
            all_day_events.forEach(event => {
                if (event_occurs_on_day(event, current_day)) {
                    const existing = all_day_in_week.find(e => e.event.id === event.id);
                    if (existing) {
                        existing.end_col = col;
                    } else {
                        all_day_in_week.push({ event, start_col: col, end_col: col });
                    }
                }
            });
        }
        
        // Ordenar y asignar slots
        all_day_in_week.sort((a, b) => (b.end_col - b.start_col) - (a.end_col - a.start_col));
        const used_all_day_slots: boolean[][] = Array.from({ length: 7 }, () => []);
        
        all_day_in_week.forEach(({ event, start_col, end_col }) => {
            let slot = 0;
            while (true) {
                let free = true;
                for (let c = start_col; c <= end_col; c++) {
                    if (used_all_day_slots[c][slot]) { free = false; break; }
                }
                if (free) break;
                slot++;
            }
            for (let c = start_col; c <= end_col; c++) {
                used_all_day_slots[c][slot] = true;
            }
            all_day_slots.set(event.id, slot);
        });

        const max_all_day_slots = Math.max(0, ...Array.from(all_day_slots.values())) + 1;
        const all_day_section_height = all_day_in_week.length > 0 ? max_all_day_slots * 24 + 8 : 0;

        return (
            <section className="flex flex-col" aria-label="Vista semanal del calendario">
                {/* Header con días de la semana */}
                <div className="flex border-b-3 border-basmati-black bg-white sticky top-0 z-20">
                    {/* Columna de hora vacía */}
                    <div className="w-16 shrink-0 border-r-3 border-basmati-black"></div>
                    {/* Días */}
                    <div className="flex-1 grid grid-cols-7">
                        {week_dates.map((date, idx) => {
                            const is_today = get_date_only(date).getTime() === get_date_only(new Date()).getTime();
                            return (
                                <div 
                                    key={idx} 
                                    className={`text-center py-2 border-r border-gray-200 last:border-r-0 ${is_today ? 'bg-basmati-yellow/20' : ''}`}
                                >
                                    <div className="text-xs uppercase text-gray-500 font-bold">{days_labels[idx].substring(0, 3)}</div>
                                    <time 
                                        className={`text-2xl font-black ${is_today ? 'bg-basmati-blue text-white rounded-full w-10 h-10 flex items-center justify-center mx-auto' : ''}`}
                                        dateTime={date.toISOString()}
                                    >
                                        {date.getDate()}
                                    </time>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Sección de eventos multi-día (all-day) */}
                {all_day_in_week.length > 0 && (
                    <div className="flex border-b-3 border-basmati-black bg-gray-50">
                        <div className="w-16 shrink-0 border-r-3 border-basmati-black flex items-center justify-center text-xs text-gray-500 font-bold">
                            Todo el día
                        </div>
                        <div className="flex-1 grid grid-cols-7 relative" style={{ minHeight: `${all_day_section_height}px` }}>
                            {/* Líneas de separación de columnas */}
                            {week_dates.map((_, idx) => (
                                <div key={idx} className="border-r border-gray-200 last:border-r-0"></div>
                            ))}
                            {/* Eventos multi-día */}
                            {all_day_in_week.map(({ event, start_col, end_col }) => {
                                const event_color = event.color || '#EBBE4D';
                                const slot = all_day_slots.get(event.id) || 0;
                                const col_width = 100 / 7;
                                const left = start_col * col_width;
                                const width = (end_col - start_col + 1) * col_width;
                                const event_start = get_date_only(new Date(event.start_time));
                                const event_end = get_date_only(new Date(event.end_time));
                                const is_start = get_date_only(week_dates[start_col]).getTime() === event_start.getTime();
                                const is_end = get_date_only(week_dates[end_col]).getTime() === event_end.getTime();
                                
                                return (
                                    <div
                                        key={event.id}
                                        className="absolute cursor-pointer group"
                                        style={{
                                            left: `${left}%`,
                                            width: `${width}%`,
                                            top: `${4 + slot * 24}px`,
                                            paddingLeft: '2px',
                                            paddingRight: '2px',
                                        }}
                                        onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                        title={event.title}
                                    >
                                        <div 
                                            className={`
                                                h-5 text-xs font-bold truncate px-2 pr-6 flex items-center relative
                                                border-t-2 border-b-2 border-basmati-black
                                                ${is_start ? 'border-l-2 rounded-l' : ''}
                                                ${is_end ? 'border-r-2 rounded-r' : ''}
                                            `}
                                            style={{ backgroundColor: event_color }}
                                        >
                                            {is_start && event.title}
                                            {is_end && (
                                                <button
                                                    type="button"
                                                    className="absolute right-0.5 top-0 bottom-0 flex items-center opacity-0 group-hover:opacity-100 transition-opacity bg-basmati-red text-white px-1 hover:bg-red-700 focus:outline-none focus:opacity-100 z-10 rounded-r"
                                                    onClick={(e) => { 
                                                        e.stopPropagation(); 
                                                        onDeleteEvent(event.id);
                                                    }}
                                                    aria-label={`Eliminar evento ${event.title}`}
                                                    tabIndex={0}
                                                >
                                                    <FontAwesomeIcon icon={faTrash} className="w-2.5 h-2.5" />
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Grid principal con horas */}
                <div className="flex flex-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
                    {/* Columna de horas */}
                    <div 
                        className="w-16 shrink-0 border-r-3 border-basmati-black bg-white"
                        style={{ height: `${24 * hour_height}px` }}
                    >
                        {hours.map(hour => (
                            <div 
                                key={hour} 
                                className="text-xs text-gray-500 text-right pr-2 font-medium relative"
                                style={{ height: `${hour_height}px` }}
                            >
                                <span className="absolute -top-2 right-2">
                                    {hour === 0 ? '' : `${hour}:00`}
                                </span>
                                <div className="absolute bottom-0 left-0 right-0 border-b border-gray-200"></div>
                            </div>
                        ))}
                    </div>
                    
                    {/* Grid de días */}
                    <div className="flex-1 grid grid-cols-7 relative">
                        {/* Líneas horizontales de horas */}
                        <div className="absolute inset-0 pointer-events-none">
                            {hours.map(hour => (
                                <div 
                                    key={hour}
                                    className="border-b border-gray-200"
                                    style={{ height: `${hour_height}px` }}
                                ></div>
                            ))}
                        </div>
                        
                        {/* Columnas de días */}
                        {week_dates.map((date, col_idx) => {
                            const is_today = get_date_only(date).getTime() === get_date_only(new Date()).getTime();
                            // Filtrar eventos que ocurren en este día (solo eventos con hora, no multi-día)
                            const day_timed_events = timed_events.filter((e: Event_Model) => event_occurs_on_day(e, date));
                            
                            return (
                                <div 
                                    key={col_idx}
                                    className={`relative border-r border-gray-200 last:border-r-0 ${is_today ? 'bg-basmati-yellow/5' : ''}`}
                                    style={{ height: `${24 * hour_height}px` }}
                                    onClick={() => handle_day_click(date)}
                                >
                                    {/* Eventos posicionados por hora */}
                                    {day_timed_events.map((event: Event_Model) => {
                                        const event_color = event.color || '#EBBE4D';
                                        const event_start = new Date(event.start_time);
                                        const event_end = new Date(event.end_time);
                                        
                                        // Calcular posición y altura
                                        const top = get_top_position(event_start);
                                        const height = get_event_height(event_start, event_end);
                                        
                                        return (
                                            <div
                                                key={event.id}
                                                className="absolute left-1 right-1 cursor-pointer group overflow-hidden border-2 border-basmati-black rounded shadow-sm hover:shadow-md transition-shadow z-10"
                                                style={{
                                                    top: `${top}px`,
                                                    height: `${height}px`,
                                                    backgroundColor: event_color,
                                                }}
                                                onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                                title={`${event.title} - ${event_start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} a ${event_end.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`}
                                            >
                                                    <div className="absolute inset-0 p-1 text-xs font-bold overflow-hidden">
                                                    <div className="truncate leading-none">{event.title}</div>
                                                    {height > 30 && (
                                                        <div className="text-[10px] opacity-80 leading-none mt-0.5 truncate">
                                                            {event_start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - {event_end.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                                        </div>
                                                    )}
                                                </div>
                                                <button
                                                    type="button"
                                                    className="absolute right-0 top-0 bottom-0 flex items-center opacity-0 group-hover:opacity-100 transition-opacity bg-basmati-red text-white px-1.5 hover:bg-red-700 focus:outline-none focus:opacity-100 z-10 rounded-r"
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
                                        );
                                    })}
                                </div>
                            );
                        })}
                    </div>
                </div>
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
                        day_events.map(event => {
                            const event_color = event.color || '#EBBE4D';
                            return (
                                <article 
                                    key={event.id} 
                                    className="flex gap-4 border-b border-gray-200 py-4 cursor-pointer hover:bg-gray-50 group relative"
                                    onClick={(e) => { e.stopPropagation(); handle_event_click(event.id); }}
                                >
                                    <time className="w-20 font-bold text-gray-500" dateTime={event.start_time.toISOString()}>
                                        {new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                    </time>
                                    <div 
                                        className="flex-1 border-l-4 p-2 rounded"
                                        style={{ 
                                            backgroundColor: hex_to_rgba(event_color, 0.2),
                                            borderLeftColor: event_color
                                        }}
                                    >
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
                            );
                        })
                    )}
                </div>
            </section>
        );
    }

    return null;
};

export const Dashboard_Page = () => {
    use_page_title('Dashboard');
    const [searchParams, setSearchParams] = useSearchParams();
    const calendar_id = searchParams.get('calendar_id') || undefined;
    const { hidden_calendar_ids } = use_calendar_visibility();
    
    // Obtener el usuario actual del contexto
    const { user } = use_user_context();
    const current_user_id = user?.external_id || 'user_dev_1';
    
    const [current_date, set_current_date] = useState(new Date());
    const [view, set_view] = useState<ViewType>('month');
    const { events, loading, refresh } = use_calendar_events(current_date, view, calendar_id, hidden_calendar_ids, current_user_id);
    
    // Modal de confirmación para borrar
    const [delete_modal_open, set_delete_modal_open] = useState(false);
    const [event_to_delete, set_event_to_delete] = useState<{ id: string, title: string } | null>(null);
    const [deleting, set_deleting] = useState(false);
    const [error, set_error] = useState<string | null>(null);

    const handle_delete_request = (event_id: string) => {
        const event = events.find(e => e.id === event_id);
        if (event) {
            set_event_to_delete({ id: event.id, title: event.title });
            set_delete_modal_open(true);
            set_error(null);
        }
    };

    const handle_confirm_delete = async () => {
        if (!event_to_delete) return;
        
        set_deleting(true);
        set_error(null);
        try {
            await delete_event_use_case.execute(event_to_delete.id, current_user_id);
            
            // Cerrar modal
            set_delete_modal_open(false);
            set_event_to_delete(null);
            
            // Recargar eventos
            refresh();
        } catch (error: any) {
            console.error('Error al eliminar evento:', error);
            set_error(error.message || "Error desconocido al eliminar el evento");
        } finally {
            set_deleting(false);
        }
    };

    const handle_close_delete_modal = () => {
        if (!deleting) {
            set_delete_modal_open(false);
            set_event_to_delete(null);
            set_error(null);
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

    const clear_calendar_filter = () => {
        const newParams = new URLSearchParams(searchParams);
        newParams.delete('calendar_id');
        setSearchParams(newParams);
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
                        <div className="flex items-center gap-2">
                            <p className="font-medium text-gray-600">La vida es eso que pasa mientras haces otros planes.</p>
                            {calendar_id && (
                                <button 
                                    onClick={clear_calendar_filter}
                                    className="text-xs bg-basmati-blue text-white px-2 py-1 rounded-full flex items-center gap-1 hover:bg-blue-600 transition-colors"
                                    title="Quitar filtro de calendario"
                                >
                                    <FontAwesomeIcon icon={faFilter} />
                                    Filtro activo
                                    <span className="ml-1 font-bold">×</span>
                                </button>
                            )}
                        </div>
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
                        calendar_id={calendar_id}
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
                        {error && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mt-4" role="alert">
                                <span className="block sm:inline">{error}</span>
                            </div>
                        )}
                    </Neo_Modal>
                </>
            )}
        </MainLayout>
    );
};
