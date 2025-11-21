import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Get_Events_By_Date_Range_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    async execute(start: Date, end: Date): Promise<Event_Model[]> {
        return await this.repository.get_events_by_date_range(start, end);
    }
}
