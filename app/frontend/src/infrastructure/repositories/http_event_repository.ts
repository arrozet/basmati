import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Http_Event_Repository implements Event_Repository_Interface {
    async get_events(calendar_id: string): Promise<Event_Model[]> {
         // Mock implementation for scaffolding
        return Promise.resolve([]);
    }
    async create(event: Omit<Event_Model, 'id'>): Promise<Event_Model> {
        throw new Error("Method not implemented.");
    }
}

