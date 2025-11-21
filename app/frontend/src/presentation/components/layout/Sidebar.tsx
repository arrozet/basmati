import React from 'react';
import { Link } from 'react-router-dom';
import { Neo_Button } from '../ui/Neo_Button';
import { Neo_Card } from '../ui/Neo_Card';
import { clsx } from 'clsx';

interface SidebarProps {
    isOpen?: boolean;
    onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
    return (
        <>
            {/* Overlay for mobile */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-30 md:hidden"
                    onClick={onClose}
                />
            )}

            <aside className={clsx(
                "fixed md:sticky top-16 h-[calc(100vh-64px)] w-64 border-r-3 border-basmati-black bg-basmati-bg p-4 flex flex-col gap-6 overflow-y-auto transition-transform duration-300 z-40",
                "md:translate-x-0", // Always visible on desktop
                isOpen ? "translate-x-0" : "-translate-x-full" // Toggle on mobile
            )}>
                
                <div>
                    <Link to="/events/new" onClick={onClose}>
                        <Neo_Button className="w-full flex items-center justify-center gap-2">
                            <span>+</span> Crear evento
                        </Neo_Button>
                    </Link>
                </div>

                <div className="flex flex-col gap-2">
                    <h4 className="font-bold text-lg">Mis calendarios</h4>
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
                    <h4 className="font-bold text-lg">Otros calendarios</h4>
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
        </>
    );
};
