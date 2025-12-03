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

        // 1. Actualizar datos básicos del evento
        const updated_event = await this.event_repository.update(event);

        // 2. Gestionar nuevos adjuntos
        // Identificar adjuntos nuevos (aquellos que no tienen ID generado por el backend o que sabemos que son nuevos)
        // En este caso simple, si el front envía adjuntos en 'event.attachments', asumimos que
        // debemos intentar añadirlos si no están ya. 
        // Como el update del backend NO toca adjuntos, debemos llamar a add_attachment por cada uno.
        // Pero cuidado de no duplicar.
        
        if (event.attachments && event.attachments.length > 0) {
            // Obtener adjuntos actuales del evento (del backend) para no duplicar
            const current_event_state = await this.event_repository.get_event(event.id);
            const current_attachment_urls = new Set(current_event_state?.attachments?.map(a => a.url) || []);

            const new_attachments = event.attachments.filter(att => !current_attachment_urls.has(att.url));

            if (new_attachments.length > 0) {
                try {
                    const attachments_promises = new_attachments.map(attachment => 
                        this.event_repository.add_attachment(updated_event.id, attachment)
                    );
                    await Promise.all(attachments_promises);
                    
                    // Actualizar el modelo devuelto
                    if (!updated_event.attachments) updated_event.attachments = [];
                    updated_event.attachments.push(...new_attachments);
                    
                } catch (error) {
                    console.error("Error adding new attachments:", error);
                }
            }
        }

        return updated_event;
    }
}
