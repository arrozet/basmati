import { useState, useEffect } from "react";
import { Get_User_Calendars_Use_Case } from "../../application/calendar/get_user_calendars_use_case";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Calendar_Model } from "../../domain/models/calendar_model";

const repository = new Http_Calendar_Repository();
const get_user_calendars_use_case = new Get_User_Calendars_Use_Case(repository);

export const use_user_calendars = (user_id: string) => {
    const [calendars, set_calendars] = useState<Calendar_Model[]>([]);
    const [loading, set_loading] = useState(true);
    const [error, set_error] = useState<string | null>(null);

    useEffect(() => {
        const fetch_calendars = async () => {
            try {
                const result = await get_user_calendars_use_case.execute(user_id);
                set_calendars(result);
            } catch (err: any) {
                console.error(err);
                set_error("Error al cargar calendarios");
            } finally {
                set_loading(false);
            }
        };

        if (user_id) {
            fetch_calendars();
        }
    }, [user_id]);

    return { calendars, loading, error };
};
