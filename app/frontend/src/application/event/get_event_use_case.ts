import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Get_Event_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Obtiene un evento por su ID.
     * @param id - ID del evento.
     * @returns El evento encontrado o null.
     */
    async execute(id: string): Promise<Event_Model | null> {
        if (!id) throw new Error("Event ID is required");
        return await this.repository.get_event(id);
    }
}

