import React, { useState, FormEvent, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Back_Button } from "../components/ui/Back_Button";
import { Avatar } from "../components/ui/Avatar";
import {
  use_user_context,
  Notification_Preferences_V2,
} from "../context/UserContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUser,
  faBell,
  faCheck,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import { Logout_Button } from "../components/ui/Logout_Button";
import { use_page_title } from "../hooks/use_page_title";

type SettingsTab = "profile" | "notifications";
type NotificationFrequency = "instant" | "daily";

/**
 * Página de configuración del usuario con secciones de perfil y notificaciones.
 * Implementa estándares de accesibilidad WCAG 2.1 AA.
 * Usa el contexto de usuario para obtener y actualizar datos reales.
 */
export const Settings_Page: React.FC = () => {
  use_page_title("Ajustes");
  const navigate = useNavigate();
  const {
    user,
    loading,
    error: context_error,
    update_user,
    update_preferences,
  } = use_user_context();

  const [active_tab, set_active_tab] = useState<SettingsTab>("profile");
  const [success_message, set_success_message] = useState<string | null>(null);
  const [form_error, set_form_error] = useState<string | null>(null);
  const [saving, set_saving] = useState(false);

  // Estados del formulario de perfil
  const [display_name, set_display_name] = useState<string>("");
  const [email, set_email] = useState<string>("");

  // Estados del formulario de notificaciones
  const [notification_email_enabled, set_notification_email_enabled] =
    useState<boolean>(true);
  const [notification_in_app_enabled, set_notification_in_app_enabled] =
    useState<boolean>(true);
  const [notification_frequency, set_notification_frequency] =
    useState<NotificationFrequency>("instant");

  // Cargar datos del usuario cuando esté disponible
  useEffect(() => {
    if (user) {
      set_display_name(user.display_name || "");
      set_email(user.email || "");
      set_notification_email_enabled(
        user.notification_preferences?.email ?? true
      );
      set_notification_in_app_enabled(
        user.notification_preferences?.in_app ?? true
      );
      set_notification_frequency(
        user.notification_preferences?.frequency || "instant"
      );
    }
  }, [user]);

  /**
   * Maneja el envío del formulario de perfil.
   */
  const handle_profile_submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    set_form_error(null);
    set_success_message(null);
    set_saving(true);

    try {
      await update_user({
        display_name,
        email,
      });
      set_success_message("✅ Perfil actualizado correctamente");
      setTimeout(() => set_success_message(null), 3000);
    } catch (err) {
      set_form_error(
        err instanceof Error ? err.message : "Error al actualizar el perfil"
      );
    } finally {
      set_saving(false);
    }
  };

  /**
   * Maneja el envío del formulario de notificaciones.
   */
  const handle_notifications_submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    set_form_error(null);
    set_success_message(null);
    set_saving(true);

    try {
      const preferences: Notification_Preferences_V2 = {
        email: notification_email_enabled,
        in_app: notification_in_app_enabled,
        email_address: user?.notification_preferences?.email_address || null,
        frequency: notification_frequency,
      };
      await update_preferences(preferences);
      set_success_message("✅ Preferencias actualizadas correctamente");
      setTimeout(() => set_success_message(null), 3000);
    } catch (err) {
      set_form_error(
        err instanceof Error
          ? err.message
          : "Error al actualizar las preferencias"
      );
    } finally {
      set_saving(false);
    }
  };

  /**
   * Renderiza el contenido de la pestaña activa.
   */
  const render_tab_content = () => {
    if (active_tab === "profile") {
      return (
        <section aria-labelledby="profile-heading">
          <div className="flex justify-between items-center mb-6">
            <h2 id="profile-heading" className="text-2xl font-black">
              Mi perfil
            </h2>
            <Logout_Button
              variant="text"
              title="Cerrar sesión de la cuenta actual"
            />
          </div>

          <form onSubmit={handle_profile_submit} className="space-y-6">
            <div className="flex items-center gap-4 mb-8">
              <Avatar
                src={user?.avatar_url}
                alt={user?.display_name || "Usuario"}
                size="xl"
                className="w-20 h-20 text-3xl shadow-hard"
              />
              <div>
                <p className="font-bold text-lg">{user?.external_id}</p>
                <p className="text-sm text-gray-600">
                  Proveedor: {user?.provider || "N/A"}
                </p>
              </div>
            </div>

            <Neo_Input
              label="Nombre para mostrar"
              type="text"
              id="display-name"
              value={display_name}
              onChange={(e) => set_display_name(e.target.value)}
              placeholder="Ej: Juan Pérez"
              required
              helper_text="Este es el nombre que verán otros usuarios"
            />

            <Neo_Input
              label="ID de usuario"
              type="text"
              id="external-id"
              value={user?.external_id || ""}
              placeholder="external_id"
              helper_text="ID único del usuario (no editable)"
              disabled
            />

            <Neo_Input
              label="Correo electrónico"
              type="email"
              id="email"
              value={email}
              onChange={(e) => set_email(e.target.value)}
              placeholder="ejemplo@correo.com"
              required
              helper_text="Usado para recuperación de cuenta y notificaciones"
            />

            <div className="flex gap-4 pt-4">
              <Neo_Button
                type="submit"
                variant="primary"
                loading={saving}
                disabled={saving}
                className="flex-1"
              >
                Guardar cambios
              </Neo_Button>
              <Neo_Button
                type="button"
                variant="secondary"
                onClick={() => navigate("/dashboard")}
                className="flex-1"
              >
                Cancelar
              </Neo_Button>
            </div>
          </form>
        </section>
      );
    }

    if (active_tab === "notifications") {
      return (
        <section aria-labelledby="notifications-heading">
          <h2 id="notifications-heading" className="text-2xl font-black mb-6">
            Notificaciones
          </h2>

          <form onSubmit={handle_notifications_submit} className="space-y-8">
            <fieldset className="border-3 border-basmati-black p-6 bg-white shadow-hard">
              <legend className="font-black text-lg px-2 bg-basmati-bg">
                Recibir notificaciones por:
              </legend>

              <div className="space-y-4 mt-4">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="notification-email"
                    checked={notification_email_enabled}
                    onChange={(e) =>
                      set_notification_email_enabled(e.target.checked)
                    }
                    className="mt-1 w-5 h-5 border-3 border-basmati-black focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 rounded cursor-pointer accent-basmati-yellow"
                    aria-describedby="notification-email-description"
                  />
                  <div className="flex-1">
                    <label
                      htmlFor="notification-email"
                      className="font-bold cursor-pointer hover:text-basmati-yellow transition-colors"
                    >
                      Correo electrónico habilitado
                    </label>
                    <p
                      id="notification-email-description"
                      className="text-sm text-gray-600 mt-1"
                    >
                      Recibirás notificaciones en {user?.email || "tu correo"}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="notification-in-app"
                    checked={notification_in_app_enabled}
                    onChange={(e) =>
                      set_notification_in_app_enabled(e.target.checked)
                    }
                    className="mt-1 w-5 h-5 border-3 border-basmati-black focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 rounded cursor-pointer accent-basmati-yellow"
                    aria-describedby="notification-in-app-description"
                  />
                  <div className="flex-1">
                    <label
                      htmlFor="notification-in-app"
                      className="font-bold cursor-pointer hover:text-basmati-yellow transition-colors"
                    >
                      Dentro de la app
                    </label>
                    <p
                      id="notification-in-app-description"
                      className="text-sm text-gray-600 mt-1"
                    >
                      Verás notificaciones mientras usas Basmati
                    </p>
                  </div>
                </div>
              </div>
            </fieldset>

            <fieldset className="border-3 border-basmati-black p-6 bg-white shadow-hard">
              <legend className="font-black text-lg px-2 bg-basmati-bg">
                Frecuencia
              </legend>

              <div
                className="space-y-3 mt-4"
                role="radiogroup"
                aria-labelledby="notifications-heading"
              >
                <div className="flex items-start gap-3">
                  <input
                    type="radio"
                    id="frequency-instant"
                    name="notification-frequency"
                    value="instant"
                    checked={notification_frequency === "instant"}
                    onChange={() => set_notification_frequency("instant")}
                    className="mt-1 w-5 h-5 border-3 border-basmati-black focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 cursor-pointer accent-basmati-yellow"
                    aria-describedby="frequency-instant-description"
                  />
                  <div className="flex-1">
                    <label
                      htmlFor="frequency-instant"
                      className="font-bold cursor-pointer hover:text-basmati-yellow transition-colors"
                    >
                      Instantánea
                    </label>
                    <p
                      id="frequency-instant-description"
                      className="text-sm text-gray-600 mt-1"
                    >
                      Te notificaremos inmediatamente cuando ocurra algo
                      importante
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <input
                    type="radio"
                    id="frequency-daily"
                    name="notification-frequency"
                    value="daily"
                    checked={notification_frequency === "daily"}
                    onChange={() => set_notification_frequency("daily")}
                    className="mt-1 w-5 h-5 border-3 border-basmati-black focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 cursor-pointer accent-basmati-yellow"
                    aria-describedby="frequency-daily-description"
                  />
                  <div className="flex-1">
                    <label
                      htmlFor="frequency-daily"
                      className="font-bold cursor-pointer hover:text-basmati-yellow transition-colors"
                    >
                      Diaria - Resumen
                    </label>
                    <p
                      id="frequency-daily-description"
                      className="text-sm text-gray-600 mt-1"
                    >
                      Recibirás un resumen diario con todas las novedades a las
                      00:00
                    </p>
                  </div>
                </div>
              </div>
            </fieldset>

            <div className="flex gap-4 pt-4">
              <Neo_Button
                type="submit"
                variant="primary"
                loading={saving}
                disabled={saving}
                className="flex-1"
              >
                Guardar preferencias
              </Neo_Button>
              <Neo_Button
                type="button"
                variant="secondary"
                onClick={() => navigate("/dashboard")}
                className="flex-1"
              >
                Cancelar
              </Neo_Button>
            </div>
          </form>
        </section>
      );
    }

    return null;
  };

  if (loading) {
    return (
      <MainLayout>
        <div
          className="flex justify-center items-center min-h-[60vh]"
          role="status"
          aria-live="polite"
        >
          <div
            className="animate-spin rounded-full h-12 w-12 border-b-3 border-basmati-black"
            aria-hidden="true"
          ></div>
          <span className="sr-only">Cargando configuración del usuario...</span>
        </div>
      </MainLayout>
    );
  }

  if (context_error && !user) {
    return (
      <MainLayout>
        <div className="max-w-2xl mx-auto py-8 px-4" role="alert">
          <Neo_Card className="bg-basmati-red/10 border-basmati-red">
            <div className="flex items-center gap-3">
              <FontAwesomeIcon
                icon={faExclamationCircle}
                className="text-2xl text-basmati-red"
                aria-hidden="true"
              />
              <div>
                <h2 className="font-black text-lg">
                  Error al cargar configuración
                </h2>
                <p className="text-sm">{context_error}</p>
              </div>
            </div>
          </Neo_Card>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Header */}
        <header className="mb-8">
          <div className="mb-4">
            <Back_Button to="/dashboard" />
          </div>
          <h1 className="text-4xl font-black uppercase">Configuración</h1>
          <p className="text-gray-600 mt-2">
            Conectado como:{" "}
            <span className="font-bold">{user?.display_name}</span> (
            {user?.external_id})
          </p>
        </header>

        {/* Mensajes de éxito/error */}
        {success_message && (
          <div
            role="status"
            aria-live="polite"
            className="mb-6 p-4 bg-basmati-green/20 border-3 border-basmati-green shadow-hard"
          >
            <div className="flex items-center gap-3">
              <FontAwesomeIcon
                icon={faCheck}
                className="text-xl text-basmati-green"
                aria-hidden="true"
              />
              <span className="font-bold">{success_message}</span>
            </div>
          </div>
        )}

        {form_error && (
          <div
            role="alert"
            aria-live="assertive"
            className="mb-6 p-4 bg-basmati-red/20 border-3 border-basmati-red shadow-hard"
          >
            <div className="flex items-center gap-3">
              <FontAwesomeIcon
                icon={faExclamationCircle}
                className="text-xl text-basmati-red"
                aria-hidden="true"
              />
              <span className="font-bold">{form_error}</span>
            </div>
          </div>
        )}

        {/* Tabs Navigation */}
        <nav
          className="mb-8 flex gap-2 border-b-3 border-basmati-black"
          role="tablist"
          aria-label="Secciones de configuración"
        >
          <button
            type="button"
            role="tab"
            aria-selected={active_tab === "profile"}
            aria-controls="profile-panel"
            id="profile-tab"
            onClick={() => set_active_tab("profile")}
            className={`
                            flex items-center gap-2 px-6 py-3 font-bold border-3 border-basmati-black transition-all
                            focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2
                            ${
                              active_tab === "profile"
                                ? "bg-basmati-yellow shadow-hard -mb-[3px]"
                                : "bg-white hover:bg-gray-100 shadow-none"
                            }
                        `}
          >
            <FontAwesomeIcon icon={faUser} aria-hidden="true" />
            <span>Mi perfil</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={active_tab === "notifications"}
            aria-controls="notifications-panel"
            id="notifications-tab"
            onClick={() => set_active_tab("notifications")}
            className={`
                            flex items-center gap-2 px-6 py-3 font-bold border-3 border-basmati-black transition-all
                            focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2
                            ${
                              active_tab === "notifications"
                                ? "bg-basmati-yellow shadow-hard -mb-[3px]"
                                : "bg-white hover:bg-gray-100 shadow-none"
                            }
                        `}
          >
            <FontAwesomeIcon icon={faBell} aria-hidden="true" />
            <span>Notificaciones</span>
          </button>
        </nav>

        {/* Tab Content */}
        <Neo_Card
          role="tabpanel"
          id={`${active_tab}-panel`}
          aria-labelledby={`${active_tab}-tab`}
          className="bg-white"
        >
          {render_tab_content()}
        </Neo_Card>
      </div>
    </MainLayout>
  );
};
