import React, { useState, FormEvent } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Neo_Input } from '../components/ui/Neo_Input';
import { Neo_Card } from '../components/ui/Neo_Card';
// TODO BACKEND: Descomentar cuando el backend esté listo
// import { use_user_profile } from '../hooks/use_user_profile';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBell, faArrowLeft, faCheck, faExclamationCircle } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { use_page_title } from '../hooks/use_page_title';

type SettingsTab = 'profile' | 'notifications';
type NotificationFrequency = 'instant' | 'daily';

// ============================================================================
// DATOS MOCK TEMPORALES - ELIMINAR CUANDO SE CONECTE AL BACKEND
// ============================================================================
const MOCK_USER_DATA = {
    display_name: "Usuario Demo",
    email: "usuario@example.com",
    avatar_url: null,
    notification_preferences: {
        in_app: true,
        email: true,
        email_address: null
    }
};

/**
 * Página de configuración del usuario con secciones de perfil y notificaciones.
 * Implementa estándares de accesibilidad WCAG 2.1 AA.
 * 
 * ============================================================================
 * NOTA PARA EL EQUIPO DE BACKEND:
 * ============================================================================
 * Esta página actualmente usa datos MOCK para desarrollo del frontend.
 * Para conectar al backend, debes:
 * 
 * 1. Descomentar el import de use_user_profile (línea ~6)
 * 2. Descomentar el hook y eliminar los datos MOCK (línea ~49)
 * 3. Asegurarte de que estos endpoints funcionen:
 *    - GET  /v1/users/{user_id}  (obtener perfil)
 *    - PUT  /v1/users/{user_id}  (actualizar perfil y preferencias)
 * 4. El hook usa localStorage.getItem('basmati_user_id') para el user_id
 * 5. En producción, reemplazar esto con el ID del token JWT de OAuth
 * ============================================================================
 */
