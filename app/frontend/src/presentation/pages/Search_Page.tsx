import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { use_search_events } from "../hooks/use_search_events";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";

export const Search_Page: React.FC = () => {
    const [search_params, set_search_params] = useSearchParams();
    
    // Estado local para los filtros
    const [title, set_title] = useState(search_params.get("title") || "");
    const [organizer, set_organizer] = useState(search_params.get("organizer") || "");
    const [keywords, set_keywords] = useState(search_params.get("keywords") || "");
    
    // Si hay un parámetro "q" (búsqueda simple desde navbar), lo ponemos en keywords o title
    useEffect(() => {
        const q = search_params.get("q");
        if (q) {
            set_keywords(q);
            // Limpiamos q de la URL para usar los filtros avanzados
            // set_search_params({ keywords: q });
        }
    }, []);

    // Hook de búsqueda
    const { events, loading, error } = use_search_events({ title, organizer, keywords });

    const handle_change = (field: string, value: string) => {
        if (field === 'title') set_title(value);
        if (field === 'organizer') set_organizer(value);
        if (field === 'keywords') set_keywords(value);
        
        // Actualizar URL (opcional, para compartir búsqueda)
        // update_params({ title, organizer, keywords, [field]: value });
    };

    return (
        <div className="p-8 w-full max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-4xl font-bold text-basmati-black">Búsqueda de Eventos</h1>
                <Link to="/dashboard">
                    <Neo_Button variant="secondary">
                        ← Volver al Calendario
                    </Neo_Button>
                </Link>
            </div>
            
            <Neo_Card className="mb-8 p-6 bg-basmati-bg">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Neo_Input
                        label="Título"
                        placeholder="Ej. Reunión de equipo"
                        value={title}
                        onChange={(e) => handle_change('title', e.target.value)}
                    />
                    <Neo_Input
                        label="Organizador"
                        placeholder="Ej. Calendario de Marketing"
                        value={organizer}
                        onChange={(e) => handle_change('organizer', e.target.value)}
                    />
                    <Neo_Input
                        label="Palabras clave"
                        placeholder="Ej. presupuesto, urgente"
                        value={keywords}
                        onChange={(e) => handle_change('keywords', e.target.value)}
                    />
                </div>
            </Neo_Card>

            {loading && <p className="text-lg text-center py-8">Buscando...</p>}
            
            {error && (
                <div className="bg-basmati-red text-white p-4 border-3 border-basmati-black shadow-hard mb-4">
                    {error}
                </div>
            )}

            {!loading && events.length === 0 && (title || organizer || keywords) && (
                <div className="text-center py-12 bg-white border-3 border-basmati-black border-dashed">
                    <p className="text-xl text-gray-600">No se encontraron eventos con estos criterios.</p>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {events.map((event) => (
                    <Neo_Card key={event.id} className="hover:translate-x-[-4px] hover:translate-y-[-4px] transition-transform h-full flex flex-col">
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="text-xl font-bold leading-tight">{event.title}</h3>
                            {event.color && (
                                <div className="w-4 h-4 rounded-full border-2 border-basmati-black" style={{ backgroundColor: event.color }}></div>
                            )}
                        </div>
                        
                        <div className="text-sm font-bold mb-2 text-basmati-blue">
                            {event.start_time.toLocaleDateString()} • {event.start_time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                        
                        {event.description && (
                            <p className="mb-4 text-gray-700 line-clamp-3 flex-grow">{event.description}</p>
                        )}
                        
                        <div className="mt-auto pt-4 border-t-2 border-gray-100 flex justify-end">
                            <Neo_Button variant="primary" className="text-xs px-3 py-1">
                                Ver detalles
                            </Neo_Button>
                        </div>
                    </Neo_Card>
                ))}
            </div>
        </div>
    );
};
