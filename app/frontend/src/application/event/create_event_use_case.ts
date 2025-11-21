import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Create_Event_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    async execute(event: Omit<Event_Model, 'id'>): Promise<Event_Model> {
        // Basic validation
        if (!event.title) throw new Error("Title is required");
        if (!event.start_time) throw new Error("Start time is required");
        if (!event.end_time) throw new Error("End time is required");
        if (event.end_time <= event.start_time) throw new Error("End time must be after start time");

        return await this.repository.create(event);
    }
}
