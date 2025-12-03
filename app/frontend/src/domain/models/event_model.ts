import { Event_Location } from './integration_models';

export interface Event_Comment {
    id: string;
    author_external_id: string;
    author_display_name: string;
    text: string;
    created_at: Date;
}

export interface Event_Attachment {
    id?: string;
    filename: string;
    url: string;
    size: number;
    mime_type: string;
    uploaded_at?: Date;
    uploaded_by: string;
    is_image: boolean;
    thumbnail_url?: string;
}

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
    /** Lista de archivos adjuntos (imágenes) */
    attachments?: Event_Attachment[];
    /** Lista de comentarios asociados */
    comments?: Event_Comment[];
}
