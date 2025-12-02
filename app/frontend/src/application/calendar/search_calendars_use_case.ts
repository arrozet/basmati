import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";

export class Search_Calendars_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la búsqueda de calendarios.
     * @param query - Texto a buscar.
     */
    async execute(query: string): Promise<Calendar_Model[]> {
        if (!query.trim()) {
            return [];
        }
        return await this.repository.search(query);
    }
}

