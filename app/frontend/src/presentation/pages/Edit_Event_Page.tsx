import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { Neo_Button } from '../components/ui/Neo_Button';
import { Http_Event_Repository } from '../../infrastructure/repositories/http_event_repository';
import { Event_Model } from '../../domain/models/event_model';

const repository = new Http_Event_Repository();

export const Edit_Event_Page = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, set_loading] = useState(true);
    const [saving, set_saving] = useState(false);
    const [error, set_error] = useState<string | null>(null);
    const [event, set_event] = useState<Event_Model | null>(null);
    
    const [form_data, set_form_data] = useState({
        title: '',
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        description: '',
        color: '#3B82F6'
    });

    useEffect(() => {
        const fetch_event = async () => {
            if (!id) return;
            try {
                const fetched_event = await repository.get_event(id);
                if (fetched_event) {
                    set_event(fetched_event);
                    
                    // Format dates for inputs
                    const start = fetched_event.start_time;
                    const end = fetched_event.end_time;
                    
                    // Handle timezone offset for input type="date" and "time"
                    // Using local time components
                    const format_date = (d: Date) => {
                        const year = d.getFullYear();
                        const month = String(d.getMonth() + 1).padStart(2, '0');
                        const day = String(d.getDate()).padStart(2, '0');
                        return `${year}-${month}-${day}`;
                    };
                    
                    const format_time = (d: Date) => {
                        const hours = String(d.getHours()).padStart(2, '0');
                        const minutes = String(d.getMinutes()).padStart(2, '0');
                        return `${hours}:${minutes}`;
                    };

                    set_form_data({
                        title: fetched_event.title,
                        start_date: format_date(start),
                        start_time: format_time(start),
                        end_date: format_date(end),
                        end_time: format_time(end),
                        description: fetched_event.description || '',
                        color: fetched_event.color || '#3B82F6'
                    });
                } else {
                    set_error("Evento no encontrado");
                }
            } catch (err) {
                console.error(err);
                set_error("Error al cargar el evento");
            } finally {
                set_loading(false);
            }
        };
        fetch_event(); 
    }, [id]);

    const handle_submit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!event) return;
        
        set_saving(true);
        set_error(null);

        try {
            const start_iso = new Date(`${form_data.start_date}T${form_data.start_time}:00`);
            const end_iso = new Date(`${form_data.end_date}T${form_data.end_time}:00`);

            const updated_event: Event_Model = {
                ...event,
                title: form_data.title,
                description: form_data.description,
                start_time: start_iso,
                end_time: end_iso,
                color: form_data.color
            };

            await repository.update(updated_event);
            navigate('/dashboard');
        } catch (err) {
            console.error(err);
            set_error("Error al guardar los cambios");
        } finally {
            set_saving(false);
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center h-64">
                    <div className="text-xl text-gray-600">Cargando evento...</div>
                </div>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <div className="flex justify-center items-center h-64 flex-col">
                    <div className="text-xl text-red-600 mb-4">{error}</div>
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
                <Neo_Card className="w-full max-w-2xl" title="Editar evento">
                    <form onSubmit={handle_submit} className="space-y-6">
                        <Neo_Input
                            label="Título"
                            value={form_data.title}
                            onChange={(e) => set_form_data({...form_data, title: e.target.value})}
                            placeholder="Título del evento"
                            required
                        />

                        <div className="grid grid-cols-2 gap-4">
                            <Neo_Input
                                label="Fecha inicio"
                                type="date"
                                value={form_data.start_date}
                                onChange={(e) => set_form_data({...form_data, start_date: e.target.value})}
                                required
                            />
                            <Neo_Input
                                label="Hora inicio"
                                type="time"
                                value={form_data.start_time}
                                onChange={(e) => set_form_data({...form_data, start_time: e.target.value})}
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <Neo_Input
                                label="Fecha fin"
                                type="date"
                                value={form_data.end_date}
                                onChange={(e) => set_form_data({...form_data, end_date: e.target.value})}
                                required
                            />
                            <Neo_Input
                                label="Hora fin"
                                type="time"
                                value={form_data.end_time}
                                onChange={(e) => set_form_data({...form_data, end_time: e.target.value})}
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Descripción
                            </label>
                            <textarea
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                rows={4}
                                value={form_data.description}
                                onChange={(e) => set_form_data({...form_data, description: e.target.value})}
                                placeholder="Detalles del evento..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Color
                            </label>
                            <div className="flex gap-2">
                                {['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'].map((color) => (
                                    <button
                                        key={color}
                                        type="button"
                                        className={`w-8 h-8 rounded-full border-2 ${form_data.color === color ? 'border-gray-900' : 'border-transparent'}`}
                                        style={{ backgroundColor: color }}
                                        onClick={() => set_form_data({...form_data, color})}
                                    />
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-end space-x-4 pt-4">
                            <Neo_Button 
                                type="button" 
                                variant="secondary" 
                                onClick={() => navigate('/dashboard')}
                            >
                                Cancelar
                            </Neo_Button>
                            <Neo_Button 
                                type="submit" 
                                variant="primary"
                                disabled={saving}
                            >
                                {saving ? 'Guardando...' : 'Guardar Cambios'}
                            </Neo_Button>
                        </div>
                    </form>
                </Neo_Card>
            </div>
        </MainLayout>
    )
}
