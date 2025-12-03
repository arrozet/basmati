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

        // 1. Crear el evento
        const created_event = await this.event_repository.create(event);

        // 2. Asociar adjuntos si existen
        if (event.attachments && event.attachments.length > 0) {
            try {
                const attachments_promises = event.attachments.map(attachment => 
                    this.event_repository.add_attachment(created_event.id, attachment)
                );
                await Promise.all(attachments_promises);
                
                // Actualizamos el objeto evento con los adjuntos para devolverlo completo
                // Nota: add_attachment devuelve el attachment creado, no el evento
                // Idealmente recargaríamos el evento, pero podemos adjuntarlos manualmente
                // ya que acabamos de subirlos.
                created_event.attachments = event.attachments;
            } catch (error) {
                console.error("Error linking attachments to event:", error);
                // No fallamos toda la creación, pero logueamos el error
            }
        }

        return created_event;
    }
}
