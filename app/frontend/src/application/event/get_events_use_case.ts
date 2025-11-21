import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";

export class Get_Events_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    async execute(calendar_id: string) {
        return await this.repository.get_events(calendar_id);
    }
}

