import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Neo_Modal } from "../components/ui/Neo_Modal";
import { Location_Picker } from "../components/ui/Location_Picker";
import { Image_Uploader } from "../components/ui/Image_Uploader";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Event_Model, Event_Attachment } from "../../domain/models/event_model";
import { Event_Location } from "../../domain/models/integration_models";
import { Update_Event_Use_Case } from "../../application/event/update_event_use_case";
import { Get_Event_Use_Case } from "../../application/event/get_event_use_case";
import { Delete_Event_Use_Case } from "../../application/event/delete_event_use_case";
import { use_page_title } from "../hooks/use_page_title";
import { use_user_context } from "../context/UserContext";

// Dependencies
const event_repository = new Http_Event_Repository();
const calendar_repository = new Http_Calendar_Repository();

const get_event_use_case = new Get_Event_Use_Case(event_repository);
const update_event_use_case = new Update_Event_Use_Case(
  event_repository,
  calendar_repository
);
const delete_event_use_case = new Delete_Event_Use_Case(
  event_repository,
  calendar_repository
);

/**
 * Página de edición de evento accesible.
 * Formulario con labels asociados, botones semánticos y aria-labels.
 */
export const Edit_Event_Page = () => {
  use_page_title("Edit event");
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = use_user_context();
  const current_user_id = user?.external_id || "user_dev_1";
  const [loading, set_loading] = useState(true);
  const [saving, set_saving] = useState(false);
  const [error, set_error] = useState<string | null>(null);
  const [event, set_event] = useState<Event_Model | null>(null);
  const [calendar_info, set_calendar_info] = useState<{
    title: string;
    color: string;
  } | null>(null);

  // Modal de confirmación para borrar
  const [delete_modal_open, set_delete_modal_open] = useState(false);
  const [deleting, set_deleting] = useState(false);

  const [form_data, set_form_data] = useState({
    title: "",
    start_date: "",
    start_time: "",
    end_date: "",
    end_time: "",
    description: "",
  });

  const [location, set_location] = useState<Event_Location | null>(null);
  const [attachments, set_attachments] = useState<Event_Attachment[]>([]);

  useEffect(() => {
    const fetch_event = async () => {
      if (!id) return;
      try {
        const fetched_event = await get_event_use_case.execute(id);
        if (fetched_event) {
          set_event(fetched_event);

          // Format dates for inputs
          const start = fetched_event.start_time;
          const end = fetched_event.end_time;

          // Handle timezone offset for input type="date" and "time"
          // Using local time components
          const format_date = (d: Date) => {
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, "0");
            const day = String(d.getDate()).padStart(2, "0");
            return `${year}-${month}-${day}`;
          };

          const format_time = (d: Date) => {
            const hours = String(d.getHours()).padStart(2, "0");
            const minutes = String(d.getMinutes()).padStart(2, "0");
            return `${hours}:${minutes}`;
          };

          set_form_data({
            title: fetched_event.title,
            start_date: format_date(start),
            start_time: format_time(start),
            end_date: format_date(end),
            end_time: format_time(end),
            description: fetched_event.description || "",
          });

          // Cargar ubicación si existe
          if (fetched_event.location) {
            set_location(fetched_event.location);
          }

          // Cargar adjuntos si existen
          if (fetched_event.attachments) {
            set_attachments(fetched_event.attachments);
          }

          // Fetch calendar info
          try {
            const calendar = await calendar_repository.get_by_id(
              fetched_event.calendar_id
            );
            if (calendar) {
              set_calendar_info({
                title: calendar.title,
                color: calendar.color,
              });
            }
          } catch (cal_err) {
            console.error("Error al cargar info del calendario", cal_err);
          }
        } else {
          set_error("Evento no encontrado");
        }
      } catch (err) {
        console.error(err);
        set_error("Error al cargar el evento");
      } finally {
        set_loading(false);
      }
    };
    fetch_event();
  }, [id]);

  const handle_submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!event) return;

    set_saving(true);
    set_error(null);

    try {
      const start_iso = new Date(
        `${form_data.start_date}T${form_data.start_time}:00`
      );
      const end_iso = new Date(
        `${form_data.end_date}T${form_data.end_time}:00`
      );

      const updated_event: Event_Model = {
        ...event,
        title: form_data.title,
        description: form_data.description,
        start_time: start_iso,
        end_time: end_iso,
        location: location || undefined,
        attachments: attachments,
      };

      await update_event_use_case.execute(updated_event, current_user_id);
      navigate("/dashboard");
    } catch (err: any) {
      console.error(err);
      if (err.response && err.response.data) {
        set_error(
          `Error del servidor: ${JSON.stringify(
            err.response.data.detail || err.response.data
          )}`
        );
      } else {
        set_error(err.message || "Error al guardar los cambios");
      }
    } finally {
      set_saving(false);
    }
  };

  const handle_delete_click = () => {
    set_delete_modal_open(true);
  };

  const handle_confirm_delete = async () => {
    if (!event) return;

    set_deleting(true);
    try {
      await delete_event_use_case.execute(event.id, current_user_id);
      navigate("/dashboard");
    } catch (error: any) {
      console.error("Error al eliminar evento:", error);
      set_error(error.message || "Error al eliminar el evento");
      set_delete_modal_open(false); // Close modal if error to show message
    } finally {
      set_deleting(false);
    }
  };

  const handle_close_delete_modal = () => {
    if (!deleting) {
      set_delete_modal_open(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64">
          <div className="text-xl text-gray-600">Cargando evento...</div>
        </div>
      </MainLayout>
    );
  }

  if (error && !event) {
    // Only show full page error if event not loaded
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64 flex-col">
          <div className="text-xl text-red-600 mb-4">{error}</div>
          <Neo_Button
            onClick={() => navigate("/dashboard")}
            variant="secondary"
          >
            Volver al Dashboard
          </Neo_Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="flex justify-center">
        <div className="w-full max-w-4xl">
          <div className="mb-4">
            <Neo_Button onClick={() => navigate(-1)} variant="secondary">
              <FontAwesomeIcon icon={faArrowLeft} className="mr-2" /> Volver
            </Neo_Button>
          </div>
          <Neo_Card className="w-full">
            <header className="mb-4 flex justify-between items-center">
              <h1 className="text-2xl font-black">Editar evento</h1>
              <Neo_Button
                type="button"
                variant="danger"
                onClick={handle_delete_click}
                aria-label="Eliminar este evento"
              >
                Eliminar evento
              </Neo_Button>
            </header>

            <form
              onSubmit={handle_submit}
              className="space-y-4"
              aria-label="Formulario de edición de evento"
            >
              {/* Indicador del calendario */}
              <div className="flex items-center gap-3 p-3 border-3 border-basmati-black bg-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
                <span className="text-sm font-bold text-gray-600 uppercase">
                  Calendario:
                </span>
                <span
                  className="w-4 h-4 border-2 border-basmati-black"
                  style={{ backgroundColor: calendar_info?.color || "#EBBE4D" }}
                  aria-hidden="true"
                ></span>
                <span className="text-sm font-bold">
                  {calendar_info?.title || "Cargando..."}
                </span>
              </div>

              <fieldset className="border-0 p-0 m-0">
                <legend className="sr-only">
                  Información básica del evento
                </legend>
                <Neo_Input
                  label="Título"
                  value={form_data.title}
                  onChange={(e) =>
                    set_form_data({ ...form_data, title: e.target.value })
                  }
                  placeholder="Título del evento"
                  required
                  id="event-title"
                />
              </fieldset>

              <fieldset className="border-0 p-0 m-0">
                <legend className="text-sm font-bold text-basmati-black mb-3">
                  Fecha y hora de inicio
                </legend>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Neo_Input
                    label="Fecha inicio"
                    type="date"
                    value={form_data.start_date}
                    onChange={(e) =>
                      set_form_data({
                        ...form_data,
                        start_date: e.target.value,
                      })
                    }
                    required
                    id="event-start-date"
                  />
                  <Neo_Input
                    label="Hora inicio"
                    type="time"
                    value={form_data.start_time}
                    onChange={(e) =>
                      set_form_data({
                        ...form_data,
                        start_time: e.target.value,
                      })
                    }
                    required
                    id="event-start-time"
                  />
                </div>
              </fieldset>

              <fieldset className="border-0 p-0 m-0">
                <legend className="text-sm font-bold text-basmati-black mb-3">
                  Fecha y hora de fin
                </legend>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Neo_Input
                    label="Fecha fin"
                    type="date"
                    value={form_data.end_date}
                    onChange={(e) =>
                      set_form_data({ ...form_data, end_date: e.target.value })
                    }
                    required
                    id="event-end-date"
                  />
                  <Neo_Input
                    label="Hora fin"
                    type="time"
                    value={form_data.end_time}
                    onChange={(e) =>
                      set_form_data({ ...form_data, end_time: e.target.value })
                    }
                    required
                    id="event-end-time"
                  />
                </div>
              </fieldset>

              <fieldset className="border-0 p-0 m-0">
                <legend className="sr-only">Descripción del evento</legend>
                <label
                  htmlFor="event-description"
                  className="block text-sm font-bold text-basmati-black mb-1"
                >
                  Descripción
                </label>
                <textarea
                  id="event-description"
                  className="w-full px-3 py-2 border-3 border-basmati-black focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 bg-white rounded-sm hover:shadow-hard transition-shadow"
                  rows={4}
                  value={form_data.description}
                  onChange={(e) =>
                    set_form_data({ ...form_data, description: e.target.value })
                  }
                  placeholder="Detalles del evento..."
                  aria-label="Descripción del evento"
                />
              </fieldset>

              {/* Selector de ubicación con mapa OpenStreetMap */}
              <Location_Picker
                value={location}
                on_change={set_location}
                id="event-location"
                disabled={saving}
              />

              {/* Cargador de Imágenes */}
              <Image_Uploader
                attachments={attachments}
                onChange={set_attachments}
                disabled={saving}
              />

              {error && (
                <div
                  className="bg-basmati-red text-white p-3 font-bold border-3 border-basmati-black mt-4"
                  role="alert"
                  aria-live="assertive"
                >
                  {error}
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4 border-t-3 border-gray-200 mt-4">
                <Neo_Button
                  type="button"
                  variant="secondary"
                  onClick={() => navigate("/dashboard")}
                  aria-label="Cancelar edición y volver"
                >
                  Cancelar
                </Neo_Button>
                <Neo_Button
                  type="submit"
                  variant="primary"
                  disabled={saving}
                  loading={saving}
                  aria-label="Guardar cambios del evento"
                >
                  Guardar cambios
                </Neo_Button>
              </div>
            </form>

            {/* Modal de confirmación de borrado */}
            <Neo_Modal
              is_open={delete_modal_open}
              on_close={handle_close_delete_modal}
              on_confirm={handle_confirm_delete}
              title="¿Eliminar evento?"
              variant="danger"
              confirm_text="Eliminar"
              cancel_text="Cancelar"
              loading={deleting}
            >
              <p className="text-base">
                ¿Estás seguro de que deseas eliminar el evento{" "}
                <strong>"{event?.title}"</strong>?
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Esta acción no se puede deshacer.
              </p>
            </Neo_Modal>
          </Neo_Card>
        </div>
      </div>
    </MainLayout>
  );
};
