import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Neo_Button } from "../ui/Neo_Button";
import { Neo_Card } from "../ui/Neo_Card";
import { Neo_Modal } from "../ui/Neo_Modal";
import { clsx } from "clsx";
import { use_calendars } from "../../hooks/use_calendars";
import { Calendar_Model } from "../../domain/models/calendar_model";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEye,
  faEyeSlash,
  faTrash,
  faPlus,
  faCalendarPlus,
  faFileImport,
  faChevronRight,
  faChevronDown,
  faPencil,
  faInfoCircle,
} from "@fortawesome/free-solid-svg-icons";
import { use_calendar_visibility } from "../../context/CalendarVisibilityContext";
import { use_user_context } from "../../context/UserContext";
import daily_tips from "../../content/daily_tips.json";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

type Tips_By_Day = Record<string, string[]>;
const TIPS_BY_DAY = daily_tips as Tips_By_Day;

/**
 * Devuelve un tip pseudoaleatorio estable para el día actual.
 */
const get_today_tip = (): string => {
  const today = new Date();
  const day = today.getDate().toString(); // '1'...'31'
  const tips_for_day = TIPS_BY_DAY[day];

  if (tips_for_day && tips_for_day.length > 0) {
    const index = Math.floor(Math.random() * tips_for_day.length);
    return tips_for_day[index];
  }

  // Fallback en caso de que falte algún día en el JSON
  const fallback_day = "1";
  const fallback_tips = TIPS_BY_DAY[fallback_day] || [
    "Organiza tu caos como si de granos de arroz se tratase.",
  ];
  const index = Math.floor(Math.random() * fallback_tips.length);
  return fallback_tips[index];
};

/**
 * Componente que muestra un tip distinto cada día.
 */
const Random_Tip: React.FC = () => {
  // Se inicializa una sola vez por montaje de componente: sin parpadeos,
  // pero en cada recarga de la página se puede obtener un tip distinto.
  const [tip] = useState<string>(() => get_today_tip());
  return <p className="text-xs">{tip}</p>;
};

interface CalendarTreeItemProps {
  calendar: Calendar_Model;
  allCalendars: Calendar_Model[];
  activeCalendarId: string | null;
  onCalendarClick: (id: string) => void;
  onDelete?: (calendar: Calendar_Model) => void;
  onEdit?: (calendar: Calendar_Model) => void;
  depth?: number;
}

/**
 * Componente recursivo para renderizar items del árbol de calendarios.
 */
