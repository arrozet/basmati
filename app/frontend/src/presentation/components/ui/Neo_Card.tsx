import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Neo_Card_Props extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    title?: string;
    as_section?: boolean;
}

/**
 * Componente de tarjeta accesible siguiendo el diseño Neobrutalism.
 * @param children - Contenido de la tarjeta.
 * @param title - Título opcional de la tarjeta.
 * @param as_section - Si true, renderiza como <section>, sino como <div>.
 * @param className - Clases CSS adicionales.
 */
export const Neo_Card: React.FC<Neo_Card_Props> = ({ children, className, title, as_section = false, ...props }) => {
    const Component = as_section ? 'section' : 'div';
    
    return (
        <Component 
            className={cn(
                "bg-white border-3 border-basmati-black shadow-hard p-4 hover:shadow-hard-lg transition-shadow",
                className
            )} 
            {...props}
        >
            {title && (
                <header className="border-b-3 border-basmati-black pb-2 mb-4">
                    <h2 className="font-bold text-xl">{title}</h2>
                </header>
            )}
            {children}
        </Component>
    );
};

