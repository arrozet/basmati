import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";

export class Delete_Calendar_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para eliminar un calendario.
     * Si se proporciona la lista de calendarios, realiza un borrado recursivo de hijos.
     * 
     * @param id - ID del calendario a eliminar.
     * @param all_calendars - (Opcional) Lista completa de calendarios para calcular descendientes.
     * @returns Promesa con la lista de IDs eliminados.
     */
    async execute(id: string, all_calendars?: Calendar_Model[]): Promise<string[]> {
        if (!id || id.trim() === '') {
            throw new Error("El ID del calendario es obligatorio");
        }

        let ids_to_delete: string[] = [id];

        // Lógica de Negocio: Calcular cascada si tenemos el contexto
        if (all_calendars && all_calendars.length > 0) {
            const descendants = this.get_descendants(id, all_calendars);
            ids_to_delete = [...descendants, id];
        }

        // Orquestación de llamadas al repositorio (Infraestructura)
        // Usamos Promise.all para eficiencia, pero manejamos errores individualmente si fuera necesario
        // En este caso, si falla uno, fallará la promesa global, lo cual es comportamiento seguro por defecto.
        await Promise.all(ids_to_delete.map(target_id => this.repository.delete(target_id)));

        return ids_to_delete;
    }

    /**
     * Función pura de dominio para encontrar descendientes en una estructura de árbol plana.
     */
    private get_descendants(parent_id: string, all_calendars: Calendar_Model[]): string[] {
        const children = all_calendars.filter(cal => cal.parent_id === parent_id);
        let ids: string[] = [];
        
        for (const child of children) {
            ids.push(child.id);
            // Recursividad
            ids = [...ids, ...this.get_descendants(child.id, all_calendars)];
        }
        
        return ids;
    }
}
