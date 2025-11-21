import { Calendar_Model } from "../models/calendar_model";

export interface Calendar_Repository_Interface {
    get_all(user_id: string): Promise<Calendar_Model[]>;
    create(calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model>;
}

