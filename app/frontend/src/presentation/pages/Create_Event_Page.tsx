import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Create_Event_Use_Case } from '../../application/event/create_event_use_case';
import { Http_Event_Repository } from '../../infrastructure/repositories/http_event_repository';

const repository = new Http_Event_Repository();
const create_event_use_case = new Create_Event_Use_Case(repository);

/**
 * Página de creación de evento accesible.
 * Usa formulario semántico con labels asociados, aria-live para mensajes de error.
 */
export const Create_Event_Page = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [loading, set_loading] = useState(false);
    const [error, set_error] = useState<string | null>(null);
    
    const [form_data, set_form_data] = useState({
        title: '',
        start_time: '',
        end_time: '',
        description: '',
        calendar_id: '507f1f77bcf86cd799439011' // Default valid ObjectId
    });

    useEffect(() => {
        const dateParam = searchParams.get('date');
        if (dateParam) {
            set_form_data(prev => ({
                ...prev,
                start_time: `${dateParam}T00:00`,
                end_time: `${dateParam}T23:59`
            }));
        }
    }, [searchParams]);

    const handle_change = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        set_form_data({
            ...form_data,
            [e.target.name]: e.target.value
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
            await create_event_use_case.execute({
                title: form_data.title,
                start_time: new Date(form_data.start_time),
                end_time: new Date(form_data.end_time),
                description: form_data.description,
                calendar_id: form_data.calendar_id
            });
            navigate('/dashboard');
        } catch (err: any) {
            console.error(err);
            set_error(err.message || "Error al crear el evento");
        } finally {
            set_loading(false);
        }
    };

    return (
        <MainLayout>
            <div className="flex justify-center">
                <Neo_Card className="w-full max-w-2xl" title="Crear evento">
                    <form 
                        onSubmit={handle_submit} 
                        className="flex flex-col gap-6"
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
                            <legend className="font-bold text-sm mb-2 text-basmati-black">Fechas del evento</legend>
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
                            <label htmlFor="event-description" className="font-bold text-sm text-basmati-black">
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
                            <label htmlFor="event-calendar" className="font-bold text-sm text-basmati-black">
                                Calendario <span className="text-basmati-red" aria-label="requerido">*</span>
                            </label>
                            <select 
                                id="event-calendar"
                                className="border-3 border-basmati-black px-3 py-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 transition-all bg-white"
                                name="calendar_id"
                                value={form_data.calendar_id}
                                onChange={handle_change}
                                required
                                aria-label="Seleccionar calendario para el evento"
                            >
                                <option value="507f1f77bcf86cd799439011">Personal</option>
                                <option value="507f1f77bcf86cd799439012">Trabajo</option>
                                <option value="507f1f77bcf86cd799439013">Universidad</option>
                            </select>
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
                                loading={loading}
                            >
                                {loading ? 'Guardando...' : 'Guardar evento'}
                            </Neo_Button>
                            <Neo_Button 
                                type="button" 
                                onClick={() => navigate('/dashboard')} 
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
        </MainLayout>
    );
};
