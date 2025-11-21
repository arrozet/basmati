import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Neo_Card_Props {
    children: React.ReactNode;
    className?: string;
    title?: string;
}

export const Neo_Card: React.FC<Neo_Card_Props> = ({ children, className, title }) => {
    return (
        <div className={cn("bg-white border-3 border-basmati-black shadow-hard p-4", className)}>
            {title && <h3 className="font-bold text-xl mb-4 border-b-3 border-basmati-black pb-2">{title}</h3>}
            {children}
        </div>
    );
};

