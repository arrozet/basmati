import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Http_Integration_Repository } from "../../infrastructure/repositories/http_integration_repository";
import { Import_Google_Calendar_Use_Case } from "../../application/integration/import_google_calendar_use_case";
import { Import_Teamup_Calendar_Use_Case } from "../../application/integration/import_teamup_calendar_use_case";
import { use_page_title } from "../hooks/use_page_title";

const repository = new Http_Integration_Repository();
const import_google_use_case = new Import_Google_Calendar_Use_Case(repository);
const import_teamup_use_case = new Import_Teamup_Calendar_Use_Case(repository);

export const Import_Calendar_Page = () => {
  use_page_title("Import calendar");
  const navigate = useNavigate();
  const [active_tab, set_active_tab] = useState<"google" | "teamup">("google");
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);
  const [success, set_success] = useState<string | null>(null);

  // Google Form State
  const [google_token, set_google_token] = useState("");
  const [google_calendar_ids, set_google_calendar_ids] = useState("");

  // Teamup Form State
  const [teamup_key, set_teamup_key] = useState("");
  const [teamup_api_key, set_teamup_api_key] = useState("");

  const handle_google_import = async (e: React.FormEvent) => {
    e.preventDefault();
    set_loading(true);
    set_error(null);
    set_success(null);

    try {
      const calendar_ids = google_calendar_ids
        ? google_calendar_ids.split(",").map((id) => id.trim())
        : undefined;

      await import_google_use_case.execute({
        user_external_id: "user_dev_1", // Hardcoded for now as per AGENTS.md
        google_access_token: google_token,
        calendar_ids: calendar_ids,
      });
      set_success("Calendario de Google importado correctamente");
      setTimeout(() => navigate("/dashboard"), 2000);
    } catch (err: any) {
      set_error(err.response?.data?.detail || "Error al importar desde Google");
    } finally {
      set_loading(false);
    }
  };

  const handle_teamup_import = async (e: React.FormEvent) => {
    e.preventDefault();
    set_loading(true);
    set_error(null);
    set_success(null);

    try {
      if (!teamup_key) {
        set_error("Debes introducir al menos una Key de calendario");
        set_loading(false);
        return;
      }

      await import_teamup_use_case.execute({
        user_external_id: "user_dev_1", // Hardcoded for now
        calendar_keys: [teamup_key],
        teamup_api_key: teamup_api_key || undefined,
      });
      set_success("Calendario de Teamup importado correctamente");
      setTimeout(() => navigate("/dashboard"), 2000);
    } catch (err: any) {
      set_error(err.response?.data?.detail || "Error al importar desde Teamup");
    } finally {
      set_loading(false);
    }
  };

  return (
    <MainLayout>
      <div className="flex justify-center">
        <div className="w-full max-w-2xl">
          <Link to="/dashboard" className="inline-block mb-6">
            <Neo_Button
              variant="secondary"
              className="flex items-center gap-2 text-sm font-bold px-4 py-2"
              aria-label="Volver al dashboard"
            >
              <FontAwesomeIcon icon={faArrowLeft} />
              <span>Volver</span>
            </Neo_Button>
          </Link>
          <h1 className="text-3xl font-black uppercase mb-6">
            Importar Calendario
          </h1>

          <div className="flex gap-4 mb-6">
            <Neo_Button
              variant={active_tab === "google" ? "primary" : "secondary"}
              onClick={() => set_active_tab("google")}
              className="flex-1"
            >
              Google Calendar
            </Neo_Button>
            <Neo_Button
              variant={active_tab === "teamup" ? "primary" : "secondary"}
              onClick={() => set_active_tab("teamup")}
              className="flex-1"
            >
              Teamup
            </Neo_Button>
          </div>

          {error && (
            <div className="bg-basmati-red text-white p-4 border-3 border-basmati-black shadow-hard mb-6 font-bold">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-basmati-green text-white p-4 border-3 border-basmati-black shadow-hard mb-6 font-bold">
              {success}
            </div>
          )}

          {active_tab === "google" && (
            <Neo_Card title="Importar desde Google">
              <form
                onSubmit={handle_google_import}
                className="flex flex-col gap-4"
              >
                <div className="bg-blue-50 p-4 border-l-4 border-blue-500 text-sm mb-2">
                  <p className="font-bold">Nota para desarrolladores:</p>
                  <p>Introduce un Access Token válido de Google OAuth2.</p>
                </div>

                <Neo_Input
                  label="Google Access Token"
                  placeholder="ya29.a0..."
                  value={google_token}
                  onChange={(e) => set_google_token(e.target.value)}
                  required
                />

                <Neo_Input
                  label="Calendar IDs (Opcional)"
                  placeholder="primary, calendar_id_2..."
                  value={google_calendar_ids}
                  onChange={(e) => set_google_calendar_ids(e.target.value)}
                />
                <p className="text-xs text-gray-500 -mt-3">
                  Separados por comas. Dejar en blanco para importar el
                  principal.
                </p>

                <Neo_Button type="submit" disabled={loading} className="mt-4">
                  {loading ? "Importando..." : "Importar Calendario"}
                </Neo_Button>
              </form>
            </Neo_Card>
          )}

          {active_tab === "teamup" && (
            <Neo_Card title="Importar desde Teamup">
              <form
                onSubmit={handle_teamup_import}
                className="flex flex-col gap-4"
              >
                <Neo_Input
                  label="Calendar Key"
                  placeholder="ks..."
                  value={teamup_key}
                  onChange={(e) => set_teamup_key(e.target.value)}
                  required
                />
                <p className="text-xs text-gray-500 -mt-3">
                  La parte de la URL después de teamup.com/ (ej. ks123456)
                </p>

                <Neo_Input
                  label="Teamup API Key (Opcional)"
                  placeholder="Si tienes una propia..."
                  value={teamup_api_key}
                  onChange={(e) => set_teamup_api_key(e.target.value)}
                />
                <p className="text-xs text-gray-500 -mt-3">
                  Si se deja vacío, se usará la API Key del sistema.
                </p>

                <Neo_Button type="submit" disabled={loading} className="mt-4">
                  {loading ? "Importando..." : "Importar Calendario"}
                </Neo_Button>
              </form>
            </Neo_Card>
          )}
        </div>
      </div>
    </MainLayout>
  );
};
