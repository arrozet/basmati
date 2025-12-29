import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Neo_Input } from "../components/ui/Neo_Input";
import { Back_Button } from "../components/ui/Back_Button";
import { Http_Integration_Repository } from "../../infrastructure/repositories/http_integration_repository";
import { Import_Google_Calendar_Use_Case_V3 } from "../../application/integration/import_google_calendar_use_case_v3";
import { Import_Teamup_Calendar_Use_Case_V3 } from "../../application/integration/import_teamup_calendar_use_case_v3";
import { 
  Import_Response_V3, 
  Imported_Calendar_V3, 
  Provider_Type 
} from "../../domain/models/integration_models";
import { use_page_title } from "../hooks/use_page_title";
import { get_google_token } from "../../infrastructure/services/auth_service";
import { use_user_context } from "../context/UserContext";

// Iconos SVG para los proveedores
const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);

const TeamupIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zM9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
  </svg>
);

const CheckCircleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const ExclamationCircleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CalendarPlusIcon = () => (
  <svg viewBox="0 0 24 24" className="w-8 h-8" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 11v6m-3-3h6" />
  </svg>
);

const repository = new Http_Integration_Repository();
const import_google_use_case = new Import_Google_Calendar_Use_Case_V3(repository);
const import_teamup_use_case = new Import_Teamup_Calendar_Use_Case_V3(repository);

