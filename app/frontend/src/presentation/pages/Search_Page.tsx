import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { use_search_events } from "../hooks/use_search_events";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";

/**
 * Página de búsqueda de eventos accesible.
 * Usa formulario semántico, aria-live para resultados, headings jerárquicos.
 */
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
        }
    }, [search_params]);

    // Hook de búsqueda
    const { events, loading, error } = use_search_events({ title, organizer, keywords });

    const handle_change = (field: string, value: string) => {
        if (field === 'title') set_title(value);
        if (field === 'organizer') set_organizer(value);
        if (field === 'keywords') set_keywords(value);
    };

    const has_search_criteria = title || organizer || keywords;

    return (
        <main className="p-4 md:p-8 w-full max-w-6xl mx-auto">
            <header className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                <h1 className="text-3xl md:text-4xl font-bold text-basmati-black text-center md:text-left">Búsqueda de eventos</h1>
                <Link to="/dashboard" className="w-full md:w-auto">
                    <Neo_Button variant="secondary" className="w-full md:w-auto" aria-label="Volver al calendario principal">
                        ← Volver al calendario
                    </Neo_Button>
                </Link>
            </header>
            
            <Neo_Card className="mb-8 p-6 bg-basmati-bg">
                <form aria-label="Formulario de búsqueda de eventos">
                    <fieldset className="border-0 p-0 m-0">
                        <legend className="font-bold text-lg mb-4">Filtros de búsqueda</legend>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Neo_Input
                                label="Título"
                                placeholder="Ej. Reunión de equipo"
                                value={title}
                                onChange={(e) => handle_change('title', e.target.value)}
                                id="search-title"
                                type="search"
                            />
                            <Neo_Input
                                label="Organizador"
                                placeholder="Ej. Calendario de Marketing"
                                value={organizer}
                                onChange={(e) => handle_change('organizer', e.target.value)}
                                id="search-organizer"
                                type="search"
                            />
                            <Neo_Input
                                label="Palabras clave"
                                placeholder="Ej. presupuesto, urgente"
                                value={keywords}
                                onChange={(e) => handle_change('keywords', e.target.value)}
                                id="search-keywords"
                                type="search"
                            />
                        </div>
                    </fieldset>
                </form>
            </Neo_Card>

            {loading && (
                <div className="text-lg text-center py-8" role="status" aria-live="polite">
                    Buscando eventos...
                </div>
            )}
            
            {error && (
                <div 
                    className="bg-basmati-red text-white p-4 border-3 border-basmati-black shadow-hard mb-4" 
                    role="alert"
                    aria-live="assertive"
                >
                    {error}
                </div>
            )}

            {!loading && events.length === 0 && has_search_criteria && (
                <div className="text-center py-12 bg-white border-3 border-basmati-black border-dashed" role="status">
                    <p className="text-xl text-gray-600">No se encontraron eventos con estos criterios.</p>
                </div>
            )}

            {!loading && events.length === 0 && !has_search_criteria && (
                <div className="text-center py-12 bg-white border-3 border-basmati-black border-dashed">
                    <p className="text-xl text-gray-600">Introduce criterios de búsqueda para encontrar eventos.</p>
                </div>
            )}

            {events.length > 0 && (
                <section aria-label="Resultados de búsqueda">
                    <h2 className="text-2xl font-bold mb-4 text-basmati-black">
                        Resultados ({events.length} {events.length === 1 ? 'evento' : 'eventos'})
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {events.map((event) => (
                            <Neo_Card 
                                key={event.id} 
                                className="hover:translate-x-[-4px] hover:translate-y-[-4px] transition-transform h-full flex flex-col"
                                role="article"
                                aria-label={`Evento: ${event.title}`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-xl font-bold leading-tight">{event.title}</h3>
                                    {event.color && (
                                        <div 
                                            className="w-4 h-4 rounded-full border-2 border-basmati-black" 
                                            style={{ backgroundColor: event.color }}
                                            aria-label={`Color del evento: ${event.color}`}
                                        ></div>
                                    )}
                                </div>
                                
                                <time 
                                    className="text-sm font-bold mb-2 text-basmati-blue"
                                    dateTime={event.start_time.toISOString()}
                                >
                                    {event.start_time.toLocaleDateString()} • {event.start_time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </time>
                                
                                {event.description && (
                                    <p className="mb-4 text-gray-700 line-clamp-3 flex-grow">{event.description}</p>
                                )}
                                
                                <div className="mt-auto pt-4 border-t-2 border-gray-100 flex justify-end">
                                    <Neo_Button 
                                        variant="primary" 
                                        className="text-xs px-3 py-1"
                                        aria-label={`Ver detalles de ${event.title}`}
                                    >
                                        Ver detalles
                                    </Neo_Button>
                                </div>
                            </Neo_Card>
                        ))}
                    </div>
                </section>
            )}
        </main>
    );
};
