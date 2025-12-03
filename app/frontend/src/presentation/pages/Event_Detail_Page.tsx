import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Comments_Section } from '../components/ui/Comments_Section';
import { Http_Event_Repository } from '../../infrastructure/repositories/http_event_repository';
import { Http_Calendar_Repository } from '../../infrastructure/repositories/http_calendar_repository';
import { Event_Model, Event_Comment } from '../../domain/models/event_model';
import { Get_Event_Use_Case } from '../../application/event/get_event_use_case';
import { Add_Comment_Use_Case } from '../../application/event/add_comment_use_case';
import { use_page_title } from '../hooks/use_page_title';

// Dependencies
const event_repository = new Http_Event_Repository();
const calendar_repository = new Http_Calendar_Repository();

const get_event_use_case = new Get_Event_Use_Case(event_repository);
const add_comment_use_case = new Add_Comment_Use_Case(event_repository);

const CURRENT_USER_ID = 'user_dev_1'; // Mock ID

export const Event_Detail_Page = () => {
    use_page_title('Detalle del evento');
    const { id } = useParams();
    const navigate = useNavigate();
    
    const [loading, set_loading] = useState(true);
    const [error, set_error] = useState<string | null>(null);
    const [event, set_event] = useState<Event_Model | null>(null);
    const [calendar_info, set_calendar_info] = useState<{title: string, color: string} | null>(null);

    const fetch_event = async () => {
        if (!id) return;
        try {
            const fetched_event = await get_event_use_case.execute(id);
            if (fetched_event) {
                set_event(fetched_event);
                
                // Fetch calendar info
                try {
                    const calendar = await calendar_repository.get_by_id(fetched_event.calendar_id);
                    if (calendar) {
                        set_calendar_info({
                            title: calendar.title,
                            color: calendar.color
                        });
                    }
                } catch (cal_err) {
                    console.error("Error al cargar info del calendario", cal_err);
                }
            } else {
                set_error("Evento no encontrado");
            }
        } catch (err) {
            console.error(err);
            set_error("Error al cargar el evento");
        } finally {
            set_loading(false);
        }
    };

    useEffect(() => {
        fetch_event();
    }, [id]);

    const handle_add_comment = async (text: string) => {
        if (!event || !id) return;
        
        try {
            const new_comment = await add_comment_use_case.execute(id, text, CURRENT_USER_ID);
            set_event(prev => prev ? {
                ...prev,
                comments: [...(prev.comments || []), new_comment]
            } : null);
        } catch (error) {
            console.error("Error posting comment:", error);
            throw error;
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-basmati-black"></div>
                </div>
            </MainLayout>
        );
    }

    if (error || !event) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center h-64 flex-col">
                    <div className="text-xl font-bold text-basmati-red mb-4 border-2 border-basmati-black p-4 bg-red-50 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                        {error || "Evento no encontrado"}
                    </div>
                    <Neo_Button onClick={() => navigate('/dashboard')} variant="secondary">
                        <i className="fas fa-arrow-left mr-2"></i> Volver al Dashboard
                    </Neo_Button>
                </div>
            </MainLayout>
        );
    }

    // Formatters
    const format_day_number = (date: Date) => date.getDate();
    const format_month = (date: Date) => date.toLocaleDateString('es-ES', { month: 'short' }).toUpperCase();
    const format_year = (date: Date) => date.getFullYear();
    const format_weekday = (date: Date) => date.toLocaleDateString('es-ES', { weekday: 'long' });
    const format_time = (date: Date) => date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });

    // Helpers de mapa
    const get_map_url = (lat: number, lon: number): string => {
        return `https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.005}%2C${lat - 0.005}%2C${lon + 0.005}%2C${lat + 0.005}&layer=mapnik&marker=${lat}%2C${lon}`;
    };

    const get_osm_link = (lat: number, lon: number): string => {
        return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=17/${lat}/${lon}`;
    };

    return (
        <MainLayout>
            <div className="max-w-6xl mx-auto md:h-[calc(100vh-120px)] h-auto flex flex-col md:flex-row gap-6 pb-10 md:pb-0">
                
                {/* Columna Izquierda: Tarjeta Principal del Evento */}
                <Neo_Card className="flex-1 flex flex-col md:overflow-hidden !p-0 border-3 relative">
                    
                    {/* Header con color del calendario */}
                    <div className="h-4 w-full border-b-3 border-basmati-black shrink-0" style={{ 
                        backgroundColor: calendar_info?.color || '#EBBE4D',
                        backgroundImage: 'linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent)',
                        backgroundSize: '1rem 1rem'
                    }}></div>

                    <div className="flex-1 md:overflow-y-auto p-4 md:p-8 scrollbar-hide">
                        
                        {/* Barra superior: Calendario y Botones */}
                        <div className="flex justify-between items-start mb-6">
                            {calendar_info && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full border-2 border-basmati-black bg-white text-xs font-bold uppercase tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                                    <span className="w-2 h-2 rounded-full mr-2" style={{ backgroundColor: calendar_info.color }}></span>
                                    {calendar_info.title}
                                </span>
                            )}
                            <Neo_Button 
                                onClick={() => navigate(`/events/edit/${event.id}`)}
                                variant="secondary"
                                size="sm"
                                className="text-xs"
                            >
                                <i className="fas fa-pencil-alt mr-2"></i> Editar
                            </Neo_Button>
                        </div>

                        {/* Título Grande */}
                        <h1 className="text-4xl md:text-5xl font-black mb-8 leading-tight text-basmati-black drop-shadow-sm">
                            {event.title}
                        </h1>

                        {/* Bloque de Fecha Destacado */}
                        <div className="flex flex-col sm:flex-row gap-6 mb-8">
                            {/* Caja de Fecha (Estilo Calendario) */}
                            <div className="flex-shrink-0 bg-basmati-bg border-3 border-basmati-black rounded-sm w-24 text-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] overflow-hidden">
                                <div className="bg-basmati-red text-white font-bold py-1 text-xs uppercase border-b-3 border-basmati-black">
                                    {format_month(event.start_time)}
                                </div>
                                <div className="py-2">
                                    <span className="block text-4xl font-black">{format_day_number(event.start_time)}</span>
                                    <span className="block text-xs font-bold text-gray-500">{format_year(event.start_time)}</span>
                                </div>
                            </div>

                            {/* Detalles de Hora */}
                            <div className="flex flex-col justify-center">
                                <div className="text-xl font-bold capitalize mb-1">
                                    {format_weekday(event.start_time)}
                                </div>
                                <div className="flex items-center gap-2 text-gray-700 font-medium text-lg">
                                    <i className="far fa-clock"></i>
                                    <span>{format_time(event.start_time)} - {format_time(event.end_time)}</span>
                                </div>
                            </div>
                        </div>

                        <hr className="border-t-2 border-gray-200 border-dashed my-8" />

                        {/* Descripción */}
                        <div className="mb-8">
                            <h3 className="font-black text-lg mb-3 flex items-center gap-2 uppercase tracking-wide text-gray-400">
                                <i className="fas fa-align-left"></i> Detalles
                            </h3>
                            <div className="prose prose-lg max-w-none text-basmati-black bg-gray-50 p-4 rounded-sm border-l-4 border-basmati-yellow">
                                {event.description ? event.description : <span className="italic text-gray-400">Sin descripción.</span>}
                            </div>
                        </div>

                        {/* Ubicación */}
                        {event.location && (
                            <div className="mb-8">
                                <h3 className="font-black text-lg mb-3 flex items-center gap-2 uppercase tracking-wide text-gray-400">
                                    <i className="fas fa-map-marker-alt"></i> Ubicación
                                </h3>
                                <div className="bg-white border-3 border-basmati-black rounded-sm p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                                    <p className="font-bold text-lg">{event.location.place_name || "Ubicación"}</p>
                                    <p className="text-gray-600 mb-3">{event.location.address}</p>
                                    
                                    {/* Mapa Real */}
                                    <div className="border-3 border-basmati-black overflow-hidden rounded-sm">
                                        <iframe
                                            title="Mapa de ubicación del evento"
                                            src={get_map_url(event.location.latitude, event.location.longitude)}
                                            width="100%"
                                            height="250"
                                            style={{ border: 0 }}
                                            loading="lazy"
                                            referrerPolicy="no-referrer-when-downgrade"
                                        />
                                    </div>
                                    <div className="mt-2 text-right">
                                        <a 
                                            href={get_osm_link(event.location.latitude, event.location.longitude)}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-xs font-bold text-basmati-blue hover:underline flex items-center justify-end gap-1"
                                        >
                                            Ver mapa completo <i className="fas fa-external-link-alt"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Adjuntos */}
                        {event.attachments && event.attachments.length > 0 && (
                            <div className="mb-4">
                                <h3 className="font-black text-lg mb-3 flex items-center gap-2 uppercase tracking-wide text-gray-400">
                                    <i className="fas fa-paperclip"></i> Adjuntos ({event.attachments.length})
                                </h3>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                                    {event.attachments.map(att => (
                                        <a 
                                            key={att.id} 
                                            href={att.url} 
                                            target="_blank" 
                                            rel="noreferrer"
                                            className="group relative aspect-square border-3 border-basmati-black rounded-sm overflow-hidden hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1 transition-all bg-white"
                                        >
                                            {att.is_image ? (
                                                <img 
                                                    src={att.thumbnail_url || att.url} 
                                                    alt={att.filename} 
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex flex-col items-center justify-center bg-gray-50 text-gray-500 p-2 text-center">
                                                    <i className="fas fa-file-alt text-3xl mb-2"></i>
                                                    <span className="text-xs font-bold truncate w-full">{att.filename}</span>
                                                </div>
                                            )}
                                            {/* Overlay on Hover */}
                                            <div className="absolute inset-0 bg-basmati-black/80 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                                                <span className="text-white font-bold text-sm border-2 border-white px-2 py-1 rounded-sm">Ver</span>
                                            </div>
                                        </a>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </Neo_Card>

                {/* Columna Derecha: Comentarios */}
                <div className="w-full md:w-96 flex-shrink-0 h-[600px] md:h-full">
                    <Comments_Section 
                        comments={event.comments || []} 
                        on_add_comment={handle_add_comment}
                        current_user_id={CURRENT_USER_ID}
                    />
                </div>
            </div>
        </MainLayout>
    );
};
