import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Event_Model } from "../../domain/models/event_model";

export class Update_Event_Use_Case {
    private event_repository: Event_Repository_Interface;
    private calendar_repository: Calendar_Repository_Interface;

    constructor(
        event_repository: Event_Repository_Interface,
        calendar_repository: Calendar_Repository_Interface
    ) {
        this.event_repository = event_repository;
        this.calendar_repository = calendar_repository;
    }

    /**
     * Actualiza un evento existente verificando la propiedad del calendario.
     * @param event - El evento con los datos actualizados.
     * @param user_id - El ID del usuario que intenta actualizar.
     */
    async execute(event: Event_Model, user_id: string): Promise<Event_Model> {
        if (!event.calendar_id) throw new Error("Calendar ID is required");

        // Verificar que el calendario existe y pertenece al usuario
        const calendar = await this.calendar_repository.get_by_id(event.calendar_id);

        if (!calendar) {
            throw new Error("Calendar not found");
        }

        // Strict ownership check
        const calendarOwner = String(calendar.owner_id).trim();
        const currentUser = String(user_id).trim();

        if (calendarOwner !== currentUser) {
            throw new Error("No tienes permiso para modificar eventos en este calendario");
        }

        // Validaciones básicas
        if (!event.title) throw new Error("Title is required");
        if (!event.start_time) throw new Error("Start time is required");
        if (!event.end_time) throw new Error("End time is required");
        if (new Date(event.end_time) <= new Date(event.start_time)) throw new Error("End time must be after start time");

        // 1. Actualizar evento completo (incluyendo adjuntos)
        // El backend se encarga de reemplazar la lista de adjuntos con la nueva lista enviada
        const updated_event = await this.event_repository.update(event);

        return updated_event;
    }
}
