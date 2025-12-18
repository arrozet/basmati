import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Button } from "../components/ui/Neo_Button";
import { use_calendars } from "../hooks/use_calendars";
import { use_page_title } from "../hooks/use_page_title";
import { use_user_context } from "../context/UserContext";

/**
 * Página para crear un nuevo calendario.
 * Formulario accesible basado en los bocetos con HTML semántico.
 */
export const Create_Calendar_Page = () => {
  use_page_title("Create calendar");
  const navigate = useNavigate();

  // Obtener el usuario actual del contexto en lugar de hardcodear user_dev_1
  const { user, loading: user_loading } = use_user_context();
  const current_user_id = user?.external_id || "user_dev_1";
  const current_user_name = user?.display_name || "Usuario";

  const { create_calendar, calendars } = use_calendars(current_user_id);
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);

  const [form_data, set_form_data] = useState({
    title: "",
    color: "#EBBE4D", // Color por defecto basmati-yellow
    owner_id: current_user_id,
    icon: "",
    is_public: false,
    parent_id: "",
  });

  // Actualizar owner_id cuando el usuario cambie
  React.useEffect(() => {
    if (user?.external_id) {
      set_form_data((prev) => ({ ...prev, owner_id: user.external_id }));
    }
  }, [user?.external_id]);

  const handle_change = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    set_form_data({
      ...form_data,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handle_submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    set_loading(true);
    set_error(null);

    if (!form_data.title.trim()) {
      set_error("El título es obligatorio");
      set_loading(false);
      return;
    }

    try {
      await create_calendar({
        title: form_data.title,
        color: form_data.color,
        // Usar el ID del usuario actual de la sesión
        owner_id: current_user_id,
        icon: form_data.icon,
        is_public: form_data.is_public,
        parent_id: form_data.parent_id || undefined,
      });
      navigate("/dashboard");
    } catch (err: any) {
      console.error(err);
      set_error(err.message || "Error al crear el calendario");
    } finally {
      set_loading(false);
    }
  };

  const predefined_colors = [
    { hex: "#EBBE4D", name: "Amarillo Basmati" },
    { hex: "#5496FF", name: "Azul" },
    { hex: "#FF6B6B", name: "Rojo" },
    { hex: "#4ECDC4", name: "Verde agua" },
    { hex: "#F59E0B", name: "Naranja" },
    { hex: "#8B5CF6", name: "Morado" },
    { hex: "#EC4899", name: "Rosa" },
    { hex: "#10B981", name: "Verde" },
  ];

  // Mostrar carga mientras se obtiene el usuario
  if (user_loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-3 border-basmati-black"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="flex justify-center">
        <div className="w-full max-w-4xl">
          <Link to="/dashboard" className="inline-block mb-4">
            <Neo_Button
              variant="secondary"
              className="flex items-center gap-2 text-sm font-bold px-4 py-2"
              aria-label="Volver al dashboard"
            >
              <FontAwesomeIcon icon={faArrowLeft} />
              <span>Volver</span>
            </Neo_Button>
          </Link>
          <Neo_Card className="w-full" title="Crear calendario">
            <form
              onSubmit={handle_submit}
              className="flex flex-col gap-4"
              aria-label="Formulario de creación de calendario"
            >
              <Neo_Input
                label="Título"
                placeholder="Ej: Quedadas de coches"
                name="title"
                value={form_data.title}
                onChange={handle_change}
                required
                id="calendar-title"
                autoComplete="off"
              />

              <fieldset className="border-0 p-0 m-0">
                <legend className="font-bold text-sm mb-2 text-basmati-black">
                  Color del calendario
                </legend>
                <div
                  className="grid grid-cols-4 md:grid-cols-8 gap-3"
                  role="radiogroup"
                  aria-label="Selector de color del calendario"
                >
                  {predefined_colors.map(({ hex, name }) => (
                    <button
                      key={hex}
                      type="button"
                      className={`w-full aspect-square rounded-md border-3 transition-all focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 hover:scale-110 ${
                        form_data.color === hex
                          ? "border-basmati-black shadow-hard scale-110"
                          : "border-gray-300"
                      }`}
                      style={{ backgroundColor: hex }}
                      onClick={() =>
                        set_form_data({ ...form_data, color: hex })
                      }
                      aria-label={`Seleccionar color ${name}`}
                      aria-pressed={form_data.color === hex}
                      role="radio"
                      aria-checked={form_data.color === hex}
                      title={name}
                    >
                      <span className="sr-only">{name}</span>
                    </button>
                  ))}
                </div>
                <div className="mt-3 flex gap-2 items-center">
                  <label
                    htmlFor="custom-color"
                    className="text-sm font-medium text-basmati-black"
                  >
                    Color personalizado:
                  </label>
                  <input
                    type="color"
                    id="custom-color"
                    name="color"
                    value={form_data.color}
                    onChange={handle_change}
                    className="w-12 h-12 border-3 border-basmati-black cursor-pointer focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2"
                    aria-label="Selector de color personalizado"
                  />
                </div>
              </fieldset>

              <div className="flex flex-col gap-1">
                <label
                  htmlFor="parent-calendar"
                  className="font-bold text-sm text-basmati-black"
                >
                  Subcalendario de (Opcional)
                </label>
                <select
                  id="parent-calendar"
                  name="parent_id"
                  value={form_data.parent_id}
                  onChange={handle_change}
                  className="border-3 border-basmati-black px-3 py-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 transition-all bg-white"
                >
                  <option value="">Ninguno (Calendario principal)</option>
                  {calendars
                    .filter((c) => c.owner_id === current_user_id)
                    .map((cal) => (
                      <option key={cal.id} value={cal.id}>
                        {cal.title}
                      </option>
                    ))}
                </select>
                <p className="text-xs text-gray-600">
                  Si seleccionas un calendario padre, este calendario heredará
                  sus permisos.
                </p>
              </div>

              {/* Campo de organizador ahora muestra el nombre del usuario actual */}
              <div className="flex flex-col gap-1">
                <label className="font-bold text-sm text-basmati-black">
                  Organizador
                </label>
                <div className="border-3 border-basmati-black px-3 py-2 bg-gray-100 text-gray-700">
                  {current_user_name}
                </div>
                <p className="text-xs text-gray-600">
                  El organizador es el usuario actual de la sesión.
                </p>
              </div>

              <div className="flex flex-col gap-1">
                <label
                  htmlFor="calendar-icon"
                  className="font-bold text-sm text-basmati-black"
                >
                  Icono
                </label>
                <input
                  type="file"
                  id="calendar-icon"
                  name="icon"
                  accept="image/png,image/jpeg,image/jpg"
                  className="border-3 border-basmati-black px-3 py-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 transition-all bg-white file:mr-4 file:py-2 file:px-4 file:border-0 file:font-semibold file:bg-basmati-yellow file:text-basmati-black hover:file:bg-basmati-yellow/80"
                  aria-describedby="icon-hint"
                />
                <span id="icon-hint" className="text-xs text-gray-600">
                  Carga una imagen 256x256 píxeles. Formatos: PNG, JPG.
                </span>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="calendar-public"
                  name="is_public"
                  checked={form_data.is_public}
                  onChange={handle_change}
                  className="w-5 h-5 border-3 border-basmati-black focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 accent-basmati-yellow"
                />
                <label
                  htmlFor="calendar-public"
                  className="font-medium text-basmati-black cursor-pointer"
                >
                  Hacer público este calendario
                </label>
              </div>

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
                >
                  {loading ? "Creando..." : "Crear"}
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
