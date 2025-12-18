import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBell,
  faCheck,
  faCheckDouble,
  faTimes,
  faComment,
  faCalendar,
  faClock,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import { use_notifications } from "../../hooks/use_notifications";
import {
  Notification_Model,
  Notification_Type,
} from "../../../domain/models/notification_model";
import { useNavigate } from "react-router-dom";

interface Notification_Bell_Props {
  external_id: string;
}

/**
 * Componente de campana de notificaciones.
 * Muestra un icono de campana con un badge del número de notificaciones no leídas.
 * Al hacer clic, despliega un menú con las notificaciones recientes.
 */
export const Notification_Bell: React.FC<Notification_Bell_Props> = ({
  external_id,
}) => {
  const [is_open, set_is_open] = useState(false);
  const dropdown_ref = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const {
    notifications,
    unread_count,
    loading,
    mark_as_read,
    mark_all_as_read,
    refresh,
  } = use_notifications(external_id);

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    const handle_click_outside = (event: MouseEvent) => {
      if (
        dropdown_ref.current &&
        !dropdown_ref.current.contains(event.target as Node)
      ) {
        set_is_open(false);
      }
    };

    document.addEventListener("mousedown", handle_click_outside);
    return () =>
      document.removeEventListener("mousedown", handle_click_outside);
  }, []);

  /**
   * Obtiene el icono correspondiente al tipo de notificación.
   */
  const get_notification_icon = (type: Notification_Type) => {
    switch (type) {
      case "NEW_COMMENT":
        return faComment;
      case "CALENDAR_INVITE":
        return faCalendar;
      case "EVENT_REMINDER":
        return faClock;
      case "EVENT_UPDATE":
        return faExclamationCircle;
      default:
        return faBell;
    }
  };

  /**
   * Formatea la fecha de la notificación en formato relativo.
   * Las fechas del backend vienen en UTC pero sin el sufijo "Z", por lo que
   * hay que añadirlo para que JavaScript las interprete correctamente.
   */
  const format_relative_time = (date_string: string): string => {
    // Añadir "Z" si la fecha no tiene indicador de zona horaria (UTC)
    // Esto evita que JavaScript la interprete como hora local
    const has_timezone =
      date_string.endsWith("Z") ||
      date_string.includes("+") ||
      /T\d{2}:\d{2}:\d{2}.*-\d{2}/.test(date_string);
    const utc_date_string = has_timezone ? date_string : date_string + "Z";

    const date = new Date(utc_date_string);
    const now = new Date();
    const diff_ms = now.getTime() - date.getTime();
    const diff_minutes = Math.floor(diff_ms / 60000);
    const diff_hours = Math.floor(diff_minutes / 60);
    const diff_days = Math.floor(diff_hours / 24);

    if (diff_minutes < 1) return "Ahora mismo";
    if (diff_minutes < 60) return `Hace ${diff_minutes} min`;
    if (diff_hours < 24) return `Hace ${diff_hours}h`;
    if (diff_days < 7) return `Hace ${diff_days} días`;
    return date.toLocaleDateString("es-ES", { day: "numeric", month: "short" });
  };

  /**
   * Maneja el clic en una notificación.
   */
  const handle_notification_click = async (
    notification: Notification_Model
  ) => {
    // Marcar como leída si no lo está
    if (!notification.is_read) {
      await mark_as_read(notification.id);
    }

    // Navegar al evento relacionado si existe
    if (notification.related_event_id) {
      set_is_open(false);
      navigate(`/events/${notification.related_event_id}`);
    }
  };

  /**
   * Maneja el clic en "Marcar todas como leídas".
   */
  const handle_mark_all_read = async () => {
    await mark_all_as_read();
  };

  return (
    <div className="relative" ref={dropdown_ref}>
      {/* Botón de la campana */}
      <button
        type="button"
        onClick={() => {
          set_is_open(!is_open);
        }}
        className="relative p-2 font-bold border-3 border-basmati-black shadow-hard active:shadow-none active:translate-x-[2px] active:translate-y-[2px] transition-all focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 hover:bg-basmati-yellow bg-white"
        aria-label={`Notificaciones${
          unread_count > 0 ? `, ${unread_count} sin leer` : ""
        }`}
        aria-expanded={is_open}
        aria-haspopup="true"
      >
        <FontAwesomeIcon icon={faBell} className="text-xl" />

        {/* Badge de conteo */}
        {unread_count > 0 && (
          <span
            className="absolute -top-2 -right-2 bg-basmati-red text-white text-xs font-black w-6 h-6 flex items-center justify-center border-2 border-basmati-black rounded-full"
            aria-hidden="true"
          >
            {unread_count > 99 ? "99+" : unread_count}
          </span>
        )}
      </button>

      {/* Dropdown de notificaciones */}
      {is_open && (
        <div
          className="fixed left-2 right-2 top-[4.5rem] md:absolute md:left-auto md:right-0 md:top-full md:mt-2 md:w-96 bg-white border-3 border-basmati-black shadow-hard z-50 max-h-[70vh] overflow-hidden flex flex-col"
          role="menu"
          aria-label="Menú de notificaciones"
        >
          {/* Header del dropdown */}
          <div className="flex items-center justify-between p-3 border-b-3 border-basmati-black bg-basmati-yellow">
            <h3 className="font-black text-lg">Notificaciones</h3>
            <div className="flex gap-2">
              {unread_count > 0 && (
                <button
                  type="button"
                  onClick={handle_mark_all_read}
                  className="text-sm font-bold flex items-center gap-1 hover:text-basmati-blue transition-colors focus:outline-none focus:ring-2 focus:ring-basmati-black rounded px-2 py-1"
                  aria-label="Marcar todas como leídas"
                >
                  <FontAwesomeIcon icon={faCheckDouble} />
                  <span className="hidden sm:inline">Leer todo</span>
                </button>
              )}
              <button
                type="button"
                onClick={() => set_is_open(false)}
                className="p-1 hover:bg-basmati-black/10 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-basmati-black"
                aria-label="Cerrar notificaciones"
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
          </div>

          {/* Lista de notificaciones */}
          <div className="overflow-y-auto flex-1">
            {loading ? (
              <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-3 border-basmati-black mx-auto"></div>
                <p className="mt-2 text-sm text-gray-600">Cargando...</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-6 text-center">
                <FontAwesomeIcon
                  icon={faBell}
                  className="text-4xl text-gray-300 mb-3"
                />
                <p className="text-gray-600 font-medium">
                  No tienes notificaciones
                </p>
                <p className="text-sm text-gray-400 mt-1">
                  Las nuevas notificaciones aparecerán aquí
                </p>
              </div>
            ) : (
              <ul className="divide-y-2 divide-basmati-black/20">
                {notifications.map((notification) => (
                  <li key={notification.id}>
                    <button
                      type="button"
                      onClick={() => handle_notification_click(notification)}
                      className={`w-full text-left p-4 hover:bg-basmati-yellow/20 transition-colors focus:outline-none focus:bg-basmati-yellow/30 ${
                        !notification.is_read ? "bg-basmati-yellow/10" : ""
                      }`}
                      role="menuitem"
                    >
                      <div className="flex gap-3">
                        <div
                          className={`flex-shrink-0 w-10 h-10 rounded-full border-2 border-basmati-black flex items-center justify-center ${
                            !notification.is_read
                              ? "bg-basmati-yellow"
                              : "bg-gray-100"
                          }`}
                        >
                          <FontAwesomeIcon
                            icon={get_notification_icon(notification.type)}
                            className={
                              !notification.is_read
                                ? "text-basmati-black"
                                : "text-gray-500"
                            }
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p
                            className={`text-sm ${
                              !notification.is_read
                                ? "font-bold"
                                : "font-medium"
                            } truncate`}
                          >
                            {notification.title}
                          </p>
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {format_relative_time(notification.created_at)}
                          </p>
                        </div>
                        {!notification.is_read && (
                          <div className="flex-shrink-0">
                            <span className="block w-3 h-3 bg-basmati-blue rounded-full border border-basmati-black"></span>
                          </div>
                        )}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
