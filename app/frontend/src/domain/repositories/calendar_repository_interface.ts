import { Calendar_Model } from "../models/calendar_model";

export interface Calendar_Repository_Interface {
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

