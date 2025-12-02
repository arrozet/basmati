export interface Event_Model {
    id: string;
    title: string;
    start_time: Date;
    end_time: Date;
    description?: string;
    calendar_id: string;
    /** Color heredado del calendario asociado (se enriquece en el frontend) */
    color?: string;
}

