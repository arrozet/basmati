import React, { useState, useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { use_global_search } from "../hooks/use_global_search";
import { use_page_title } from "../hooks/use_page_title";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";

/**
 * Página de búsqueda unificada (Calendarios + Eventos).
 */
export const Search_Page: React.FC = () => {
    use_page_title('Search');
    const [search_params] = useSearchParams();
    const navigate = useNavigate();
    
    const [query, set_query] = useState(search_params.get("q") || "");
    
    useEffect(() => {
        const q = search_params.get("q");
        if (q) {
            set_query(q);
        }
    }, [search_params]);

    const { events, calendars, loading, error } = use_global_search(query);

    const handle_submit = (e: React.FormEvent) => {
        e.preventDefault();
        navigate(`/search?q=${encodeURIComponent(query)}`);
    };

    return (
        <main className="p-4 md:p-8 w-full max-w-6xl mx-auto">
            <header className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                <h1 className="text-3xl md:text-4xl font-bold text-basmati-black text-center md:text-left">Búsqueda Global</h1>
                <Link to="/dashboard" className="w-full md:w-auto">
                    <Neo_Button variant="secondary" className="w-full md:w-auto" aria-label="Volver al calendario principal">
                        ← Volver al calendario
                    </Neo_Button>
                </Link>
            </header>
            
            <Neo_Card className="mb-8 p-6 bg-basmati-bg">
                <form onSubmit={handle_submit} aria-label="Formulario de búsqueda global">
                    <div className="flex flex-col md:flex-row gap-4 items-end">
                        <div className="flex-grow w-full">
                            <Neo_Input
                                label="¿Qué estás buscando?"
                                placeholder="Buscar evento..."
                                value={query}
                                onChange={(e) => set_query(e.target.value)}
                                id="search-query"
                                type="search"
                            />
                        </div>
                        <Neo_Button type="submit" variant="primary" className="w-full md:w-auto mb-[2px]">
                            Buscar
                        </Neo_Button>
                    </div>
                </form>
            </Neo_Card>

            {loading && (
                <div className="text-lg text-center py-8" role="status" aria-live="polite">
                    Buscando resultados...
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

            {/* Resultados de Calendarios */}
            {calendars.length > 0 && (
                <section aria-label="Resultados de calendarios" className="mb-12">
                    <h2 className="text-2xl font-bold mb-4 text-basmati-black flex items-center gap-2">
                        <span>📅</span> Calendarios ({calendars.length})
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {calendars.map((calendar) => (
                            <Neo_Card 
                                key={calendar.id} 
                                className="hover:translate-x-[-4px] hover:translate-y-[-4px] transition-transform h-full flex flex-col"
                                role="article"
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <span className="text-2xl">{calendar.icon || "📅"}</span>
                                    <h3 className="text-xl font-bold">{calendar.title}</h3>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                                    <div 
                                        className="w-3 h-3 rounded-full border-2 border-basmati-black"
                                        style={{ backgroundColor: calendar.color }}
                                    />
                                    <span>{calendar.is_public ? "Público" : "Privado"}</span>
                                </div>
                                <div className="mt-auto flex justify-end">
                                     <Neo_Button variant="secondary" className="text-xs px-3 py-1">
                                        Ver Calendario
                                     </Neo_Button>
                                </div>
                            </Neo_Card>
                        ))}
                    </div>
                </section>
            )}

            {/* Resultados de Eventos */}
            {events.length > 0 && (
                <section aria-label="Resultados de eventos" className="mb-12">
                    <h2 className="text-2xl font-bold mb-4 text-basmati-black flex items-center gap-2">
                        <span>📝</span> Eventos ({events.length})
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {events.map((event) => (
                            <Neo_Card 
                                key={event.id} 
                                className="hover:translate-x-[-4px] hover:translate-y-[-4px] transition-transform h-full flex flex-col"
                                role="article"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-xl font-bold leading-tight">{event.title}</h3>
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
                                        onClick={() => navigate(`/events/${event.id}`)}
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

            {!loading && events.length === 0 && calendars.length === 0 && query && (
                <div className="text-center py-12 bg-white border-3 border-basmati-black border-dashed" role="status">
                    <p className="text-xl text-gray-600">No se encontraron resultados para "{query}".</p>
                </div>
            )}

             {!loading && !query && (
                <div className="text-center py-12 bg-white border-3 border-basmati-black border-dashed">
                    <p className="text-xl text-gray-600">Introduce un término para empezar a buscar.</p>
                </div>
            )}
        </main>
    );
};
