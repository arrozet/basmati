import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Comment } from "../../domain/models/event_model";

export class Add_Comment_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Añade un comentario a un evento.
     * @param event_id ID del evento
     * @param text Texto del comentario
     * @param user_id ID del usuario
     */
    async execute(event_id: string, text: string, user_id: string): Promise<Event_Comment> {
        if (!text || text.trim().length === 0) {
            throw new Error("El comentario no puede estar vacío");
        }
        return await this.repository.add_comment(event_id, text, user_id);
    }
}



