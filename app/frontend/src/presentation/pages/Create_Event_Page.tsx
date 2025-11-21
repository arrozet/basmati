import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Input } from '../components/ui/Neo_Input';
import { Neo_Button } from '../components/ui/Neo_Button';

export const Create_Event_Page = () => {
    const navigate = useNavigate();

    return (
        <MainLayout>
            <div className="flex justify-center">
                <Neo_Card className="w-full max-w-2xl" title="Crear evento">
                    <form className="flex flex-col gap-6">
                        <Neo_Input label="Título" placeholder="Ej: Cena con amigos" />
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Neo_Input label="Fecha inicio" type="datetime-local" />
                            <Neo_Input label="Fecha fin" type="datetime-local" />
                        </div>

                        <div className="flex flex-col gap-1">
                            <label className="font-bold text-sm">Descripción</label>
                            <textarea 
                                className="border-3 border-basmati-black p-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow/50 transition-all bg-white h-32 resize-none"
                                placeholder="Detalles del evento..."
                            />
                        </div>

                        <div className="flex flex-col gap-1">
                            <label className="font-bold text-sm">Calendario</label>
                            <select className="border-3 border-basmati-black p-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow/50 transition-all bg-white">
                                <option>Personal</option>
                                <option>Trabajo</option>
                                <option>Universidad</option>
                            </select>
                        </div>

                        <div className="flex flex-col md:flex-row gap-4 mt-4">
                            <Neo_Button type="button" onClick={() => navigate('/dashboard')} variant="success" className="flex-1">
                                Guardar evento
                            </Neo_Button>
                            <Neo_Button type="button" onClick={() => navigate('/dashboard')} variant="danger" className="flex-1">
                                Cancelar
                            </Neo_Button>
                        </div>
                    </form>
                </Neo_Card>
            </div>
        </MainLayout>
    );
};
