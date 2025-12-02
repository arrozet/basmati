import { useState, useEffect } from "react";
import { Search_Events_Use_Case } from "../../application/event/search_events_use_case";
import { Search_Calendars_Use_Case } from "../../application/calendar/search_calendars_use_case";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Event_Model } from "../../domain/models/event_model";
import { Calendar_Model } from "../../domain/models/calendar_model";

// Inyección de dependencias
const event_repository = new Http_Event_Repository();
const calendar_repository = new Http_Calendar_Repository();

const search_events_use_case = new Search_Events_Use_Case(event_repository);
const search_calendars_use_case = new Search_Calendars_Use_Case(calendar_repository);

export const use_global_search = (query: string) => {
    const [events, set_events] = useState<Event_Model[]>([]);
    const [calendars, set_calendars] = useState<Calendar_Model[]>([]);
    const [loading, set_loading] = useState(false);
    const [error, set_error] = useState<string | null>(null);

    useEffect(() => {
        const fetch_data = async () => {
            if (!query.trim()) {
                set_events([]);
                set_calendars([]);
                return;
            }

            set_loading(true);
            set_error(null);

            try {
                // Ejecutar búsquedas en paralelo
                const [events_result, calendars_result] = await Promise.all([
                    search_events_use_case.execute(query),
                    search_calendars_use_case.execute(query)
                ]);

                set_events(events_result);
                set_calendars(calendars_result);
            } catch (err) {
                console.error(err);
                set_error("Error al realizar la búsqueda");
            } finally {
                set_loading(false);
            }
        };

        // Debounce
        const timeout_id = setTimeout(() => {
            fetch_data();
        }, 500);

        return () => clearTimeout(timeout_id);
    }, [query]);

    return { events, calendars, loading, error };
};

