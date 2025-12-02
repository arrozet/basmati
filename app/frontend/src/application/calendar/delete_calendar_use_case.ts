import { Calendar_Repository_Interface, Delete_Recursive_Result } from "../../domain/repositories/calendar_repository_interface";
import { Calendar_Model } from "../../domain/models/calendar_model";

/**
 * Resultado de la eliminación de un calendario.
 * Puede ser simple (solo IDs) o completo (con detalles del backend).
 */
export interface Delete_Calendar_Result {
    /** Lista de IDs de calendarios eliminados */
    deleted_ids: string[];
    /** Número de eventos eliminados (solo en modo recursivo) */
    events_deleted?: number;
    /** Errores parciales si los hubo */
    errors?: string[];
}

export class Delete_Calendar_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para eliminar un calendario.
     * Si se proporciona la lista de calendarios, realiza un borrado recursivo
     * utilizando el endpoint V2 del backend que elimina subcalendarios y eventos.
     * 
     * @param id - ID del calendario a eliminar.
     * @param all_calendars - (Opcional) Lista completa de calendarios. Si se proporciona,
     *                        se usará eliminación recursiva via backend V2.
     * @returns Promesa con el resultado de la eliminación.
     */
    async execute(id: string, all_calendars?: Calendar_Model[]): Promise<Delete_Calendar_Result> {
        if (!id || id.trim() === '') {
            throw new Error("El ID del calendario es obligatorio");
        }

        // Si se proporciona contexto de calendarios, usar eliminación recursiva del backend
        if (all_calendars && all_calendars.length > 0) {
            // Calcular IDs que serán eliminados (para actualizar UI)
            const descendants = this.get_descendants(id, all_calendars);
            const ids_to_delete = [...descendants, id];
            
            // Llamar al endpoint V2 que elimina recursivamente en el backend
            // Esto elimina: eventos de subcalendarios, subcalendarios, eventos del calendario raíz y calendario raíz
            const result: Delete_Recursive_Result = await this.repository.delete_recursive(id);
            
            return {
                deleted_ids: ids_to_delete,
                events_deleted: result.events_deleted,
                errors: result.errors
            };
        }

        // Eliminación simple (sin recursividad)
        await this.repository.delete(id);
        return {
            deleted_ids: [id]
        };
    }

    /**
     * Función pura de dominio para encontrar descendientes en una estructura de árbol plana.
     * Se usa para calcular qué IDs deben eliminarse del estado local de la UI.
     * @param parent_id - ID del calendario padre.
     * @param all_calendars - Lista completa de calendarios.
     * @returns Lista de IDs de calendarios descendientes.
     */
    private get_descendants(parent_id: string, all_calendars: Calendar_Model[]): string[] {
        const children = all_calendars.filter(cal => cal.parent_id === parent_id);
        let ids: string[] = [];
        
        for (const child of children) {
            ids.push(child.id);
            // Recursividad para obtener todos los niveles de descendientes
            ids = [...ids, ...this.get_descendants(child.id, all_calendars)];
        }
        
        return ids;
    }
}
