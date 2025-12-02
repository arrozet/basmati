import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface CalendarVisibilityContextType {
    hidden_calendar_ids: Set<string>;
    toggle_visibility: (calendar_id: string) => void;
    set_visibility: (calendar_id: string, is_visible: boolean) => void;
    is_visible: (calendar_id: string) => boolean;
}

const CalendarVisibilityContext = createContext<CalendarVisibilityContextType | undefined>(undefined);

export const CalendarVisibilityProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [hidden_calendar_ids, set_hidden_calendar_ids] = useState<Set<string>>(() => {
        try {
            const saved = localStorage.getItem('hidden_calendar_ids');
            return saved ? new Set(JSON.parse(saved)) : new Set();
        } catch (e) {
            console.error("Failed to parse hidden_calendar_ids from localStorage", e);
            return new Set();
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem('hidden_calendar_ids', JSON.stringify(Array.from(hidden_calendar_ids)));
        } catch (e) {
            console.error("Failed to save hidden_calendar_ids to localStorage", e);
        }
    }, [hidden_calendar_ids]);

    const toggle_visibility = (calendar_id: string) => {
        set_hidden_calendar_ids(prev => {
            const next = new Set(prev);
            if (next.has(calendar_id)) {
                next.delete(calendar_id);
            } else {
                next.add(calendar_id);
            }
            return next;
        });
    };

    const set_visibility = (calendar_id: string, is_visible: boolean) => {
        set_hidden_calendar_ids(prev => {
            const next = new Set(prev);
            if (is_visible) {
                next.delete(calendar_id);
            } else {
                next.add(calendar_id);
            }
            return next;
        });
    };

    const is_visible = (calendar_id: string) => !hidden_calendar_ids.has(calendar_id);

    return (
        <CalendarVisibilityContext.Provider value={{ 
            hidden_calendar_ids,
            toggle_visibility, 
            set_visibility,
            is_visible
        }}>
            {children}
        </CalendarVisibilityContext.Provider>
    );
};

export const use_calendar_visibility = () => {
    const context = useContext(CalendarVisibilityContext);
    if (context === undefined) {
        throw new Error('use_calendar_visibility must be used within a CalendarVisibilityProvider');
    }
    return context;
};

