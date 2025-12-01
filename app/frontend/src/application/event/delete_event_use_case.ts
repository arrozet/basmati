import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";

export class Delete_Event_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para eliminar un evento.
     * @param id ID del evento a eliminar.
     */
    async execute(id: string): Promise<boolean> {
        if (!id) throw new Error("Event ID is required");
        return await this.repository.delete(id);
    }
}

