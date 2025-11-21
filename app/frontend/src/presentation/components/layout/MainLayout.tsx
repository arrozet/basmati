import React from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export const MainLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />
            <div className="flex flex-1">
                <Sidebar />
                <main className="flex-1 p-8 overflow-y-auto bg-basmati-bg relative">
                     {/* Dot pattern background effect */}
                    <div className="absolute inset-0 opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#1A1A1A 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
                    <div className="relative z-10">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};

