import { Event_Model } from "../models/event_model";

export interface Event_Repository_Interface {
    get_events(calendar_id: string): Promise<Event_Model[]>;
    create(event: Omit<Event_Model, 'id'>): Promise<Event_Model>;
}

