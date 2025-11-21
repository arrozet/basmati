import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Neo_Input_Props extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
}

export const Neo_Input: React.FC<Neo_Input_Props> = ({ label, className, ...props }) => {
    return (
        <div className="flex flex-col gap-1">
            {label && <label className="font-bold text-sm">{label}</label>}
            <input 
                className={cn(
                    "border-3 border-basmati-black p-2 focus:outline-none focus:ring-4 focus:ring-basmati-yellow/50 transition-all bg-white",
                    className
                )}
                {...props}
            />
        </div>
    );
};