export const Settings_Page: React.FC = () => {
    use_page_title('Settings');
    const navigate = useNavigate();
    
    // TODO BACKEND: Descomentar estas líneas cuando el backend esté listo
    // const { user, loading, saving, error, update_preferences, update_profile } = use_user_profile();
    
    // ========================================================================
    // MOCK DATA - ELIMINAR CUANDO SE CONECTE AL BACKEND
    // ========================================================================
    const user = MOCK_USER_DATA;
    const loading = false;
    const saving = false;
    const error = null;
    // ========================================================================
    
    const [active_tab, set_active_tab] = useState<SettingsTab>('profile');
    const [success_message, set_success_message] = useState<string | null>(null);
    const [form_error, set_form_error] = useState<string | null>(null);

    // Estados del formulario de perfil
    const [display_name, set_display_name] = useState<string>(MOCK_USER_DATA.display_name);
    const [email, set_email] = useState<string>(MOCK_USER_DATA.email);
    
    // Estados del formulario de notificaciones
    const [notification_email_enabled, set_notification_email_enabled] = useState<boolean>(MOCK_USER_DATA.notification_preferences.email);
    const [notification_in_app_enabled, set_notification_in_app_enabled] = useState<boolean>(MOCK_USER_DATA.notification_preferences.in_app);
    const [notification_frequency, set_notification_frequency] = useState<NotificationFrequency>('instant');

    /**
     * Maneja el envío del formulario de perfil.
     * 
     * TODO BACKEND: Reemplazar este mock con la llamada real:
     * await update_profile({ display_name, email });
     */
    const handle_profile_submit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        set_form_error(null);
        set_success_message(null);

        // ====================================================================
        // MOCK - SIMULA GUARDADO EXITOSO
        // ====================================================================
        console.log('📝 [MOCK] Guardando perfil:', { display_name, email });
        set_success_message('✅ Perfil actualizado correctamente (simulado)');
        setTimeout(() => set_success_message(null), 3000);
        
        // TODO BACKEND: Descomentar cuando esté listo:
        /*
        try {
            await update_profile({
                display_name,
                email
            });
            set_success_message('Perfil actualizado correctamente');
            setTimeout(() => set_success_message(null), 3000);
        } catch (err) {
            set_form_error(err instanceof Error ? err.message : 'Error al actualizar el perfil');
        }
        */
    };

    /**
     * Maneja el envío del formulario de notificaciones.
     * 
     * TODO BACKEND: Reemplazar este mock con la llamada real:
     * await update_preferences({ email, in_app, email_address });
     */
    const handle_notifications_submit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        set_form_error(null);
        set_success_message(null);

        // ====================================================================
        // MOCK - SIMULA GUARDADO EXITOSO
        // ====================================================================
        console.log('🔔 [MOCK] Guardando preferencias:', {
            email: notification_email_enabled,
            in_app: notification_in_app_enabled,
            frequency: notification_frequency
        });
        set_success_message('✅ Preferencias actualizadas correctamente (simulado)');
        setTimeout(() => set_success_message(null), 3000);
        
        // TODO BACKEND: Descomentar cuando esté listo:
        /*
        try {
            await update_preferences({
                email: notification_email_enabled,
                in_app: notification_in_app_enabled,
                email_address: user?.email || null
            });
            set_success_message('Preferencias de notificación actualizadas correctamente');
            setTimeout(() => set_success_message(null), 3000);
        } catch (err) {
            set_form_error(err instanceof Error ? err.message : 'Error al actualizar las preferencias');
        }
        */
    };

    /**
     * Renderiza el contenido de la pestaña activa.
     */
    const render_tab_content = () => {
        if (active_tab === 'profile') {
            return (
                <section aria-labelledby="profile-heading">
                    <h2 id="profile-heading" className="text-2xl font-black mb-6">Mi perfil</h2>
                    
                    <form onSubmit={handle_profile_submit} className="space-y-6">
                        <div className="flex items-center gap-4 mb-8">
                            <div 
                                className="w-20 h-20 rounded-full border-3 border-basmati-black shadow-hard bg-basmati-yellow flex items-center justify-center text-3xl font-black"
                                role="img"
                                aria-label={`Foto de perfil de ${user.display_name}`}
                            >
                                {user.avatar_url ? (
                                    <img 
                                        src={user.avatar_url} 
                                        alt={`Avatar de ${user.display_name}`}
                                        className="w-full h-full rounded-full object-cover"
                                    />
                                ) : (
                                    <FontAwesomeIcon icon={faUser} aria-hidden="true" />
                                )}
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">
                                    Esta es el control remoto de tu identidad virtual.
                                </p>
                            </div>
                        </div>

                        <Neo_Input
                            label="Apodo"
                            type="text"
                            id="display-name"
                            value={display_name}
                            onChange={(e) => set_display_name(e.target.value)}
                            placeholder="Ej: Juan Pérez"
                            required
                            helper_text="Este es el nombre que verán otros usuarios"
                        />

                        <Neo_Input
                            label="Nombre completo"
                            type="text"
                            id="full-name"
                            placeholder="Ej: Juan Pérez García"
                            helper_text="No editable - proporcionado por OAuth"
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
                                onClick={() => navigate('/dashboard')}
                                className="flex-1"
                            >
                                Cancelar
                            </Neo_Button>
                        </div>
                    </form>
                </section>
            );
        }

        if (active_tab === 'notifications') {
            return (
                <section aria-labelledby="notifications-heading">
                    <h2 id="notifications-heading" className="text-2xl font-black mb-6">Notificaciones</h2>
                    
                    <form onSubmit={handle_notifications_submit} className="space-y-8">
                        <fieldset className="border-3 border-basmati-black p-6 bg-white shadow-hard">
                            <legend className="font-black text-lg px-2 bg-basmati-bg">Recibir notificaciones por:</legend>
                            
                            <div className="space-y-4 mt-4">
                                <div className="flex items-start gap-3">
                                    <input
                                        type="checkbox"
                                        id="notification-email"
                                        checked={notification_email_enabled}
                                        onChange={(e) => set_notification_email_enabled(e.target.checked)}
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
                                        <p id="notification-email-description" className="text-sm text-gray-600 mt-1">
                                            Recibirás notificaciones en {user.email}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <input
                                        type="checkbox"
                                        id="notification-in-app"
                                        checked={notification_in_app_enabled}
                                        onChange={(e) => set_notification_in_app_enabled(e.target.checked)}
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
                                        <p id="notification-in-app-description" className="text-sm text-gray-600 mt-1">
                                            Verás notificaciones mientras usas Basmati
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </fieldset>

                        <fieldset className="border-3 border-basmati-black p-6 bg-white shadow-hard">
                            <legend className="font-black text-lg px-2 bg-basmati-bg">Frecuencia</legend>
                            
                            <div className="space-y-3 mt-4" role="radiogroup" aria-labelledby="notifications-heading">
                                <div className="flex items-start gap-3">
                                    <input
                                        type="radio"
                                        id="frequency-instant"
                                        name="notification-frequency"
                                        value="instant"
                                        checked={notification_frequency === 'instant'}
                                        onChange={() => set_notification_frequency('instant')}
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
                                        <p id="frequency-instant-description" className="text-sm text-gray-600 mt-1">
                                            Te notificaremos inmediatamente cuando ocurra algo importante
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <input
                                        type="radio"
                                        id="frequency-daily"
                                        name="notification-frequency"
                                        value="daily"
                                        checked={notification_frequency === 'daily'}
                                        onChange={() => set_notification_frequency('daily')}
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
                                        <p id="frequency-daily-description" className="text-sm text-gray-600 mt-1">
                                            Recibirás un resumen diario con todas las novedades
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
                                onClick={() => navigate('/dashboard')}
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

    // TODO BACKEND: Descomentar estos estados de carga cuando se conecte al backend
    /*
    if (loading) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center min-h-[60vh]" role="status" aria-live="polite">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-3 border-basmati-black" aria-hidden="true"></div>
                    <span className="sr-only">Cargando configuración del usuario...</span>
                </div>
            </MainLayout>
        );
    }

    if (error && !user) {
        return (
            <MainLayout>
                <div className="max-w-2xl mx-auto py-8 px-4" role="alert">
                    <Neo_Card className="bg-basmati-red/10 border-basmati-red">
                        <div className="flex items-center gap-3">
                            <FontAwesomeIcon icon={faExclamationCircle} className="text-2xl text-basmati-red" aria-hidden="true" />
                            <div>
                                <h2 className="font-black text-lg">Error al cargar configuración</h2>
                                <p className="text-sm">{error}</p>
                            </div>
                        </div>
                    </Neo_Card>
                </div>
            </MainLayout>
        );
    }
    */

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto py-8 px-4">
                {/* Header */}
                <header className="mb-8">
                    <button
                        type="button"
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center gap-2 text-gray-600 hover:text-basmati-black mb-4 focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 rounded px-2 py-1 transition-colors"
                        aria-label="Volver al dashboard"
                    >
                        <FontAwesomeIcon icon={faArrowLeft} aria-hidden="true" />
                        <span className="font-bold">Volver</span>
                    </button>
                    <h1 className="text-4xl font-black uppercase">Configuración</h1>
                    <p className="text-gray-600 mt-2">Gestiona tu perfil y preferencias de notificación</p>
                </header>

                {/* Mensajes de éxito/error */}
                {success_message && (
                    <div 
                        role="status" 
                        aria-live="polite" 
                        className="mb-6 p-4 bg-basmati-green/20 border-3 border-basmati-green shadow-hard"
                    >
                        <div className="flex items-center gap-3">
                            <FontAwesomeIcon icon={faCheck} className="text-xl text-basmati-green" aria-hidden="true" />
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
                            <FontAwesomeIcon icon={faExclamationCircle} className="text-xl text-basmati-red" aria-hidden="true" />
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
                        aria-selected={active_tab === 'profile'}
                        aria-controls="profile-panel"
                        id="profile-tab"
                        onClick={() => set_active_tab('profile')}
                        className={`
                            flex items-center gap-2 px-6 py-3 font-bold border-3 border-basmati-black transition-all
                            focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2
                            ${active_tab === 'profile' 
                                ? 'bg-basmati-yellow shadow-hard -mb-[3px]' 
                                : 'bg-white hover:bg-gray-100 shadow-none'
                            }
                        `}
                    >
                        <FontAwesomeIcon icon={faUser} aria-hidden="true" />
                        <span>Mi perfil</span>
                    </button>
                    
                    <button
                        type="button"
                        role="tab"
                        aria-selected={active_tab === 'notifications'}
                        aria-controls="notifications-panel"
                        id="notifications-tab"
                        onClick={() => set_active_tab('notifications')}
                        className={`
                            flex items-center gap-2 px-6 py-3 font-bold border-3 border-basmati-black transition-all
                            focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2
                            ${active_tab === 'notifications' 
                                ? 'bg-basmati-yellow shadow-hard -mb-[3px]' 
                                : 'bg-white hover:bg-gray-100 shadow-none'
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
