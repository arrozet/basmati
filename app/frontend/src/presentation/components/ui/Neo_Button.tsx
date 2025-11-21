import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Neo_Button_Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'success';
}

export const Neo_Button: React.FC<Neo_Button_Props> = ({ 
    children, 
    className, 
    variant = 'primary', 
    ...props 
}) => {
    const variants = {
        primary: 'bg-basmati-yellow hover:bg-[#d9ae42]',
        secondary: 'bg-white hover:bg-gray-100',
        danger: 'bg-basmati-red text-white hover:bg-[#e05a5a]',
        success: 'bg-basmati-green hover:bg-[#3dbcb3]',
    };

    return (
        <button 
            className={cn(
                "border-3 border-basmati-black shadow-hard px-6 py-2 font-bold text-basmati-black transition-all",
                "active:shadow-none active:translate-x-[4px] active:translate-y-[4px]",
                variants[variant],
                className
            )}
            {...props}
        >
            {children}
        </button>
    );
};