// Componente para mostrar resultado de importación
const Import_Result_Card: React.FC<{ result: Import_Response_V3; on_close: () => void }> = ({ 
  result, 
  on_close 
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white border-3 border-basmati-black shadow-hard max-w-md w-full overflow-hidden">
        {/* Header */}
        <div className={`p-5 ${result.success ? 'bg-basmati-green' : 'bg-basmati-red'} text-white flex items-center gap-3`}>
          {result.success ? <CheckCircleIcon /> : <ExclamationCircleIcon />}
          <div>
            <h2 className="text-lg font-bold">
              {result.success ? '¡Importación completada!' : 'Error en la importación'}
            </h2>
            <p className="text-sm opacity-90">
              {result.success 
                ? `${result.total_events_imported} eventos añadidos a tu calendario`
                : 'No se pudieron importar los eventos'}
            </p>
          </div>
        </div>
        
        <div className="p-5">
          {/* Resumen de calendarios importados */}
          {result.imported_calendars.length > 0 && (
            <div className="mb-4">
              <h3 className="font-semibold text-sm text-gray-600 mb-2">
                Calendarios procesados
              </h3>
              <div className="space-y-2">
                {result.imported_calendars.map((cal: Imported_Calendar_V3, idx: number) => (
                  <div 
                    key={idx} 
                    className="bg-gray-50 border border-gray-200 p-3 rounded"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm truncate flex-1">
                        {cal.external_id === 'primary' ? 'Calendario principal' : cal.external_id}
                      </span>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-basmati-green font-semibold">
                          {cal.events_imported} importados
                        </span>
                        {cal.events_failed > 0 && (
                          <span className="text-basmati-red font-semibold">
                            {cal.events_failed} fallidos
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Errores si los hay */}
          {result.errors.length > 0 && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="font-semibold text-sm text-red-800 mb-1">Detalles del error:</p>
              <ul className="text-sm text-red-700 list-disc list-inside">
                {result.errors.slice(0, 3).map((error: string, idx: number) => (
                  <li key={idx}>{error}</li>
                ))}
                {result.errors.length > 3 && (
                  <li className="text-red-600">...y {result.errors.length - 3} errores más</li>
                )}
              </ul>
            </div>
          )}
          
          <Neo_Button onClick={on_close} className="w-full" variant={result.success ? "primary" : "secondary"}>
            {result.success ? 'Ver mis calendarios' : 'Intentar de nuevo'}
          </Neo_Button>
        </div>
      </div>
    </div>
  );
};

export const Import_Calendar_Page = () => {
  use_page_title("Importar calendario");
  const navigate = useNavigate();
  const { user } = use_user_context();
  
  // ID del usuario actual (logeado o fallback a dev)
  const current_user_id = user?.external_id || "user_dev_1";
  
  // Estado general
  const [active_tab, set_active_tab] = useState<Provider_Type>("google");
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState<string | null>(null);
  const [import_result, set_import_result] = useState<Import_Response_V3 | null>(null);
  const [show_advanced, set_show_advanced] = useState(false);

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

  // Rango de fechas para importación (compartido entre proveedores)
  // Por defecto 1 año hacia atrás y 1 año hacia adelante
  const [days_past, set_days_past] = useState(365);
  const [days_future, set_days_future] = useState(365);

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
        days_past: days_past,
        days_future: days_future,
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
        days_past: days_past,
        days_future: days_future,
      });
      
      set_import_result(result);
    } catch (err: any) {
      set_error(err.response?.data?.detail || "Error al importar desde Teamup");
    } finally {
      set_loading(false);
    }
  };

  const handle_result_close = () => {
    if (!import_result) {
      set_import_result(null);
      return;
    }
    
    if (import_result.success) {
      navigate("/dashboard");
    } else {
      set_import_result(null);
    }
  };

  return (
    <MainLayout>
      <div className="flex justify-center">
        <div className="w-full max-w-xl">
          <div className="mb-6">
            <Back_Button to="/dashboard" />
          </div>
          
          {/* Header con icono */}
          <div className="flex items-center gap-4 mb-8">
            <div className="p-3 bg-basmati-yellow border-3 border-basmati-black shadow-hard">
              <CalendarPlusIcon />
            </div>
            <div>
              <h1 className="text-2xl font-bold">
                Importar calendario
              </h1>
              <p className="text-gray-600 text-sm">
                Conecta tus calendarios externos y sincroniza tus eventos
              </p>
            </div>
          </div>

          {/* Selector de proveedor - más limpio */}
          <div className="flex gap-2 mb-6 p-1 bg-gray-100 border-2 border-gray-200 rounded-lg">
            <button
              type="button"
              onClick={() => set_active_tab("google")}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-md font-medium transition-all ${
                active_tab === "google" 
                  ? 'bg-white shadow-sm border border-gray-200 text-gray-900' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <GoogleIcon />
              <span>Google Calendar</span>
            </button>
            <button
              type="button"
              onClick={() => set_active_tab("teamup")}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-md font-medium transition-all ${
                active_tab === "teamup" 
                  ? 'bg-white shadow-sm border border-gray-200 text-gray-900' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <TeamupIcon />
              <span>Teamup</span>
            </button>
          </div>

          {/* Mensaje de error */}
          {error && (
            <div className="bg-red-50 text-red-800 p-4 border border-red-200 rounded-lg mb-6 flex items-start gap-3">
              <ExclamationCircleIcon />
              <div>
                <p className="font-medium">No se pudo completar la importación</p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Formulario Google */}
          {active_tab === "google" && (
            <Neo_Card>
              <form onSubmit={handle_google_import} className="flex flex-col gap-5">
                {/* Estado de conexión */}
                {has_stored_token ? (
                  <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircleIcon />
                    </div>
                    <div>
                      <p className="font-medium text-green-900">Conectado con Google</p>
                      <p className="text-sm text-green-700">
                        Tu sesión se usará para importar el calendario
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <GoogleIcon />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Conecta tu cuenta de Google</p>
                        <p className="text-sm text-gray-600">
                          Para importar automáticamente, cierra sesión y vuelve a entrar con Google
                        </p>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 border-t border-gray-200 pt-3 mt-3">
                      <p className="mb-1">¿Ya tienes un token de acceso?</p>
                      <p>Puedes obtener uno desde el{" "}
                        <a 
                          href="https://developers.google.com/oauthplayground/" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="text-blue-600 hover:underline"
                        >
                          OAuth Playground de Google
                        </a>
                        {" "}seleccionando el scope <code className="bg-gray-200 px-1 rounded">calendar.readonly</code>
                      </p>
                    </div>
                  </div>
                )}

                {/* Campo de token - solo visible si no hay token o si muestra avanzado */}
                {(!has_stored_token || show_advanced) && (
                  <Neo_Input
                    label="Token de acceso de Google"
                    placeholder="ya29.a0..."
                    value={google_token}
                    onChange={(e) => set_google_token(e.target.value)}
                    required={!has_stored_token}
                  />
                )}

                {/* Rango de fechas para importar */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rango de eventos a importar
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Hacia el pasado</label>
                      <select
                        value={days_past}
                        onChange={(e) => set_days_past(Number(e.target.value))}
                        className="w-full p-2 border-2 border-gray-300 rounded-md text-sm"
                      >
                        <option value={0}>Solo desde hoy</option>
                        <option value={30}>1 mes</option>
                        <option value={90}>3 meses</option>
                        <option value={180}>6 meses</option>
                        <option value={365}>1 año</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Hacia el futuro</label>
                      <select
                        value={days_future}
                        onChange={(e) => set_days_future(Number(e.target.value))}
                        className="w-full p-2 border-2 border-gray-300 rounded-md text-sm"
                      >
                        <option value={30}>1 mes</option>
                        <option value={90}>3 meses</option>
                        <option value={180}>6 meses</option>
                        <option value={365}>1 año</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Opciones avanzadas colapsables */}
                <div>
                  <button
                    type="button"
                    onClick={() => set_show_advanced(!show_advanced)}
                    className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
                  >
                    <span className={`transform transition-transform ${show_advanced ? 'rotate-90' : ''}`}>▶</span>
                    Opciones avanzadas
                  </button>
                  
                  {show_advanced && (
                    <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <Neo_Input
                        label="IDs de calendario específicos"
                        placeholder="primary, trabajo@gmail.com..."
                        value={google_calendar_ids}
                        onChange={(e) => set_google_calendar_ids(e.target.value)}
                      />
                      <p className="text-xs text-gray-500 -mt-2">
                        Deja vacío para importar tu calendario principal
                      </p>

                      <Neo_Input
                        label="Nombre personalizado"
                        placeholder="Mi calendario de Google"
                        value={google_calendar_name}
                        onChange={(e) => set_google_calendar_name(e.target.value)}
                      />
                      <p className="text-xs text-gray-500 -mt-2">
                        Opcional: nombre con el que aparecerá en Basmati
                      </p>
                    </div>
                  )}
                </div>

                <Neo_Button 
                  type="submit" 
                  disabled={loading || (!google_token && !stored_google_token)} 
                  loading={loading}
                  className="mt-2"
                >
                  {loading ? "Importando eventos..." : "Importar desde Google Calendar"}
                </Neo_Button>
              </form>
            </Neo_Card>
          )}

          {/* Formulario Teamup */}
          {active_tab === "teamup" && (
            <Neo_Card>
              <form onSubmit={handle_teamup_import} className="flex flex-col gap-5">
                {/* Información de conexión */}
                <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <p className="text-sm text-blue-800">
                    <span className="font-medium">Conexión mediante clave.</span> Usa la clave de tu calendario Teamup.
                  </p>
                </div>

                <Neo_Input
                  label="Clave del calendario"
                  placeholder="ks123456abc"
                  value={teamup_key}
                  onChange={(e) => set_teamup_key(e.target.value)}
                  required
                />
                <p className="text-xs text-gray-500 -mt-3">
                  La encuentras en la URL de tu calendario: teamup.com/<strong>ks123456abc</strong>
                </p>

                {/* Rango de fechas para importar */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rango de eventos a importar
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Hacia el pasado</label>
                      <select
                        value={days_past}
                        onChange={(e) => set_days_past(Number(e.target.value))}
                        className="w-full p-2 border-2 border-gray-300 rounded-md text-sm"
                      >
                        <option value={0}>Solo desde hoy</option>
                        <option value={30}>1 mes</option>
                        <option value={90}>3 meses</option>
                        <option value={180}>6 meses</option>
                        <option value={365}>1 año</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Hacia el futuro</label>
                      <select
                        value={days_future}
                        onChange={(e) => set_days_future(Number(e.target.value))}
                        className="w-full p-2 border-2 border-gray-300 rounded-md text-sm"
                      >
                        <option value={30}>1 mes</option>
                        <option value={90}>3 meses</option>
                        <option value={180}>6 meses</option>
                        <option value={365}>1 año</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Opciones avanzadas colapsables */}
                <div>
                  <button
                    type="button"
                    onClick={() => set_show_advanced(!show_advanced)}
                    className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
                  >
                    <span className={`transform transition-transform ${show_advanced ? 'rotate-90' : ''}`}>▶</span>
                    Opciones avanzadas
                  </button>
                  
                  {show_advanced && (
                    <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <Neo_Input
                        label="API Key personal"
                        placeholder="Tu API Key de Teamup..."
                        value={teamup_api_key}
                        onChange={(e) => set_teamup_api_key(e.target.value)}
                      />
                      <p className="text-xs text-gray-500 -mt-2">
                        Opcional: si no la tienes, se usará la del servidor
                      </p>

                      <Neo_Input
                        label="Nombre personalizado"
                        placeholder="Mi calendario de Teamup"
                        value={teamup_calendar_name}
                        onChange={(e) => set_teamup_calendar_name(e.target.value)}
                      />
                      <p className="text-xs text-gray-500 -mt-2">
                        Opcional: nombre con el que aparecerá en Basmati
                      </p>
                    </div>
                  )}
                </div>

                <Neo_Button 
                  type="submit" 
                  disabled={loading || !teamup_key} 
                  loading={loading}
                  className="mt-2"
                >
                  {loading ? "Importando eventos..." : "Importar desde Teamup"}
                </Neo_Button>
              </form>
            </Neo_Card>
          )}

          {/* Información adicional - más sutil */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Por defecto: 1 año hacia atrás y 1 año hacia delante</p>
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
