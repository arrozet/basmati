import { useState, useEffect } from "react";
import { Get_Events_By_Date_Range_Use_Case } from "../../application/event/get_events_by_date_range_use_case";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";
import { Event_Model } from "../../domain/models/event_model";

const repository = new Http_Event_Repository();
const get_events_use_case = new Get_Events_By_Date_Range_Use_Case(repository);

export const use_calendar_events = (currentDate: Date, view: 'year' | 'month' | 'week' | 'day', calendar_id?: string) => {
    const [events, set_events] = useState<Event_Model[]>([]);
    const [loading, set_loading] = useState(false);

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

            const result = await get_events_use_case.execute(start, end, calendar_id);
            set_events(result);
        } catch (error) {
            console.error("Error fetching events:", error);
        } finally {
            set_loading(false);
        }
    };

    useEffect(() => {
        fetch_events();
    }, [currentDate, view, calendar_id]);

    return { events, loading, refresh: fetch_events };
};