const CalendarTreeItem: React.FC<CalendarTreeItemProps> = ({
  calendar,
  allCalendars,
  activeCalendarId,
  onCalendarClick,
  onDelete,
  onEdit,
  depth = 0,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { toggle_visibility, is_visible } = use_calendar_visibility();
  const navigate = useNavigate();

  const children = allCalendars.filter((c) => c.parent_id === calendar.id);
  const hasChildren = children.length > 0;
  const isActive = activeCalendarId === calendar.id;
  const visible = is_visible(calendar.id);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const handleVisibilityToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggle_visibility(calendar.id);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(calendar);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEdit) {
      onEdit(calendar);
    }
  };

  return (
    <li className="w-full">
      <div
        className={clsx(
          "flex items-center gap-2 w-full text-left rounded transition-all p-1 group",
          isActive
            ? "bg-basmati-yellow/20 font-bold border-r-4 border-basmati-yellow"
            : "hover:bg-white"
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }} // Indentación dinámica
      >
        {hasChildren ? (
          <button
            onClick={handleToggle}
            className="w-4 h-4 flex items-center justify-center hover:bg-gray-100 rounded-sm transition-colors text-basmati-black"
            aria-label={isExpanded ? "Colapsar" : "Expandir"}
          >
            <FontAwesomeIcon
              icon={isExpanded ? faChevronDown : faChevronRight}
              size="xs"
            />
          </button>
        ) : (
          // Spacer for alignment
          <div className="w-4 h-4" />
        )}

        <button
          type="button"
          className="flex items-center gap-2 flex-1 min-w-0 text-left focus:outline-none"
          onClick={() => onCalendarClick(calendar.id)}
          aria-label={`Ver calendario ${calendar.title}`}
        >
          {calendar.icon ? (
            <img
              src={calendar.icon}
              alt=""
              className="w-5 h-5 border-2 border-basmati-black shrink-0 object-cover"
              aria-hidden="true"
            />
          ) : (
            <div
              className="w-3 h-3 border-2 border-basmati-black shrink-0"
              style={{ backgroundColor: calendar.color || "#EBBE4D" }}
              aria-hidden="true"
            ></div>
          )}
          <span className="truncate text-sm">{calendar.title}</span>
        </button>

        <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleVisibilityToggle}
            className="w-5 h-5 flex items-center justify-center hover:bg-gray-200 rounded transition-colors text-basmati-black"
            aria-label={visible ? "Ocultar calendario" : "Mostrar calendario"}
          >
            <FontAwesomeIcon
              icon={visible ? faEye : faEyeSlash}
              className={visible ? "" : "opacity-50"}
              size="xs"
            />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/calendars/${calendar.id}`);
            }}
            className="w-5 h-5 flex items-center justify-center hover:bg-basmati-blue/20 text-basmati-blue rounded transition-colors"
            aria-label="Ver detalles del calendario"
            title="Ver detalles"
          >
            <FontAwesomeIcon icon={faInfoCircle} size="xs" />
          </button>
          {onEdit && (
            <button
              onClick={handleEdit}
              className="w-5 h-5 flex items-center justify-center hover:bg-basmati-blue/20 text-basmati-blue rounded transition-colors"
              aria-label="Editar calendario"
              title="Editar calendario"
            >
              <FontAwesomeIcon icon={faPencil} size="xs" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={handleDelete}
              className="w-5 h-5 flex items-center justify-center hover:bg-basmati-red/20 text-basmati-red rounded transition-colors"
              aria-label="Eliminar calendario"
              title="Eliminar calendario"
            >
              <FontAwesomeIcon icon={faTrash} size="xs" />
            </button>
          )}
        </div>
      </div>

      {hasChildren && isExpanded && (
        <ul className="flex flex-col gap-1 list-none p-0 mt-1">
          {children.map((child) => (
            <CalendarTreeItem
              key={child.id}
              calendar={child}
              allCalendars={allCalendars}
              activeCalendarId={activeCalendarId}
              onCalendarClick={onCalendarClick}
              onDelete={onDelete}
              onEdit={onEdit}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
};

/**
 * Barra lateral de navegación con listado de calendarios.
 * Usa elemento semántico <aside> y navegación accesible.
 */
export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  // Obtener el usuario actual del contexto
  const { user } = use_user_context();
  const current_user_id = user?.external_id || "user_dev_1";

  const { calendars, loading, delete_calendar } =
    use_calendars(current_user_id);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const active_calendar_id = searchParams.get("calendar_id");
  const { toggle_visibility, is_visible } = use_calendar_visibility();

  // Estado para el modal de borrado
  const [calendarToDelete, setCalendarToDelete] =
    useState<Calendar_Model | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const myCalendars = calendars.filter(
    (cal) => cal.owner_id === current_user_id
  );
  // Solo mostramos raíces en el nivel superior
  const myRootCalendars = myCalendars.filter((cal) => !cal.parent_id);

  // Para "Otros calendarios" también filtramos solo las raíces para respetar la jerarquía
  const otherCalendars = calendars.filter(
    (cal) => cal.owner_id !== current_user_id
  );
  const otherRootCalendars = otherCalendars.filter((cal) => !cal.parent_id);

  const handle_calendar_click = (calendar_id: string) => {
    navigate(`/dashboard?calendar_id=${calendar_id}`);
    if (onClose) onClose();
  };

  // Abre el modal
  const prompt_delete_calendar = (calendar: Calendar_Model) => {
    setCalendarToDelete(calendar);
  };

  const confirm_delete_calendar = async () => {
    if (!calendarToDelete) return;

    setIsDeleting(true);
    try {
      // Delegamos la lógica de borrado recursivo al hook (Capa de Presentación/Controlador)
      // Pasamos true para activar el borrado recursivo
      await delete_calendar(calendarToDelete.id, true);

      // Forzar recarga completa para actualizar eventos en el dashboard
      window.location.href = "/dashboard";
    } catch (error) {
      console.error("Failed to delete calendar", error);
      // Podríamos mostrar un toast de error aquí si existiera un sistema de notificaciones global
      alert("Error al eliminar el calendario. Por favor intente nuevamente.");
      setIsDeleting(false);
      setCalendarToDelete(null);
    }
  };

  const handle_edit_calendar = (calendar: Calendar_Model) => {
    navigate(`/calendars/edit/${calendar.id}`);
    if (onClose) onClose();
  };

  const createEventLink = active_calendar_id
    ? `/events/new?calendar_id=${active_calendar_id}`
    : "/events/new";

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={clsx(
          "fixed md:sticky top-16 h-[calc(100vh-64px)] w-64 border-r-3 border-basmati-black bg-basmati-bg p-4 flex flex-col gap-6 overflow-y-auto transition-transform duration-300 z-40",
          "md:translate-x-0", // Always visible on desktop
          isOpen ? "translate-x-0" : "-translate-x-full" // Toggle on mobile
        )}
        aria-label="Menú lateral de calendarios"
        id="sidebar-menu"
      >
        <div>
          <Link to={createEventLink} onClick={onClose}>
            <Neo_Button
              className="w-full flex items-center justify-center gap-2"
              aria-label="Crear nuevo evento"
            >
              <FontAwesomeIcon icon={faPlus} aria-hidden="true" /> Crear evento
            </Neo_Button>
          </Link>
        </div>

        <div>
          <Link to="/calendars/new" onClick={onClose}>
            <Neo_Button
              variant="secondary"
              className="w-full flex items-center justify-center gap-2"
              aria-label="Crear nuevo calendario"
            >
              <FontAwesomeIcon icon={faCalendarPlus} aria-hidden="true" /> Crear
              calendario
            </Neo_Button>
          </Link>
          <Link to="/calendars/import" onClick={onClose} className="block mt-2">
            <Neo_Button
              variant="secondary"
              className="w-full flex items-center justify-center gap-2 text-sm"
              aria-label="Importar calendario"
            >
              <FontAwesomeIcon icon={faFileImport} aria-hidden="true" />{" "}
              Importar calendario
            </Neo_Button>
          </Link>
        </div>

        <nav aria-label="Mis calendarios">
          <h2 className="font-bold text-lg mb-2">Mis calendarios</h2>
          {loading ? (
            <div className="text-sm text-gray-500">Cargando...</div>
          ) : (
            <ul className="flex flex-col gap-2 list-none p-0">
              {myRootCalendars.map((cal) => (
                <CalendarTreeItem
                  key={cal.id}
                  calendar={cal}
                  allCalendars={myCalendars}
                  activeCalendarId={active_calendar_id}
                  onCalendarClick={handle_calendar_click}
                  onDelete={prompt_delete_calendar}
                  onEdit={handle_edit_calendar}
                />
              ))}
              {myCalendars.length === 0 && (
                <li className="text-sm text-gray-500 italic">
                  No tienes calendarios.
                </li>
              )}
            </ul>
          )}
        </nav>

        <nav aria-label="Otros calendarios">
          <h2 className="font-bold text-lg mb-2">Otros calendarios</h2>
          {loading ? (
            <div className="text-sm text-gray-500">Cargando...</div>
          ) : (
            <ul className="flex flex-col gap-2 list-none p-0">
              {otherRootCalendars.map((cal) => (
                <CalendarTreeItem
                  key={cal.id}
                  calendar={cal}
                  allCalendars={otherCalendars}
                  activeCalendarId={active_calendar_id}
                  onCalendarClick={handle_calendar_click}
                />
              ))}
              {otherCalendars.length === 0 && (
                <li className="text-sm text-gray-500 italic">
                  No hay otros calendarios.
                </li>
              )}
            </ul>
          )}
        </nav>

        <div className="mt-auto">
          <Neo_Card
            className="bg-basmati-green/20"
            role="complementary"
            aria-label="Consejo del día"
          >
            <p className="text-xs font-bold mb-2">Tip del día:</p>
            <Random_Tip />
          </Neo_Card>
        </div>
      </aside>

      {/* Modal de confirmación de borrado */}
      <Neo_Modal
        is_open={!!calendarToDelete}
        on_close={() => setCalendarToDelete(null)}
        on_confirm={confirm_delete_calendar}
        title="Eliminar Calendario"
        confirm_text="Sí, eliminar"
        variant="danger"
        loading={isDeleting}
      >
        <div className="text-base">
          <p className="mb-2">
            ¿Estás seguro de que deseas eliminar el calendario{" "}
            <strong>{calendarToDelete?.title}</strong>?
          </p>
          <p className="text-sm text-basmati-red font-bold">
            Esta acción no se puede deshacer. Se eliminarán permanentemente:
          </p>
          <ul className="list-disc pl-5 mt-1 text-sm text-gray-700">
            <li>Todos los eventos asociados.</li>
            <li>Todos los subcalendarios que pertenezcan a este calendario.</li>
          </ul>
        </div>
      </Neo_Modal>
    </>
  );
};
