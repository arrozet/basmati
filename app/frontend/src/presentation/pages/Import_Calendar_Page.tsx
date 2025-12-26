import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Back_Button } from "../components/ui/Back_Button";
import { Http_Integration_Repository } from "../../infrastructure/repositories/http_integration_repository";
import { Import_Google_Calendar_Use_Case_V3 } from "../../application/integration/import_google_calendar_use_case_v3";
import { Import_Teamup_Calendar_Use_Case_V3 } from "../../application/integration/import_teamup_calendar_use_case_v3";
import { Get_Providers_Use_Case } from "../../application/integration/get_providers_use_case";
import { 
  Import_Response_V3, 
  Imported_Calendar_V3, 
  Provider_Capabilities,
  Provider_Type 
} from "../../domain/models/integration_models";
import { use_page_title } from "../hooks/use_page_title";
import { get_google_token } from "../../infrastructure/services/auth_service";
import { use_user_context } from "../context/UserContext";

const repository = new Http_Integration_Repository();
const import_google_use_case = new Import_Google_Calendar_Use_Case_V3(repository);
const import_teamup_use_case = new Import_Teamup_Calendar_Use_Case_V3(repository);
const get_providers_use_case = new Get_Providers_Use_Case(repository);

// Componente para mostrar resultado de importación
const Import_Result_Card: React.FC<{ result: Import_Response_V3; on_close: () => void }> = ({ 
  result, 
  on_close 
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white border-3 border-basmati-black shadow-hard max-w-lg w-full max-h-[80vh] overflow-y-auto">
        <div className={`p-4 ${result.success ? 'bg-basmati-green' : 'bg-basmati-red'} text-white`}>
          <h2 className="text-xl font-black uppercase">
            {result.success ? '✓ Importación Completada' : '✗ Error en Importación'}
          </h2>
        </div>
        
        <div className="p-6">
          <p className="font-medium mb-4">{result.message}</p>
          
          {result.imported_calendars.length > 0 && (
            <div className="mb-4">
              <h3 className="font-bold text-sm uppercase mb-2 text-gray-600">
                Calendarios Importados
              </h3>
              <div className="space-y-2">
                {result.imported_calendars.map((cal: Imported_Calendar_V3, idx: number) => (
                  <div 
                    key={idx} 
                    className="bg-gray-50 border-2 border-gray-200 p-3"
                  >
                    <p className="font-mono text-sm text-gray-600 truncate">
                      ID: {cal.external_id}
                    </p>
                    <div className="flex gap-4 mt-1 text-sm">
                      <span className="text-basmati-green font-bold">
                        ✓ {cal.events_imported} eventos
                      </span>
                      {cal.events_failed > 0 && (
                        <span className="text-basmati-red font-bold">
                          ✗ {cal.events_failed} fallidos
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Resumen total */}
          <div className="bg-gray-100 border-2 border-gray-300 p-3 mb-4">
            <div className="flex justify-between text-sm">
              <span>Total eventos importados:</span>
              <span className="font-bold text-basmati-green">{result.total_events_imported}</span>
            </div>
            {result.total_events_failed > 0 && (
              <div className="flex justify-between text-sm mt-1">
                <span>Eventos fallidos:</span>
                <span className="font-bold text-basmati-red">{result.total_events_failed}</span>
              </div>
            )}
          </div>
          
          {result.errors.length > 0 && (
            <div className="mb-4">
              <h3 className="font-bold text-sm uppercase mb-2 text-basmati-red">
                Errores
              </h3>
              <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                {result.errors.map((error: string, idx: number) => (
                  <li key={idx}>{error}</li>
                ))}
              </ul>
            </div>
          )}
          
          <Neo_Button onClick={on_close} className="w-full">
            {result.success ? 'Ir al Dashboard' : 'Cerrar'}
          </Neo_Button>
        </div>
      </div>
    </div>
  );
};

// Componente para mostrar información del proveedor
const Provider_Info_Badge: React.FC<{ provider: Provider_Capabilities }> = ({ provider }) => {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      {provider.supports_oauth && (
        <span className="bg-blue-100 text-blue-800 px-2 py-1 border border-blue-300">
          OAuth
        </span>
      )}
      {provider.supports_api_key && (
        <span className="bg-purple-100 text-purple-800 px-2 py-1 border border-purple-300">
          API Key
        </span>
      )}
    </div>
  );
};

export const Import_Calendar_Page = () => {
  use_page_title("Import calendar");
  const navigate = useNavigate();
  const { user } = use_user_context();
  
  // ID del usuario actual (logeado o fallback a dev)
  const current_user_id = user?.external_id || "user_dev_1";
  
  // Estado general
  const [active_tab, set_active_tab] = useState<Provider_Type>("google");
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);
  const [import_result, set_import_result] = useState<Import_Response_V3 | null>(null);
  const [providers, set_providers] = useState<Provider_Capabilities[]>([]);
  const [loading_providers, set_loading_providers] = useState(true);

  // Google Form State - inicializado con token almacenado
  const stored_google_token = get_google_token();
  const [google_token, set_google_token] = useState(stored_google_token || "");
  const [google_calendar_ids, set_google_calendar_ids] = useState("");
  const [google_calendar_name, set_google_calendar_name] = useState("");
  const has_stored_token = Boolean(stored_google_token);

  // Teamup Form State
  const [teamup_key, set_teamup_key] = useState("");
  const [teamup_api_key, set_teamup_api_key] = useState("");
  const [teamup_calendar_name, set_teamup_calendar_name] = useState("");

  // Cargar proveedores al montar
  useEffect(() => {
    const load_providers = async () => {
      try {
        const result = await get_providers_use_case.execute();
        set_providers(result);
      } catch (err) {
        console.error("Error loading providers:", err);
        // Usar valores por defecto si falla
        set_providers([
          { provider: 'google', name: 'Google Calendar', supports_oauth: true, supports_api_key: false, supports_sync: false, requires_calendar_selection: true },
          { provider: 'teamup', name: 'Teamup', supports_oauth: false, supports_api_key: true, supports_sync: false, requires_calendar_selection: true }
        ]);
      } finally {
        set_loading_providers(false);
      }
    };
    load_providers();
  }, []);

  const handle_google_import = async (e: React.FormEvent) => {
    e.preventDefault();
    set_loading(true);
    set_error(null);

    try {
      const calendar_ids = google_calendar_ids
        ? google_calendar_ids.split(",").map((id) => id.trim()).filter(Boolean)
        : ["primary"];

      // Usar token manual si se proporciona, sino el almacenado
      const token_to_use = google_token || stored_google_token;
      
      if (!token_to_use) {
        set_error("Se requiere un token de Google. Introduce uno manualmente o inicia sesión con Google.");
        set_loading(false);
        return;
      }

      const result = await import_google_use_case.execute({
        user_external_id: current_user_id,
        access_token: token_to_use,
        calendar_ids: calendar_ids,
        calendar_name: google_calendar_name || undefined,
      });
      
      // Si hay errores en el resultado, mostrarlos
      if (!result.success && result.errors && result.errors.length > 0) {
        set_error(result.errors.join(". "));
      }
      
      set_import_result(result);
    } catch (err: any) {
      set_error(err.response?.data?.detail || "Error al importar desde Google Calendar");
    } finally {
      set_loading(false);
    }
  };

  const handle_teamup_import = async (e: React.FormEvent) => {
    e.preventDefault();
    set_loading(true);
    set_error(null);

    try {
      if (!teamup_key) {
        set_error("Debes introducir al menos una Key de calendario");
        set_loading(false);
        return;
      }

      const result = await import_teamup_use_case.execute({
        user_external_id: current_user_id,
        calendar_ids: [teamup_key],
        api_key: teamup_api_key || undefined,
        calendar_name: teamup_calendar_name || undefined,
      });
      
      set_import_result(result);
    } catch (err: any) {
      set_error(err.response?.data?.detail || "Error al importar desde Teamup");
    } finally {
      set_loading(false);
    }
  };

  const handle_result_close = () => {
    if (import_result?.success) {
      navigate("/dashboard");
    } else {
      set_import_result(null);
    }
  };

  const get_provider_info = (type: Provider_Type): Provider_Capabilities | undefined => {
    return providers.find(p => p.provider === type);
  };

  return (
    <MainLayout>
      <div className="flex justify-center">
        <div className="w-full max-w-2xl">
          <div className="mb-6">
            <Back_Button to="/dashboard" />
          </div>
          
          <div className="flex items-center gap-3 mb-6">
            <h1 className="text-3xl font-black uppercase">
              Importar Calendario
            </h1>
            <span className="bg-basmati-yellow text-basmati-black px-2 py-1 text-xs font-bold border-2 border-basmati-black">
              V3
            </span>
          </div>

          {/* Selector de proveedor */}
          <div className="flex gap-4 mb-6">
            <Neo_Button
              variant={active_tab === "google" ? "primary" : "secondary"}
              onClick={() => set_active_tab("google")}
              className="flex-1"
              disabled={loading_providers}
            >
              <div className="flex flex-col items-center gap-1">
                <span>Google Calendar</span>
                {get_provider_info('google') && (
                  <Provider_Info_Badge provider={get_provider_info('google')!} />
                )}
              </div>
            </Neo_Button>
            <Neo_Button
              variant={active_tab === "teamup" ? "primary" : "secondary"}
              onClick={() => set_active_tab("teamup")}
              className="flex-1"
              disabled={loading_providers}
            >
              <div className="flex flex-col items-center gap-1">
                <span>Teamup</span>
                {get_provider_info('teamup') && (
                  <Provider_Info_Badge provider={get_provider_info('teamup')!} />
                )}
              </div>
            </Neo_Button>
          </div>

          {/* Mensaje de error */}
          {error && (
            <div className="bg-basmati-red text-white p-4 border-3 border-basmati-black shadow-hard mb-6 font-bold">
              {error}
            </div>
          )}

          {/* Formulario Google */}
          {active_tab === "google" && (
            <Neo_Card title="Importar desde Google Calendar">
              <form onSubmit={handle_google_import} className="flex flex-col gap-4">
                {has_stored_token ? (
                  <div className="bg-yellow-50 p-4 border-l-4 border-yellow-500 text-sm mb-2">
                    <p className="font-bold mb-1">⚠️ Limitación de Scopes de Google</p>
                    <p className="text-gray-600 mb-2">
                      El token de tu sesión puede no tener permisos para leer calendarios. 
                      Si la importación falla, necesitarás obtener un token con el scope 
                      <code className="bg-gray-200 px-1 mx-1 rounded">calendar.readonly</code> 
                      desde el <a href="https://developers.google.com/oauthplayground/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">OAuth Playground de Google</a>.
                    </p>
                    <p className="text-gray-600">
                      Puedes probar con el token automático primero, o introducir uno manualmente.
                    </p>
                  </div>
                ) : (
                  <div className="bg-yellow-50 p-4 border-l-4 border-yellow-500 text-sm mb-2">
                    <p className="font-bold mb-1">⚠️ Token Manual Requerido</p>
                    <p className="text-gray-600">
                      Para usar la importación automática, cierra sesión y vuelve a iniciar con Google.
                      Alternativamente, puedes introducir un Access Token manualmente.
                    </p>
                  </div>
                )}

                <Neo_Input
                  label={has_stored_token ? "Google Access Token (Opcional - usa el de tu sesión si está vacío)" : "Google Access Token"}
                  placeholder="ya29.a0..."
                  value={google_token}
                  onChange={(e) => set_google_token(e.target.value)}
                  required={!has_stored_token}
                />

                <Neo_Input
                  label="Calendar IDs (Opcional)"
                  placeholder="primary, calendar_id_2..."
                  value={google_calendar_ids}
                  onChange={(e) => set_google_calendar_ids(e.target.value)}
                />
                <p className="text-xs text-gray-500 -mt-3">
                  Separados por comas. Dejar en blanco para importar el calendario principal.
                </p>

                <Neo_Input
                  label="Nombre del Calendario (Opcional)"
                  placeholder="Mi calendario personalizado"
                  value={google_calendar_name}
                  onChange={(e) => set_google_calendar_name(e.target.value)}
                />
                <p className="text-xs text-gray-500 -mt-3">
                  Nombre personalizado para el calendario importado. Dejar en blanco para usar el nombre original.
                </p>

                <Neo_Button 
                  type="submit" 
                  disabled={loading || (!google_token && !stored_google_token)} 
                  className="mt-4"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span>
                      Importando...
                    </span>
                  ) : (
                    "Importar desde Google"
                  )}
                </Neo_Button>
              </form>
            </Neo_Card>
          )}

          {/* Formulario Teamup */}
          {active_tab === "teamup" && (
            <Neo_Card title="Importar desde Teamup">
              <form onSubmit={handle_teamup_import} className="flex flex-col gap-4">
                <div className="bg-purple-50 p-4 border-l-4 border-purple-500 text-sm mb-2">
                  <p className="font-bold mb-1">🔑 Autenticación API Key</p>
                  <p className="text-gray-600">
                    La API Key es opcional. Si no la proporcionas, se usará la 
                    configurada en el servidor.
                  </p>
                </div>

                <Neo_Input
                  label="Calendar Key"
                  placeholder="ks..."
                  value={teamup_key}
                  onChange={(e) => set_teamup_key(e.target.value)}
                  required
                />
                <p className="text-xs text-gray-500 -mt-3">
                  La parte de la URL después de teamup.com/ (ej: ks123456abc)
                </p>

                <Neo_Input
                  label="Teamup API Key (Opcional)"
                  placeholder="Si tienes una API Key propia..."
                  value={teamup_api_key}
                  onChange={(e) => set_teamup_api_key(e.target.value)}
                />
                <p className="text-xs text-gray-500 -mt-3">
                  Si se deja vacío, se usará la API Key del servidor.
                </p>

                <Neo_Input
                  label="Nombre del Calendario (Opcional)"
                  placeholder="Mi calendario personalizado"
                  value={teamup_calendar_name}
                  onChange={(e) => set_teamup_calendar_name(e.target.value)}
                />
                <p className="text-xs text-gray-500 -mt-3">
                  Nombre personalizado para el calendario importado. Dejar en blanco para usar el nombre original.
                </p>

                <Neo_Button 
                  type="submit" 
                  disabled={loading || !teamup_key} 
                  className="mt-4"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span>
                      Importando...
                    </span>
                  ) : (
                    "Importar desde Teamup"
                  )}
                </Neo_Button>
              </form>
            </Neo_Card>
          )}

          {/* Información adicional */}
          <div className="mt-6 p-4 bg-gray-50 border-2 border-gray-200 text-sm text-gray-600">
            <p className="font-bold mb-2">ℹ️ Sobre la importación V3</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Los calendarios se crean automáticamente en Basmati</li>
              <li>Los eventos de los próximos 90 días serán importados</li>
              <li>La importación soporta paginación automática</li>
              <li>Los eventos recurrentes se expanden individualmente</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Modal de resultado */}
      {import_result && (
        <Import_Result_Card 
          result={import_result} 
          on_close={handle_result_close} 
        />
      )}
    </MainLayout>
  );
};
