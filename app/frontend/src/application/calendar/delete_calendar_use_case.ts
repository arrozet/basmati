import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";

export class Delete_Calendar_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para eliminar un calendario.
     * @param id - ID del calendario a eliminar.
     * @returns Promesa que se resuelve cuando se elimina correctamente.
     */
    async execute(id: string): Promise<void> {
        if (!id || id.trim() === '') {
            throw new Error("El ID del calendario es obligatorio");
        }

        await this.repository.delete(id);
    }
}
