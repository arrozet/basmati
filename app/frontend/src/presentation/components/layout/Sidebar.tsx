import React from 'react';
import { Link } from 'react-router-dom';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Card } from '../ui/Neo_Card';

export const Sidebar = () => {
    return (
        <aside className="w-64 h-[calc(100vh-64px)] border-r-3 border-basmati-black bg-basmati-bg p-4 flex flex-col gap-6 sticky top-16 overflow-y-auto">
            
            <div>
                <Link to="/events/new">
                    <Neo_Button className="w-full flex items-center justify-center gap-2">
                        <span>+</span> Crear Evento
                    </Neo_Button>
                </Link>
            </div>

            <div className="flex flex-col gap-2">
                <h4 className="font-bold text-lg">Mis Calendarios</h4>
                <div className="flex flex-col gap-2">
                    {['Personal', 'Trabajo', 'Universidad', 'Gimnasio'].map((cal) => (
                        <div key={cal} className="flex items-center gap-2 cursor-pointer hover:translate-x-1 transition-transform">
                             <div className="w-4 h-4 border-3 border-basmati-black bg-basmati-yellow"></div>
                             <span className="font-medium">{cal}</span>
                        </div>
                    ))}
                </div>
            </div>

             <div className="flex flex-col gap-2">
                <h4 className="font-bold text-lg">Otros Calendarios</h4>
                <div className="flex flex-col gap-2">
                    {['Festivos', 'Cumpleaños'].map((cal) => (
                        <div key={cal} className="flex items-center gap-2 cursor-pointer hover:translate-x-1 transition-transform">
                             <div className="w-4 h-4 border-3 border-basmati-black bg-basmati-blue"></div>
                             <span className="font-medium">{cal}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-auto">
                <Neo_Card className="bg-basmati-green/20">
                    <p className="text-xs font-bold mb-2">Tip del día:</p>
                    <p className="text-xs">Organiza tu caos como si de granos de arroz se tratase.</p>
                </Neo_Card>
            </div>
        </aside>
    );
};

