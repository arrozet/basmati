import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { Neo_Button } from '../components/ui/Neo_Button';
import { use_calendars } from '../hooks/use_calendars';

// Mock user ID (En producción vendría del contexto de autenticación)
const CURRENT_USER_ID = 'user_dev_1';

/**
 * Página para crear un nuevo calendario.
 * Formulario accesible basado en los bocetos con HTML semántico.
 */
export const Create_Calendar_Page = () => {
    const navigate = useNavigate();
    const { create_calendar } = use_calendars(CURRENT_USER_ID);
    const [loading, set_loading] = useState(false);
    const [error, set_error] = useState<string | null>(null);
    
    const [form_data, set_form_data] = useState({
        title: '',
        color: '#EBBE4D', // Color por defecto basmati-yellow
        owner_id: CURRENT_USER_ID,
        icon: '',
        is_public: false
    });

    const handle_change = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        const checked = (e.target as HTMLInputElement).checked;
        
        set_form_data({
            ...form_data,
            [name]: type === 'checkbox' ? checked : value
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
                owner_id: form_data.owner_id,
                icon: form_data.icon,
                is_public: form_data.is_public
            });
            navigate('/dashboard');
        } catch (err: any) {
            console.error(err);
            set_error(err.message || "Error al crear el calendario");
        } finally {
            set_loading(false);
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

    return (
        <MainLayout>
            <div className="flex justify-center">
                <Neo_Card className="w-full max-w-2xl" title="Crear calendario">
                    <form 
                        onSubmit={handle_submit} 
                        className="flex flex-col gap-6"
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
                                disabled={loading}
                            >
                                {loading ? 'Creando...' : 'Crear'}
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
