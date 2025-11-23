import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";

export class Update_Calendar_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para actualizar un calendario.
     * @param calendar - Datos del calendario incluyendo su ID.
     * @returns Promesa con el calendario actualizado.
     */
    async execute(calendar: Calendar_Model): Promise<Calendar_Model> {
        if (!calendar.id || calendar.id.trim() === '') {
            throw new Error("El ID del calendario es obligatorio");
        }
        
        if (!calendar.title || calendar.title.trim() === '') {
            throw new Error("El título del calendario es obligatorio");
        }
        
        if (!calendar.color || calendar.color.trim() === '') {
            throw new Error("El color del calendario es obligatorio");
        }

        return await this.repository.update(calendar);
    }
}
