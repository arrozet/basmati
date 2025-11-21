import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Search_Events_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la búsqueda de eventos.
     * @param query Texto a buscar (simple) o objeto de criterios (avanzada).
     * @returns Lista de eventos encontrados.
     */
    async execute(query: string | { title?: string; organizer?: string; keywords?: string }): Promise<Event_Model[]> {
        if (typeof query === 'string') {
            if (!query || query.trim() === "") {
                return [];
            }
            return await this.repository.search_events(query);
        } else {
            // Búsqueda avanzada
            const { title, organizer, keywords } = query;
            if (!title && !organizer && !keywords) {
                return [];
            }
            return await this.repository.search_advanced(query);
        }
    }
}
