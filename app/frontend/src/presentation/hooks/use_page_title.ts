import { useEffect } from 'react';

/**
 * Hook personalizado para actualizar el título de la página.
 * @param title - El título que se mostrará en la pestaña del navegador.
 */
export const use_page_title = (title: string) => {
    useEffect(() => {
        const prevTitle = document.title;
        document.title = `${title} | Basmati`;

        return () => {
            document.title = prevTitle;
        };
    }, [title]);
};

