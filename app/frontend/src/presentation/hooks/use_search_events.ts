import { useState, useEffect } from "react";
import { Search_Events_Use_Case } from "../../application/event/search_events_use_case";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";
import { Event_Model } from "../../domain/models/event_model";

// Inyección de dependencias manual
const repository = new Http_Event_Repository();
const search_events_use_case = new Search_Events_Use_Case(repository);

export const use_search_events = (query: string | { title?: string; organizer?: string; keywords?: string }) => {
    const [events, set_events] = useState<Event_Model[]>([]);
    const [loading, set_loading] = useState(false);
    const [error, set_error] = useState<string | null>(null);

    useEffect(() => {
        const fetch_data = async () => {
            const is_empty = typeof query === 'string' 
                ? !query 
                : (!query.title && !query.organizer && !query.keywords);

            if (is_empty) {
                set_events([]);
                return;
            }
            
            set_loading(true);
            set_error(null);
            try {
                const result = await search_events_use_case.execute(query);
                set_events(result);
            } catch (err) {
                console.error(err);
                set_error("Error al buscar eventos");
            } finally {
                set_loading(false);
            }
        };

        // Debounce simple
        const timeout_id = setTimeout(() => {
            fetch_data();
        }, 500);

        return () => clearTimeout(timeout_id);
    }, [JSON.stringify(query)]); // Deep dependency check

    return { events, loading, error };
};
