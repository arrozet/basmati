import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Back_Button } from "../components/ui/Back_Button";
import { Location_Picker } from "../components/ui/Location_Picker";
import { Image_Uploader } from "../components/ui/Image_Uploader";
import { Create_Event_Use_Case } from "../../application/event/create_event_use_case";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { use_calendars } from "../hooks/use_calendars";
import { use_page_title } from "../hooks/use_page_title";
import { use_user_context } from "../context/UserContext";
import { Event_Location } from "../../domain/models/integration_models";
import { Event_Attachment } from "../../domain/models/event_model";

const event_repository = new Http_Event_Repository();
const calendar_repository = new Http_Calendar_Repository();
const create_event_use_case = new Create_Event_Use_Case(
  event_repository,
  calendar_repository
);

/**
 * Página de creación de evento accesible.
 * Usa formulario semántico con labels asociados, aria-live para mensajes de error.
 */
export const Create_Event_Page = () => {
  use_page_title("Create event");
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = use_user_context();
  const current_user_id = user?.external_id || "user_dev_1";
  const { calendars, loading: loading_calendars } =
    use_calendars(current_user_id);
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);

  const [form_data, set_form_data] = useState({
    title: "",
    start_time: "",
    end_time: "",
    description: "",
    calendar_id: "",
  });

  const [location, set_location] = useState<Event_Location | null>(null);
  const [attachments, set_attachments] = useState<Event_Attachment[]>([]);

  useEffect(() => {
    const dateParam = searchParams.get("date");
    const calendarIdParam = searchParams.get("calendar_id");

    if (dateParam) {
      set_form_data((prev) => ({
        ...prev,
        start_time: `${dateParam}T00:00`,
        end_time: `${dateParam}T23:59`,
      }));
    }

    // Set default calendar
    if (calendarIdParam) {
      set_form_data((prev) => ({
        ...prev,
        calendar_id: calendarIdParam,
      }));
    } else if (calendars.length > 0 && !form_data.calendar_id) {
      set_form_data((prev) => ({
        ...prev,
        calendar_id: calendars[0].id,
      }));
    }
  }, [searchParams, calendars]);

  const handle_change = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    set_form_data({
      ...form_data,
      [e.target.name]: e.target.value,
    });
  };

  const handle_submit = async (e: React.FormEvent) => {
    e.preventDefault();
    set_loading(true);
    set_error(null);

    if (!form_data.title || !form_data.start_time || !form_data.end_time) {
      set_error("Por favor completa el título y las fechas.");
      set_loading(false);
      return;
    }

    try {
      await create_event_use_case.execute(
        {
          title: form_data.title,
          start_time: new Date(form_data.start_time),
          end_time: new Date(form_data.end_time),
          description: form_data.description,
          calendar_id: form_data.calendar_id,
          location: location || undefined,
          attachments: attachments,
        },
        current_user_id
      );
      navigate("/dashboard");
    } catch (err: any) {
      console.error("Error completo:", err);
      if (err.response && err.response.data) {
        console.error("Detalles del error del servidor:", err.response.data);
        set_error(
          `Error del servidor: ${JSON.stringify(
            err.response.data.detail || err.response.data
          )}`
        );
      } else {
        set_error(err.message || "Error al crear el evento");
      }
    } finally {
      set_loading(false);
    }
  };

  return (
    <MainLayout>
      <div className="flex justify-center">
        <div className="w-full max-w-4xl">
          <div className="mb-4">
            <Back_Button to="/dashboard" />
          </div>
          <Neo_Card className="w-full" title="Crear evento">
            <form
              onSubmit={handle_submit}
              className="flex flex-col gap-4"
              aria-label="Formulario de creación de evento"
            >
              <Neo_Input
                label="Título"
                placeholder="Ej: Cena con amigos"
                name="title"
                value={form_data.title}
                onChange={handle_change}
                required
                id="event-title"
                autoComplete="off"
              />

              <fieldset className="border-0 p-0 m-0">
                <legend className="font-bold text-sm mb-2 text-basmati-black">
                  Fechas del evento
                </legend>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Neo_Input
                    label="Fecha inicio"
                    type="datetime-local"
                    name="start_time"
                    value={form_data.start_time}
                    onChange={handle_change}
                    required
                    id="event-start"
                  />
                  <Neo_Input
                    label="Fecha fin"
                    type="datetime-local"
                    name="end_time"
                    value={form_data.end_time}
                    onChange={handle_change}
                    required
                    id="event-end"
                  />
                </div>
              </fieldset>

              <div className="flex flex-col gap-1">
                <label
                  htmlFor="event-description"
                  className="font-bold text-sm text-basmati-black"
                >
                  Descripción
                </label>
                <textarea
                  id="event-description"
                  className="border-3 border-basmati-black px-3 py-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 transition-all bg-white h-32 resize-none"
                  placeholder="Detalles del evento..."
                  name="description"
                  value={form_data.description}
                  onChange={handle_change}
                  aria-label="Descripción del evento"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label
                  htmlFor="event-calendar"
                  className="font-bold text-sm text-basmati-black"
                >
                  Calendario{" "}
                  <span className="text-basmati-red" aria-label="requerido">
                    *
                  </span>
                </label>
                {loading_calendars ? (
                  <div className="border-3 border-basmati-black px-3 py-2 bg-gray-100 text-gray-500">
                    Cargando calendarios...
                  </div>
                ) : calendars.length === 0 ? (
                  <div className="border-3 border-basmati-black px-3 py-2 bg-gray-100 text-gray-500">
                    No tienes calendarios.{" "}
                    <button
                      type="button"
                      onClick={() => navigate("/calendars/new")}
                      className="underline text-basmati-blue hover:text-basmati-blue/80"
                    >
                      Crear uno
                    </button>
                  </div>
                ) : (
                  <select
                    id="event-calendar"
                    className="border-3 border-basmati-black px-3 py-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 transition-all bg-white"
                    name="calendar_id"
                    value={form_data.calendar_id}
                    onChange={handle_change}
                    required
                    aria-label="Seleccionar calendario para el evento"
                  >
                    {calendars.map((cal) => (
                      <option key={cal.id} value={cal.id}>
                        {cal.title}
                      </option>
                    ))}
                  </select>
                )}
                {form_data.calendar_id && calendars.length > 0 && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      Color del calendario:
                    </span>
                    <div
                      className="w-8 h-8 rounded border-3 border-basmati-black"
                      style={{
                        backgroundColor:
                          calendars.find((c) => c.id === form_data.calendar_id)
                            ?.color || "#EBBE4D",
                      }}
                      aria-label="Vista previa del color del calendario"
                    ></div>
                  </div>
                )}
              </div>

              {/* Selector de ubicación con mapa OpenStreetMap */}
              <Location_Picker
                value={location}
                on_change={set_location}
                id="event-location"
                disabled={loading}
              />

              {/* Cargador de Imágenes */}
              <Image_Uploader
                attachments={attachments}
                onChange={set_attachments}
                disabled={loading}
              />

              {error && (
                <div
                  className="bg-basmati-red text-white p-3 font-bold border-3 border-basmati-black"
                  role="alert"
                  aria-live="assertive"
                >
                  {error}
                </div>
              )}

              <div className="flex flex-col md:flex-row gap-4 mt-4">
                <Neo_Button
                  type="submit"
                  variant="success"
                  className="flex-1"
                  disabled={loading}
                  loading={loading}
                >
                  {loading ? "Guardando..." : "Guardar evento"}
                </Neo_Button>
                <Neo_Button
                  type="button"
                  onClick={() => navigate("/dashboard")}
                  variant="danger"
                  className="flex-1"
                  disabled={loading}
                >
                  Cancelar
                </Neo_Button>
              </div>
            </form>
          </Neo_Card>
        </div>
      </div>
    </MainLayout>
  );
};
