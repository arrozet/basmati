import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Neo_Input } from './Neo_Input';
import { Neo_Button } from './Neo_Button';
import { Http_Integration_Repository } from '../../../infrastructure/repositories/http_integration_repository';
import { Location_Result, Event_Location } from '../../../domain/models/integration_models';

const integration_repository = new Http_Integration_Repository();

interface Location_Picker_Props {
    /** Valor actual de la ubicación */
    value?: Event_Location | null;
    /** Callback cuando cambia la ubicación */
    on_change: (location: Event_Location | null) => void;
    /** ID para accesibilidad */
    id?: string;
    /** Deshabilitar el componente */
    disabled?: boolean;
}

/**
 * Componente selector de ubicación con mapa OpenStreetMap.
 * Permite buscar direcciones, seleccionar en el mapa y ver la ubicación elegida.
 */
export const Location_Picker: React.FC<Location_Picker_Props> = ({
    value,
    on_change,
    id = 'location-picker',
    disabled = false
}) => {
    const [search_query, set_search_query] = useState('');
    const [search_results, set_search_results] = useState<Location_Result[]>([]);
    const [is_searching, set_is_searching] = useState(false);
    const [show_results, set_show_results] = useState(false);
    const [error, set_error] = useState<string | null>(null);
    const [is_expanded, set_is_expanded] = useState(!!value);
    
    const results_ref = useRef<HTMLDivElement>(null);
    const search_timeout_ref = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Cerrar resultados al hacer clic fuera
    useEffect(() => {
        const handle_click_outside = (event: MouseEvent) => {
            if (results_ref.current && !results_ref.current.contains(event.target as Node)) {
                set_show_results(false);
            }
        };

        document.addEventListener('mousedown', handle_click_outside);
        return () => document.removeEventListener('mousedown', handle_click_outside);
    }, []);

    // Debounced search
    const search_address = useCallback(async (query: string) => {
        if (query.length < 3) {
            set_search_results([]);
            set_show_results(false);
            return;
        }

        set_is_searching(true);
        set_error(null);

        try {
            const response = await integration_repository.geocode_address(query, 5);
            if (response.success) {
                set_search_results(response.results);
                set_show_results(response.results.length > 0);
            } else {
                set_error(response.message || 'Error al buscar dirección');
                set_search_results([]);
            }
        } catch (err) {
            console.error('Error buscando dirección:', err);
            set_error('Error de conexión al buscar');
            set_search_results([]);
        } finally {
            set_is_searching(false);
        }
    }, []);

    const handle_search_change = (e: React.ChangeEvent<HTMLInputElement>) => {
        const query = e.target.value;
        set_search_query(query);

        // Cancelar búsqueda anterior
        if (search_timeout_ref.current) {
            clearTimeout(search_timeout_ref.current);
        }

        // Debounce de 500ms para evitar muchas peticiones
        search_timeout_ref.current = setTimeout(() => {
            search_address(query);
        }, 500);
    };

    const handle_select_location = (result: Location_Result) => {
        const location: Event_Location = {
            address: result.address,
            latitude: result.latitude,
            longitude: result.longitude,
            place_name: result.place_name,
            map_provider: 'openstreetmap'
        };
        on_change(location);
        set_search_query(result.address);
        set_show_results(false);
        set_is_expanded(true);
    };

    const handle_clear_location = () => {
        on_change(null);
        set_search_query('');
        set_search_results([]);
        set_is_expanded(false);
    };

    const toggle_expanded = () => {
        set_is_expanded(!is_expanded);
    };

    // Generar URL del mapa estático de OpenStreetMap
    const get_map_url = (lat: number, lon: number): string => {
        // Usamos OpenStreetMap directamente para embeber un iframe
        return `https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.01}%2C${lat - 0.01}%2C${lon + 0.01}%2C${lat + 0.01}&layer=mapnik&marker=${lat}%2C${lon}`;
    };

    // URL para abrir en OpenStreetMap
    const get_osm_link = (lat: number, lon: number): string => {
        return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=17/${lat}/${lon}`;
    };

    return (
        <div className="flex flex-col gap-2" id={id}>
            <div className="flex items-center justify-between">
                <label className="font-bold text-sm text-basmati-black">
                    Ubicación
                </label>
                {!is_expanded && !value && (
                    <button
                        type="button"
                        onClick={toggle_expanded}
                        className="text-sm text-basmati-blue hover:underline"
                        disabled={disabled}
                    >
                        + Añadir ubicación
                    </button>
                )}
            </div>

            {(is_expanded || value) && (
                <div className="border-3 border-basmati-black p-4 bg-white">
                    {/* Buscador de direcciones */}
                    <div className="relative" ref={results_ref}>
                        <Neo_Input
                            label="Buscar dirección"
                            placeholder="Ej: Calle Larios, Málaga"
                            value={search_query}
                            onChange={handle_search_change}
                            disabled={disabled}
                            id={`${id}-search`}
                            autoComplete="off"
                        />
                        
                        {is_searching && (
                            <div className="absolute right-3 top-9 text-gray-500 text-sm">
                                Buscando...
                            </div>
                        )}

                        {/* Resultados de búsqueda */}
                        {show_results && search_results.length > 0 && (
                            <div 
                                className="absolute z-50 w-full mt-1 bg-white border-3 border-basmati-black max-h-60 overflow-y-auto shadow-hard"
                                role="listbox"
                                aria-label="Resultados de búsqueda de ubicación"
                            >
                                {search_results.map((result, index) => (
                                    <button
                                        key={result.osm_id || index}
                                        type="button"
                                        className="w-full text-left px-3 py-2 hover:bg-basmati-yellow border-b border-gray-200 last:border-b-0 transition-colors"
                                        onClick={() => handle_select_location(result)}
                                        role="option"
                                    >
                                        <div className="font-medium text-sm truncate">
                                            {result.place_name || result.address.split(',')[0]}
                                        </div>
                                        <div className="text-xs text-gray-600 truncate">
                                            {result.address}
                                        </div>
                                        {result.city && result.country && (
                                            <div className="text-xs text-gray-500">
                                                {result.city}, {result.country}
                                            </div>
                                        )}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {error && (
                        <div className="text-basmati-red text-sm mt-2" role="alert">
                            {error}
                        </div>
                    )}

                    {/* Vista previa del mapa y ubicación seleccionada */}
                    {value && (
                        <div className="mt-4">
                            <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                    <div className="font-bold text-sm text-basmati-black">
                                        Ubicación seleccionada:
                                    </div>
                                    <div className="text-sm text-gray-700 mt-1">
                                        {value.place_name && (
                                            <span className="font-medium">{value.place_name} - </span>
                                        )}
                                        {value.address}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        Coordenadas: {value.latitude.toFixed(6)}, {value.longitude.toFixed(6)}
                                    </div>
                                </div>
                                <Neo_Button
                                    type="button"
                                    variant="danger"
                                    onClick={handle_clear_location}
                                    disabled={disabled}
                                    className="ml-2 text-sm"
                                >
                                    Quitar
                                </Neo_Button>
                            </div>

                            {/* Mapa embebido de OpenStreetMap */}
                            <div className="border-3 border-basmati-black overflow-hidden">
                                <iframe
                                    title="Mapa de ubicación del evento"
                                    src={get_map_url(value.latitude, value.longitude)}
                                    width="100%"
                                    height="250"
                                    style={{ border: 0 }}
                                    loading="lazy"
                                    referrerPolicy="no-referrer-when-downgrade"
                                    aria-label={`Mapa mostrando la ubicación: ${value.address}`}
                                />
                            </div>

                            {/* Link para abrir en OpenStreetMap */}
                            <a
                                href={get_osm_link(value.latitude, value.longitude)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-sm text-basmati-blue hover:underline mt-2"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                                Ver en OpenStreetMap
                            </a>
                        </div>
                    )}

                    {/* Botón para cerrar si no hay ubicación */}
                    {!value && (
                        <div className="mt-4 text-right">
                            <Neo_Button
                                type="button"
                                variant="secondary"
                                onClick={toggle_expanded}
                                disabled={disabled}
                                className="text-sm"
                            >
                                Cancelar
                            </Neo_Button>
                        </div>
                    )}
                </div>
            )}

            {/* Vista compacta cuando hay ubicación pero está colapsado */}
            {value && !is_expanded && (
                <button
                    type="button"
                    onClick={toggle_expanded}
                    className="text-left border-3 border-basmati-black p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                    disabled={disabled}
                >
                    <div className="flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-basmati-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <span className="text-sm font-medium truncate">
                            {value.place_name || value.address.split(',')[0]}
                        </span>
                        <span className="text-xs text-gray-500 ml-auto">
                            (clic para expandir)
                        </span>
                    </div>
                </button>
            )}
        </div>
    );
};
