import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Create_Event_Use_Case {
    private event_repository: Event_Repository_Interface;
    private calendar_repository: Calendar_Repository_Interface;

    constructor(
        event_repository: Event_Repository_Interface,
        calendar_repository: Calendar_Repository_Interface
    ) {
        this.event_repository = event_repository;
        this.calendar_repository = calendar_repository;
    }

    async execute(event: Omit<Event_Model, 'id'>, user_id: string): Promise<Event_Model> {
        // Basic validation
        if (!event.title) throw new Error("Title is required");
        if (!event.start_time) throw new Error("Start time is required");
        if (!event.end_time) throw new Error("End time is required");
        if (event.end_time <= event.start_time) throw new Error("End time must be after start time");
        if (!event.calendar_id) throw new Error("Calendar ID is required");

        // Verify ownership
        const calendar = await this.calendar_repository.get_by_id(event.calendar_id);
        if (!calendar) throw new Error("Calendar not found");
        
        if (calendar.owner_id !== user_id) {
            throw new Error("No tienes permiso para crear eventos en este calendario");
        }

        return await this.event_repository.create(event);
    }
}
