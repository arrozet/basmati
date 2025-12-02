import { useState, useEffect } from "react";
import { Calendar_Model } from "../../domain/models/calendar_model";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Create_Calendar_Use_Case } from "../../application/calendar/create_calendar_use_case";
import { Update_Calendar_Use_Case } from "../../application/calendar/update_calendar_use_case";
import { Delete_Calendar_Use_Case } from "../../application/calendar/delete_calendar_use_case";

// Inyección de dependencias manual
const repository = new Http_Calendar_Repository();
const create_calendar_use_case = new Create_Calendar_Use_Case(repository);
const update_calendar_use_case = new Update_Calendar_Use_Case(repository);
const delete_calendar_use_case = new Delete_Calendar_Use_Case(repository);

/**
 * Hook personalizado para gestionar calendarios.
 * Proporciona funciones para crear, actualizar, eliminar y obtener calendarios.
 */
export const use_calendars = (user_id: string) => {
    const [calendars, set_calendars] = useState<Calendar_Model[]>([]);
    const [loading, set_loading] = useState(true);
    const [error, set_error] = useState<string | null>(null);

    /**
     * Carga los calendarios del usuario.
     */
    const fetch_calendars = async () => {
        set_loading(true);
        set_error(null);
        try {
            const result = await repository.get_all(user_id);
            set_calendars(result);
        } catch (err: any) {
            console.error("Error fetching calendars:", err);
            set_error(err.message || "Error al cargar calendarios");
        } finally {
            set_loading(false);
        }
    };

    useEffect(() => {
        if (user_id) {
            fetch_calendars();
        }
    }, [user_id]);

    /**
     * Crea un nuevo calendario.
     */
    const create_calendar = async (calendar: Omit<Calendar_Model, 'id'>): Promise<Calendar_Model> => {
        try {
            const new_calendar = await create_calendar_use_case.execute(calendar);
            set_calendars((prev: Calendar_Model[]) => [...prev, new_calendar]);
            return new_calendar;
        } catch (err: any) {
            console.error("Error creating calendar:", err);
            throw err;
        }
    };

    /**
     * Actualiza un calendario existente.
     */
    const update_calendar = async (calendar: Calendar_Model): Promise<Calendar_Model> => {
        try {
            const updated_calendar = await update_calendar_use_case.execute(calendar);
            set_calendars((prev: Calendar_Model[]) => prev.map((c: Calendar_Model) => c.id === updated_calendar.id ? updated_calendar : c));
            return updated_calendar;
        } catch (err: any) {
            console.error("Error updating calendar:", err);
            throw err;
        }
    };

    /**
     * Elimina un calendario por su ID.
     * Si recursive es true, elimina también todos los subcalendarios descendientes.
     */
    const delete_calendar = async (id: string, recursive: boolean = false): Promise<void> => {
        try {
            // Pasamos la lista completa de calendarios al caso de uso si es recursivo
            // El Caso de Uso encapsula la lógica de "qué" se debe borrar.
            const context_calendars = recursive ? calendars : undefined;
            
            const deleted_ids = await delete_calendar_use_case.execute(id, context_calendars);
            
            // Actualizamos el estado local eliminando todos los IDs que el Caso de Uso nos reportó como borrados
            set_calendars((prev: Calendar_Model[]) => prev.filter((c: Calendar_Model) => !deleted_ids.includes(c.id)));
        } catch (err: any) {
            console.error("Error deleting calendar:", err);
            throw err;
        }
    };

    /**
     * Obtiene un calendario específico por su ID.
     */
    const get_calendar_by_id = async (id: string): Promise<Calendar_Model | null> => {
        try {
            return await repository.get_by_id(id);
        } catch (err: any) {
            console.error("Error fetching calendar:", err);
            return null;
        }
    };

    return {
        calendars,
        loading,
        error,
        create_calendar,
        update_calendar,
        delete_calendar,
        get_calendar_by_id,
        refresh: fetch_calendars
    };
};
