import { Calendar_Model } from "../models/calendar_model";

/**
 * Resultado de la eliminación recursiva de un calendario.
 * Contiene información sobre los calendarios y eventos eliminados.
 */
export interface Delete_Recursive_Result {
    /** Mensaje descriptivo del resultado */
    message: string;
    /** ID del calendario raíz eliminado */
    calendar_id: string;
    /** Número de calendarios eliminados (incluyendo subcalendarios) */
    calendars_deleted: number;
    /** Número de eventos eliminados */
    events_deleted: number;
    /** Lista de errores si hubo problemas parciales */
    errors?: string[];
}

export interface Calendar_Repository_Interface {
    /**
     * Obtiene todos los calendarios del sistema (usando el nuevo endpoint v2).
     * @param limit Número máximo de calendarios a devolver.
     * @returns Promesa con la lista de calendarios.
     */
    get_all_calendars(limit?: number): Promise<Calendar_Model[]>;
    
    /**
     * Obtiene todos los calendarios de un usuario.
     * @param user_id - ID del usuario propietario.
     * @returns Promesa con la lista de calendarios.
     */
    get_all(user_id: string): Promise<Calendar_Model[]>;
    
    /**
     * Crea un nuevo calendario.
     * @param calendar - Datos del calendario sin ID.
     * @returns Promesa con el calendario creado incluyendo su ID.
     */
    create(calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model>;
    
    /**
     * Actualiza un calendario existente.
     * @param calendar - Datos del calendario incluyendo su ID.
     * @returns Promesa con el calendario actualizado.
     */
    update(calendar: Calendar_Model): Promise<Calendar_Model>;
    
    /**
     * Elimina un calendario por su ID.
     * @param id - ID del calendario a eliminar.
     * @returns Promesa que se resuelve cuando se elimina correctamente.
     */
    delete(id: string): Promise<void>;
    
    /**
     * Elimina un calendario recursivamente junto con todos sus subcalendarios y eventos.
     * Utiliza el endpoint v2 del backend que maneja la eliminación en cascada.
     * @param id - ID del calendario raíz a eliminar.
     * @returns Promesa con el resultado de la eliminación (IDs eliminados y contadores).
     */
    delete_recursive(id: string): Promise<Delete_Recursive_Result>;
    
    /**
     * Obtiene un calendario específico por su ID.
     * @param id - ID del calendario.
     * @returns Promesa con el calendario o null si no existe.
     */
    get_by_id(id: string): Promise<Calendar_Model | null>;

    /**
     * Busca calendarios por texto.
     * @param query - Texto a buscar.
     * @returns Promesa con la lista de calendarios encontrados.
     */
    search(query: string): Promise<Calendar_Model[]>;
}

