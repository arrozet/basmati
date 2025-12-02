import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";

export class Delete_Event_Use_Case {
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
     * Ejecuta la lógica de negocio para eliminar un evento.
     * @param id ID del evento a eliminar.
     * @param user_id ID del usuario actual.
     */
    async execute(id: string, user_id: string): Promise<boolean> {
        if (!id) throw new Error("Event ID is required");

        // Get event to check calendar
        const event = await this.event_repository.get_event(id);
        if (!event) throw new Error("Event not found");

        // Get calendar to check ownership
        const calendar = await this.calendar_repository.get_by_id(event.calendar_id);
        
        // If calendar is not found but event exists, it might be a data inconsistency 
        // or a system calendar event. For safety, if we can't verify ownership, we block deletion.
        if (!calendar) {
            // Alternative: Allow deletion if it's an orphan event? 
            // Strict Clean Architecture: No, we must verify permissions.
             throw new Error("Calendar not found associated with this event. Cannot verify permission.");
        }

        // Strict ownership check
        // Ensure both IDs are strings and trimmed for comparison to avoid false negatives
        const calendarOwner = String(calendar.owner_id).trim();
        const currentUser = String(user_id).trim();

        if (calendarOwner !== currentUser) {
            console.error(`Permission denied: Calendar Owner '${calendarOwner}' !== Current User '${currentUser}'`);
            throw new Error("No tienes permiso para eliminar eventos de este calendario");
        }

        return await this.event_repository.delete(id);
    }
}
