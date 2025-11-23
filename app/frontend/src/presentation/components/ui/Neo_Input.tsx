import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Neo_Input_Props extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helper_text?: string;
}

/**
 * Componente de input accesible siguiendo estándares WCAG 2.1 AA.
 * @param label - Etiqueta descriptiva del campo (asociada automáticamente al input).
 * @param error - Mensaje de error para mostrar debajo del input.
 * @param helper_text - Texto de ayuda contextual.
 * @param props - Props nativas de HTMLInputElement.
 */
export const Neo_Input: React.FC<Neo_Input_Props> = ({ 
    label, 
    className, 
    error, 
    helper_text,
    id,
    required,
    ...props 
}) => {
    // Generar ID único si no se proporciona uno
    const input_id = id || `input-${React.useId()}`;
    const error_id = error ? `${input_id}-error` : undefined;
    const helper_id = helper_text ? `${input_id}-helper` : undefined;

    return (
        <div className="flex flex-col gap-1">
            {label && (
                <label 
                    htmlFor={input_id} 
                    className="font-bold text-sm text-basmati-black"
                >
                    {label}
                    {required && <span className="text-basmati-red ml-1" aria-label="requerido">*</span>}
                </label>
            )}
            <input 
                id={input_id}
                className={cn(
                    "border-3 border-basmati-black px-3 py-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow ring-offset-2 transition-all bg-white",
                    error && "border-basmati-red focus:ring-basmati-red",
                    props.disabled && "bg-gray-100 cursor-not-allowed opacity-60",
                    className
                )}
                aria-invalid={error ? "true" : "false"}
                aria-describedby={cn(error_id, helper_id)}
                required={required}
                {...props}
            />
            {helper_text && !error && (
                <p id={helper_id} className="text-xs text-gray-600 mt-1">
                    {helper_text}
                </p>
            )}
            {error && (
                <p id={error_id} className="text-xs text-basmati-red font-bold mt-1" role="alert">
                    {error}
                </p>
            )}
        </div>
    );
};

