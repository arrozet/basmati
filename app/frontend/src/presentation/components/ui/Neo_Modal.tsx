import React, { useEffect, useRef } from 'react';
import { Neo_Button } from './Neo_Button';
import { clsx } from 'clsx';

interface Neo_Modal_Props {
    is_open: boolean;
    on_close: () => void;
    on_confirm?: () => void;
    title: string;
    children: React.ReactNode;
    confirm_text?: string;
    cancel_text?: string;
    variant?: 'danger' | 'primary' | 'success';
    loading?: boolean;
}

/**
 * Modal accesible siguiendo WCAG 2.1 AA.
 * Implementa focus trap, aria-modal, y navegación por teclado (Escape para cerrar).
 * @param is_open - Estado de visibilidad del modal.
 * @param on_close - Función para cerrar el modal.
 * @param on_confirm - Función opcional para acción de confirmación.
 * @param title - Título del modal.
 * @param children - Contenido del modal.
 * @param confirm_text - Texto del botón de confirmación.
 * @param cancel_text - Texto del botón de cancelar.
 * @param variant - Variante visual del botón de confirmación.
 * @param loading - Estado de carga durante la confirmación.
 */
export const Neo_Modal: React.FC<Neo_Modal_Props> = ({
    is_open,
    on_close,
    on_confirm,
    title,
    children,
    confirm_text = 'Confirmar',
    cancel_text = 'Cancelar',
    variant = 'primary',
    loading = false
}) => {
    const modal_ref = useRef<HTMLDivElement>(null);
    const first_focusable_ref = useRef<HTMLButtonElement>(null);

    useEffect(() => {
        if (!is_open) return;

        // Focus trap: Enfocar el primer elemento cuando se abre
        const timer = setTimeout(() => {
            first_focusable_ref.current?.focus();
        }, 100);

        // Cerrar con tecla Escape
        const handle_escape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                on_close();
            }
        };

        // Trap focus dentro del modal
        const handle_tab = (e: KeyboardEvent) => {
            if (!modal_ref.current) return;
            
            const focusable_elements = modal_ref.current.querySelectorAll<HTMLElement>(
                'button:not([disabled]), [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const first_element = focusable_elements[0];
            const last_element = focusable_elements[focusable_elements.length - 1];

            if (e.key === 'Tab') {
                if (e.shiftKey && document.activeElement === first_element) {
                    e.preventDefault();
                    last_element?.focus();
                } else if (!e.shiftKey && document.activeElement === last_element) {
                    e.preventDefault();
                    first_element?.focus();
                }
            }
        };

        document.addEventListener('keydown', handle_escape);
        document.addEventListener('keydown', handle_tab);

        // Prevenir scroll del body
        document.body.style.overflow = 'hidden';

        return () => {
            clearTimeout(timer);
            document.removeEventListener('keydown', handle_escape);
            document.removeEventListener('keydown', handle_tab);
            document.body.style.overflow = 'unset';
        };
    }, [is_open, on_close]);

    if (!is_open) return null;

    return (
        <div 
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            {/* Overlay */}
            <div 
                className="absolute inset-0 bg-black/60"
                onClick={on_close}
                aria-hidden="true"
            />

            {/* Modal Content */}
            <div 
                ref={modal_ref}
                className={clsx(
                    "relative bg-white border-3 border-basmati-black shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]",
                    "w-full max-w-md p-6 flex flex-col gap-4",
                    "animate-in fade-in zoom-in-95 duration-200"
                )}
            >
                {/* Header */}
                <header className="border-b-3 border-basmati-black pb-3">
                    <h2 
                        id="modal-title" 
                        className="text-2xl font-black uppercase"
                    >
                        {title}
                    </h2>
                </header>

                {/* Body */}
                <div className="py-2">
                    {children}
                </div>

                {/* Footer */}
                <footer className="flex justify-end gap-3 pt-2">
                    <Neo_Button
                        ref={first_focusable_ref}
                        type="button"
                        variant="secondary"
                        onClick={on_close}
                        disabled={loading}
                    >
                        {cancel_text}
                    </Neo_Button>
                    {on_confirm && (
                        <Neo_Button
                            type="button"
                            variant={variant}
                            onClick={on_confirm}
                            loading={loading}
                            disabled={loading}
                        >
                            {confirm_text}
                        </Neo_Button>
                    )}
                </footer>
            </div>
        </div>
    );
};
