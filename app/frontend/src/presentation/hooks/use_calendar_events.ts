import { useState, useEffect } from "react";
import { Get_Events_By_Date_Range_Use_Case } from "../../application/event/get_events_by_date_range_use_case";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Event_Model } from "../../domain/models/event_model";
import { use_user_calendars } from "./use_user_calendars";
import { Calendar_Model } from "../../domain/models/calendar_model";

const calendar_repository = new Http_Calendar_Repository();
const repository = new Http_Event_Repository(calendar_repository);
const get_events_use_case = new Get_Events_By_Date_Range_Use_Case(repository);

// Helper to recursively find all descendant IDs
const get_all_descendant_ids = (rootId: string, allCalendars: Calendar_Model[]): string[] => {
    const children = allCalendars.filter(c => c.parent_id === rootId);
    let ids = [rootId];
    for (const child of children) {
        ids = [...ids, ...get_all_descendant_ids(child.id, allCalendars)];
    }
    return ids;
};

export const use_calendar_events = (
    currentDate: Date, 
    view: 'year' | 'month' | 'week' | 'day', 
    calendar_id?: string,
    hidden_calendar_ids?: Set<string>,
    user_id?: string
) => {
    const [events, set_events] = useState<Event_Model[]>([]);
    const [loading, set_loading] = useState(false);
    
    // We need the full calendar list to resolve hierarchy - use provided user_id or fallback
    const { calendars } = use_user_calendars(user_id || 'user_dev_1');

    const fetch_events = async () => {
        set_loading(true);
        try {
            let start = new Date(currentDate);
            let end = new Date(currentDate);

            if (view === 'month') {
                start.setDate(1);
                end.setMonth(end.getMonth() + 1);
                end.setDate(0);
            } else if (view === 'week') {
                const day = start.getDay() || 7;
                start.setDate(start.getDate() - (day - 1));
                end = new Date(start);
                end.setDate(end.getDate() + 6);
            } else if (view === 'day') {
                start.setHours(0, 0, 0, 0);
                end.setHours(23, 59, 59, 999);
            } else {
                // Year view - maybe fetch all year? or just don't fetch for now
                set_loading(false);
                return;
            }

            // Add buffer to start/end to cover edge cases
            start.setHours(0,0,0,0);
            end.setHours(23,59,59,999);

            let target_calendar_ids: string[] | undefined = undefined;
            
            if (calendar_id) {
                // If a specific calendar is selected, find it and all its descendants
                target_calendar_ids = get_all_descendant_ids(calendar_id, calendars);
            } else if (hidden_calendar_ids) {
                target_calendar_ids = calendars
                    .filter(c => !hidden_calendar_ids.has(c.id))
                    .map(c => c.id);
            }

            const result = await get_events_use_case.execute(start, end, target_calendar_ids);
            
            // Enriquecer eventos con el color del calendario asociado
            const calendar_color_map = new Map(calendars.map(c => [c.id, c.color]));
            const enriched_events = result.map(event => ({
                ...event,
                color: calendar_color_map.get(event.calendar_id) || '#EBBE4D'
            }));
            
            set_events(enriched_events);
        } catch (error) {
            console.error("Error fetching events:", error);
        } finally {
            set_loading(false);
        }
    };

    useEffect(() => {
        // Only fetch if we have calendars loaded (if we need them for hierarchy)
        // If calendar_id is undefined (view all), we don't strictly need calendars list if backend handles "all"
        // But if calendar_id is defined, we definitely need calendars to find descendants.
        if (calendar_id && calendars.length === 0) return;
        // If we are filtering by hidden_ids, we also need calendars loaded.
        if (!calendar_id && hidden_calendar_ids && calendars.length === 0) return;

        fetch_events();
    }, [currentDate, view, calendar_id, calendars, hidden_calendar_ids, user_id]); // Add calendars and user_id to dependency to re-fetch when they load

    return { events, loading, refresh: fetch_events };
};
