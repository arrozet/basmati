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
const search_calendars_use_case = new Search_Calendars_Use_Case(
  calendar_repository
);

/**
 * Parámetros de filtro para búsqueda avanzada.
 */
export interface Search_Filters {
  query: string;
  creator_name?: string;
  date_from?: string;
  date_to?: string;
}

export const use_global_search = (
  query: string,
  filters?: Omit<Search_Filters, "query">
) => {
  const [events, set_events] = useState<Event_Model[]>([]);
  const [calendars, set_calendars] = useState<Calendar_Model[]>([]);
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);

  useEffect(() => {
    const fetch_data = async () => {
      // No buscar si no hay ningún criterio
      const has_query = query.trim().length > 0;
      const has_creator =
        filters?.creator_name && filters.creator_name.trim().length > 0;
      const has_dates = filters?.date_from || filters?.date_to;

      if (!has_query && !has_creator && !has_dates) {
        set_events([]);
        set_calendars([]);
        return;
      }

      set_loading(true);
      set_error(null);

      try {
        // Obtener usuario actual
        const current_user =
          localStorage.getItem("basmati_current_user") || "user_dev_1";

        let events_result: Event_Model[] = [];
        let calendars_result: Calendar_Model[] = [];

        // Búsqueda de calendarios
        if (has_query) {
          // Buscar por texto
          calendars_result = await search_calendars_use_case.execute(query);
        }

        // Si hay filtro de creador, buscar calendarios por nombre de creador
        if (has_creator && filters?.creator_name) {
          const creator_calendars =
            await calendar_repository.search_by_creator_name(
              filters.creator_name
            );
          if (has_query) {
            // Intersección: calendarios que coincidan con ambos criterios
            const creator_ids = new Set(creator_calendars.map((c) => c.id));
            calendars_result = calendars_result.filter((c) =>
              creator_ids.has(c.id)
            );
          } else {
            calendars_result = creator_calendars;
          }
        }

        // Filtrar calendarios por fecha de creación si hay filtros de fecha
        if (has_dates) {
          const from_date = filters?.date_from
            ? new Date(filters.date_from)
            : null;
          const to_date = filters?.date_to
            ? new Date(filters.date_to + "T23:59:59")
            : null;

          calendars_result = calendars_result.filter((cal) => {
            if (!cal.created_at) return true; // Si no tiene fecha, no filtrar
            const created = new Date(cal.created_at);
            if (from_date && created < from_date) return false;
            if (to_date && created > to_date) return false;
            return true;
          });
        }

        // Búsqueda de eventos por texto
        if (has_query) {
          events_result = await search_events_use_case.execute(query);

          // Filtrar eventos por rango de fechas si hay filtros
          if (has_dates) {
            const from_date = filters?.date_from
              ? new Date(filters.date_from)
              : null;
            const to_date = filters?.date_to
              ? new Date(filters.date_to + "T23:59:59")
              : null;

            events_result = events_result.filter((evt) => {
              const event_date = new Date(evt.start_time);
              if (from_date && event_date < from_date) return false;
              if (to_date && event_date > to_date) return false;
              return true;
            });
          }
        } else if (has_dates) {
          // Si solo hay filtros de fecha (sin query de texto), buscar eventos por rango
          const from_date = filters?.date_from
            ? new Date(filters.date_from)
            : new Date(0); // Fecha mínima si no se especifica
          const to_date = filters?.date_to
            ? new Date(filters.date_to + "T23:59:59")
            : new Date("2100-12-31"); // Fecha máxima si no se especifica

          events_result = await event_repository.get_events_by_date_range(
            from_date,
            to_date
          );
        }

        // Filtrar calendarios: solo mostrar públicos si no son del usuario actual
        const filtered_calendars = calendars_result.filter(
          (cal) => cal.owner_id === current_user || cal.is_public === true
        );

        set_events(events_result);
        set_calendars(filtered_calendars);
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
  }, [query, filters?.creator_name, filters?.date_from, filters?.date_to]);

  return { events, calendars, loading, error };
};
