import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";

export class Create_Calendar_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para crear un calendario.
     * @param calendar - Datos del calendario sin ID.
     * @returns Promesa con el calendario creado.
     */
    async execute(calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model> {
        if (!calendar.title || calendar.title.trim() === '') {
            throw new Error("El título del calendario es obligatorio");
        }
        
        if (!calendar.color || calendar.color.trim() === '') {
            throw new Error("El color del calendario es obligatorio");
        }
        
        if (!calendar.owner_id || calendar.owner_id.trim() === '') {
            throw new Error("El propietario del calendario es obligatorio");
        }

        return await this.repository.create(calendar);
    }
}
