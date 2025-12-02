import { Event_Location } from './integration_models';

export interface Event_Model {
    id: string;
    title: string;
    start_time: Date;
    end_time: Date;
    description?: string;
    calendar_id: string;
    /** Color heredado del calendario asociado (se enriquece en el frontend) */
    color?: string;
    /** Ubicación del evento con coordenadas para mostrar en mapa */
    location?: Event_Location;
}

