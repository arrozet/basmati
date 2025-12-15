import React from 'react';

interface AvatarProps {
    src?: string | null;
    alt: string;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
}

/**
 * Componente de Avatar.
 * Muestra la imagen del usuario o sus iniciales si no hay imagen.
 */
export const Avatar: React.FC<AvatarProps> = ({ 
    src, 
    alt, 
    size = 'md',
    className = ''
}) => {
    // Calcular iniciales
    const get_initials = (name: string) => {
        return name
            .split(' ')
            .map(part => part[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    };

    const size_classes = {
        sm: 'w-8 h-8 text-xs',
        md: 'w-10 h-10 text-sm',
        lg: 'w-12 h-12 text-base',
        xl: 'w-16 h-16 text-lg'
    };

    return (
        <div 
            className={`
                relative inline-flex items-center justify-center 
                rounded-full overflow-hidden
                border-2 border-basmati-black 
                bg-basmati-yellow text-basmati-black font-bold
                ${size_classes[size]}
                ${className}
            `}
            role="img"
            aria-label={alt}
        >
            {src ? (
                <img 
                    src={src} 
                    alt={alt} 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                        // Fallback a iniciales si la imagen falla
                        e.currentTarget.style.display = 'none';
                        const parent = e.currentTarget.parentElement;
                        if (parent) {
                            const span = document.createElement('span');
                            span.textContent = get_initials(alt);
                            parent.appendChild(span);
                        }
                    }}
                />
            ) : (
                <span>{get_initials(alt)}</span>
            )}
        </div>
    );
};

