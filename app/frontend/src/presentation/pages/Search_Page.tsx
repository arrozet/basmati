import React, { useState, useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { use_global_search } from "../hooks/use_global_search";
import { use_page_title } from "../hooks/use_page_title";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faSearch,
  faArrowLeft,
  faCalendarAlt,
  faClipboardList,
  faClock,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";

/**
 * Página de búsqueda unificada (Calendarios + Eventos).
 */
export const Search_Page: React.FC = () => {
  use_page_title("Búsqueda");
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
      <Link to="/dashboard" className="inline-block mb-6">
        <Neo_Button
          variant="secondary"
          className="flex items-center gap-2 text-sm font-bold px-4 py-2"
          aria-label="Volver al calendario principal"
        >
          <FontAwesomeIcon icon={faArrowLeft} />
          <span>Volver al calendario</span>
        </Neo_Button>
      </Link>

      <header className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <div className="flex items-center gap-3 w-full">
          <div className="flex items-center justify-center w-12 h-12 bg-basmati-yellow rounded-none border-3 border-basmati-black shadow-hard flex-shrink-0">
            <FontAwesomeIcon
              icon={faSearch}
              className="text-xl text-basmati-black"
            />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-basmati-black">
            Búsqueda global
          </h1>
        </div>
      </header>

      <Neo_Card className="mb-12 p-6 bg-white">
        <form
          onSubmit={handle_submit}
          aria-label="Formulario de búsqueda global"
        >
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-grow w-full">
              <Neo_Input
                label="¿Qué estás buscando?"
                placeholder="Buscar evento, calendario..."
                value={query}
                onChange={(e) => set_query(e.target.value)}
                id="search-query"
                type="search"
              />
            </div>
            <Neo_Button
              type="submit"
              variant="primary"
              className="w-full md:w-auto mb-[2px] flex items-center justify-center gap-2"
            >
              <FontAwesomeIcon icon={faSearch} />
              <span>Buscar</span>
            </Neo_Button>
          </div>
        </form>
      </Neo_Card>

      {loading && (
        <div
          className="text-lg text-center py-12 flex flex-col items-center gap-4"
          role="status"
          aria-live="polite"
        >
          <div className="animate-spin w-8 h-8 border-4 border-basmati-yellow border-t-basmati-black rounded-full"></div>
          <span className="font-bold text-gray-600">
            Buscando resultados...
          </span>
        </div>
      )}

      {error && (
        <div
          className="bg-basmati-red/10 text-basmati-red p-4 border-3 border-basmati-red shadow-hard mb-8 flex items-center gap-3"
          role="alert"
          aria-live="assertive"
        >
          <FontAwesomeIcon icon={faExclamationCircle} className="text-xl" />
          <span className="font-bold">{error}</span>
        </div>
      )}

      {/* Resultados de Calendarios */}
      {calendars.length > 0 && (
        <section aria-label="Resultados de calendarios" className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-basmati-black flex items-center gap-3 pb-2 border-b-3 border-basmati-black w-fit">
            <FontAwesomeIcon
              icon={faCalendarAlt}
              className="text-basmati-blue"
            />
            <span>Calendarios ({calendars.length})</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {calendars.map((calendar) => (
              <Neo_Card
                key={calendar.id}
                className="hover:translate-x-[-4px] hover:translate-y-[-4px] transition-transform h-full flex flex-col group bg-white"
                role="article"
              >
                <div className="flex items-center gap-3 mb-3 border-b-2 border-gray-100 pb-3">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center border-2 border-basmati-black bg-gray-50 text-basmati-black">
                    <FontAwesomeIcon icon={faCalendarAlt} className="text-lg" />
                  </div>
                  <h3
                    className="text-xl font-bold truncate"
                    title={calendar.title}
                  >
                    {calendar.title}
                  </h3>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-4 px-1">
                  <div
                    className="w-3 h-3 rounded-full border-2 border-basmati-black"
                    style={{ backgroundColor: calendar.color }}
                  />
                  <span className="font-medium">
                    {calendar.is_public ? "Público" : "Privado"}
                  </span>
                </div>
                <div className="mt-auto flex justify-end">
                  <Neo_Button
                    variant="secondary"
                    className="text-xs px-3 py-1"
                    onClick={() => navigate(`/calendars/${calendar.id}`)}
                    aria-label={`Ver calendario ${calendar.title}`}
                  >
                    Ver calendario
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
          <h2 className="text-2xl font-bold mb-6 text-basmati-black flex items-center gap-3 pb-2 border-b-3 border-basmati-black w-fit">
            <FontAwesomeIcon
              icon={faClipboardList}
              className="text-basmati-yellow"
            />
            <span>Eventos ({events.length})</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => (
              <Neo_Card
                key={event.id}
                className="hover:translate-x-[-4px] hover:translate-y-[-4px] transition-transform h-full flex flex-col bg-white relative overflow-hidden"
                role="article"
              >
                <div className="absolute top-0 left-0 w-1 h-full bg-basmati-yellow"></div>
                <div className="pl-3 flex justify-between items-start mb-3">
                  <h3 className="text-xl font-bold leading-tight line-clamp-2">
                    {event.title}
                  </h3>
                </div>

                <div className="pl-3 flex items-center gap-2 text-sm font-bold mb-3 text-basmati-blue w-fit">
                  <FontAwesomeIcon icon={faClock} />
                  <time dateTime={event.start_time.toISOString()}>
                    {event.start_time.toLocaleDateString()} •{" "}
                    {event.start_time.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </time>
                </div>

                {event.description && (
                  <p className="pl-3 mb-4 text-gray-700 line-clamp-3 flex-grow text-sm">
                    {event.description}
                  </p>
                )}

                <div className="mt-auto pt-4 border-t-2 border-gray-100 flex justify-end pl-3">
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
        <div className="text-center py-16 bg-white border-3 border-basmati-black border-dashed flex flex-col items-center gap-4 rounded-lg">
          <FontAwesomeIcon
            icon={faExclamationCircle}
            className="text-4xl text-gray-300"
          />
          <p className="text-xl text-gray-600 font-bold">
            No se encontraron resultados para "{query}".
          </p>
          <p className="text-gray-500">Intenta con otros términos.</p>
        </div>
      )}

      {!loading && !query && (
        <div className="text-center py-16 bg-white border-3 border-basmati-black border-dashed flex flex-col items-center gap-4 rounded-lg">
          <FontAwesomeIcon icon={faSearch} className="text-4xl text-gray-300" />
          <p className="text-xl text-gray-600 font-bold">
            Introduce un término para empezar a buscar.
          </p>
        </div>
      )}
    </main>
  );
};
