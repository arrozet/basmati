import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { Neo_Button } from '../components/ui/Neo_Button';
import { use_calendars } from '../hooks/use_calendars';
import { Calendar_Model } from '../../domain/models/calendar_model';
import { use_page_title } from '../hooks/use_page_title';
import { use_user_context } from '../context/UserContext';

/**
 * Página para editar un calendario existente.
 * Incluye funcionalidad de modificación y eliminación.
 */
export const Edit_Calendar_Page = () => {
    use_page_title('Edit calendar');
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { user } = use_user_context();
    const current_user_id = user?.external_id || 'user_dev_1';
    const { calendars, update_calendar, delete_calendar, get_calendar_by_id } = use_calendars(current_user_id);
    const [loading, set_loading] = useState(true);
    const [saving, set_saving] = useState(false);
    const [deleting, set_deleting] = useState(false);
    const [error, set_error] = useState<string | null>(null);
    const [calendar, set_calendar] = useState<Calendar_Model | null>(null);
    
    const [form_data, set_form_data] = useState({
        title: '',
        color: '#EBBE4D',
        owner_id: CURRENT_USER_ID,
        icon: '',
        is_public: false,
        parent_id: ''
    });

    useEffect(() => {
        const fetch_calendar = async () => {
            if (!id) return;
            try {
                const fetched_calendar = await get_calendar_by_id(id);
                if (fetched_calendar) {
                    set_calendar(fetched_calendar);
                    set_form_data({
                        title: fetched_calendar.title,
                        color: fetched_calendar.color,
                        owner_id: fetched_calendar.owner_id,
                        icon: fetched_calendar.icon || '',
                        is_public: fetched_calendar.is_public,
                        parent_id: fetched_calendar.parent_id || ''
                    });
                } else {
                    set_error("Calendario no encontrado");
                }
            } catch (err) {
                console.error(err);
                set_error("Error al cargar el calendario");
            } finally {
                set_loading(false);
            }
        };
        fetch_calendar();
    }, [id]);

    const handle_change = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        const checked = (e.target as HTMLInputElement).checked;
        
        set_form_data({
            ...form_data,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handle_submit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!calendar) return;
        
        set_saving(true);
        set_error(null);

        try {
            await update_calendar({
                id: calendar.id,
                title: form_data.title,
                color: form_data.color,
                owner_id: form_data.owner_id,
                icon: form_data.icon,
                is_public: form_data.is_public,
                parent_id: form_data.parent_id || undefined
            });
            navigate('/dashboard');
        } catch (err: any) {
            console.error(err);
            set_error(err.message || "Error al guardar los cambios");
        } finally {
            set_saving(false);
        }
    };

    const handle_delete = async () => {
        if (!calendar) return;
        
        const confirmation = window.confirm(
            `¿Estás seguro de que quieres eliminar el calendario "${calendar.title}"? Esta acción no se puede deshacer.`
        );
        
        if (!confirmation) return;
        
        set_deleting(true);
        set_error(null);

        try {
            await delete_calendar(calendar.id);
            navigate('/dashboard');
        } catch (err: any) {
            console.error(err);
            set_error(err.message || "Error al eliminar el calendario");
        } finally {
            set_deleting(false);
        }
    };

    const predefined_colors = [
        { hex: '#EBBE4D', name: 'Amarillo Basmati' },
        { hex: '#5496FF', name: 'Azul' },
        { hex: '#FF6B6B', name: 'Rojo' },
        { hex: '#4ECDC4', name: 'Verde agua' },
        { hex: '#F59E0B', name: 'Naranja' },
        { hex: '#8B5CF6', name: 'Morado' },
        { hex: '#EC4899', name: 'Rosa' },
        { hex: '#10B981', name: 'Verde' }
    ];

    if (loading) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center h-64" role="status" aria-live="polite">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-basmati-black" aria-hidden="true"></div>
                    <span className="sr-only">Cargando calendario...</span>
                </div>
            </MainLayout>
        );
    }

    if (error && !calendar) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center h-64 flex-col gap-4">
                    <div className="text-xl text-basmati-red font-bold border-3 border-basmati-black bg-white p-6" role="alert">
                        {error}
                    </div>
                    <Neo_Button onClick={() => navigate('/dashboard')} variant="secondary">
                        Volver al Dashboard
                    </Neo_Button>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="flex justify-center">
                <Neo_Card className="w-full max-w-2xl" title="Modificar calendario">
                    <form 
                        onSubmit={handle_submit} 
                        className="flex flex-col gap-6"
                        aria-label="Formulario de modificación de calendario"
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
                            <div className="grid grid-cols-4 md:grid-cols-8 gap-3" role="radiogroup" aria-label="Selector de color del calendario">
                                {predefined_colors.map(({ hex, name }) => (
                                    <button
                                        key={hex}
                                        type="button"
                                        className={`w-full aspect-square rounded-md border-3 transition-all focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 hover:scale-110 ${
                                            form_data.color === hex 
                                                ? 'border-basmati-black shadow-hard scale-110' 
                                                : 'border-gray-300'
                                        }`}
                                        style={{ backgroundColor: hex }}
                                        onClick={() => set_form_data({...form_data, color: hex})}
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
                                <label htmlFor="custom-color" className="text-sm font-medium text-basmati-black">
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
                            <label htmlFor="parent-calendar" className="font-bold text-sm text-basmati-black">
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
                                    .filter(c => c.owner_id === CURRENT_USER_ID && c.id !== calendar?.id)
                                    .map(cal => (
                                    <option key={cal.id} value={cal.id}>
                                        {cal.title}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <Neo_Input 
                            label="Organizador" 
                            placeholder="Ej: Mi padre" 
                            name="owner_id"
                            value={form_data.owner_id}
                            onChange={handle_change}
                            required
                            id="calendar-owner"
                            autoComplete="off"
                        />

                        <div className="flex flex-col gap-1">
                            <label htmlFor="calendar-icon" className="font-bold text-sm text-basmati-black">
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
                            <label htmlFor="calendar-public" className="font-medium text-basmati-black cursor-pointer">
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
                                disabled={saving || deleting}
                            >
                                {saving ? 'Guardando...' : 'Modificar'}
                            </Neo_Button>
                            <Neo_Button 
                                type="button" 
                                onClick={() => navigate('/dashboard')} 
                                variant="secondary" 
                                className="flex-1"
                                disabled={saving || deleting}
                            >
                                Cancelar
                            </Neo_Button>
                        </div>

                        <hr className="border-t-3 border-basmati-black my-2" />

                        <div className="flex flex-col gap-2">
                            <h3 className="font-bold text-basmati-black text-lg">Zona peligrosa</h3>
                            <p className="text-sm text-gray-600">
                                Eliminar este calendario es una acción permanente. Todos los eventos asociados también serán eliminados.
                            </p>
                            <Neo_Button 
                                type="button" 
                                onClick={handle_delete} 
                                variant="danger" 
                                className="w-full md:w-auto"
                                disabled={saving || deleting}
                            >
                                {deleting ? 'Eliminando...' : 'Eliminar calendario'}
                            </Neo_Button>
                        </div>
                    </form>
                </Neo_Card>
            </div>
        </MainLayout>
    );
};
