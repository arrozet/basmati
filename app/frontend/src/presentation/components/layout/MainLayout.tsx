import React, { useState } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

/**
 * Layout principal de la aplicación.
 * Usa landmarks semánticos para mejorar la navegación con tecnologías asistivas.
 * Estructura: <header> (Navbar) + <aside> (Sidebar) + <main> (contenido).
 */
export const MainLayout = ({ children }: { children: React.ReactNode }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header implícito dentro de Navbar (etiqueta nav con role navigation) */}
            <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
            
            <div className="flex flex-1 relative">
                {/* Aside: Navegación secundaria de calendarios */}
                <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
                
                {/* Main: Contenido principal de la página */}
                <main 
                    className="flex-1 p-4 md:p-8 overflow-y-auto bg-basmati-bg relative w-full"
                    id="main-content"
                    role="main"
                >
                    {/* Dot pattern background effect */}
                    <div 
                        className="absolute inset-0 opacity-5 pointer-events-none" 
                        style={{ backgroundImage: 'radial-gradient(#1A1A1A 1px, transparent 1px)', backgroundSize: '20px 20px' }}
                        aria-hidden="true"
                    ></div>
                    <div className="relative z-10">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};
