import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Neo_Button_Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'success';
    loading?: boolean;
}

/**
 * Componente de botón accesible siguiendo estándares WCAG 2.1 AA.
 * @param variant - Variante visual del botón.
 * @param loading - Estado de carga que deshabilita el botón.
 * @param type - Tipo de botón (button por defecto para evitar envíos accidentales).
 * @param disabled - Estado deshabilitado.
 * @param children - Contenido del botón.
 */
export const Neo_Button: React.FC<Neo_Button_Props> = ({ 
    children, 
    className, 
    variant = 'primary',
    type = 'button',
    loading = false,
    disabled = false,
    ...props 
}) => {
    const variants = {
        primary: 'bg-basmati-yellow hover:bg-[#d9ae42] text-basmati-black',
        secondary: 'bg-white hover:bg-gray-100 text-basmati-black',
        danger: 'bg-basmati-red text-white hover:bg-[#e05a5a]',
        success: 'bg-basmati-green text-basmati-black hover:bg-[#3dbcb3]',
    };

    const is_disabled = disabled || loading;

    return (
        <button 
            type={type}
            disabled={is_disabled}
            className={cn(
                "border-3 border-basmati-black shadow-hard px-6 py-2 font-bold transition-all",
                "focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2",
                "active:shadow-none active:translate-x-[4px] active:translate-y-[4px]",
                !is_disabled && variants[variant],
                is_disabled && "opacity-60 cursor-not-allowed bg-gray-300 text-gray-600",
                className
            )}
            aria-busy={loading}
            {...props}
        >
            {loading ? (
                <span className="flex items-center gap-2">
                    <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" aria-hidden="true"></span>
                    <span>Cargando...</span>
                </span>
            ) : (
                children
            )}
        </button>
    );
};

