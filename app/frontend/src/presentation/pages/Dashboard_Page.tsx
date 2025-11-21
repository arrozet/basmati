import React from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { Neo_Card } from '../components/ui/Neo_Card';
import { Neo_Button } from '../components/ui/Neo_Button';

// Simple mock for a calendar grid
const CalendarGrid = () => {
    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    // Generating a 5-week grid for visual
    const weeks = [0, 1, 2, 3, 4];

    return (
        <div className="w-full">
            {/* Desktop Header */}
            <div className="hidden md:grid grid-cols-7 gap-4 mb-4">
                {days.map(day => (
                    <div key={day} className="text-center font-black text-xl uppercase">{day}</div>
                ))}
            </div>
            
            <div className="flex flex-col gap-4">
                {weeks.map((week) => (
                    <div key={week} className="grid grid-cols-1 md:grid-cols-7 gap-4 md:h-32">
                        {days.map((day, index) => (
                            <div 
                                key={day} 
                                className="bg-white border-3 border-basmati-black shadow-hard p-2 hover:-translate-y-1 hover:shadow-[6px_6px_0px_0px_rgba(26,26,26,1)] transition-all cursor-pointer relative min-h-[100px] md:min-h-0"
                            >
                                {/* Mobile Day Label */}
                                <span className="md:hidden font-black uppercase text-xs mb-2 block text-gray-500">{day}</span>
                                
                                <span className="font-bold text-gray-400 absolute top-2 right-2">{week * 7 + index + 1 <= 31 ? week * 7 + index + 1 : ''}</span>
                                
                                {/* Random events for mockup */}
                                {(week === 1 && index === 2) && (
                                    <div className="bg-basmati-yellow border-2 border-basmati-black p-1 text-xs font-bold mt-6 truncate shadow-[2px_2px_0px_0px_rgba(26,26,26,1)]">
                                        Reunión
                                    </div>
                                )}
                                {(week === 2 && index === 5) && (
                                    <div className="bg-basmati-blue text-white border-2 border-basmati-black p-1 text-xs font-bold mt-6 truncate shadow-[2px_2px_0px_0px_rgba(26,26,26,1)]">
                                        Entrega P2
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};

export const Dashboard_Page = () => {
    return (
        <MainLayout>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
                <div>
                    <h2 className="text-3xl md:text-4xl font-black uppercase mb-1">Septiembre 2025</h2>
                    <p className="font-medium text-gray-600">La vida es eso que pasa mientras haces otros planes.</p>
                </div>
                <div className="flex gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
                    <Neo_Button variant="secondary" className="flex-1 md:flex-none">Mes</Neo_Button>
                    <Neo_Button variant="secondary" className="flex-1 md:flex-none">Semana</Neo_Button>
                    <Neo_Button variant="secondary" className="flex-1 md:flex-none">Día</Neo_Button>
                </div>
            </div>
            
            <CalendarGrid />
        </MainLayout>
    );
};
