import { useState, useEffect, useCallback } from "react";
import { Notification_Model } from "../../domain/models/notification_model";
import { Http_Notification_Repository } from "../../infrastructure/repositories/http_notification_repository";

// Inyección de dependencias manual
const repository = new Http_Notification_Repository();

// Intervalo de polling para notificaciones (30 segundos)
const POLLING_INTERVAL = 30000;

/**
 * Hook personalizado para gestionar notificaciones del usuario.
 * Proporciona funciones para obtener, marcar como leídas y contar notificaciones.
 * 
 * @param external_id - ID externo del usuario actual
 * @returns Objeto con estado y funciones de notificaciones
 */
export const use_notifications = (external_id: string) => {
    const [notifications, set_notifications] = useState<Notification_Model[]>([]);
    const [unread_count, set_unread_count] = useState<number>(0);
    const [loading, set_loading] = useState<boolean>(true);
    const [error, set_error] = useState<string | null>(null);

    /**
     * Carga todas las notificaciones del usuario.
     */
    const fetch_notifications = useCallback(async () => {
        if (!external_id) return;
        
        try {
            const result = await repository.get_user_notifications(external_id);
            set_notifications(result);
            // Calcular conteo de no leídas
            const unread = result.filter(n => !n.is_read).length;
            set_unread_count(unread);
            set_error(null);
        } catch (err: any) {
            console.error("Error fetching notifications:", err);
            set_error(err.message || "Error al cargar notificaciones");
        } finally {
            set_loading(false);
        }
    }, [external_id]);

    /**
     * Actualiza solo el conteo de notificaciones no leídas.
     * Más ligero que cargar todas las notificaciones.
     */
    const update_unread_count = useCallback(async () => {
        if (!external_id) return;
        
        try {
            const count = await repository.get_unread_count(external_id);
            set_unread_count(count);
        } catch (err: any) {
            console.error("Error updating unread count:", err);
        }
    }, [external_id]);

    /**
     * Marca una notificación como leída.
     * @param notification_id - ID de la notificación
     */
    const mark_as_read = async (notification_id: string) => {
        try {
            await repository.mark_as_read(notification_id);
            // Actualizar estado local
            set_notifications(prev => 
                prev.map(n => 
                    n.id === notification_id ? { ...n, is_read: true } : n
                )
            );
            set_unread_count(prev => Math.max(0, prev - 1));
        } catch (err: any) {
            console.error("Error marking notification as read:", err);
            throw err;
        }
    };

    /**
     * Marca todas las notificaciones como leídas.
     */
    const mark_all_as_read = async () => {
        try {
            await repository.mark_all_as_read(external_id);
            // Actualizar estado local
            set_notifications(prev => prev.map(n => ({ ...n, is_read: true })));
            set_unread_count(0);
        } catch (err: any) {
            console.error("Error marking all notifications as read:", err);
            throw err;
        }
    };

    // Cargar notificaciones al montar
    useEffect(() => {
        if (external_id) {
            fetch_notifications();
        }
    }, [external_id, fetch_notifications]);

    // Polling para actualizar notificaciones periódicamente
    useEffect(() => {
        if (!external_id) return;

        const interval = setInterval(() => {
            update_unread_count();
        }, POLLING_INTERVAL);

        return () => clearInterval(interval);
    }, [external_id, update_unread_count]);

    return {
        notifications,
        unread_count,
        loading,
        error,
        mark_as_read,
        mark_all_as_read,
        refresh: fetch_notifications
    };
};
