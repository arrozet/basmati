import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";

export class Http_Calendar_Repository implements Calendar_Repository_Interface {
    async get_all(user_id: string): Promise<Calendar_Model[]> {
        // Mock implementation for scaffolding
        return Promise.resolve([]);
    }
    async create(calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model> {
        throw new Error("Method not implemented.");
    }
}

