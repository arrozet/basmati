import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Input } from "../components/ui/Neo_Input";
import { use_page_title } from "../hooks/use_page_title";
import { use_user_context } from "../context/UserContext";
import { DEV_USER_1, DEV_USER_2 } from "../../infrastructure/config/dev_users";
import { get_google_login_url } from "../../infrastructure/services/auth_service";

/**
 * Página de inicio de sesión con Google OAuth.
 * Mantiene compatibilidad con usuarios de desarrollo para pruebas.
 */
export const Login_Page = () => {
  use_page_title("Iniciar sesión");
  const navigate = useNavigate();
  const { switch_user } = use_user_context();
  const [username, set_username] = useState("");
  const [loading, set_loading] = useState(false);
  const [google_loading, set_google_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);
  const [show_dev_login, set_show_dev_login] = useState(false);

  /**
   * Inicia el flujo de login con Google OAuth.
   */
  const handle_google_login = async () => {
    set_google_loading(true);
    set_error(null);

    try {
      const auth_url = await get_google_login_url("/dashboard");
      // Redirigir a la página de autorización de Google
      window.location.href = auth_url;
    } catch (err: any) {
      console.error("Error al iniciar login con Google:", err);
      set_error("Error al conectar con Google. Inténtalo de nuevo.");
      set_google_loading(false);
    }
  };

  /**
   * Login de desarrollo (para usuarios de prueba sin OAuth).
   */
  const handle_dev_login = async (e: React.FormEvent) => {
    e.preventDefault();
    set_error(null);
    set_loading(true);

    try {
      await switch_user(username.trim());
      navigate("/dashboard");
    } catch (err: any) {
      console.error("Error al iniciar sesión:", err);
      if (err.response?.status === 404) {
        set_error(
          "Usuario no encontrado. Por favor, usa uno de los usuarios registrados."
        );
      } else {
        set_error("Error al verificar el usuario. Inténtalo de nuevo.");
      }
    } finally {
      set_loading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-basmati-bg p-4">
      <Neo_Card className="w-full max-w-md flex flex-col gap-6 bg-white">
        <header className="text-center">
          <h1 className="text-4xl font-black uppercase mb-2">Basmati</h1>
          <p className="text-gray-600">Organiza tu caos.</p>
        </header>

        {/* Botón de Google OAuth */}
        <div className="flex flex-col gap-4">
          <Neo_Button
            onClick={handle_google_login}
            loading={google_loading}
            disabled={google_loading}
            className="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-300 hover:border-basmati-yellow text-gray-700"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            {google_loading ? "Conectando..." : "Continuar con Google"}
          </Neo_Button>

          {error && (
            <div
              className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-2 rounded"
              role="alert"
            >
              {error}
            </div>
          )}
        </div>

        {/* Separador */}
        <div className="relative my-2">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t-2 border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">o</span>
          </div>
        </div>

        {/* Toggle para mostrar login de desarrollo */}
        <button
          type="button"
          onClick={() => set_show_dev_login(!show_dev_login)}
          className="text-sm text-gray-500 hover:text-basmati-yellow transition-colors"
        >
          {show_dev_login
            ? "▲ Ocultar login de desarrollo"
            : "▼ Login de desarrollo (para pruebas)"}
        </button>

        {/* Login de desarrollo (colapsable) */}
        {show_dev_login && (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 space-y-4">
            <p className="text-sm text-gray-500 text-center">
              Solo para pruebas locales sin OAuth
            </p>

            <form onSubmit={handle_dev_login} className="flex flex-col gap-4">
              <Neo_Input
                label="Usuario de desarrollo"
                placeholder="Ej: user_dev_1, user_dev_2"
                value={username}
                onChange={(e) => set_username(e.target.value)}
                autoComplete="username"
                id="login-username"
                helper_text="Introduce el external_id de un usuario existente"
              />

              <Neo_Button
                type="submit"
                className="w-full"
                loading={loading}
                disabled={loading || !username.trim()}
              >
                {loading ? "Verificando..." : "Entrar como usuario dev"}
              </Neo_Button>
            </form>

            <div className="grid grid-cols-1 gap-2 mt-4">
              <button
                type="button"
                onClick={() => set_username(DEV_USER_1.id)}
                className="text-left p-2 border border-gray-200 rounded text-sm hover:border-basmati-yellow hover:bg-basmati-yellow/10 transition-all"
              >
                <span className="font-bold">{DEV_USER_1.id}</span>
                <span className="text-gray-400 text-xs ml-2">
                  {DEV_USER_1.email}
                </span>
              </button>
              <button
                type="button"
                onClick={() => set_username(DEV_USER_2.id)}
                className="text-left p-2 border border-gray-200 rounded text-sm hover:border-basmati-blue hover:bg-basmati-blue/10 transition-all"
              >
                <span className="font-bold">{DEV_USER_2.id}</span>
                <span className="text-gray-400 text-xs ml-2">
                  {DEV_USER_2.email}
                </span>
              </button>
            </div>
          </div>
        )}
      </Neo_Card>
    </div>
  );
};
